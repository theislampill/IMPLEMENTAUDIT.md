#!/usr/bin/env python3
"""Offline unit controls for the V21 public-input G1/G3 operator.

No network, no root, no subprocess, no native case, no hosted operation. Every
mutation runs on a private temporary copy of the packet. Any Root, receiver or
role-1 body constructed here is a TEST-ONLY fixture and is never written into
the repository. Host-only properties are listed in HOST_ONLY at the bottom.
"""
import copy
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile
import types
import unittest

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
PACKET = EPISODE / 'packet'
ENTRY = EPISODE / 'entry'
REPO = EPISODE.parents[1]
WORKFLOW = REPO / '.github/workflows/dg16-r5-g1-hosted-episode-v21.yml'
V21 = dict(commit='338c4c36d2ac95ca24345bc92fe8c53d66eaa15d', tree='53498df783ed441744ae5080982c2d5e59c34bbc')
SUCC = 'OPUS-5.5-DG16, sole DG16 executor designated by owner'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def pretty(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def compact(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def load(path, name, **inject):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    module.__dict__.update(inject)
    exec(compile(Path(path).read_bytes(), str(path), 'exec'), module.__dict__)
    return module


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix='v21-operator-'))
        self.packet = self.tmp / 'packet'
        shutil.copytree(PACKET, self.packet)
        self.S = load(self.packet / 'public_inputs.py', 'v21_selector_under_test')
        self.E = load(self.packet / 'evidence_io.py', 'v21_evidence_under_test')

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def index(self):
        return json.loads((self.packet / 'PUBLIC_INPUT_INDEX.json').read_bytes())

    def write_index(self, value):
        raw = pretty(value)
        (self.packet / 'PUBLIC_INPUT_INDEX.json').write_bytes(raw)
        self.S.INDEX_SHA256 = sha(raw)
        return raw

    def body(self, name):
        return (self.packet / 'public-inputs' / name).read_bytes()

    def put(self, role, raw, index=None):
        """Replace one role body and re-pin its index row (test-only)."""
        index = index or self.index()
        row = index['roles'][str(role)]
        (self.packet / 'public-inputs' / row['name']).write_bytes(raw)
        row.update(bytes=len(raw), sha256=sha(raw))
        self.write_index(index)
        return index

    def make_admission(self, index=None):
        """TEST-ONLY role-1 body satisfying the prospective contract on the shipped roles 2-11."""
        index = index or self.index()
        inputs = {}
        for key, row in index['roles'].items():
            if key != '1':
                inputs[row['name']] = sha(self.body(row['name']))
        for row in index['support']:
            inputs[row['name']] = sha(self.body(row['name']))
        return compact(dict(schema='dg16.current-core-host-root-admission.v2', issuer='R5_ROOT_GOVERNOR', successor=SUCC,
            source_commit=V21['commit'], source_tree=V21['tree'],
            workflow_branch='engineering/opus-dg16-g1-v21-trigger-20261126',
            control_branch='engineering/opus-dg16-g3-v21-control-20261126',
            source_branch='engineering/opus-dg16-v21-source-20261126', run_attempt=1, automatic_retry=False,
            original_awards=[], prospective_operation='ONE_ORIGINAL_G1_PAIR_AND_TWO_STAGE_CORE_G3_L04_SEPARATE',
            component_scope='CORE_G1_Q06_NATURAL_L04_SEPARATE',
            input_route='PINNED_PUBLIC_INPUT_SELECTOR_NO_CARRIER_NO_PRIVATE_SENDER', input_sha256=inputs))

    def all_present(self, admission=True):
        """TEST-ONLY: mark every HELD row present (role 1 test body; role 8 as shipped bytes)."""
        index = self.index()
        if admission:
            raw = self.make_admission(index)
            (self.packet / 'public-inputs' / 'COMPOSITION_ROOT_ADMISSION.json').write_bytes(raw)
            index['roles']['1'] = dict(role=1, name='COMPOSITION_ROOT_ADMISSION.json', state='PRESENT',
                issuer='R5_ROOT_GOVERNOR', issuer_field='issuer', subject_field=None, bytes=len(raw), sha256=sha(raw),
                origin='TEST-ONLY')
        row8 = index['roles']['8']
        row8.pop('held_subrecords')
        row8['state'] = 'PRESENT'
        index['contract_holds'] = {}
        self.write_index(index)
        return index

    def refuses(self, code, function, *args, **kwargs):
        with self.assertRaises(Exception) as caught:
            function(*args, **kwargs)
        self.assertEqual(caught.exception.args[0], code)


