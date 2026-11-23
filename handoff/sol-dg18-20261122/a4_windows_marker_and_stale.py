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

        def test_disposable_windows_criterion4_stale_receipt_and_wrong_controller(self):
            rotated = self.rotate()
            self.assertEqual(rotated['status'], 'ROTATED')
            joined = self.owner.require_current_generation_join_v1(self.context)
            self.assertEqual(joined['receipt_token'], rotated['receipt_token'])
            epoch, _ = self.owner.read_epoch(self.context, 'G0002')
            prepared = epoch['prepared']
            marker_ref, good = self.context['marker_ref'], joined['marker_oid']
            marker = self.owner.tsv(self.owner.read_blob(self.fixture.repo, good), 10, terminal_lf=False)
            marker[1] = 'wrong-controller'
            substituted = self.fixture.blob('\t'.join(marker).encode())
            self.fixture.git('update-ref', marker_ref, substituted, good)
            try:
                wrong = self.check_refusal(prepared, 'foreign_controller_in_marker')
            finally:
                self.fixture.git('update-ref', marker_ref, good, substituted)
            restored = self.fixture.claim('--require-current-continuity', fixture.CONTROLLER)
            self.assertEqual(restored.returncode, 0)
            self.assertEqual(restored.stdout.decode().strip(), joined['receipt_token'])
            advance = self.fixture.claim('--invalidate-continuity', fixture.CONTROLLER,
                                         '--boundary', 'new-session', '--event', 'criterion4-fixture-later-boundary')
            self.assertEqual(advance.returncode, 0, advance.stderr.decode())
            self.assertNotEqual(advance.stdout.decode().strip().split('@')[-1], joined['pointer']['invalidation_oid'])
            stale = self.check_refusal(prepared, 'new_fixture_invalidation_stales_old_receipt')
            print(json.dumps({'initial_rotation': rotated['status'], 'marker_restore_receipt_equal': True,
                              'controls': [wrong, stale]}), flush=True)

    test = ScopedRefusals('test_disposable_windows_criterion4_stale_receipt_and_wrong_controller')
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite([test]))
    entries = sorted(item.name for item in scratch.iterdir())
print(json.dumps({'ok':result.wasSuccessful(),'scratch_entries':entries,'scratch_removed':not scratch.exists()}))
sys.exit(0 if result.wasSuccessful() and not entries and not scratch.exists() else 1)
