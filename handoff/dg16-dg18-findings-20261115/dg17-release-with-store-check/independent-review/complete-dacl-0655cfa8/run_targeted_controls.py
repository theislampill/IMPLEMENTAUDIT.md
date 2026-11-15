"""Only the eleven fixture-specific tests; no earlier lifecycle suite rerun."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path('/workspace/scratch/0269e6626329/dg17')
REVIEW=Path(__file__).absolute().parent
COMMIT='0655cfa87cc3b81ed59ffa046d07b1ba616d631e'
PATH=ROOT/'handoff/dg16-dg18-findings-20261115/dg17-release-with-store-check/tools/test_driver_bundle.py'
packet=json.loads((ROOT/'.IMPLEMENTAUDIT/dg17-dacl-reconstructed-20261115/AUTHOR_REVIEW_PACKET.json').read_bytes())
assert packet['candidate_commit']==COMMIT
names=packet['focused_green']['command'][3:]
assert len(names)==11 and all(n.startswith('DriverBundle.test_store_fixture_') for n in names)
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==COMMIT
assert not subprocess.check_output(['git','status','--porcelain=v1'],cwd=ROOT)
assert PATH.read_bytes()==subprocess.check_output(['git','show',COMMIT+':'+str(PATH.relative_to(ROOT))],cwd=ROOT)
spec=importlib.util.spec_from_file_location('reviewed_fixture_controls',PATH)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
suite=unittest.TestSuite(module.DriverBundle(n.split('.',1)[1]) for n in names)
original=tempfile.TemporaryDirectory
def review_temp(*args,**kwargs):return original(*args,**(kwargs|{'dir':REVIEW}))
with patch.object(module.tempfile,'TemporaryDirectory',review_temp):
    result=unittest.TextTestRunner(verbosity=2).run(suite)
assert result.testsRun==11
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==COMMIT
assert not subprocess.check_output(['git','status','--porcelain=v1'],cwd=ROOT)
sys.exit(0 if result.wasSuccessful() else 1)
