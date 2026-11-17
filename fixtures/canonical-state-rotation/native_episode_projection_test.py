#!/usr/bin/env python3
"""Portable R0039 protected native-owner artifact controls.

All native-shaped inputs here are explicitly constructed. No native calls,
owner selection, pending store, producer authentication or canary PASS occurs.
The source-peer contract is inspected in TEST CODE only; the packaged hot
projection remains self-contained. No private history or external task path.
"""
from __future__ import annotations
import argparse
import ast
import base64
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import types
import unittest

sys.dont_write_bytecode = True
options = argparse.ArgumentParser(add_help=False)
options.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
options.add_argument('--projection', type=Path)
selected, unittest_args = options.parse_known_args()
REPO = selected.repo_root.resolve(strict=True)
PROJECTION = selected.projection or REPO/'skills/implementaudit/scripts/canonical_hot_projection.py'
FUNCTIONS = {'require', 'closed', 'canonical', 'digest', 'before',
    '_episode_export_scope', '_episode_export_pin', '_episode_export_source',
    '_episode_export_locator', '_episode_export_physical', '_episode_export_path',
    '_episode_export_route_binding', '_episode_export_code_pins', 'validate_frozen_episode_export_v1'}
CONSTANTS = {'MAX_TOTAL', 'NONPROTECTED_PROFILE', 'OWNED_STDIO_PROFILE'}


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

B = types.SimpleNamespace(canonical=canonical, sha=sha,
    NATIVE_IDS={'export': 'c5-native-export', 'capture': 'c5-fresh-cd', 'facts': 'c5-owner-facts'},
    NATIVE_FILES={'export': 'native-export.json', 'capture': 'fresh-C-D.json', 'facts': 'native-owner-facts.json'})
F = load('_portable_original_fixture', REPO/'fixtures/canonical-state-rotation/protected_projection_v2_test.py')
M = load('_portable_protected_native_projection', PROJECTION)
support = load('native_test_support', REPO/'fixtures/operational-evidence/native-episode-controls/native_test_support.py')
support.configure(REPO, REPO)  # Selected pure fixture methods do not write SCRATCH.
N = load('_portable_native_fixture', REPO/'fixtures/operational-evidence/native-episode-controls/test_episode_export.py')


