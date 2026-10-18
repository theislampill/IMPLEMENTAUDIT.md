"""Frozen route-projection controls; constructed data grants no native credit."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import sys
import unittest

ROOT = Path(sys.argv.pop(1)).resolve()
spec = importlib.util.spec_from_file_location("oe_native_route_tests", ROOT / "scripts/operational-evidence.py")
oe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oe)
SEED = json.loads((ROOT / "fixtures/operational-evidence/review-native-before.json").read_bytes())


from unittest.mock import patch

# These are explicit injected source/interface inputs, never native witnesses.
LANE = PurePosixPath('/r0038-source-interface-fixture')
PEERS = ROOT / 'source-peers/route-graph/skills/implementaudit/scripts'
def load_peer(name):
    path = PEERS / name
    return oe._native_module_from_bytes(path.read_bytes(), path,
        'fixture_' + name.replace('-', '_'), '$fixture.owner')
RT = load_peer('route-transaction.py')
WG = load_peer('compile-work-graph.py')

def h(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()).hexdigest()

def ident(text):
    return {'identity': text, 'digest': 'sha256:' + h({'identity': text})}

def seal(value):
    value = copy.deepcopy(value)
    value.pop('digest', None)
    value['digest'] = h(value)
    return value

def record(root):
    scope = ident('review:bounded')
    boundary = {'kind': 'handoff-resume', 'event_id': 'nonprotected-source-control'}
    boundary['digest'] = 'sha256:' + h(boundary)
    action = {'identity': 'review', 'class': 'INDEPENDENT_REVIEW', 'argv': ['route-trigger', 'INDEPENDENT_REVIEW']}
    action['digest'] = 'sha256:' + h(action)
    return dict(schema='implementaudit.route-decision.v1', predicate_version='R0033.route-predicate.v1',
        controller_id='bounded-control', claim_id='1' * 32, explicit_run_root=str(root),
        continuity_generation='G000A', continuity_receipt='refs/implementaudit/continuity-receipts/bounded-control/G000A@' + 'a' * 40,
        host_id='source-control-host', host_session_id='source-control-session', host_binding_generation='G000B',
        host_correlation_id='sha256:' + 'b' * 64, scope=scope, boundary=boundary, action=action,
        inputs=[dict(identity='test-input', path='input.txt', digest='sha256:' + 'c' * 64, status='CURRENT')],
        record_identity='sha256:' + 'd' * 64, expiry_fingerprint='sha256:' + 'e' * 64,
        decision='REQUIRED', classification='MECHANICALLY_REQUIRED', route_transaction_id='sha256:' + 'f' * 64,
        obligation_id='sha256:' + '1' * 64, route_state='UNSATISFIED')

def summary(rec):
    return dict(controller_id=rec['controller_id'], controller_record_oid='2' * 40,
        ref='refs/implementaudit/route-decisions/' + rec['controller_id'], record_oid='3' * 40,
        **{k: rec[k] for k in ('record_identity', 'decision', 'classification', 'route_transaction_id', 'obligation_id', 'route_state')})

def export_value(rec):
    """Actual new adapter, with pre-existing native IO predicates injected."""
    route = summary(rec)
    with patch.object(RT, 'validate_pure_current_route', return_value=route), \
         patch.object(RT, 'current_ref', return_value=(route['record_oid'], rec)), \
         patch.object(RT, 'validate_canonical_route_record_bytes'):
        return RT.read_current_route_scope_v1(LANE, rec['controller_id'])

def binding(rec):
    return dict(acquisition='NATIVE_CONTINUITY_VERIFIED', controller=rec['controller_id'], claim=rec['claim_id'],
        receipt=rec['continuity_receipt'], epoch=rec['continuity_generation'], candidate_head='4' * 40,
        candidate_tree='5' * 40, worktree_digest='6' * 64, continuity_helper_digest='7' * 64,
        read_set={}, input_root_identity=hashlib.sha256(str(LANE).encode()).hexdigest())

def node(name, *, kind='TASK', scopes=(), requires=()):
    return dict(id=name, parent=None if name == 'root' else 'root', kind=kind, state='OPEN', requires=list(requires),
        optional=[], reads=[], writes=[], acceptance=[], resources=[], authority=[], effect='READ_ONLY',
        authorization='PERMITTED', independence='KNOWN', resource_demand=1, rank=0, route_scopes=list(scopes),
        logical_delivery=None, future_consumer=None, invalidators=[], independent_results=True,
        context=dict(locality='GOVERNOR', governor_cost=1, child_cost=2, return_cost=1, useful_value=3), done_evidence=None)

def fenced(value):
    return ('```implementaudit-work-graph\n' + json.dumps(value, ensure_ascii=False) + '\n```\n').encode()

def snapshot(rec, *, version=2):
    first = dict(schema='implementaudit.work-graph-route-fact.v1',
        scope=rec['scope']['identity'], obligation=rec['obligation_id'], generation='G000A', binding='legacy',
        continuity='legacy', status='SATISFIED', satisfaction='caller-yes', expected_satisfaction='caller-yes', source_digest='9' * 64)
    nodes = [node('root', kind='PLAN'), node('scoped', scopes=[rec['scope']['identity']]),
        node('scoped_two', scopes=[rec['scope']['identity'], 'second-boundary']),
        node('dependent', requires=['scoped']), node('independent'), node('uncovered', scopes=['second-boundary'])]
    state = dict(schema='implementaudit.native-state.v1', campaign='source-control', root='root', original_scope='source-interface',
        nodes=sorted(n['id'] for n in nodes), event=dict(id='event-one', kind='REDERIVE', subject='root'),
        context=dict(host_capacity=4, operator_ceiling=None, reserve=0, route_facts=[] if version == 2 else [first], outstanding_deliveries=[]))
    return {'STATE.md': fenced(state), 'ROADMAP.md': fenced(dict(schema='implementaudit.native-roadmap.v1', phases=[])),
            'tasks/controls.md': fenced(dict(schema='implementaudit.native-spec.v1', nodes=nodes))}

def native_compile(rec):
    observed = WG._RouteScopeObservation(export_value(rec), WG._NATIVE_ROUTE_OBSERVATION_KEY)
    # Explicit fixture injection. This is not acquired native evidence.
    return WG._compile_native_documents_v1(snapshot(rec), binding(rec), _route_observation=observed)

class NativeRouteProjectionTests(unittest.TestCase):
    def test_source_peer_inventory_and_cross_source_pins(self):
        for group in ("route-graph", "native-runtime"):
            directory = ROOT / "source-peers" / group
            manifest = json.loads((directory / "SOURCE_MANIFEST.json").read_bytes())
            declared = set()
            for row in manifest["files"]:
                path = ROOT / row["path"]
                self.assertFalse(path.is_symlink())
                self.assertEqual(path.resolve(), path)
                self.assertTrue(path.is_relative_to(directory))
                self.assertEqual(path.relative_to(directory).as_posix(), row["materialized_path"])
                self.assertNotIn(path, declared)
                declared.add(path)
                raw = path.read_bytes()
                self.assertEqual(len(raw), row["bytes"])
                self.assertEqual(hashlib.sha256(raw).hexdigest(), row["sha256"])
            actual = {p for p in directory.rglob("*") if p.is_file() and p.name != "SOURCE_MANIFEST.json"}
            self.assertEqual(actual, declared)
        primary = (ROOT / "scripts/operational-evidence.py").read_bytes()
        producer = (PEERS / "route-transaction.py").read_bytes()
        self.assertEqual(WG._NATIVE_STATIC_OWNER_SHA256, hashlib.sha256(primary).hexdigest())
        self.assertEqual(WG._NATIVE_STATIC_OWNER_BYTES, len(primary))
        self.assertEqual(WG._NATIVE_ROUTE_PRODUCER_SHA256, hashlib.sha256(producer).hexdigest())
        self.assertEqual(WG._NATIVE_ROUTE_PRODUCER_BYTES, len(producer))

    def material(self, satisfied=False):
        rec = record(LANE / ".IMPLEMENTAUDIT/runs/native-route-projection")
        baseline = native_compile(rec)
        if satisfied:
            rec["route_state"] = "SATISFIED"
            rec["record_identity"] = "sha256:" + "7" * 64
            rec["lifecycle"] = {"governor_decision": {"digest": "sha256:" + "8" * 64}}
        graph = native_compile(rec)
        cells = [dict(id=n["id"], deps=n["requires"], optional_deps=n["optional"],
            route_scopes=n["route_scopes"], state=n["state"]) for n in baseline["nodes"]]
        canonical = oe.canonical_json_v1(dict(schema="implementaudit.work-graph.v1",
            population={"total_cells": len(cells)}, cells=cells, serialization_groups={}))
        relation = WG.bind_native_route_relation_v1(graph, canonical)
        collections = copy.deepcopy(SEED["collections"])
        native = collections["native_current"]["value"]
        native.update(schema=oe.NATIVE_CURRENT_SCHEMA, route_graph=graph,
            route_relation=relation, canonical_work_graph=canonical.decode(), route=summary(rec))
        native["controller"]["id"] = rec["controller_id"]
        native["claim"]["id"] = rec["claim_id"]
        native["claim"].update(run_id="native-route-projection",
            run_root=".IMPLEMENTAUDIT/runs/native-route-projection")
        native["continuity"].update(generation=rec["continuity_generation"],
            source_epoch=rec["continuity_generation"], receipt=rec["continuity_receipt"])
        native["hot"].update(state_sha256=hashlib.sha256(graph["source_documents"]["STATE.md"].encode()).hexdigest(),
            roadmap_sha256=hashlib.sha256(graph["source_documents"]["ROADMAP.md"].encode()).hexdigest(),
            work_graph_sha256=hashlib.sha256(canonical).hexdigest(),
            work_graph_compiler_sha256=hashlib.sha256((PEERS / "compile-work-graph.py").read_bytes()).hexdigest())
        native["frontier"] = WG.compile_frontier_projection(canonical)
        return collections

    def payload(self, collections):
        native = collections["native_current"]["value"]
        native.pop("semantic_sha256", None)
        native["semantic_sha256"] = hashlib.sha256(oe.canonical_json_v1(native)).hexdigest()
        collections["native_current"]["sha256"] = hashlib.sha256(oe.canonical_json_v1(native)).hexdigest()
        built = oe._build_snapshot_material_v1(native, collections,
            (ROOT / "docs/operational-evidence-schema.json").read_bytes(),
            (ROOT / "scripts/operational-evidence.py").read_bytes())
        return json.loads(built["payload_raw"])

    def test_complete_mapping_reaches_query_why_and_self_diff(self):
        value = self.payload(self.material())
        self.assertEqual(oe.diff_snapshots(value, value)["counts"]["changed"], 0)
        rows = oe._snapshot_query_records_v1(value)
        relation, = [row for row in rows if row["record"]["record_type"] == "RouteAffectedNodes"]
        self.assertEqual(relation["record"]["observation"]["affected_nodes"],
            ["dependent", "root", "scoped", "scoped_two"])
        nodes = [row for row in rows if row["record"]["record_type"] == "GovernedWorkNode"]
        self.assertEqual(len(nodes), 6)
        state = {row["record"]["observation"]["id"]: row["record"]["observation"]["state"] for row in nodes}
        self.assertEqual(state["independent"], "READY")
        self.assertEqual(state["scoped"], "BLOCKED")
        oe.explain_history_why_v1(value, relation["record"]["id"])
        scoped = next(row for row in nodes if row["record"]["observation"]["id"] == "scoped")
        why = oe.explain_history_why_v1(value, scoped["record"]["id"])
        self.assertTrue(any(row["record_type"] == "RouteObligation" for row in why["chain"]))
        self.assertTrue(any(row.get("code") == "NATIVE_ROUTE_SCOPE_UNCOVERED"
            for row in oe.evaluate_currentness(value)["missing_or_omitted_state"]))

    def test_satisfaction_recomputes_only_governed_scope(self):
        before, after = self.payload(self.material()), self.payload(self.material(satisfied=True))
        def nodes(value):
            return {row["record"]["observation"]["id"]: row["record"]
                for row in oe._snapshot_query_records_v1(value)
                if row["record"]["record_type"] == "GovernedWorkNode"}
        left, right = nodes(before), nodes(after)
        self.assertEqual(left["independent"], right["independent"])
        self.assertEqual(left["scoped"]["observation"]["state"], "BLOCKED")
        self.assertEqual(right["scoped"]["observation"]["state"], "READY")
        self.assertEqual(right["scoped_two"]["observation"]["state"], "BLOCKED")
        self.assertIn("ROUTE_SCOPE_UNCOVERED", right["scoped_two"]["observation"]["blocked_reasons"])
        changed = oe.diff_snapshots(before, after)["changed"]
        self.assertFalse(any(row["before"].get("id") == left["independent"]["id"] for row in changed))

    def test_rehashed_wrong_mapping_is_refused(self):
        for field, replacement in (("affected_nodes", ["independent"]),
                ("node_population", ["scoped"]), ("route_transaction_id", "sha256:" + "0" * 64),
                ("receipt", "foreign"), ("scope", ident("foreign"))):
            collections = self.material()
            relation = collections["native_current"]["value"]["route_relation"]
            relation[field] = replacement
            relation.update(seal(relation))
            value = self.payload(collections)
            with self.subTest(field=field), self.assertRaises(oe.OperationalEvidenceError):
                oe.diff_snapshots(value, value)

    def test_changed_canonical_graph_cannot_keep_hot_identity(self):
        collections = self.material()
        native = collections["native_current"]["value"]
        native["canonical_work_graph"] += " "
        value = self.payload(collections)
        with self.assertRaises(oe.OperationalEvidenceError):
            oe.diff_snapshots(value, value)

    def rewrite_graph(self, collections, *, foreign_run=False, foreign_input=False, mixed_edges=False):
        native = collections["native_current"]["value"]
        graph = native["route_graph"]
        sources = {path: value.encode() for path, value in graph["source_documents"].items()}
        bound = {key: value for key, value in graph["binding"].items() if key != "source_digest"}
        scope = copy.deepcopy(graph["route_scope"])
        if foreign_run:
            scope["owner"]["explicit_run_root"] = "/foreign/.IMPLEMENTAUDIT/runs/native-route-projection"
        if foreign_input:
            bound["input_root_identity"] = "0" * 64
        if mixed_edges:
            spec = WG._native_document(sources["tasks/controls.md"], "tasks/controls.md", "implementaudit.native-spec.v1")
            next(n for n in spec["nodes"] if n["id"] == "root")["requires"] = ["scoped"]
            sources["tasks/controls.md"] = fenced(spec)
        observed = WG._RouteScopeObservation(seal(scope), WG._CAPTURED_ROUTE_REPLAY_KEY)
        graph = WG._compile_native_documents_v1(sources, bound, _route_observation=observed)
        cells = [dict(id=n["id"], deps=n["requires"], optional_deps=n["optional"],
            route_scopes=n["route_scopes"], state=n["state"]) for n in graph["nodes"]]
        source = oe.canonical_json_v1(dict(schema="implementaudit.work-graph.v1",
            population={"total_cells": len(cells)}, cells=cells, serialization_groups={}))
        native.update(route_graph=graph, route_relation=WG.bind_native_route_relation_v1(graph, source),
            canonical_work_graph=source.decode(), frontier=WG.compile_frontier_projection(source))
        native["hot"]["work_graph_sha256"] = hashlib.sha256(source).hexdigest()

    def test_resealed_foreign_run_or_input_root_refuses(self):
        for mutation in ({"foreign_run": True}, {"foreign_input": True}):
            collections = self.material()
            self.rewrite_graph(collections, **mutation)
            value = self.payload(collections)
            with self.subTest(mutation=mutation), self.assertRaises(oe.OperationalEvidenceError):
                oe.diff_snapshots(value, value)

    def test_dependency_and_containment_remain_distinct_in_why(self):
        collections = self.material()
        self.rewrite_graph(collections, mixed_edges=True)
        value = self.payload(collections)
        rows = oe.query_family(value, "EXECUTION")["rows"]
        for node in ("root", "scoped"):
            record = next(row["record"] for row in rows if row["record"]["record_type"] == "GovernedWorkNode"
                          and row["record"]["observation"]["id"] == node)
            why = oe.explain_history_why_v1(value, record["id"])
            self.assertEqual(why["status"], "FOUND")
            self.assertTrue({"DEPENDS_ON", "PART_OF"} <= {row["relation_type"] for row in why["relations"]})

    def test_frozen_consumers_never_acquire_native_graph(self):
        value = self.payload(self.material())
        # Load-time guard replaces only the owner's acquisition entry. Its pure
        # validation still runs against actual byte-bound source and operands.
        original = oe._native_module_from_bytes
        def load(*args):
            module = original(*args)
            module.read_native_run_v1 = lambda *a, **k: self.fail("frozen consumer acquired native state")
            return module
        with patch.object(oe, "_native_module_from_bytes", side_effect=load), \
                patch.object(oe, "collect_native_current", side_effect=AssertionError("native refresh")), \
                patch.object(oe.subprocess, "Popen", side_effect=AssertionError("subprocess")):
            oe.diff_snapshots(value, value)
            for family in oe.FAMILIES:
                oe.query_family(value, family)

    def test_legacy_native_facts_preserve_mandatory_mapping_omission(self):
        collections = copy.deepcopy(SEED["collections"])
        native = collections["native_current"]["value"]
        material = oe._build_snapshot_material_v1(native, collections,
            (ROOT / "docs/operational-evidence-schema.json").read_bytes(),
            (ROOT / "scripts/operational-evidence.py").read_bytes())
        payload = json.loads(material["payload_raw"])
        status = oe.evaluate_currentness(payload)
        rows = [row for row in status["missing_or_omitted_state"]
                if row.get("code") == "NATIVE_ROUTE_NODE_MAPPING_UNAVAILABLE"]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["state"], "UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
