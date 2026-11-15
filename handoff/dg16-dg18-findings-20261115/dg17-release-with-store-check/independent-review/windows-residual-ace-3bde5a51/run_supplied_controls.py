"""Run frozen supplied controls, redirecting only disposable output to review dir."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path('/workspace/scratch/0269e6626329/dg17')
COMMIT='3bde5a5123d3b1c6cf908b2e263504dce994d4e7'
REVIEW=Path(__file__).absolute().parent
PATH=ROOT/'handoff/dg16-dg18-findings-20261115/dg17-release-with-store-check/tools/test_driver_bundle.py'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==COMMIT
assert not subprocess.check_output(['git','status','--porcelain=v1'],cwd=ROOT)
assert PATH.read_bytes()==subprocess.check_output(['git','show',COMMIT+':'+str(PATH.relative_to(ROOT))],cwd=ROOT)
spec=importlib.util.spec_from_file_location('reviewed_supplied_controls',PATH)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
original=tempfile.TemporaryDirectory
def review_temp(*args,**kwargs):return original(*args,**(kwargs|{'dir':REVIEW}))
with patch.object(module.tempfile,'TemporaryDirectory',review_temp):
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromModule(module))
assert result.testsRun==25
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()==COMMIT
assert not subprocess.check_output(['git','status','--porcelain=v1'],cwd=ROOT)
sys.exit(0 if result.wasSuccessful() else 1)