def constructed_native():
    fixture = N.FrozenExportTests()
    fixture.setUp()
    exported = fixture.available()
    controller, claim = 'r0039-fixture', 'e'*32
    exported['owner']['canonical_route'].update(controller_id=controller, ref='refs/implementaudit/route-decisions/'+controller)
    scope = exported['owner']['host_and_scope']
    scope.update(controller_id=controller, claim_id=claim, continuity_generation='G0001',
                 continuity_receipt='refs/implementaudit/continuity-receipts/'+controller+'/G0001@'+'d'*40)
    c = exported['pending']['covered_scope'][0]
    d = {'id': 'boundary-uncovered-D-fixture', 'kind': 'COMPLETED_RESUMED_BOUNDARY', 'version': 1}
    exported['pending']['observations'].append({**d, 'consumed_version': 0, 'assignment_children': []})
    exported['pending']['pending_scope'] = [d]
    document = b'{"constructed":"no-native-authority"}\n'
    evidence_pin = {'path': 'constructed-fixture.json', 'bytes': len(document), 'sha256': B.sha(document)}
    for name in ('candidate', 'qualification', 'episode', 'attestation'):
        exported['custody'][name] = copy.deepcopy(evidence_pin)
    exported['episode']['Q_digest'] = exported['episode']['E_digest'] = evidence_pin['sha256']
    fixture.reseal(exported)
    capture = {'boundaries': [], 'C': c, 'D': d, 'H0_currentness_checkpoints': [],
               'original13520_14114_credit': False, 'authority_ceiling': 'NONE'}
    facts = {'schema': 'implementaudit.native-owner-facts.v1', 'export_digest': exported['export_digest'],
        'pending_revision': exported['pending']['revision'], 'observation_proofs': {}, 'assignments': {},
        'custody_documents': {name: {'pin': copy.deepcopy(evidence_pin), 'bytes_b64': base64.b64encode(document).decode()}
            for name in ('candidate', 'qualification', 'episode', 'attestation')},
        'uncertainty': {'source_problem': None, 'unknown_result': True}, 'source_state_sha256': 'a'*64,
        'authority_ceiling': 'NONE'}
    facts['assignments'][exported['episode']['actual_child_identity']['thread_id']] = {
        'source_assignment_sha256': 'a'*64, 'scope': [c], 'native_lifecycle': 'CONSTRUCTED',
        'reservation_request': {'child_id': exported['episode']['actual_child_identity']['thread_id']},
        'observations': {}, 'return_state': 'SUCCEEDED', 'return_digest': exported['episode']['result_digest'],
        'join_state': 'JOINED_EVIDENCE_ONLY', 'joined_scope': [c], 'hold_failures': {}, 'hold_refusals': {}}
    for index, boundary in enumerate((c, d), 1):
        summary = {'resume_turn': 'constructed-resume-'+str(index), 'markers': [{'offset': index*100, 'bytes': 10, 'sha256': 'b'*64}]}
        capture['boundaries'].append({'label': 'C' if index == 1 else 'D', 'compaction_turn': 'constructed-compact-'+str(index),
            'resume_turn': summary['resume_turn'], 'summary': summary, 'source_bytes': index*200, 'source_sha256': 'c'*64})
        original = next(row for row in exported['pending']['observations'] if row['id'] == boundary['id'])
        facts['observation_proofs'][boundary['id']] = {key: original[key] for key in ('id', 'kind', 'version', 'consumed_version')}
        facts['observation_proofs'][boundary['id']]['proof'] = {**summary, 'source': {
            'path': exported['custody']['source_cutoffs']['parent']['path'],
            'physical': exported['custody']['source_cutoffs']['parent']['physical']}}
    for index in range(3):
        capture['H0_currentness_checkpoints'].append({'binding': {'fixture_only': True},
            'receipt': scope['continuity_receipt'], 'opening_digest': exported['owner']['canonical_opening_digest'],
            'observed_wall_ns': index+1, 'observed_monotonic_ns': index+1})
    # Use the existing pending owner's exact identity formula for these
    # explicitly constructed physical proof objects.
    mapping = {identifier: 'boundary-'+B.sha(B.canonical(row['proof']))
               for identifier, row in facts['observation_proofs'].items()}
    def rename(value):
        if type(value) is dict:
            return {mapping.get(key, key): rename(item) for key, item in value.items()}
        if type(value) is list:
            return [rename(item) for item in value]
        return mapping.get(value, value) if type(value) is str else value
    exported, capture, facts = (rename(value) for value in (exported, capture, facts))
    fixture.reseal(exported)
    facts['export_digest'] = exported['export_digest']
    return exported, capture, facts

def native_pair():
    bodies = F.fixture_bodies()
    bodies['STATE']['payload']['identity']['value']['claim_id'] = 'e'*32
    exported, capture, facts = constructed_native()
    bodies['STATE']['payload']['native_episode'] = {'owner': 'R0033/continuity', 'value': {
        'schema_version': 'implementaudit.protected-native-episode-reference.v1',
        'export_artifact_id': B.NATIVE_IDS['export'], 'capture_artifact_id': B.NATIVE_IDS['capture'],
        'facts_artifact_id': B.NATIVE_IDS['facts'], 'contract_sha256': M.NATIVE_EPISODE_CONTRACT_SHA256}}
    texts = json.loads(F.FIXTURE.read_text())['artifact_texts']
    for kind, value in (('export', exported), ('capture', capture), ('facts', facts)):
        name = B.NATIVE_IDS[kind]
        bodies['STATE']['artifact_refs'].append({'artifact_id': name, 'owner': 'R0033/continuity',
            'role': 'EVIDENCE', 'locator': 'cold-receiving/'+B.NATIVE_FILES[kind], 'object_format': 'sha1'})
        bodies['STATE']['payload']['runtime_artifacts']['value'].append(name)
        texts[name] = B.canonical(value).decode()
    return bodies, texts