class SelectorControls(Base):
    def test_shipped_index_refuses_first_held_role_before_any_body_read(self):
        reads = []
        original = self.S.read_exact
        self.S.read_exact = lambda path, maximum: (reads.append(Path(path).name), original(path, maximum))[1]
        before = sorted((p.relative_to(self.packet).as_posix(), sha(p.read_bytes())) for p in self.packet.rglob('*') if p.is_file())
        self.refuses('PUBLIC_INPUT_HELD_ROLE_01', self.S.admit, self.packet)
        self.assertEqual(reads, ['PUBLIC_INPUT_INDEX.json'])
        after = sorted((p.relative_to(self.packet).as_posix(), sha(p.read_bytes())) for p in self.packet.rglob('*') if p.is_file())
        self.assertEqual(before, after)

    def test_held_report_names_owners_and_decisions(self):
        _, value = self.S.load_index(self.packet)
        report = self.S.held_report(value)
        codes = [r['code'] for r in report]
        self.assertEqual(codes[0], 'PUBLIC_INPUT_HELD_ROLE_01')
        self.assertIn('PUBLIC_INPUT_HELD_ROLE_08', codes)
        self.assertIn('PUBLIC_INPUT_HELD_CONTRACT_G1_HOST_PROFILE_ADOPTION_ROUTE', codes)
        self.assertIn('PUBLIC_INPUT_HELD_CONTRACT_BOOTSTRAP_ADMISSION', codes)
        sub = [r for r in report if r['code'] == 'PUBLIC_INPUT_HELD_ROLE_08'][0]
        self.assertEqual((sub['subrecord'], sub['owner']), ('ROOT_SOURCE_RECEIVING.json', 'Astra Root'))
        self.assertTrue(all(r['owner'] and r['decision_ref'] for r in report))

    def test_first_held_order(self):
        index = self.index()
        raw = self.make_admission(index)
        (self.packet / 'public-inputs' / 'COMPOSITION_ROOT_ADMISSION.json').write_bytes(raw)
        index['roles']['1'] = dict(role=1, name='COMPOSITION_ROOT_ADMISSION.json', state='PRESENT', issuer='R5_ROOT_GOVERNOR',
            issuer_field='issuer', subject_field=None, bytes=len(raw), sha256=sha(raw), origin='TEST-ONLY')
        self.write_index(index)
        self.refuses('PUBLIC_INPUT_HELD_ROLE_08', self.S.admit, self.packet)
        index['roles']['8'].pop('held_subrecords')
        index['roles']['8']['state'] = 'PRESENT'
        self.write_index(index)
        self.refuses('PUBLIC_INPUT_HELD_CONTRACT_G1_HOST_PROFILE_ADOPTION_ROUTE', self.S.admit, self.packet)
        held = dict(index['roles']['5'])
        index['roles']['5'] = dict(role=5, name=held['name'], state='HELD_PENDING_ROOT_DECISION', owner='x', decision_ref='y',
                                   expected_issuer='z')
        self.write_index(index)
        self.refuses('PUBLIC_INPUT_HELD_ROLE_05', self.S.admit, self.packet)

    def test_selector_acquires_exact_bodies(self):
        index = self.all_present()
        selected = self.S.admit(self.packet)
        for key, row in index['roles'].items():
            self.assertEqual(selected['bodies'][int(key)], self.body(row['name']))
        self.assertEqual(set(selected['support']), {'PLACEMENT_ARTIFACT_MANIFEST.json'})
        self.assertEqual(selected['index_sha256'], self.S.INDEX_SHA256)

    def test_byte_digest_subject_issuer_mismatch_refused(self):
        index = self.all_present()
        name = index['roles']['3']['name']
        raw = self.body(name)
        (self.packet / 'public-inputs' / name).write_bytes(raw + b' ')
        self.refuses('PUBLIC_INPUT_BYTE_MISMATCH', self.S.admit, self.packet)
        (self.packet / 'public-inputs' / name).write_bytes(raw.replace(b'UNPROVED', b'UNPROVEN'))
        self.refuses('PUBLIC_INPUT_DIGEST_MISMATCH', self.S.admit, self.packet)
        self.put(3, raw.replace(V21['commit'].encode(), b'e76a07b2bae7c945e5a9d529ed8cf9069f4c9064'), index)
        self.refuses('PUBLIC_INPUT_SUBJECT_MISMATCH', self.S.admit, self.packet)
        self.put(3, raw.replace(b'"Astra Root"', b'"Other Root"'), self.index())
        self.refuses('PUBLIC_INPUT_ISSUER_MISMATCH', self.S.admit, self.packet)

    def test_missing_and_extra_body_refused(self):
        self.all_present()
        extra = self.packet / 'public-inputs' / 'EXTRA.json'
        extra.write_bytes(b'{}\n')
        self.refuses('PUBLIC_INPUT_EXTRA_BODY', self.S.admit, self.packet)
        extra.unlink()
        (self.packet / 'public-inputs' / 'PACKAGE_ROOT_RECEIVING.json').unlink()
        self.refuses('PUBLIC_INPUT_MISSING_BODY', self.S.admit, self.packet)

    def test_index_pin_and_carrier_not_selected(self):
        index = self.all_present()
        raw = (self.packet / 'PUBLIC_INPUT_INDEX.json').read_bytes()
        (self.packet / 'PUBLIC_INPUT_INDEX.json').write_bytes(raw.replace(b'"original_awards": []', b'"original_awards": [] '))
        self.refuses('PUBLIC_INPUT_INDEX_PIN', self.S.admit, self.packet)
        index['carrier_selected'] = True
        self.write_index(index)
        self.refuses('PUBLIC_INPUT_INDEX_SCOPE', self.S.admit, self.packet)
        index['carrier_selected'] = False
        self.write_index(index)
        (self.packet / 'carrier').mkdir()
        self.refuses('PUBLIC_INPUT_CARRIER_OR_PRIVATE_ROUTE_PRESENT', self.S.admit, self.packet)
        (self.packet / 'carrier').rmdir()
        (self.packet / 'private-inputs').mkdir()
        self.refuses('PUBLIC_INPUT_CARRIER_OR_PRIVATE_ROUTE_PRESENT', self.S.admit, self.packet)

    def test_shipped_population_has_no_carrier_or_sender(self):
        self.assertFalse((PACKET / 'carrier').exists())
        manifest = json.loads((ENTRY / 'PUBLIC_PACKET_MANIFEST.json').read_bytes())
        self.assertFalse([n for n in manifest['members'] if n.startswith('carrier/') or 'sender' in n])
        text = WORKFLOW.read_text()
        for word in ('DG16_CARRIER_READ_TOKEN', 'recipient', 'host_tool', 'pro/', 'carrier'):
            self.assertNotIn(word, text)
        historical = json.loads((EPISODE / 'HISTORICAL_CARRIER.json').read_bytes())
        self.assertIn('qualification/dg16-r5-g1-hosted-episode/carrier/carrier.py', historical['excluded'])


