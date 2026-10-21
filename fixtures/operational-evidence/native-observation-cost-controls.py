"""Constructed C03 owner-lifetime controls; no native acceptance or timing credit.

The real native 410-second RED is retained outside source. These controls catch
repeated semantic acquisition and loss of terminal guards, using the existing
owner harness only at its explicit filesystem/continuity test boundary.
"""
import argparse
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
SOURCE = ROOT


def load(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


class ObservationCostControls(unittest.TestCase):
    def setUp(self):
        fixture = load(ROOT / 'fixtures/operational-evidence/native-route-cost-controls.py', 'route_harness')
        fixture.PEERS = SOURCE / 'source-peers/route-graph/skills/implementaudit/scripts'
        self.temp = tempfile.TemporaryDirectory(prefix='observation-cost-')
        self.addCleanup(self.temp.cleanup)
        self.h = fixture.Harness(Path(self.temp.name))
        self.refusal = fixture.Refusal
        self.scope = self.h.patched()
        self.scope.__enter__()
        self.addCleanup(self.scope.__exit__, None, None, None)
        self.oe = load(SOURCE / 'scripts/operational-evidence.py', 'observation_primary')
        self.continuity_sources = {'claim_sha256': hashlib.sha256(b'claim fixture').hexdigest(),
                                   'validate_sha256': hashlib.sha256(b'validate fixture').hexdigest()}

    def test_combined_native_episode_observation_has_no_caller_episode_operand(self):
        import inspect
        method = getattr(self.h.wg, 'observe_native_run_episode_sources_v1')
        self.assertEqual(list(inspect.signature(method).parameters),
                         ['run_root', 'repo_root', 'input_root', 'expected_current'])

    @contextlib.contextmanager
    def composed_episode(self, on_episode_close=None, shared_continuity=False):
        h=self.h
        policy={'code_pins':{'implementaudit/scripts/compile-work-graph.py':
                           hashlib.sha256(Path(h.wg.__file__).read_bytes()).hexdigest()}}
        self.episode_events=[]
        @contextlib.contextmanager
        def episode(native):
            self.episode_view, graph_raw, actual=native
            self.assertEqual(actual,dict(repository=str(h.root.absolute()),controller=h.controller,
                module_pin=dict(path=str(Path(h.rt.__file__)),bytes=len(h.producer_bytes),sha256=hashlib.sha256(h.producer_bytes).hexdigest())))
            self.assertEqual(json.loads(self.episode_view.ordinary_result_bytes()),h.expected_result())
            self.assertIs(type(graph_raw),bytes)
            self.episode_events.append('entry')
            yield b'{"status":"AVAILABLE","fixture":"constructed owner boundary"}'
            self.episode_events.append('exit')
            if on_episode_close:on_episode_close()
        owner=types.SimpleNamespace(ordinary_policy_v1=lambda:copy.deepcopy(policy),
                                    _ordinary_episode_observation_v1=episode)
        with h.graph_patched():
            h.graph_binding['continuity_helper_digest']=self.continuity_sources['claim_sha256']
            continuity=h.continuity.side_effect
            def capture(*a,**kw):
                result=continuity(*a)
                if kw.get('_source_reads') is not None:kw['_source_reads'].append(copy.deepcopy(self.continuity_sources))
                if shared_continuity and kw.get('_current_reads') is not None:
                    kw['_current_reads'].append(dict(controller_result=[h.controller,str(h.root),str(h.root),h.current['claim_id']],
                                                     receipt=h.current['continuity_receipt']))
                return result
            compile_docs=h.wg._compile_native_documents_v1.side_effect
            def project(*a,**kw):
                value=compile_docs(*a,**kw)
                if not kw.get('acquire_only'):value['binding']=copy.deepcopy(a[1])
                return value
            with patch.object(h.rt,'_current_controller_from_owner_read_v1',
                    side_effect=lambda *a:copy.deepcopy(h.current),create=True), \
                 patch.object(h.wg,'_native_continuity',side_effect=capture), \
                 patch.object(h.wg,'_compile_native_documents_v1',side_effect=project), \
                 patch.object(h.rt,'_ordinary_receiver_binding_from_read_v1',return_value={'source_pins':{},'policy':policy}), \
                 patch.object(h.rt,'_ordinary_fixed_source_owner_v2',side_effect=lambda *a:contextlib.nullcontext(owner)):
                with h.wg.observe_native_run_episode_sources_v1(h.root,h.root) as raw:
                    yield json.loads(raw)

    def test_shared_actual_continuity_does_not_repeat_nested_owner_invocations(self):
        with self.composed_episode(shared_continuity=True) as value:
            self.assertEqual(value['ordinary_episode']['status'],'AVAILABLE')
        self.assertEqual(self.h.validation.call_count,2)
        self.assertEqual(self.h.rt.current_controller.call_count,0,
                         'R0035 already performs actual fixed-owner currentness at both ends')

    def test_shared_actual_continuity_still_refuses_each_changed_current_field(self):
        for key in self.h.current:
            with self.subTest(key=key):
                original=copy.deepcopy(self.h.current)
                with self.assertRaises((self.refusal,self.h.wg.WorkGraphError)):
                    with self.composed_episode(shared_continuity=True):self.h.current[key]='changed'
                self.h.current=original

    def test_available_episode_and_graph_share_one_actual_route_observation(self):
        with self.composed_episode() as value:
            self.assertEqual(value['ordinary_episode']['status'],'AVAILABLE')
            self.assertEqual(value['continuity_sources'],self.continuity_sources)
            self.assertEqual(self.episode_events,['entry'])
        self.assertEqual(self.episode_events,['entry','exit'])
        self.assertEqual(self.h.validation.call_count,2)
        self.assertEqual(self.h.rt.current_controller.call_count,2)
        with self.assertRaises(self.refusal):self.episode_view.ordinary_result_bytes()

    def test_episode_exit_changes_are_seen_by_final_graph_and_route_guards(self):
        for field in ('document','readset','route'):
            def late_change():
                if field=='document':self.h.graph_snapshot['STATE.md']=b'changed'
                elif field=='readset':self.h.graph_read_set['path:new']={'status':'MISSING','sha256':None}
                else:self.h.input.write_bytes(b'changed')
            with self.subTest(field=field):
                original=self.h.input.read_bytes()
                with self.assertRaises((self.h.wg.WorkGraphError,self.refusal)):
                    with self.composed_episode(late_change):pass
                self.h.input.write_bytes(original)

    def ordinary(self):
        # The preimage uses its existing strict reader at this call site.
        reader = getattr(self.h.rt, 'read_applicable_ordinary_result_v1', self.h.rt.read_current_ordinary_result_v1)
        return reader(self.h.root, self.h.controller)

    def unrelated(self):
        self.h.request['action']['argv'][1] = 'STALE_CONTEXT_RECONSTRUCTION'
        value = {k: v for k, v in self.h.request['action'].items() if k != 'digest'}
        self.h.request['action']['digest'] = 'sha256:' + hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()
        self.h.create_records()

    def test_unrelated_role_only_returns_non_authoritative_floor_without_full_validation(self):
        self.unrelated()
        self.assertEqual(self.ordinary(), {'status': 'CANONICAL_REVIEW_ABSENT', 'canonical_route': None})
        self.assertEqual(self.h.validation.call_count, 0)

    def test_applicable_role_preserves_full_reader_and_oracle(self):
        self.assertEqual(self.ordinary(), self.h.expected_result())
        self.assertEqual(self.h.validation.call_count, 2)

    def test_unrelated_role_still_refuses_noncanonical_record(self):
        self.unrelated()
        self.h.record['record_identity'] = 'sha256:' + '0' * 64
        with self.assertRaises(self.refusal):
            self.ordinary()

    def test_unrelated_role_ref_change_is_not_a_reusable_absence(self):
        self.unrelated()
        original = self.h.rt.validate_canonical_route_record_bytes.side_effect
        def change(*args, **kwargs):
            original(*args, **kwargs)
            self.h.oid = '9' * 40
        with patch.object(self.h.rt, 'validate_canonical_route_record_bytes', side_effect=change):
            with self.assertRaises(self.refusal):
                self.ordinary()

    def test_unrelated_role_source_change_refuses(self):
        self.unrelated()
        original = self.h.rt.validate_canonical_route_record_bytes.side_effect
        def change(*args, **kwargs):
            original(*args, **kwargs)
            self.h.source_digest = 'sha256:' + '9' * 64
        with patch.object(self.h.rt, 'validate_canonical_route_record_bytes', side_effect=change):
            with self.assertRaises(self.refusal):
                self.ordinary()

    @contextlib.contextmanager
    def primary(self, legacy=False, source_observation=False, expected_sources=None):
        h, oe = self.h, self.oe
        with h.graph_patched():
            if source_observation:
                h.graph_binding['continuity_helper_digest'] = self.continuity_sources['claim_sha256']
                continuity = h.continuity.side_effect
                def capture_sources(*a, **kw):
                    value = continuity(*a)
                    if kw.get('_source_reads') is not None:
                        kw['_source_reads'].append(copy.deepcopy(self.continuity_sources))
                    return value
                h.continuity.side_effect = capture_sources
            original = h.wg._compile_native_documents_v1.side_effect
            def project(*args, **kwargs):
                value = original(*args, **kwargs)
                if 'route' in value:
                    value['route_scope'] = value.pop('route')
                if source_observation and not kwargs.get('acquire_only'):
                    value['binding'] = copy.deepcopy(args[1])
                return value
            compiler = h.wg
            if legacy:
                compiler = types.SimpleNamespace(read_native_run_v1=h.wg.read_native_run_v1,
                    bind_native_route_relation_v1=lambda *a: {'scope': 'constructed relation'})
            with patch.object(h.wg, '_compile_native_documents_v1', side_effect=project), \
                    patch.object(h.wg, 'bind_native_route_relation_v1', return_value={'scope': 'constructed relation'}), \
                    patch.object(oe, '_native_module_from_bytes', return_value=compiler), \
                    patch.object(oe, '_native_file', return_value=b'compiler source'), \
                    patch.object(oe, '_native_require_current_receipt', return_value=(
                        Path('claim-run.sh'), b'claim fixture', Path('validate-run-root.sh'), b'validate fixture')) as direct:
                self.direct_receipt = direct
                c = h.current
                args = (h.root, h.root, h.controller, c['controller_record_oid'], c['claim_id'], h.root,
                    c['continuity_generation'], c['continuity_receipt'], c['boundary_kind'],
                    c['boundary_event_id'], c['next_action'], b'canonical graph', Path(h.wg.__file__),
                    b'compiler source', h.rt)
                observer = getattr(oe, '_native_current_observation_v1', None)
                if observer is None:
                    # Exact preimage orchestration; no production path is replaced.
                    route_args = args[1:11] + (h.rt,)
                    route = oe._native_route(*route_args)
                    relation = oe._native_route_relation(h.root, h.root, args[11], route, args[12], args[13], h.rt)
                    yield route, relation
                    if oe._native_route_relation(h.root, h.root, args[11], route, args[12], args[13], h.rt) != relation:
                        raise AssertionError('legacy late relation refusal')
                    if oe._native_route(*route_args) != route:
                        raise AssertionError('legacy late route refusal')
                else:
                    kwargs = ({'continuity_sources': copy.deepcopy(expected_sources or self.continuity_sources)}
                              if source_observation else {})
                    with observer(*args, **kwargs) as value:
                        yield value

    def test_owned_source_observation_reuses_same_actual_R0011_checks(self):
        with self.primary(source_observation=True) as (route, _):
            self.assertEqual(route, self.h.summary())
        self.assertEqual(self.direct_receipt.call_count, 0)
        self.assertEqual(self.h.continuity.call_count, 2)
        self.assertEqual(self.h.validation.call_count, 2)

    def test_legacy_source_observation_keeps_direct_R0011_check(self):
        with self.primary(legacy=True, source_observation=True):
            pass
        self.assertEqual(self.direct_receipt.call_count, 1)

    def test_foreign_executed_helper_bytes_refuse(self):
        wrong = {**self.continuity_sources, 'validate_sha256': '9' * 64}
        with self.assertRaises(self.oe.OperationalEvidenceError):
            with self.primary(source_observation=True, expected_sources=wrong):
                self.fail('foreign helper bytes yielded an accepted observation')

    def test_executed_helper_change_at_close_refuses(self):
        with self.assertRaises(self.oe.OperationalEvidenceError):
            with self.primary(source_observation=True):
                self.continuity_sources['validate_sha256'] = '9' * 64

    def test_primary_one_owner_transaction_preserves_projection(self):
        with self.primary() as (route, (graph, relation)):
            self.assertEqual(route, self.h.summary())
            self.assertEqual(graph['route_scope'], self.h.expected_scope())
            self.assertEqual(relation, {'scope': 'constructed relation'})
        self.assertEqual(self.h.validation.call_count, 2)
        self.assertEqual((self.h.continuity.call_count, self.h.documents.call_count, self.h.readset.call_count), (2, 2, 2))

    def test_legacy_owner_keeps_full_original_checks(self):
        with self.primary(legacy=True) as (route, _):
            self.assertEqual(route, self.h.summary())
        self.assertEqual(self.h.validation.call_count, 6)

    def test_late_input_change_is_rejected_after_caller_use(self):
        with self.assertRaises(self.oe.OperationalEvidenceError):
            with self.primary():
                self.h.input.write_bytes(b'changed after projection')

    def test_provisional_projection_mutation_is_rejected(self):
        for proof in (False, True):
            with self.subTest(source_observation=proof), self.assertRaises(self.oe.OperationalEvidenceError):
                with self.primary(source_observation=proof) as (_, (graph, _)):
                    graph['nodes'][0]['id'] = 'forged'

    def test_late_native_document_readset_receipt_and_producer_changes_refuse(self):
        changes = (
            lambda: self.h.graph_snapshot.update({'STATE.md': b'changed'}),
            lambda: self.h.graph_read_set.update({'path:new': {'status': 'MISSING', 'sha256': None}}),
            lambda: self.h.graph_binding.update(receipt='changed'),
            lambda: setattr(self.h, 'producer_bytes', b'changed owner source'),
        )
        for change in changes:
            with self.subTest(change=change):
                self.h.producer_bytes = b'fixed source fixture'
                with self.assertRaises(self.oe.OperationalEvidenceError):
                    with self.primary():
                        change()

    def test_expected_current_identity_cannot_be_replaced_by_projection(self):
        original = self.h.expected_scope()
        for field in ('controller_record_oid', 'claim_id', 'continuity_receipt', 'boundary_event_id', 'next_action'):
            with self.subTest(field=field):
                old = self.h.current[field]
                # Change the corroborating collector operand only, not the owner.
                with patch.object(self.h.rt, 'current_controller', return_value=copy.deepcopy(self.h.current)):
                    self.h.current[field] = 'foreign'
                    with self.assertRaises(self.oe.OperationalEvidenceError):
                        with self.primary():
                            pass
                self.h.current[field] = old
        self.assertEqual(self.h.expected_scope(), original)

    def test_valid_pending_stale_request_keeps_current_owner_corroboration(self):
        for field in ('boundary_kind', 'boundary_event_id', 'next_action'):
            with self.subTest(field=field):
                h = self.h
                original = copy.deepcopy(h.request)
                if field == 'next_action':
                    h.request['scope'] = {'identity': 'retained-prior-scope'}
                    h.request['scope']['digest'] = h.rt.digest_json(h.request['scope'])
                else:
                    boundary = h.request['boundary']
                    boundary['kind' if field == 'boundary_kind' else 'event_id'] = (
                        'new-session' if field == 'boundary_kind' else 'retained-prior-boundary')
                    boundary['digest'] = h.rt.digest_json({k: boundary[k] for k in ('kind', 'event_id')})
                h.create_records()
                h.record.pop('lifecycle')
                h.record.update(route_state=None, obligation_id=None, predecessor_record_oid=None,
                                child_lifecycle_owned=False, consumed_record_oid=None, expires_on=h.rt.EXPIRES_ON)
                h.record['record_identity'] = h.rt.digest_json({k: v for k, v in h.record.items() if k != 'record_identity'})
                h.rt.validate_route_record_semantics(h.root, h.controller, h.oid, h.record)
                self.assertEqual(h.record['decision'], 'PENDING')
                for proof in (False, True):
                    with self.primary(source_observation=proof) as (route, _):
                        self.assertEqual(route['decision'], 'PENDING')
                h.request = original
                h.create_records()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo-root', type=Path, default=ROOT)
    parser.add_argument('--source-root', type=Path)
    args, remainder = parser.parse_known_args()
    ROOT = args.repo_root.resolve(strict=True)
    SOURCE = (args.source_root or ROOT).resolve(strict=True)
    unittest.main(argv=[__file__, *remainder])
