from native_test_support import source_path, source_text, functions as selected_functions, load, source_api, SCRATCH, PUBLIC_OWNERS
from unittest import mock
import os
'Focused existing-owner integration controls; no actual native episode credit.'
import ast
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest
HERE = SCRATCH

class PendingIntegrationControls(unittest.TestCase):

    def test_selected_reservation_release_and_join_reach_same_existing_owner(self):
        text = source_text('compaction-audit-pending.py')
        nodes = {n.name: n for n in ast.parse(text).body if isinstance(n, ast.FunctionDef)}
        operate = ast.unparse(nodes['operate'])
        release = ast.unparse(nodes['boundary_release_subject'])
        self.assertIn('OBSERVATION.bind_nonprotected_sources', operate)
        self.assertIn('NONPROTECTED_RESERVED_ACTUAL_CHILD_DIFFERS', operate)
        self.assertIn('_assignment_code_identity(assignment)', operate)
        self.assertIn('OBSERVATION.acquire_episode', operate)
        self.assertIn('_rebind_selected_assignment(assignment, session, child)', release)
        self.assertIn('_assignment_code_identity(assignment)', release)
        self.assertIn("exec(compile(raw, module.__file__, 'exec'", release)

    def test_helpers_are_defined_before_cli_main(self):
        for name in PUBLIC_OWNERS:
            text = source_text(name)
            tree = ast.parse(text)
            guards = [n.lineno for n in tree.body if isinstance(n, ast.If) and '__main__' in ast.unparse(n.test)]
            if guards:
                if name == 'compaction-source-owner-codex-app.py':
                    # The original universal syntactic placement check was too
                    # broad for appended imported-only fresh/mechanical APIs.
                    # Preserve the actual two-entry ordinary CLI requirement.
                    from native_test_support import ordinary_cli_definition_closure
                    closure = ordinary_cli_definition_closure(text)
                    self.assertEqual(closure['entries'], ['ordinary_receiver_check_v1', 'execute_ordinary_receiver_v1'])
                    self.assertIn('_ordinary_selection_v1', closure['dependencies'])
                    self.assertEqual(len(closure['after_dispatch_imported_only']), 14)
                    # Move a REAL required selection helper after dispatch.
                    # Its unchanged body/source pin cannot bypass the order check.
                    moved = ast.parse(text)
                    helper = next(n for n in moved.body if isinstance(n, ast.FunctionDef) and n.name == '_ordinary_selection_v1')
                    moved.body.remove(helper); moved.body.append(helper)
                    with self.assertRaisesRegex(ValueError, '^CLI_REACHABLE_LATE_DEFINITION:_ordinary_selection_v1$'):
                        ordinary_cli_definition_closure(ast.unparse(moved))
                    # A changed actual profile gate cannot authorize an exclusion.
                    changed = text.replace("selected['profile_id'] == 'codex-app-ordinary-review-v1'",
                                           "selected['profile_id'] == FRESH_CANARY_PROFILE")
                    self.assertNotEqual(changed, text)
                    with self.assertRaisesRegex(ValueError, '^CLI_CRITICAL_SOURCE_CHANGED:_ordinary_selection_v1$'):
                        ordinary_cli_definition_closure(changed)
                else:
                    self.assertTrue(all((n.lineno < guards[0] for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)))), name)

    def test_current_scanner_requires_owner_selected_version_and_keeps_metadata_only(self):
        text = source_text('compaction-audit-pending.py')
        names = {'_scan_source_unheld', 'physical', 'text', 'decode', 'unique', 'digest', 'require'}
        tree = ast.parse(text)
        nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and getattr(n, 'name', None) in names | {'Refusal'}]
        import os, stat
        env = dict(Path=Path, os=os, stat=stat, json=json, hashlib=hashlib, MAX_SOURCE=8 * 1024 * 1024, MAX_ROWS=4096, OBSERVATION=types.SimpleNamespace(MAX_TOTAL=2 * 1024 * 1024, MAX_RECORDS=64))
        exec(compile(ast.Module(body=nodes, type_ignores=[]), '<existing-scanner>', 'exec'), env)
        with tempfile.TemporaryDirectory(dir=HERE) as directory:
            path = Path(directory) / 'fixture.jsonl'
            values = [{'timestamp': 'fixture', 'ordinal': 0, 'type': 'session_meta', 'payload': {'cli_version': '0.163.0-alpha.10.2'}}, {'timestamp': 'fixture', 'ordinal': 1, 'type': 'compacted', 'payload': {'replacement_body': 'not an exported witness'}}, {'timestamp': 'fixture', 'ordinal': 2, 'type': 'event_msg', 'payload': {'type': 'task_started', 'turn_id': 'fixture-turn'}}]
            path.write_bytes(b''.join(((json.dumps(v) + '\n').encode() for v in values)))
            with self.assertRaisesRegex(ValueError, 'SOURCE_SESSION_META'):
                env['_scan_source_unheld'](path)
            observed = env['_scan_source_unheld'](path, native_cli_version='0.163.0-alpha.10.2')
            self.assertEqual(len(observed['summaries']), 1)
            self.assertNotIn('replacement_body', json.dumps(observed['summaries']))
            self.assertEqual(observed['summaries'][0]['resume']['physical_line'], 3)
            with self.assertRaisesRegex(ValueError, 'SOURCE_SESSION_META'):
                env['_scan_source_unheld'](path, native_cli_version='wrong-version')
if __name__ == '__main__':
    unittest.main(verbosity=2)
