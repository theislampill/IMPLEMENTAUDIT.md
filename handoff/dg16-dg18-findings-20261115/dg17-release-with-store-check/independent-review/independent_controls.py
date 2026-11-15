"""Independent source review controls. No native execution or acceptance."""
import ast
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import types
import unittest
from unittest.mock import patch

ROOT = Path('/workspace/scratch/0269e6626329/dg17')
REVIEW = ROOT.parent / 'dg17-review'
TOOLS = ROOT / 'handoff/dg16-dg18-findings-20261115/dg17-release-with-store-check/tools'
BASE = ROOT / 'handoff/dg16-dg18-findings-20261115/dg17-next-release/author'
AUTHOR = REVIEW / 'generated/author'
CLONE = REVIEW / 'source-negative-fixture'
HEAD = '017d652586004b86468042b7142b4349c2a07619'
PARENT = 'e4cba42cb5704f00b78d64e43f5da88501c28229'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def function(tree, name):
    return next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name)


builder = load(TOOLS / 'build_release_acl.py', 'review_builder')
parent = load(AUTHOR / 'parent_launch_a.py', 'review_parent')
rehearsal = load(TOOLS / 'rehearse_lifecycle.py', 'review_rehearsal')


class IndependentControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = REVIEW / 'adversarial'
        cls.work.mkdir(exist_ok=False)
        cls.op = json.loads((AUTHOR / 'OPERATION_A.json').read_bytes())
        cls.old = json.loads((BASE / 'OPERATION_A.json').read_bytes())

    def test_manifest_exact_population_and_hashes(self):
        manifest_path = TOOLS.parent / 'SOURCE_QUALIFICATION_MANIFEST.json'
        manifest = json.loads(manifest_path.read_bytes())
        changed = set(subprocess.check_output(['git', '-C', str(ROOT), 'diff', '--name-only', PARENT, HEAD], text=True).splitlines())
        described = {x['path'] for x in manifest['changed_file_population_excludes_this_manifest']}
        self.assertEqual(changed, described | {manifest_path.relative_to(ROOT).as_posix()})
        for item in manifest['changed_file_population_excludes_this_manifest']:
            raw = (ROOT / item['path']).read_bytes()
            self.assertEqual((len(raw), digest(raw)), (item['bytes'], item['sha256']))
        self.assertFalse(any(x.startswith(('skills/', 'package/')) for x in changed))

    def test_all_generated_source_and_skill_pins_match_frozen_git_objects(self):
        self.assertEqual(self.op['source_head'], HEAD)
        self.assertEqual(self.op['source_tree'], 'f168ff1e66d06619fa138b500009059ceff40d77')
        for path, expected in self.op['source_pins'].items():
            raw = subprocess.check_output(['git', '-C', str(ROOT), 'show', HEAD + ':' + path])
            self.assertEqual(digest(raw), expected)
        for skill, expected in self.op['native_skill_pins'].items():
            raw = subprocess.check_output(['git', '-C', str(ROOT), 'show', HEAD + ':skills/' + skill + '/SKILL.md'])
            self.assertEqual(digest(raw), expected)
        for item in self.op['readset']:
            path = Path(item['path'])
            if path.is_absolute():
                raw = path.read_bytes()
                self.assertEqual((len(raw), digest(raw)), (item['bytes'], item['sha256']))

    def test_limits_and_native_driver_assertions_preserved(self):
        self.assertEqual(self.op['limits'], self.old['limits'])
        self.assertEqual((AUTHOR / 'native_rpc.py').read_bytes(), (BASE / 'native_rpc.py').read_bytes())
        old_a = ast.parse((BASE / 'stage_a.py').read_bytes())
        new_a = ast.parse((AUTHOR / 'stage_a.py').read_bytes())
        for tree in (old_a, new_a):
            function(tree, 'write_state').body = []
        self.assertEqual(ast.dump(old_a), ast.dump(new_a))
        old_b = ast.parse((BASE / 'stage_b.py').read_bytes())
        new_b = ast.parse((AUTHOR / 'stage_b.py').read_bytes())
        new_b.body = [n for n in new_b.body if not (isinstance(n, ast.FunctionDef) and n.name == 'private_store_directory')]
        class RemoveCustodyCall(ast.NodeTransformer):
            def visit_Assign(self, node):
                if isinstance(node.value, ast.Call) and isinstance(node.value.func, ast.Name) and node.value.func.id == 'private_store_directory':
                    return None
                return self.generic_visit(node)
        RemoveCustodyCall().visit(new_b)
        self.assertEqual(ast.dump(old_b), ast.dump(new_b))
        old_parent = ast.parse((BASE / 'parent_launch_a.py').read_bytes())
        new_parent = ast.parse((AUTHOR / 'parent_launch_a.py').read_bytes())
        self.assertEqual(ast.dump(function(old_parent, 'capture')), ast.dump(function(new_parent, 'capture')))

    def test_dirty_runtime_bytes_refused_before_output(self):
        target = CLONE / 'skills/implementaudit/scripts/host-session-binding.py'
        original = target.read_bytes()
        output = self.work / 'dirty-runtime/author'
        try:
            target.write_bytes(original + b'\n# SIMULATED reviewer mutation\n')
            with self.assertRaisesRegex(ValueError, 'differs from selected HEAD'):
                builder.build(BASE, output, CLONE)
            self.assertFalse(output.exists())
        finally:
            target.write_bytes(original)

    def test_symlinked_runtime_source_refused_before_output(self):
        target = CLONE / 'skills/implementaudit/scripts/host-session-binding.py'
        original = target.read_bytes()
        carrier = self.work / 'source-carrier.py'
        carrier.write_bytes(original)
        output = self.work / 'aliased-runtime/author'
        try:
            target.unlink()
            target.symlink_to(carrier)
            with self.assertRaisesRegex(ValueError, 'Aliased or reparse'):
                builder.build(BASE, output, CLONE)
            self.assertFalse(output.exists())
        finally:
            target.unlink()
            target.write_bytes(original)

    def test_dangling_output_alias_and_manifest_collision_refused(self):
        alias = self.work / 'dangling'
        alias.symlink_to(self.work / 'missing', target_is_directory=True)
        with self.assertRaisesRegex(ValueError, 'Aliased or reparse'):
            builder.build(BASE, alias / 'author', ROOT)
        output = self.work / 'manifest-collision/author'
        output.parent.mkdir()
        (output.parent / 'PINS.json').write_bytes(b'SIMULATED prior record')
        with self.assertRaisesRegex(ValueError, 'manifest already exists'):
            builder.build(BASE, output, ROOT)
        self.assertFalse(output.exists())

    def test_capture_refuses_actual_open_time_substitution(self):
        target = self.work / 'open-race.py'
        target.write_bytes(b'SIMULATED identical bytes')
        replacement = self.work / 'open-race-replacement.py'
        replacement.write_bytes(target.read_bytes())
        expected = digest(target.read_bytes())
        original_open = os.open
        def swapped_open(path, *args, **kwargs):
            if Path(path) == target:
                os.replace(replacement, target)
            return original_open(path, *args, **kwargs)
        with patch.object(os, 'O_BINARY', 0, create=True), patch.object(os, 'O_NOINHERIT', 0, create=True), patch.object(os, 'open', swapped_open):
            with self.assertRaises(AssertionError):
                parent.capture(target, expected, keep=True)

    def test_capture_refuses_actual_after_read_substitution(self):
        target = self.work / 'read-race.py'
        target.write_bytes(b'SIMULATED identical bytes')
        replacement = self.work / 'read-race-replacement.py'
        replacement.write_bytes(target.read_bytes())
        expected = digest(target.read_bytes())
        original_fstat = os.fstat
        calls = 0
        def swapped_fstat(fd):
            nonlocal calls
            result = original_fstat(fd)
            calls += 1
            if calls == 2:
                os.replace(replacement, target)
            return result
        with patch.object(os, 'O_BINARY', 0, create=True), patch.object(os, 'O_NOINHERIT', 0, create=True), patch.object(os, 'fstat', swapped_fstat):
            with self.assertRaises(AssertionError):
                parent.capture(target, expected, keep=True)

    def test_child_loader_executes_only_exact_captured_bytes(self):
        target = self.work / 'inert-loader-fixture.py'
        target.write_bytes(b"raise RuntimeError('SIMULATED exact bytes executed')\n")
        expected = digest(target.read_bytes())
        with patch.object(parent, 'DRIVER_SHA', expected), patch.object(os, 'O_BINARY', 0, create=True), patch.object(os, 'O_NOINHERIT', 0, create=True), patch.object(sys, 'argv', []):
            loader = parent.driver_loader(target, [str(target)])
            with self.assertRaisesRegex(RuntimeError, 'SIMULATED exact bytes executed'):
                exec(compile(loader, 'review-exact-loader', 'exec'), {})
            target.write_bytes(b"raise RuntimeError('SIMULATED substituted bytes executed')\n")
            with self.assertRaises(AssertionError):
                exec(compile(loader, 'review-altered-loader', 'exec'), {})
            target.unlink()
            target.symlink_to(self.work / 'source-carrier.py')
            with self.assertRaises(AssertionError):
                exec(compile(loader, 'review-symlink-loader', 'exec'), {})

    def test_rehearsal_direct_native_and_shell_launches_refused(self):
        python = str(Path(sys.executable).resolve())
        bash = str(Path(shutil.which('bash')).resolve())
        git = str(Path(shutil.which('git')).resolve())
        fixture = types.SimpleNamespace(python=python, bash=bash, op={'git':git})
        for args, kwargs in [(['codex', 'app-server'], {}), ([python, 'app-server'], {}), ([bash, 'codex.exe'], {}), ('codex app-server', {}), ([bash, '-c', 'true'], {'shell':True})]:
            def run(args=args, kwargs=kwargs):
                return subprocess.Popen(args, **kwargs)
            fixture.run = run
            with self.subTest(args=args), patch.object(rehearsal, 'Fixture', return_value=fixture), patch.object(sys, 'argv', ['review', '--author', str(AUTHOR), '--work', str(self.work / 'unused')]):
                with self.assertRaises(AssertionError):
                    rehearsal.main()

    def test_local_native_boundary_refused_without_native_effects(self):
        evidence = REVIEW / 'native-boundary/SIMULATED-case/evidence'
        for number in range(1, 6):
            path = next(evidence.glob(f'{number:02d}-*.json'))
            self.assertEqual(json.loads(path.read_bytes())['exit'], 0)
        sixth = json.loads((evidence / '06-new-claim.json').read_bytes())
        self.assertEqual(sixth['exit'], 1)
        self.assertIn('supported physical Python 3 interpreter', sixth['stderr'])
        post = json.loads((evidence / 'POST_A.json').read_bytes())
        self.assertEqual(post['status'], 'STAGE_A_STOPPED_FIRST_REFUSAL_OR_UNKNOWN_NO_RETRY')
        for name in ['thread_start_calls', 'model_turns', 'H0_effects', 'trust_effects', 'qualifying_events']:
            self.assertEqual(post[name], 0)


if __name__ == '__main__':
    with (REVIEW / 'independent-controls.log').open('w') as stream:
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(IndependentControls))
    print((REVIEW / 'independent-controls.log').read_text())
    raise SystemExit(not result.wasSuccessful())