class GateEntry(Base):
    def test_gate_refuses_role1_with_report(self):
        gate = load(ENTRY / 'admit_public_inputs.py', 'v21_gate_under_test')
        code, value = gate.gate(PACKET)
        self.assertEqual((code, value['status'], value['code']), (1, 'REFUSED', 'PUBLIC_INPUT_HELD_ROLE_01'))
        self.assertEqual(value['effects_before_refusal'], [])
        self.assertTrue(value['held'])


class StubPlacement:
    PROFILE = 'FRESH_ROOT_ISLAND_FIXED_SIBLINGS_V1'

    def __init__(self, root):
        self.root = root

    def paths(self, context):
        return dict(source=self.root / 'source', private_output=self.root / 'output', packet=self.root / 'packet')

    def require_current(self, context, packet, phase='live'):
        return dict(stub=True, phase=phase)


class CompositionControls(Base):
    def composition(self, state='REVIEWED_EXACT_COMPOSITION'):
        hc_path = self.packet / 'HOST_COMPOSITION.json'
        value = json.loads(hc_path.read_bytes())
        value['state'] = state
        value['public_input_index'] = dict(path='PUBLIC_INPUT_INDEX.json', sha256=self.S.INDEX_SHA256)
        raw = compact(value)
        hc_path.write_bytes(raw)
        module = load(self.packet / 'host_composition.py', 'v21_composition_under_test', _HOST_EVIDENCE_IO=self.E,
                      _ROOT_PLACEMENT=StubPlacement(self.tmp), _PUBLIC_INPUTS=self.S)
        module.BINDING_SHA256 = sha(raw)
        return module

    def launch(self, module):
        g3 = types.SimpleNamespace(NATURAL_SCOPE='ORIGINAL_RLGWO_PREREQUISITE_AND_NATURAL_SHAPE_NOT_RECEIVED')
        context = dict(branch='engineering/opus-dg16-g1-v21-trigger-20261126')
        return module.require_launch(self.packet, self.tmp / 'source', self.tmp / 'output', context, g3)

    def test_shipped_state_refuses_held_before_composition(self):
        module = self.composition(state='PROPOSED_EXACT_COMPOSITION_PENDING_REVIEW_AND_HELD_INPUTS')
        self.refuses('PUBLIC_INPUT_HELD_ROLE_01', self.launch, module)

    def test_actual_root_bodies_satisfy_adapted_checks(self):
        self.all_present()
        module = self.composition()
        approved = self.launch(module)
        self.assertEqual(set(approved['bodies']), {'root_admission', 'placement_receiving', 'placement_evidence_index',
                                                   'native_applicability_adoption'})
        self.assertEqual(approved['placement']['root']['decision'], 'ACCEPTED_AT_HOST_PLACEMENT_DIAGNOSTIC_SCOPE')

    def test_unreviewed_composition_refused(self):
        self.all_present()
        module = self.composition(state='PROPOSED_EXACT_COMPOSITION_PENDING_REVIEW_AND_HELD_INPUTS')
        self.refuses('CURRENT_HOST_COMPOSITION_UNRESOLVED', self.launch, module)

    def test_tampered_records_refused(self):
        index = self.all_present()
        module = self.composition()
        raw3 = self.body('COMPOSITION_PLACEMENT_RECEIVING.json')
        self.put(3, raw3.replace(b'ACCEPTED_PUBLIC_REPLACEMENT_AT_DIAGNOSTIC_SCOPE', b'ACCEPTED_PUBLIC_REPLACEMENT_AT_FULL_SCOPE'), index)
        self.refuses('WORKING_PLACEMENT_SCOPE_REFUSED', module.check_placement, self.S.admit(self.packet)['bodies'],
                     self.S.admit(self.packet)['support'])
        self.put(3, raw3, self.index())
        raw2 = self.body('COMPOSITION_NATIVE_APPLICABILITY_ADOPTION.json')
        self.put(2, raw2.replace(b'"changed_members": 20', b'"changed_members": 3'), self.index())
        self.refuses('NATIVE_APPLICABILITY_ADOPTION_REQUIRED', module.check_native_adoption,
                     self.body('COMPOSITION_NATIVE_APPLICABILITY_ADOPTION.json'), self.packet)

    def test_admission_contract(self):
        self.all_present()
        module = self.composition()
        selected = self.S.admit(self.packet)
        context = dict(branch='engineering/opus-dg16-g1-v21-trigger-20261126')
        module.check_admission(selected['bodies'][1], selected['bodies'], selected['support'], context)
        old = selected['bodies'][1].replace(SUCC.encode(), b'PRO-EXECUTOR-01, designated by owner')
        self.refuses('ROOT_ADMISSION_SCOPE_REFUSED', module.check_admission, old, selected['bodies'], selected['support'], context)
        value = json.loads(selected['bodies'][1])
        value['input_sha256'].pop('SOURCE_ACQUISITION.json')
        self.refuses('ROOT_ADMISSION_BODY_BINDING', module.check_admission, compact(value), selected['bodies'],
                     selected['support'], context)
        self.refuses('ROOT_ADMISSION_SCOPE_REFUSED', module.check_admission, selected['bodies'][1], selected['bodies'],
                     selected['support'], dict(branch='pro/dg16-g132-original-20261120-01'))


