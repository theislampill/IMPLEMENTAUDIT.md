"""New inert regressions for the independently observed file-open race."""
import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE=Path(__file__).with_name('semantic_receiver.py')
spec=importlib.util.spec_from_file_location('custody_subject',SOURCE)
S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)

class FileCustody(unittest.TestCase):
    def test_regular_to_fifo_race_refuses_without_waiting_for_writer(self):
        worker='''import importlib.util,os,sys
from pathlib import Path
spec=importlib.util.spec_from_file_location("subject",sys.argv[1]);S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)
p=Path(sys.argv[2]);p.write_bytes(b"inert public input")
original=os.open
def swap(path,flags,*args,**kwargs):
 if str(path)==str(p):
  p.unlink();os.mkfifo(p,0o600)
 return original(path,flags,*args,**kwargs)
S.os.open=swap
try:S.checked_file(p,100)
except ValueError as exc:print("REFUSED:"+str(exc))
else:raise RuntimeError("race accepted")
'''
        with tempfile.TemporaryDirectory(prefix='INERT_FIFO_') as tmp:
            result=subprocess.run([sys.executable,'-I','-B','-c',worker,str(SOURCE),str(Path(tmp)/'input')],
                                  capture_output=True,text=True,timeout=1)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(result.stdout,'REFUSED:INPUT_CHANGED\n')

    def test_replaced_regular_file_refuses_before_any_body_read(self):
        with tempfile.TemporaryDirectory(prefix='INERT_REPLACE_') as tmp:
            p=Path(tmp)/'input';p.write_bytes(b'original')
            replacement=Path(tmp)/'replacement';replacement.write_bytes(b'changed!')
            original=os.open
            def swap(path,flags,*args,**kwargs):
                replacement.replace(p)
                return original(path,flags,*args,**kwargs)
            with patch.object(S.os,'open',side_effect=swap),patch.object(S.os,'fdopen',side_effect=AssertionError('BODY_READ_BEFORE_IDENTITY')):
                with self.assertRaisesRegex(ValueError,'INPUT_CHANGED'):
                    S.checked_file(p,100)

    def test_closing_identity_still_refuses_replacement_after_read(self):
        with tempfile.TemporaryDirectory(prefix='INERT_CLOSING_') as tmp:
            p=Path(tmp)/'input';p.write_bytes(b'original')
            replacement=Path(tmp)/'replacement';replacement.write_bytes(b'changed!')
            original=os.fdopen
            class ReadThenReplace:
                def __init__(self,*args,**kwargs):self.stream=original(*args,**kwargs)
                def __enter__(self):return self
                def __exit__(self,*args):self.stream.close()
                def read(self,maximum):
                    result=self.stream.read(maximum);replacement.replace(p);return result
            with patch.object(S.os,'fdopen',side_effect=ReadThenReplace):
                with self.assertRaisesRegex(ValueError,'INPUT_CHANGED'):
                    S.checked_file(p,100)

if __name__=='__main__':unittest.main(verbosity=2)
