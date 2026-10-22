from native_test_support import source_path, source_text, functions as selected_functions, load, source_api, SCRATCH, PUBLIC_OWNERS
from unittest import mock
import os
'Pure frozen-reader controls; fixtures confer no native episode credit.'
import ast
import copy
import hashlib
import json
from pathlib import Path
import re
import os
import tempfile
import types
import unittest
from datetime import datetime
HERE = SCRATCH

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def require(ok, reason):
    if not ok:
        raise ValueError(reason)

def closed(value, keys, reason):
    require(type(value) is dict and set(value) == set(keys), reason)
    return value

class FrozenExportTests(unittest.TestCase):

    def setUp(self):
        source = source_text('compaction-result-observation.py')
        tree = ast.parse(source)
        names = {'validate_frozen_episode_export_v1', '_episode_export_scope', '_episode_export_pin', '_episode_export_source', '_episode_export_locator', '_episode_export_physical', '_episode_export_path', '_episode_export_route_binding', '_episode_export_code_pins', 'before'}
        nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
        self.assertEqual({n.name for n in nodes}, names)
        self.ns = dict(require=require, closed=closed, canonical=canonical, digest=digest, re=re, datetime=datetime, MAX_TOTAL=2 * 1024 * 1024, NONPROTECTED_PROFILE='codex-app-bounded-public-nonprotected-v1')
        exec(compile(ast.Module(body=nodes, type_ignores=[]), '<pure-validator>', 'exec'), self.ns)
        self.validate = self.ns['validate_frozen_episode_export_v1']

    def unavailable(self):
        value = dict(schema='implementaudit.native-episode-export.v1', status='UNAVAILABLE', reason_code='FIXED_SELECTION_UNBOUND', owner=None, episode=None, pending=None, lifecycle=None, occurrences=None, custody=None, authority_ceiling='NONE')
        return {**value, 'export_digest': digest(canonical(value))}

    def test_unavailable_is_closed_and_has_no_io_dependencies(self):
        value = self.unavailable()
        self.assertEqual(self.validate(value), value)
        self.assertEqual(set(self.ns) & {'open', 'subprocess', '_np_runtime', 'Path'}, set())

    def test_modified_payload_or_authority_refuses(self):
        for key, value in [('reason_code', 'OWNER_SAYS_OK'), ('authority_ceiling', 'OWNER'), ('pending', {})]:
            candidate = self.unavailable()
            candidate[key] = value
            with self.assertRaises(ValueError):
                self.validate(candidate)

    def test_unknown_keys_and_oversized_capture_refuse(self):
        candidate = self.unavailable()
        candidate['unselected_profile'] = 'x'
        with self.assertRaises(ValueError):
            self.validate(candidate)

    def available(self):
        h = 'a' * 64
        parent = {'thread_id': 'fixture-parent', 'agent_path': '/root'}
        child = {'thread_id': 'fixture-child', 'parent_thread_id': 'fixture-parent', 'agent_path': '/root/fixture'}
        covered = [{'id': 'boundary-fixture', 'version': 1, 'kind': 'COMPLETED_RESUMED_BOUNDARY'}]
        paths = {role: 'C:/fixture/sessions/rollout-fixture-' + role + '.jsonl' for role in ('parent', 'child')}

        def record(offset):
            return {'path': paths['child'], 'physical': {'device': 1, 'inode': 2}, 'role': 'child', 'locator': {'offset': offset, 'bytes': 4, 'sha256': h, 'embedded_ordinal': offset, 'physical_line': offset + 1}, 'timestamp': '2026-10-18T00:00:%02dZ' % offset, 'message_or_call_id': 'fixture-' + str(offset)}
        rows = [{'population': 'CURRENT', 'attempt_class': 'ORIGINAL', 'semantic': name, 'observation_id': h, 'completion': 'COMPLETED', 'records': {'call': record(i * 10), 'result': record(i * 10 + 5)}} for i, name in enumerate(('LOAD', 'EXCHANGE', 'BIND'), 1)]
        cutoff = {'path': paths['child'], 'physical': {'device': 1, 'inode': 2}, 'prefix_bytes': 100, 'prefix_sha256': h, 'physical_records': 100, 'history_start_ordinal': 1, 'host_producer_authenticated': False, 'original_bind': rows[2]['records']}
        sources = {role: {'path': paths[role], 'physical': {'device': 1, 'inode': 1 if role == 'parent' else 2}, 'metadata': {'offset': 0, 'bytes': 5, 'sha256': h, 'embedded_ordinal': 0, 'physical_line': 1}, 'metadata_payload_digest': h, 'history_start_ordinal': 0 if role == 'parent' else 1, 'allowed_ranges': [{'offset': 0, 'bytes': 2 * 1024 * 1024}], 'canonical_open_binding_digest': 'sha256:' + h} for role in ('parent', 'child')}
        compact = {'path': paths['parent'], 'task_id': parent['thread_id'], 'session_id': parent['thread_id'], 'sessions_root': 'C:/fixture/sessions', 'physical': sources['parent']['physical'], 'session_meta_sha256': h, 'prefix_bytes': 100, 'prefix_sha256': h, 'provenance': 'HOST_STORE_OWNER_REGISTERED_PHYSICAL_NATIVE_SESSION_PREFIX', 'native_producer_runtime_equivalence': 'UNVERIFIED'}
        pin = {'path': 'fixture.json', 'bytes': 100, 'sha256': h}
        value = {'schema': 'implementaudit.native-episode-export.v1', 'status': 'AVAILABLE', 'reason_code': None, 'owner': {'profile_id': 'codex-app-bounded-public-nonprotected-v1', 'issuer_id': 'fixture-only', 'policy_digest': h, 'code_pins': {'fixture.py': h}, 'canonical_opening_digest': 'sha256:' + h}, 'episode': {'parent_identity': parent, 'actual_child_identity': child, 'assignment_identity': h, 'obligation_digest': h, 'observation_id': h, 'covered_boundary_versions': covered, 'result_digest': h, 'acceptance_digest': h, 'Q_digest': h, 'E_digest': h}, 'pending': {'revision': 2, 'observations': [{**covered[0], 'consumed_version': 1, 'assignment_children': []}], 'assignment_scope': covered, 'covered_scope': covered, 'pending_scope': []}, 'lifecycle': {'result': {'status': 'SUCCEEDED', 'return_digest': h}, 'acceptance': {'status': 'ACCEPTED_EXACT_RESULT', 'digest': h}, 'join': {'status': 'JOINED_EVIDENCE_ONLY', 'covered': covered, 'pending_consumed': True}, 'h0': {'status': 'NOT_RECORDED', 'stage_receipts': {}}, 'source_terminal_release': {'status': 'SOURCE_OWNER_VALIDATED', 'digest': h}}, 'occurrences': {'schema': 'implementaudit.compaction-selected-occurrences.v1', 'observation_id': h, 'actual_child_identity': child, 'covered_boundary_versions': covered, 'source_cutoff': cutoff, 'occurrences': rows, 'authority_ceiling': 'NONE'}, 'custody': {'candidate': pin, 'qualification': pin, 'episode': pin, 'attestation': pin, 'source_cutoffs': {**sources, 'compaction_cutoff': compact, 'hold_history': cutoff}}, 'authority_ceiling': 'NONE'}
        value['owner']['canonical_route'] = {'controller_id': 'fixture-controller', 'controller_record_oid': 'b' * 40, 'ref': 'refs/implementaudit/route-decisions/fixture-controller', 'record_oid': 'c' * 40, 'record_identity': 'sha256:' + h, 'decision': 'REQUIRED', 'classification': 'MECHANICALLY_REQUIRED', 'route_transaction_id': 'sha256:' + h, 'obligation_id': 'sha256:' + h, 'route_state': 'OPEN'}
        value['owner']['host_and_scope'] = {'host_id': 'codex', 'host_session_id': parent['thread_id'], 'host_binding_generation': 'G0001', 'host_correlation_id': 'sha256:' + h, 'continuity_generation': 'G0002', 'continuity_receipt': 'refs/implementaudit/continuity-receipts/fixture-controller/G0002@' + 'd' * 40, 'obligation_id': 'sha256:' + h, 'route_transaction_id': 'sha256:' + h, 'controller_id': 'fixture-controller', 'claim_id': 'e' * 32, 'explicit_run_root': '/fixture/repo/.IMPLEMENTAUDIT/runs/run'}
        value['owner']['issuer_id'] = 'codex-app-canonical-episode-public-source-v1'
        names = ['implementaudit/SKILL.md', 'audit-state/SKILL.md',
            'implementaudit/references/child-agents.md', 'implementaudit/references/continuity.md']
        names += ['implementaudit/scripts/' + name for name in (
            'compaction-audit-pending.py', 'compaction-result-observation.py',
            'compaction-source-owner-codex-app.py', 'codex-recovery-native-reader.py',
            'bounded_file_custody.py', 'bounded_native_reader.py', 'bounded_source_owner.py',
            'host-session-binding.py', 'route-transaction.py')]
        value['owner']['code_pins'] = {name: h for name in names}
        return {**value, 'export_digest': digest(canonical(value))}

    def reseal(self, value):
        value['export_digest'] = digest(canonical({k: v for k, v in value.items() if k != 'export_digest'}))
        return value

    def test_bound_fixture_preserves_lifecycle_distinctions(self):
        value = self.available()
        self.assertEqual(self.validate(value), value)
        changed = copy.deepcopy(value)
        changed['lifecycle']['h0'] = {'status': 'RECORDED', 'stage_receipts': {}}
        with self.assertRaisesRegex(ValueError, 'H0_BINDING'):
            self.validate(self.reseal(changed))
        changed = copy.deepcopy(value)
        changed['pending']['observations'][0]['consumed_version'] = 0
        with self.assertRaisesRegex(ValueError, 'CONSUMPTION_BINDING'):
            self.validate(self.reseal(changed))
        changed = copy.deepcopy(value)
        changed['occurrences']['occurrences'][2]['records']['result'] = None
        with self.assertRaisesRegex(ValueError, 'OCCURRENCE_COMPLETION'):
            self.validate(self.reseal(changed))

    def test_foreign_source_and_range_or_cutoff_mismatch_refuse(self):
        value = self.available()
        for change in ('missing-code-pin', 'foreign-code-pin', 'foreign-issuer'):
            changed = copy.deepcopy(value)
            pins = changed['owner']['code_pins']
            if change == 'missing-code-pin':
                del pins['audit-state/SKILL.md']
            elif change == 'foreign-code-pin':
                pins['foreign.py'] = pins.pop('audit-state/SKILL.md')
            else:
                changed['owner']['issuer_id'] = 'caller-selected-owner'
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.validate(self.reseal(changed))
        for field in ('parent', 'child', 'compaction_cutoff', 'hold_history'):
            changed = copy.deepcopy(value)
            changed['custody']['source_cutoffs'][field] = {'foreign': True}
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.validate(self.reseal(changed))
        for operation in ('wrong_inode', 'negative_offset', 'beyond_cutoff', 'wrong_path', 'wrong_header'):
            changed = copy.deepcopy(value)
            pin = changed['occurrences']['occurrences'][0]['records']['call']
            if operation == 'wrong_inode':
                pin['physical']['inode'] += 1
            if operation == 'negative_offset':
                pin['locator']['offset'] = -1
            if operation == 'beyond_cutoff':
                pin['locator']['offset'] = 1001
            if operation == 'wrong_path':
                pin['path'] = 'C:/fixture/sessions/rollout-other.jsonl'
            if operation == 'wrong_header':
                changed['custody']['source_cutoffs']['compaction_cutoff']['session_meta_sha256'] = 'b' * 64
            with self.subTest(operation=operation), self.assertRaises(ValueError):
                self.validate(self.reseal(changed))
        for key, bad in [('controller_id', 'foreign'), ('continuity_receipt', 'refs/foreign/G0002@' + 'd' * 40), ('route_transaction_id', 'sha256:' + 'f' * 64), ('host_session_id', 'foreign'), ('host_binding_generation', -1)]:
            changed = copy.deepcopy(value)
            changed['owner']['host_and_scope'][key] = bad
            with self.subTest(canonical_field=key), self.assertRaises(ValueError):
                self.validate(self.reseal(changed))
        changed = copy.deepcopy(value)
        changed['owner']['host_and_scope']['unadmitted'] = True
        with self.assertRaises(ValueError):
            self.validate(self.reseal(changed))

    def test_irrelevant_append_keeps_exact_original_prefix(self):
        tree = ast.parse(source_text('compaction-audit-pending.py'))
        node = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == '_validate_registered_prefix'))
        identity = lambda info: {'device': info.st_dev, 'inode': info.st_ino}
        env = dict(require=require, physical=lambda value: Path(value), OBSERVATION=types.SimpleNamespace(identity=identity, MAX_TOTAL=2 * 1024 * 1024, MAX_RECORDS=64), MAX_SOURCE=8 * 1024 * 1024, os=os, digest=digest, hashlib=hashlib)
        exec(compile(ast.Module(body=[node], type_ignores=[]), '<fixed-prefix>', 'exec'), env)
        with tempfile.TemporaryDirectory(dir=HERE) as directory:
            path = Path(directory) / 'fixture.jsonl'
            raw = b'{"type":"session_meta"}\n{"public":"fixture"}\n'
            path.write_bytes(raw)
            prefix = {'path': str(path), 'physical': identity(path.stat()), 'prefix_bytes': len(raw), 'prefix_sha256': digest(raw), 'session_meta_sha256': digest(raw.splitlines(keepends=True)[0])}
            before = copy.deepcopy(prefix)
            value = self.available()
            encoded = canonical(self.validate(value))
            env['_validate_registered_prefix'](prefix)
            with path.open('ab') as stream:
                stream.write(b'irrelevant later append is outside accepted cutoff\n')
            env['_validate_registered_prefix'](prefix)
            self.assertEqual(prefix, before)
            self.assertEqual(canonical(self.validate(value)), encoded)
            with path.open('r+b') as stream:
                stream.seek(1)
                stream.write(b'X')
            with self.assertRaisesRegex(ValueError, 'PREFIX_HEADER_CHANGED'):
                env['_validate_registered_prefix'](prefix)
        candidate = self.unavailable()
        candidate['reason_code'] = 'x' * (2 * 1024 * 1024)
        with self.assertRaises(ValueError):
            self.validate(candidate)
if __name__ == '__main__':
    unittest.main(verbosity=2)