class G3Base(Base):
    def g3(self):
        return load(self.packet / 'g3_receiving.py', 'v21_g3_under_test')

    def scope_dir(self):
        root = self.tmp / 'scope'
        root.mkdir()
        for name in ('SOURCE_ACQUISITION.json', 'PACKAGE_ROOT_RECEIVING.json', 'PACKAGE_BODY_RECEIVING.json',
                     'PACKAGE_TERMINAL_RECEIVING.json'):
            (root / name).write_bytes(self.body(name))
        return root


class PackageRelationControls(G3Base):
    def with_root_source(self, mutate=None):
        """TEST-ONLY Root source receiving inserted into role 8; ORIGINAL_SCOPE re-pinned in the temp copy."""
        acquisition = json.loads(self.body('SOURCE_ACQUISITION.json'))
        manifest = (self.packet / 'SOURCE_MANIFEST.json').read_bytes()
        if mutate:
            mutate(acquisition)
        root = compact(dict(issuer='Astra Root', subject=V21, decision='ACCEPTED_V21_SELECTED_SOURCE_MANIFEST_FOR_THIS_OPERATION',
                            source_manifest=dict(bytes=len(manifest), sha256=sha(manifest)), files=1982, bytes=175292551,
                            package_relation_sha256=sha(compact(acquisition['package_relation'])), original_awards=[])).decode()
        acquisition['evidence']['ROOT_SOURCE_RECEIVING.json'] = dict(bytes=len(root.encode()), sha256=sha(root.encode()), text=root)
        raw = pretty(acquisition)
        (self.packet / 'public-inputs' / 'SOURCE_ACQUISITION.json').write_bytes(raw)
        scope = json.loads((self.packet / 'ORIGINAL_SCOPE.json').read_bytes())
        scope['received_inputs']['SOURCE_ACQUISITION.json'] = dict(bytes=len(raw), sha256=sha(raw))
        scope['retained_package_relation'] = acquisition['package_relation']
        scope_raw = pretty(scope)
        (self.packet / 'ORIGINAL_SCOPE.json').write_bytes(scope_raw)
        g3 = self.g3()
        g3.SCOPE_SHA = sha(scope_raw)
        return g3

    def test_shipped_role8_refuses_root_source_receiving_held(self):
        self.refuses('ROOT_SOURCE_RECEIVING_HELD', self.g3().scope_input_bodies, self.scope_dir())

    def test_relation_accepts_actual_roles_9_to_11_with_test_root_source(self):
        g3 = self.with_root_source()
        bodies = g3.scope_input_bodies(self.scope_dir())
        self.assertEqual(set(bodies), set(g3.SCOPE_INPUT_NAMES))

    def test_unchanged_dependency_claim_and_archive_identity_refused(self):
        def claim(a):
            a['package_relation']['unchanged_dependency_claim'] = 'MADE'
        g3 = self.with_root_source(claim)
        self.refuses('V21_PACKAGE_RELATION_SCOPE', g3.scope_input_bodies, self.scope_dir())
        rows = json.loads(self.body('PACKAGE_BODY_RECEIVING.json'))['artifacts']
        rows = copy.deepcopy(rows)
        rows[0]['sha256'] = '0' * 64
        self.refuses('V21_ARCHIVE_IDENTITY', g3.archive_projection, rows)

    def test_historical_schema_not_selected(self):
        g3 = self.g3()
        self.refuses('HISTORICAL_ACQUISITION_SCHEMA_NOT_SELECTED_FOR_V21', g3.receive_retained_package_relation,
                     dict(schema='dg16.current-source-unchanged-package-acquisition.v4'), {}, {})


class FakeClock:
    def __init__(self, start_wall=1_800_000_000.0):
        self.mono = 1000.0
        self.wall = start_wall
        self.sleeps = []

    def monotonic(self):
        return self.mono

    def time(self):
        return self.wall

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.mono += seconds
        self.wall += seconds


