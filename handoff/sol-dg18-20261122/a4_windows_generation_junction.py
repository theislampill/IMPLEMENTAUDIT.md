import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

root = Path.cwd().resolve()
suite = root / 'fixtures/canonical-state-rotation/claim_transaction_test.py'
bash = Path(r'C:\Program Files\Git\bin\bash.exe')
os.environ['PATH'] = str(bash.parent) + os.pathsep + os.environ['PATH']
assert Path(shutil.which('bash')).resolve() == bash.resolve()
with tempfile.TemporaryDirectory(prefix='a4-', dir=root) as temporary:
    scratch = Path(temporary).resolve()
    assert scratch.parent == root
    os.environ['R0039_CLAIM_EVIDENCE_DIR'] = str(scratch)
    spec = importlib.util.spec_from_file_location('criterion4_base', suite)
    fixture = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fixture)

    class ScopedRefusals(fixture.CompleteOwnerDiscriminators):
        def check_pair(self, prepared):
            manifest = self.helper.verify_canonical_archive(
                self.fixture.repo, fixture.CONTROLLER, prepared['archive_ref'], prepared['archive_manifest_sha256'])
            recovered = {}
            for role, original in self.original_pair.items():
                entry, = [row for row in manifest['entries'] if row['role'] == role + '_PREIMAGE']
                raw = self.owner.read_blob(self.fixture.repo, entry['blob_oid'])
                self.assertEqual(raw, original)
                self.assertEqual((self.fixture.run_root / (role + '.md')).read_bytes(), raw)
                recovered[role] = {'bytes':len(raw), 'sha256':hashlib.sha256(raw).hexdigest()}
            return recovered

        def check_refusal(self, prepared, reason):
            before = self.snapshot()
            refused = self.fixture.claim('--require-current-continuity', fixture.CONTROLLER)
            self.assertNotEqual(refused.returncode, 0)
            self.assertEqual(refused.stdout, b'')
            after = self.snapshot()
            self.assertEqual(after, before)
            return {'fault':reason, 'code':refused.returncode, 'diagnostic':refused.stderr.decode().splitlines()[-1],
                    'snapshot_equal':True, 'exact_preimage':self.check_pair(prepared)}

        def test_disposable_windows_criterion4_junction_preserves_preimage(self):
            rotated = self.rotate()
            self.assertEqual(rotated['status'], 'ROTATED')
            joined = self.owner.require_current_generation_join_v1(self.context)
            self.assertEqual(joined['receipt_token'], rotated['receipt_token'])
            epoch, _ = self.owner.read_epoch(self.context, 'G0002')
            prepared = epoch['prepared']
            generation = joined['state_path'].parent
            saved = generation.with_name(generation.name + '-saved-fixture')
            target = self.fixture.repo / 'outside-generation-fixture'
            target.mkdir()
            sentinels = {'STATE.md': b'outside state sentinel\n', 'ROADMAP.md': b'outside roadmap sentinel\n'}
            for name, body in sentinels.items():
                (target / name).write_bytes(body)
            generation.rename(saved)
            try:
                proc = subprocess.run([os.environ.get('COMSPEC', r'C:\Windows\System32\cmd.exe'),
                                       '/d', '/c', 'mklink', '/J', str(generation), str(target)],
                                       cwd=self.fixture.repo, capture_output=True, check=False, timeout=10)
                self.assertEqual(proc.returncode, 0, 'junction fixture setup failed')
                try:
                    before = self.fixture.git('for-each-ref', '--format=%(refname) %(objectname)', 'refs/implementaudit/')
                    blocked = self.fixture.claim('--read-current-state', fixture.CONTROLLER, 'STATE',
                                                 '--expected-pointer', rotated['pointer_token'])
                    self.assertNotEqual(blocked.returncode, 0)
                    self.assertEqual(blocked.stdout, b'')
                    self.assertEqual(self.fixture.git('for-each-ref', '--format=%(refname) %(objectname)',
                                                      'refs/implementaudit/'), before)
                    for name, body in sentinels.items():
                        self.assertEqual((target / name).read_bytes(), body)
                    preimage = self.check_pair(prepared)
                finally:
                    generation.rmdir()
            finally:
                saved.rename(generation)
            verified = self.fixture.claim('--require-current-continuity', fixture.CONTROLLER)
            self.assertEqual(verified.returncode, 0)
            self.assertEqual(verified.stdout.decode().strip(), joined['receipt_token'])
            print(json.dumps({'fault':'junction_at_published_generation', 'code':blocked.returncode,
                              'diagnostic':blocked.stderr.decode().splitlines()[-1], 'refs_equal':True,
                              'outside_sentinels_equal':True, 'exact_preimage':preimage,
                              'restored_receipt_equal':True}), flush=True)

    test = ScopedRefusals('test_disposable_windows_criterion4_junction_preserves_preimage')
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([test]))
    entries = sorted(item.name for item in scratch.iterdir())
print(json.dumps({'ok':result.wasSuccessful(),'scratch_entries':entries,'scratch_removed':not scratch.exists()}))
sys.exit(0 if result.wasSuccessful() and not entries and not scratch.exists() else 1)