def parse(bodies=None, texts=None):
    if bodies is None:
        bodies, texts = native_pair()
    state, roadmap, owners, artifacts = F.fixture_pair(bodies, texts)
    return M.parse_canonical_pair_v2(state, roadmap, owner_map=owners, artifacts=artifacts)

class NativeEpisodeProjectionControls(unittest.TestCase):
    def test_old_plain_v2_and_native_guards_are_unchanged(self):
        for bodies in (F.fixture_bodies(), F.native_profile_bodies()):
            state, road, owners, artifacts = F.fixture_pair(bodies)
            old = F.MODULE.parse_canonical_pair_v2(state, road, owner_map=owners, artifacts=artifacts)
            new = M.parse_canonical_pair_v2(state, road, owner_map=owners, artifacts=artifacts)
            self.assertEqual(old, new)
            self.assertEqual(F.MODULE.derive_hot_pair_v2(old, transition=None, archive_pointers=F.archive_pointers(old), **F.LIMITS),
                             M.derive_hot_pair_v2(new, transition=None, archive_pointers=F.archive_pointers(new), **F.LIMITS))

    def test_full_native_leaf_denominator_and_c_only_d_pending(self):
        old = parse()
        candidate = M.derive_hot_pair_v2(old, transition=F.successor(old), archive_pointers=F.archive_pointers(old), **F.LIMITS)
        native = candidate['protected_manifest']['PRESERVED_PAYLOAD']['native_episode']
        self.assertEqual(native, old['protected_manifest']['PRESERVED_PAYLOAD']['native_episode'])
        self.assertEqual(native['protected_leaf_count'], sum(len(list(F.leaves(v))) for v in native['values'].values()))
        self.assertEqual(native['values']['export']['pending']['covered_scope'], [native['values']['capture']['C']])
        self.assertIn(native['values']['capture']['D'], native['values']['export']['pending']['pending_scope'])
        self.assertEqual(candidate['protected_manifest']['DERIVED_BINDINGS']['native_episode_applicability']['current_use'],
                         'INAPPLICABLE_AFTER_CONTINUITY_CHANGE')
        self.assertEqual(candidate['payload']['STATE']['pending_boundaries'], old['payload']['STATE']['pending_boundaries'])
        self.assertTrue(M.verify_projection_equivalence_v2(old, candidate)['equivalent'])

    def test_each_native_leaf_omission_and_semantic_change_refuses(self):
        old = parse()
        candidate = M.derive_hot_pair_v2(old, transition=None, archive_pointers=F.archive_pointers(old), **F.LIMITS)
        native = candidate['protected_manifest']['PRESERVED_PAYLOAD']['native_episode']
        # Denominator omission is tested for every actual derived leaf.
        for index in range(len(native['owner_map'])):
            changed = copy.deepcopy(candidate)
            del changed['protected_manifest']['PRESERVED_PAYLOAD']['native_episode']['owner_map'][index]
            with self.subTest(index=index), self.assertRaises(M.ProjectionV2Error):
                M.verify_projection_equivalence_v2(old, changed)
        changed = copy.deepcopy(candidate)
        changed['protected_manifest']['PRESERVED_PAYLOAD']['native_episode']['values']['export']['pending']['pending_scope'] = []
        with self.assertRaises(M.ProjectionV2Error):
            M.verify_projection_equivalence_v2(old, changed)

    def test_absent_changed_ordinary_unavailable_and_unentitled_artifacts_refuse(self):
        bodies, texts = native_pair()
        state, road, owners, artifacts = F.fixture_pair(bodies, texts)
        altered = dict(artifacts)
        del altered[B.NATIVE_IDS['export']]
        with self.assertRaises(M.ProjectionV2Error):
            M.parse_canonical_pair_v2(state, road, owner_map=owners, artifacts=altered)
        altered = dict(artifacts)
        altered[B.NATIVE_IDS['export']] += b' '
        with self.assertRaises(M.ProjectionV2Error):
            M.parse_canonical_pair_v2(state, road, owner_map=owners, artifacts=altered)
        for kind in ('ordinary', 'unavailable', 'foreign_owner', 'unknown_profile'):
            body, content = native_pair()
            value = json.loads(content[B.NATIVE_IDS['export']])
            if kind == 'ordinary':
                value['schema'] = 'implementaudit.ordinary-episode-export.v1'
            elif kind == 'unavailable':
                fixture = N.FrozenExportTests(); fixture.setUp(); value = fixture.unavailable()
            elif kind == 'foreign_owner':
                next(row for row in body['STATE']['artifact_refs'] if row['artifact_id'] == B.NATIVE_IDS['export'])['owner'] = 'STATE.md'
            else:
                body['STATE']['payload']['native_episode']['value']['schema_version'] += '.unknown'
            content[B.NATIVE_IDS['export']] = B.canonical(value).decode()
            with self.subTest(kind=kind), self.assertRaises(M.ProjectionV2Error):
                parse(body, content)

    def test_original_physical_prior_retry_and_failure_facts_cannot_be_reclassified(self):
        old = parse()
        candidate = M.derive_hot_pair_v2(old, transition=None, archive_pointers=F.archive_pointers(old), **F.LIMITS)
        for kind in ('copied', 'foreign', 'changed_offset', 'later_repaired', 'pending_erasure'):
            changed = copy.deepcopy(candidate)
            values = changed['protected_manifest']['PRESERVED_PAYLOAD']['native_episode']['values']
            selected = values['export']['occurrences']['occurrences'][0]
            if kind == 'copied': selected['population'] = 'PRIOR'
            elif kind == 'foreign': selected['records']['call']['physical']['inode'] += 1
            elif kind == 'changed_offset': selected['records']['call']['locator']['offset'] += 1
            elif kind == 'later_repaired': selected['records']['result']['locator']['sha256'] = 'f'*64
            else: values['facts']['uncertainty'] = {}
            with self.subTest(kind=kind), self.assertRaises(M.ProjectionV2Error):
                M.verify_projection_equivalence_v2(old, changed)

    def test_exact_existing_route_gate_refuses_changed_continuity(self):
        path = REPO/'source-peers/route-graph/skills/implementaudit/scripts/route-transaction.py'
        node = next(node for node in ast.parse(path.read_text()).body
                    if isinstance(node, ast.FunctionDef) and node.name == '_pure_route_semantics_v1')
        def fail(reason, **kwargs):
            raise ValueError(reason)
        namespace = {'fail': fail}
        exec(compile(ast.Module(body=[node], type_ignores=[]), str(path), 'exec'), namespace)
        original = {'controller_id': 'actual-constructed-owner', 'claim_id': 'e'*32,
                    'explicit_run_root': 'task-run', 'continuity_generation': 'G0002', 'continuity_receipt': 'old-receipt'}
        current = {**original, 'continuity_generation': 'G0003', 'continuity_receipt': 'new-receipt'}
        with self.assertRaisesRegex(ValueError, 'route decision expired because bound continuity_generation changed'):
            namespace['_pure_route_semantics_v1'](None, original['controller_id'], None, original, current, None)

    def test_rehashed_changed_proof_and_capture_cannot_keep_original_exported_id(self):
        bodies, texts = native_pair()
        parse(bodies, texts)
        capture = json.loads(texts[B.NATIVE_IDS['capture']])
        facts = json.loads(texts[B.NATIVE_IDS['facts']])
        original_export = texts[B.NATIVE_IDS['export']]
        selected = capture['C']['id']
        facts['observation_proofs'][selected]['proof']['markers'][0]['offset'] += 1
        capture['boundaries'][0]['summary']['markers'][0]['offset'] += 1
        self.assertNotEqual(selected, 'boundary-'+B.sha(B.canonical(facts['observation_proofs'][selected]['proof'])))
        texts[B.NATIVE_IDS['capture']] = B.canonical(capture).decode()
        texts[B.NATIVE_IDS['facts']] = B.canonical(facts).decode()
        self.assertEqual(texts[B.NATIVE_IDS['export']], original_export)
        # fixture_pair recomputes the outer owner map: ID/proof binding still refuses.
        with self.assertRaisesRegex(M.ProjectionV2Error, 'boundary ID differs from original physical proof'):
            parse(bodies, texts)

    def test_generated_contract_is_exact_owner_ast_and_has_no_runtime_peer_import(self):
        text = (REPO/'source-peers/native-runtime/skills/implementaudit/scripts/compaction-result-observation.py').read_text(encoding='utf-8')
        nodes = [node for node in ast.parse(text).body
                 if isinstance(node, ast.FunctionDef) and node.name in FUNCTIONS
                 or isinstance(node, ast.Assign) and len(node.targets) == 1
                 and isinstance(node.targets[0], ast.Name) and node.targets[0].id in CONSTANTS]
        contract = '\n\n'.join(ast.get_source_segment(text, node) for node in nodes)+'\n'
        self.assertEqual(sha(contract.encode()), M.NATIVE_EPISODE_CONTRACT_SHA256)
        candidate_text = PROJECTION.read_text(encoding='utf-8')
        function = next(node for node in ast.parse(candidate_text).body
            if isinstance(node, ast.FunctionDef) and node.name == '_v2_validate_native_export')
        copied = {node.name: ast.dump(node, include_attributes=False) for node in function.body if isinstance(node, ast.FunctionDef)}
        expected = {node.name: ast.dump(node, include_attributes=False) for node in nodes if isinstance(node, ast.FunctionDef)}
        self.assertEqual(copied, expected)
        self.assertNotIn('source-peers', ast.get_source_segment(candidate_text, function))


    def test_tc06_continuing_duties_and_tc11_original_scope_survive(self):
        bodies, texts = native_pair()
        for grant in bodies['STATE']['payload']['authorisations']['value']:
            grant.update(status='REVOKED', applicability='DOES_NOT_APPLY')
        duties = ['marker reader', 'pointer and receipt reader', 'typed archive retrieval', 'pending acceptance duties']
        for index, duty in enumerate(duties):
            bodies['ROADMAP']['payload']['obligations']['value'].append({
                'record_id': 'TC06-old-consumer-'+str(index), 'status': 'OPEN',
                'description': 'Disabling new rotations does not retire '+duty,
                'scope': 'Explicit constructed qualification case', 'evidence_refs': ['evidence']})
        original = parse(bodies, texts)
        candidate = M.derive_hot_pair_v2(original, transition=F.successor(original),
            archive_pointers=F.archive_pointers(original), **F.LIMITS)
        self.assertEqual(candidate['payload']['ROADMAP']['obligations'], original['payload']['ROADMAP']['obligations'])
        self.assertEqual(candidate['payload']['STATE']['pending_boundaries'], original['payload']['STATE']['pending_boundaries'])
        historical = next(row for row in bodies['STATE']['history'] if row['record_id'] == 'TC11-admission-history')
        pointer = next(row for row in candidate['archive_pointers'] if row['record_id'] == historical['record_id'])
        self.assertEqual(pointer['record_sha256'], sha(canonical(historical)))
        self.assertEqual(historical['payload']['current_applicability'], 'INVALIDATED_CURRENT_USE')
        self.assertEqual(candidate['protected_manifest']['DERIVED_BINDINGS']['native_episode_applicability']['current_use'],
                         'INAPPLICABLE_AFTER_CONTINUITY_CHANGE')


if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0], *unittest_args])