class DecisionControls(G3Base):
    def request(self, g3, hold=6000, shared=13200, issued=1_800_000_000_000):
        value = dict(schema='dg16.g3-root-consumption-request.v2', authority='NONE', source_commit=g3.SOURCE_COMMIT,
            source_tree=g3.SOURCE_TREE, source_parent=g3.SOURCE_PARENT, run_id='45600842791', attempt=1, nonce='a' * 32,
            control_branch=g3.CONTROL_BRANCH, control_path=g3.CONTROL_PATH, root=g3.ROOT, join=g3.JOIN,
            original_scope_sha256=g3.SCOPE_SHA, graph_sha256='1' * 64, dispatch_sha256='2' * 64, transition_sha256='3' * 64,
            join_sha256='4' * 64, scope_return_sha256='5' * 64, g1_return_sha256='6' * 64, complete_input_key='7' * 64,
            returned_nodes=g3.SELECTED, issued_unix_ms=issued, expires_unix_ms=issued + hold * 1000, hold_seconds=hold,
            shared_expires_unix_ms=issued + shared * 1000, shared_window_seconds=shared, decision_before=g3.BEFORE,
            decision_after=g3.AFTER, original_total=157, original_awards=0,
            full_g2='NOT_DISPATCHED_OR_CONSUMED_IN_THIS_HOST', status='ROOT_REQUEST_READY')
        return value

    def decision(self, g3, request, request_raw, issued=None, **change):
        value = dict(schema='dg16.g3-root-consumption-decision.v2', issuer='R5_ROOT_GOVERNOR', successor=SUCC,
            action='CONSUME_COMPONENT_RETURNS_ONLY', request_sha256=sha(request_raw), run_id=request['run_id'], attempt=1,
            nonce=request['nonce'], source_commit=request['source_commit'], source_tree=request['source_tree'],
            graph_sha256=request['graph_sha256'], dispatch_sha256=request['dispatch_sha256'], join_sha256=request['join_sha256'],
            outputs={g3.PAIR: request['g1_return_sha256'], g3.SCOPE: request['scope_return_sha256']},
            consumed_nodes=g3.SELECTED, decision_before=request['decision_before'], decision_after=request['decision_after'],
            owner_arrangement=g3.OWNER_ARRANGEMENT, full_g2=request['full_g2'], original_awards=0,
            issued_unix_ms=request['issued_unix_ms'] + 1000 if issued is None else issued,
            expires_unix_ms=request['expires_unix_ms'])
        value.update(change)
        return g3.encode(value)

    def test_request_window_bounds_under_new_profile(self):
        g3 = self.g3()
        g3.validate_public_request(g3.encode(self.request(g3)))
        self.refuses('INTEGER_BOUND', g3.validate_public_request, g3.encode(self.request(g3, hold=6001, shared=13200)))
        self.refuses('INTEGER_BOUND', g3.validate_public_request, g3.encode(self.request(g3, hold=6000, shared=13201)))
        self.refuses('SHARED_DECISION_WINDOW', g3.validate_public_request, g3.encode(self.request(g3, hold=6000, shared=6100)))
        bad = self.request(g3)
        bad['control_branch'] = 'pro/dg16-g132-g3-control-20261120-01'
        self.refuses('PUBLIC_REQUEST_ROUTE', g3.validate_public_request, g3.encode(bad))

    def test_decision_binding_expiry_late_stale_invalid_mismatch(self):
        g3 = self.g3()
        request = self.request(g3)
        raw = g3.encode(request)
        req_sha = sha(raw)
        now = request['issued_unix_ms'] + 5000
        g3.validate_decision(self.decision(g3, request, raw), request, req_sha, now)
        self.refuses('ROOT_DECISION_EXPIRED_OR_FUTURE', g3.validate_decision, self.decision(g3, request, raw), request, req_sha,
                     request['expires_unix_ms'])
        self.refuses('INTEGER_BOUND', g3.validate_decision, self.decision(g3, request, raw, issued=request['expires_unix_ms'] + 1),
                     request, req_sha, request['expires_unix_ms'] + 2)
        self.refuses('ROOT_DECISION_EXPIRED_OR_FUTURE', g3.validate_decision,
                     self.decision(g3, request, raw, issued=now + 1), request, req_sha, now)
        self.refuses('ROOT_DECISION_ACTION_OR_REQUEST', g3.validate_decision,
                     self.decision(g3, request, raw, request_sha256='f' * 64), request, req_sha, now)
        self.refuses('ROOT_DECISION_ACTION_OR_REQUEST', g3.validate_decision,
                     self.decision(g3, request, raw, successor='PRO-EXECUTOR-01, designated by owner'), request, req_sha, now)
        self.refuses('ROOT_DECISION_BINDING', g3.validate_decision,
                     self.decision(g3, request, raw, source_commit='e76a07b2bae7c945e5a9d529ed8cf9069f4c9064'), request, req_sha, now)
        canonical = self.decision(g3, request, raw)
        self.refuses('ROOT_DECISION_CANONICAL_BYTES', g3.validate_decision, canonical.replace(b'{', b'{ ', 1), request, req_sha, now)

    def control(self, g3, clock, answers):
        """Local fake control source: ref + decision bodies by poll ordinal; no network."""
        calls = []

        def http(url, maximum, deadline):
            calls.append(url)
            if clock.monotonic() >= deadline:
                raise g3.Refusal('ROOT_HOLD_EXPIRED')
            ordinal = sum(1 for u in calls if '/git/ref/heads/' in u) - 1
            answer = answers(ordinal)
            if answer is None:
                return None
            if '/git/ref/heads/' in url:
                return json.dumps(dict(ref='refs/heads/' + g3.CONTROL_BRANCH, object=dict(type='commit', sha='c' * 40))).encode()
            return answer
        g3.http_bytes = http
        g3.time = clock
        return calls

    def test_hold_blocks_until_decision_then_consumes_once(self):
        g3 = self.g3()
        clock = FakeClock()
        request = self.request(g3, issued=int(clock.wall * 1000))
        raw = g3.encode(request)
        decision = self.decision(g3, request, raw)
        ready_at = 150  # polls (75 min) of 404 before Root publishes
        calls = self.control(g3, clock, lambda n: decision if n >= ready_at else None)
        out_raw, value, commit = g3.read_root_decision(request, sha(raw), clock.monotonic() + 6000)
        self.assertEqual(out_raw, decision)
        self.assertEqual(commit, 'c' * 40)
        self.assertEqual(len(clock.sleeps), ready_at)
        self.assertTrue(all(s == g3.POLL_SECONDS for s in clock.sleeps))
        self.assertTrue(any('/' + g3.CONTROL_BRANCH in u for u in calls))
        self.assertTrue(all(g3.CONTROL_PATH in u for u in calls if 'raw.githubusercontent.com' in u))

    def test_hold_expires_by_window_not_poll_bound(self):
        g3 = self.g3()
        clock = FakeClock()
        request = self.request(g3, issued=int(clock.wall * 1000))
        self.control(g3, clock, lambda n: None)
        self.refuses('ROOT_HOLD_EXPIRED', g3.read_root_decision, request, sha(g3.encode(request)), clock.monotonic() + 6000)
        self.assertLessEqual(len(clock.sleeps), g3.POLL_COUNT)
        self.assertGreaterEqual(sum(clock.sleeps), 6000)

    def test_second_decision_bound_to_final_packet_not_first(self):
        g3 = self.g3()
        first = self.request(g3)
        first_raw = g3.encode(first)
        final = dict(nonce=first['nonce'], run_id=first['run_id'], attempt=1, source_commit=first['source_commit'],
                     source_tree=first['source_tree'], final_graph_sha256='8' * 64, current_receipt_sha256='9' * 64,
                     proofs={}, expires_unix_ms=first['shared_expires_unix_ms'], issued_unix_ms=first['issued_unix_ms'],
                     retained_m4={})
        final_sha = 'e' * 64
        value = dict(schema='dg16.g3-root-original-decision.v3', issuer='R5_ROOT_GOVERNOR', successor=SUCC,
                     action='RECEIVE_EXACT_ORIGINAL_IDS_AND_GATES', request_sha256=sha(first_raw), run_id=final['run_id'],
                     attempt=1, nonce=final['nonce'], source_commit=final['source_commit'], source_tree=final['source_tree'],
                     final_graph_sha256=final['final_graph_sha256'], current_receipt_sha256=final['current_receipt_sha256'],
                     proofs={}, independent_review_sha256='a' * 64, source_applicability_review_sha256='b' * 64,
                     original_rows=[], gate_decisions={}, whole_DG16_awarded=False,
                     full_g2='NOT_DISPATCHED_OR_CONSUMED_IN_THIS_HOST', v041_admission='PENDING_NOT_GRANTED_BY_THIS_EPISODE',
                     global_liveness='NOT_ESTABLISHED', retirement_or_transfer='NOT_PERFORMED',
                     issued_unix_ms=final['issued_unix_ms'] + 1, expires_unix_ms=final['expires_unix_ms'], retained_m4={})
        # A decision naming the first request packet is not a decision on the final packet.
        self.refuses('FINAL_ROOT_DECISION_ACTION', g3.validate_final_decision, g3.encode(value), final, final_sha,
                     final['issued_unix_ms'] + 2)
        value['request_sha256'] = final_sha
        value['nonce'] = 'b' * 32
        self.refuses('FINAL_ROOT_DECISION_BINDING', g3.validate_final_decision, g3.encode(value), final, final_sha,
                     final['issued_unix_ms'] + 2)
        source = (self.packet / 'g3_receiving.py').read_text()
        self.assertIn("initial_request_sha256=sha(read_file(private/'G3_ROOT_REQUEST.json',REQUEST_LIMIT))", source)
        self.assertIn("expires_unix_ms=initial['shared_expires_unix_ms']", source)


