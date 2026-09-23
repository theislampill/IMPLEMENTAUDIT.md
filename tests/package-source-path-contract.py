#!/usr/bin/env python3
"""Package source-path boundaries using owned Git fixtures; no build/install effects."""
from __future__ import annotations
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('package_source_path_contract', ROOT/'scripts/package-contract.py')
PACKAGE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PACKAGE)

class PackageSourcePaths(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='package-source-paths-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'source'
        self.gov = self.root/'skills/implementaudit'
        (self.gov/'scripts').mkdir(parents=True)
        (self.gov/'SKILL.md').write_bytes(b'# Governed fixture\n')
        self.script = self.gov/'scripts/probe.sh'
        self.script.write_bytes(b'#!/bin/sh\r\nprintf fixture\r\n')
        subprocess.run(['git','init','-q',str(self.root)], check=True)
        self.track()

    def track(self):
        subprocess.run(['git','-C',str(self.root),'add','--all','--force'],check=True,
                       stdout=subprocess.PIPE,stderr=subprocess.PIPE)

    def link(self, destination, target):
        try:
            destination.symlink_to(target, target_is_directory=target.is_dir())
        except OSError as exc:
            self.skipTest('platform cannot create the required alias fixture: '+str(exc))

    def test_regular_source_preserves_bytes_and_executable_projection(self):
        rows = {p.as_posix():(b,m) for p,b,m in PACKAGE.source_skill_entries(self.root)}
        self.assertEqual(rows['scripts/probe.sh'],(b'#!/bin/sh\nprintf fixture\n',0o755))
        self.assertEqual(rows['SKILL.md'][1],0o644)

    def test_tracked_file_alias_cannot_import_external_bytes(self):
        external = Path(self.tmp.name)/'synthetic-outside.txt'
        external.write_bytes(b'SYNTHETIC OUTSIDE SOURCE, NOT A SECRET\n')
        self.script.unlink(); self.link(self.script,external); self.track()
        with self.assertRaisesRegex(PACKAGE.ContractError, "must not be aliased"):
            PACKAGE.source_skill_entries(self.root)

    def test_tracked_dangling_alias_is_not_silently_omitted(self):
        self.script.unlink(); self.link(self.script,Path(self.tmp.name)/'absent'); self.track()
        with self.assertRaisesRegex(PACKAGE.ContractError, "must not be aliased"):
            PACKAGE.source_skill_entries(self.root)

    def test_directory_alias_is_not_a_partial_governor_projection(self):
        scripts = self.gov/'scripts'; outside = Path(self.tmp.name)/'external-scripts'
        shutil.move(str(scripts),str(outside)); self.link(scripts,outside); self.track()
        with self.assertRaisesRegex(PACKAGE.ContractError, "must not be aliased"):
            PACKAGE.source_skill_entries(self.root)

    def test_untracked_file_still_cannot_bless_its_inventory(self):
        (self.gov/'untracked.md').write_bytes(b'untracked\n')
        with self.assertRaises(PACKAGE.ContractError):
            PACKAGE.source_skill_entries(self.root)

    def test_standalone_projection_does_not_require_canonical_host_metadata(self):
        # The standalone role consumes child cognition, not plugin manifests/hooks.
        contract_path = self.root / PACKAGE.CONTRACT_PATH
        contract_path.parent.mkdir(parents=True, exist_ok=True)
        contract_path.write_bytes((ROOT / PACKAGE.CONTRACT_PATH).read_bytes())
        for name in PACKAGE.EXPECTED_REQUIRED_SKILLS[1:]:
            child = self.root / 'skills' / name / 'SKILL.md'
            child.parent.mkdir(parents=True, exist_ok=True)
            child.write_bytes((ROOT / 'skills' / name / 'SKILL.md').read_bytes())
        self.track()
        import json
        contract = json.loads(contract_path.read_bytes())
        entries = PACKAGE.artifact_payload_entries(self.root, 'standalone_compatibility', contract)
        names = [name for name, _data, _mode in entries]
        self.assertIn('internal-procedures/audit-state.md', names)
        self.assertNotIn('hooks/hooks.json', names)
        self.assertNotIn('.codex-plugin/plugin.json', names)

    def test_registry_invokes_this_contract_once(self):
        self.assertEqual((ROOT/'tests/package-contract.test.sh').read_text().count(
            'tests/package-source-path-contract.py'),1)

class PackageInventorySourceState(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='package-inventory-state-')
        self.addCleanup(self.tmp.cleanup)
        self.asset = Path(self.tmp.name) / 'IMPLEMENTAUDIT.plugin.zip'
        self.contract = json.loads((ROOT / PACKAGE.CONTRACT_PATH).read_bytes())

    def expect_state_refusal(self, state, message, *, require_clean=False):
        # This metadata-only witness deliberately has a malformed commit. Valid
        # state strings must reach that later identity gate, without claiming a
        # complete package acceptance or bypassing source equality and size caps.
        inventory = {
            'schema': self.contract['inventory_contract']['format'],
            'artifact_role': 'canonical_plugin',
            **{field: self.contract[field] for field in (
                'package_name', 'runtime_version', 'release_family',
                'public_governor', 'required_skills', 'internal_skills')},
            'source': {'commit': 'not-a-commit', 'tree': 'b' * 40,
                       'worktree_state': state},
            'members': [],
        }
        entries = {PACKAGE.PACKAGE_NAME: self.contract, PACKAGE.INVENTORY_NAME: inventory}
        with zipfile.ZipFile(self.asset, 'w') as archive:
            for name, value in sorted(entries.items()):
                info = zipfile.ZipInfo(name)
                info.create_system = 3
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                archive.writestr(info, (json.dumps(value) + '\n').encode('utf-8'))
        before = self.asset.read_bytes()
        argv = [sys.executable, '-B', str(ROOT / 'scripts/package-contract.py'),
                '--repo-root', str(ROOT), '--verify-artifact',
                'canonical_plugin', str(self.asset)]
        if require_clean:
            argv.append('--require-clean-source')
        result = subprocess.run(argv, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertNotIn('Traceback', result.stderr, result.stderr)
        self.assertEqual(result.stderr.strip(), 'package-contract: ' + message)
        with self.assertRaisesRegex(PACKAGE.ContractError, message):
            PACKAGE.verify_artifact(ROOT, 'canonical_plugin', self.asset,
                                    self.contract, require_clean_source=require_clean)
        self.assertEqual(self.asset.read_bytes(), before)

    def test_malformed_states_use_typed_refusal(self):
        for state in ([], {}, None, True, False, 0, 1, 1.5, '', 'CLEAN',
                      'unknown', ['clean'], {'state': 'clean'}):
            with self.subTest(state=state):
                self.expect_state_refusal(state, 'inventory worktree_state must be clean or dirty')

    def test_clean_and_dirty_states_reach_identity_validation(self):
        for state in ('clean', 'dirty'):
            with self.subTest(state=state):
                self.expect_state_refusal(state, 'inventory commit/tree identity is malformed')

    def test_dirty_state_still_refuses_require_clean_source(self):
        self.expect_state_refusal('dirty', 'release/install artifact source binding is dirty',
                                  require_clean=True)

if __name__ == '__main__':
    unittest.main(verbosity=2)
