"""Constructed selected-reader lifetime controls; no native acceptance credit."""
import argparse
import contextlib
import copy
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2]

class SelectedNativeReadControls(unittest.TestCase):
    def setUp(self):
        path=ROOT/'fixtures/operational-evidence/repository-fence-cost-controls.py'
        fixture=types.ModuleType('selected_read_repository_harness');fixture.__file__=str(path)
        with patch.object(sys,'argv',[str(path),str(ROOT)]):
            exec(compile(path.read_bytes(),str(path),'exec'),fixture.__dict__)
        self.case=fixture.RepositoryFenceCostTests('test_native_drift_is_still_observed')
        self.case.setUp();self.addCleanup(self.case.doCleanups)
        self.oe=fixture.oe;self.case.publish()
        self.openings=0;self.closings=0;self.on_close=lambda:None

    @contextlib.contextmanager
    def native_observation(self):
        self.openings+=1;before=copy.deepcopy(self.case.native)
        yield copy.deepcopy(before)
        self.on_close();self.closings+=1
        if before!=self.case.native:
            raise self.oe.OperationalEvidenceError('OE_NATIVE_CURRENT_CHANGED','$native.fixture','constructed late native drift')

    @contextlib.contextmanager
    def selected(self):
        with patch.object(self.oe,'__file__',str(self.case.root/'scripts/operational-evidence.py')), \
                patch.object(self.oe,'collect_native_current',side_effect=lambda:copy.deepcopy(self.case.native)) as repeated, \
                patch.object(self.oe,'_observe_native_current_v1',side_effect=self.native_observation,create=True):
            yield repeated

    def test_selected_reader_uses_one_completed_native_observation(self):
        with self.selected() as repeated:
            payload=self.oe._load_selected_snapshot_v1()
        self.assertEqual(payload['snapshot_id'],__import__('json').loads(self.case.current.read_bytes())['snapshot_id'])
        self.assertEqual((self.openings,self.closings,repeated.call_count),(1,1,0))

    def test_late_native_change_after_materialization_refuses(self):
        original=self.oe._build_snapshot_material_v1
        def changed(*args):
            result=original(*args)
            self.case.native['hot']['state_sha256']='9'*64
            return result
        with self.selected(),patch.object(self.oe,'_build_snapshot_material_v1',side_effect=changed):
            with self.assertRaises(self.oe.OperationalEvidenceError):
                self.oe._load_selected_snapshot_v1()

    def test_repository_change_during_native_close_still_refuses(self):
        self.on_close=lambda:(self.case.root/'local.py').write_bytes(b'VALUE = 2\n')
        with self.selected(),self.assertRaises(self.oe.OperationalEvidenceError):
            self.oe._load_selected_snapshot_v1()
        self.assertEqual(self.closings,1)

    def test_CURRENT_change_during_native_close_still_refuses(self):
        self.on_close=lambda:self.case.current.write_bytes(b'changed CURRENT\n')
        with self.selected(),self.assertRaises(self.oe.OperationalEvidenceError):
            self.oe._load_selected_snapshot_v1()
        self.assertEqual(self.closings,1)

    def test_native_close_failure_never_returns_selected_payload(self):
        def refuse():
            raise self.oe.OperationalEvidenceError('OE_NATIVE_CURRENT_CHANGED','$native.fixture','constructed closing refusal')
        self.on_close=refuse
        with self.selected(),self.assertRaises(self.oe.OperationalEvidenceError):
            self.oe._load_selected_snapshot_v1()

    def test_each_selected_transaction_has_its_own_native_observation(self):
        with self.selected() as repeated:
            first=self.oe._load_selected_snapshot_v1();second=self.oe._load_selected_snapshot_v1()
        self.assertEqual(first,second)
        self.assertEqual((self.openings,self.closings,repeated.call_count),(2,2,0))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--repo-root',type=Path,default=ROOT)
    args,rest=parser.parse_known_args();ROOT=args.repo_root.resolve()
    unittest.main(argv=[__file__,*rest])