class TimingControls(Base):
    def setUp(self):
        super().setUp()
        self.profile = json.loads((EPISODE / 'TIMING_PROFILE.json').read_bytes())
        self.v = self.profile['values']
        self.g3 = load(self.packet / 'g3_receiving.py', 'v21_g3_timing')
        self.workflow = json.loads(WORKFLOW.read_bytes())

    def test_constants_match_profile(self):
        g3, v = self.g3, self.v
        self.assertEqual((g3.HOLD_SECONDS, g3.POLL_SECONDS, g3.POLL_COUNT, g3.HTTP_SECONDS, g3.RESUME_RESERVE_SECONDS,
                          g3.FIRST_HOLD_MAX_SECONDS, g3.ENCLOSING_SECONDS),
                         (v['shared_window_max_seconds'], v['poll_seconds'], v['poll_count'], v['http_seconds'],
                          v['resume_reserve_seconds'], v['first_hold_max_seconds'], v['run_seconds']))
        run_text = (self.packet / 'run.py').read_text()
        self.assertIn('RUN_SECONDS=%d ' % v['run_seconds'], run_text)
        proof = (self.packet / 'proof_consumer.py').read_text()
        self.assertIn('RESERVE_SECONDS = %d ' % v['resume_reserve_seconds'], proof)
        self.assertIn("'core_seconds':%d}" % v['run_seconds'], proof)

    def test_budget_arithmetic(self):
        v = self.v
        self.assertEqual(v['shared_window_max_seconds'], v['first_hold_max_seconds'] + v['intervening_budget_seconds']
                         + v['second_hold_nominal_seconds'])
        self.assertEqual(v['run_seconds'], v['pre_hold_core_budget_seconds'] + v['shared_window_max_seconds']
                         + v['resume_reserve_seconds'])
        self.assertLessEqual(v['pre_core_budget_seconds'] + v['run_seconds'] + v['post_core_budget_seconds'],
                             v['job_timeout_minutes'] * 60)
        self.assertLess(v['job_timeout_minutes'], v['hosted_job_ceiling_minutes'])
        self.assertGreaterEqual(v['resume_reserve_seconds'], 1800)
        self.assertGreaterEqual(v['poll_count'] * v['poll_seconds'], v['shared_window_max_seconds'])
        self.assertLessEqual(v['first_hold_max_seconds'], v['shared_window_max_seconds'] - v['shared_margin_seconds'])

    def test_every_wait_fits_remaining_budget(self):
        """Simulate the unchanged issuing formulas at the latest admissible g3-receive time."""
        v = self.v
        for used in (0, 600, v['pre_hold_core_budget_seconds'], v['pre_hold_core_budget_seconds'] + 3000):
            remaining = v['run_seconds'] - used
            shared = min(v['shared_window_max_seconds'], int(remaining - v['resume_reserve_seconds']))
            if not 180 <= shared:
                continue
            hold1 = min(v['first_hold_max_seconds'], shared - 120)
            self.assertLessEqual(hold1 + v['resume_reserve_seconds'], remaining)
            self.assertLessEqual(shared + v['resume_reserve_seconds'], remaining)
            self.assertLessEqual(hold1, shared - 120)
            if used <= v['pre_hold_core_budget_seconds']:
                self.assertEqual((shared, hold1), (v['shared_window_max_seconds'], v['first_hold_max_seconds']))

    def test_workflow_profile_and_single_trigger(self):
        w, v = self.workflow, self.v
        self.assertEqual(w['on'], {'push': {'branches': ['engineering/opus-dg16-g1-v21-trigger-20261126'],
            'paths': ['.github/workflows/dg16-r5-g1-hosted-episode-v21.yml', 'qualification/dg16-r5-g1-hosted-episode-v21/**']}})
        job = w['jobs']['qualify']
        self.assertIn("github.ref == 'refs/heads/engineering/opus-dg16-g1-v21-trigger-20261126'", job['if'])
        self.assertIn("github.run_attempt == '1'", job['if'])
        self.assertEqual(job['timeout-minutes'], v['job_timeout_minutes'])
        names = [s['name'] for s in job['steps']]
        self.assertEqual(names[1], 'Admit pinned public inputs before any effect')
        self.assertEqual(names[2], 'Create exclusive fixed root island and exact packet')
        self.assertNotIn('sudo', job['steps'][1]['run'])
        for step in job['steps'][2:]:
            if 'always()' in step.get('if', ''):
                self.assertIn("steps.public_input_gate.outcome == 'success'", step['if'])
        for step in job['steps']:
            if step['name'].startswith('Core '):
                self.assertGreaterEqual(step['timeout-minutes'] * 60, v['run_seconds'])
                self.assertLess(step['timeout-minutes'], v['job_timeout_minutes'])
        self.assertEqual(w['permissions'], {'contents': 'read', 'actions': 'read'})

    def test_other_workflows_do_not_fire_on_trigger_or_control(self):
        for path in sorted((REPO / '.github/workflows').iterdir()):
            if path.name == WORKFLOW.name:
                continue
            text = path.read_text()
            self.assertNotIn('engineering/opus-dg16', text)
            self.assertNotIn("'**'", text)
            self.assertNotIn('engineering/**', text)


class PacketIntegrity(Base):
    def test_manifest_pins_and_population(self):
        manifest_raw = (ENTRY / 'PUBLIC_PACKET_MANIFEST.json').read_bytes()
        manifest = json.loads(manifest_raw)
        files = {p.relative_to(PACKET).as_posix(): p.read_bytes() for p in PACKET.rglob('*') if p.is_file()}
        self.assertEqual(set(files), set(manifest['members']))
        for name, raw in files.items():
            self.assertEqual(manifest['members'][name], dict(bytes=len(raw), mode=256, sha256=sha(raw)))
        placement = load(PACKET / 'root_placement.py', 'v21_placement_static')
        placement.manifest(manifest_raw)
        boot = (ENTRY / 'bootstrap_entry.py').read_text()
        self.assertIn("MANIFEST_SHA256 = '%s'" % sha(manifest_raw), boot)
        self.assertIn('ADMISSION_SHA256 = None', boot)

    def test_module_and_data_pins(self):
        run = (PACKET / 'run.py').read_text()
        import ast
        import re
        pins = ast.literal_eval(re.search(r'^MODULE_PINS = (\{.*\})$', run, re.M).group(1))
        data = ast.literal_eval(re.search(r'^G3_DATA_PINS = (\{.*\})$', run, re.M).group(1))
        for name, pin in pins.items():
            self.assertEqual(sha((PACKET / (name + '.py')).read_bytes()), pin, name)
        for name, pin in data.items():
            self.assertEqual(sha((PACKET / name).read_bytes()), pin, name)
        self.assertIn('public_inputs', pins)
        self.assertIn('PUBLIC_INPUT_INDEX.json', data)
        proof = json.loads((PACKET / 'INDEPENDENT_PROOF_PINS.json').read_bytes())
        self.assertEqual(proof['scope_module_sha256'], sha((PACKET / 'g3_receiving.py').read_bytes()))
        self.assertEqual(proof['consumer_sha256'], sha((PACKET / 'proof_consumer.py').read_bytes()))
        self.assertEqual(proof['initial_control_branch'], 'engineering/opus-dg16-g3-v21-control-20261126')
        run_sha = sha((PACKET / 'run.py').read_bytes())
        self.assertIn(run_sha, (ENTRY / 'public_export.py').read_text())
        self.assertIn(run_sha, (ENTRY / 'core_prepare_entry.py').read_text())
        selector_sha = sha((PACKET / 'public_inputs.py').read_bytes())
        self.assertIn(selector_sha, (ENTRY / 'admit_public_inputs.py').read_text())
        self.assertIn(selector_sha, (ENTRY / 'core_prepare_entry.py').read_text())
        self.assertIn("'PUBLIC_INPUT_HELD_ROLE_01'", run)

    def test_subject_facts(self):
        manifest = (PACKET / 'SOURCE_MANIFEST.json').read_bytes()
        self.assertEqual((len(manifest), sha(manifest)),
                         (557766, '1f9b80be380e29ce363fe7af2963db001a15a4aa43a148166ead4f6ca75783c3'))
        value = json.loads(manifest)
        self.assertEqual((value['commit'], value['tree'], value['file_count'], value['total_bytes']),
                         (V21['commit'], V21['tree'], 1982, 175292551))
        g3 = load(PACKET / 'g3_receiving.py', 'v21_g3_static')
        self.assertEqual((g3.SOURCE_COMMIT, g3.SOURCE_TREE, g3.PACKAGE_COMMIT, g3.SOURCE_FILES, g3.SOURCE_BYTES, g3.COMPILER_SHA,
                          g3.COMPILER_BYTES), (V21['commit'], V21['tree'], V21['commit'], 1982, 175292551,
                          'e65f13db74a29b4e8773997465361676d75a99de1c9fe0dca889e86353caece2', 261264))
        for name in ('ROOT_SOURCE_RECEIVING_HELD', 'HISTORICAL_ACQUISITION_SCHEMA_NOT_SELECTED_FOR_V21', 'V21_PACKAGE_RELATION_SCOPE'):
            self.assertIn(name, g3.REFUSAL_CODES)
        for path in PACKET.rglob('*.py'):
            text = path.read_text()
            self.assertNotIn('PRO-EXECUTOR-01', text, path.name)

    def test_all_modules_compile(self):
        for path in sorted(list(PACKET.rglob('*.py')) + list(ENTRY.glob('*.py'))):
            compile(path.read_bytes(), str(path), 'exec')

    def test_execute_admits_public_inputs_first(self):
        run = (PACKET / 'run.py').read_text()
        start = run.index('def execute(step,source,output,*,host_profile_binding=None):')
        body = run[start:start + 1600]
        self.assertLess(body.index('require_complete_packet()'), body.index("load_module('public_inputs').admit("))
        self.assertLess(body.index("load_module('public_inputs').admit("), body.index('context=host_context('))
        self.assertLess(body.index("load_module('public_inputs').admit("), body.index("require_launch("))
        self.assertLess(body.index("require_launch("), body.index('observe_g1_host_profile'))


HOST_ONLY = (
    'actual uid-0 fresh root island creation, ancestry/ACL/mode and FD route on a fresh ubuntu-24.04 runner',
    'actual clone of the source branch, provider/setup, NSS change, controller creation and every native call',
    'actual G1 pair, raw receiving and both Root holds against the real GitHub control branch',
    'actual hosted timings of g1/receive/g3 steps (no historical run reached them)',
    'the five native predicates (commit B consumer; native cases not run here)',
    'artifact upload and job-level timeout behaviour',
)


if __name__ == '__main__':
    unittest.main(verbosity=2)
