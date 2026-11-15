"""Independent controls for replacement-only intent, UNKNOWN and optimization edges.

All receiver/provenance/frame inputs are explicit inert test seams. The original
private journal, new run() and original tree function remain actual local code.
No provider, native episode, original baseline suite or effect grant is invoked.
"""
import importlib.util,json,subprocess,sys,tempfile,types,unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parent
SOURCE=HERE/'source-copy/qualification/dg16-github-evidence/semantic-integration'
sys.path.insert(0,str(SOURCE))
import semantic_receiver as S
import test_support as F

class IndependentEdges(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='INERT_REVIEW_EDGE_',dir=HERE)
        self.addCleanup(self.tmp.cleanup)
        self.workspace=Path(self.tmp.name)

    def test_intent_expiry_marks_unknown_before_any_frame(self):
        f=F.runtime_fixture(S,self.workspace,live_seconds=5)
        _,Writer=S.source_owners();frames=[]
        class DelayedIntent(Writer):
            def write(self,name,raw):
                super().write(name,raw)
                if name=='INTENT.json':f.clock[0]=f.request['expires_utc_epoch']
        def frame(*args):frames.append(1);return f.frame
        with patch.object(S,'load_receiver',return_value=f.R),patch.object(S,'source_owners',return_value=(types.SimpleNamespace(read_ephemeral_frame=frame),DelayedIntent)),patch.object(S.time,'time',side_effect=lambda:f.clock[0]):
            result=S.run(f.selected_runtime)
        self.assertEqual(result['status'],'REFUSED_OR_UNCERTAIN_NO_RETRY')
        self.assertEqual(result['stage'],'intent');self.assertEqual(frames,[])
        self.assertEqual(len(list(f.journal.glob('*/INTENT.json'))),1)
        self.assertEqual(len(list(f.journal.glob('*/UNKNOWN.json'))),1)
        self.assertEqual(list(f.journal.glob('*/FINAL.json')),[])

    def test_lost_frame_is_unknown_and_stays_spent_without_echo(self):
        f=F.runtime_fixture(S,self.workspace)
        _,Writer=S.source_owners();frames=[]
        def lost(*args):frames.append(1);raise RuntimeError('INERT_UNTRUSTED_EXCEPTION_TEXT')
        with patch.object(S,'load_receiver',return_value=f.R),patch.object(S,'source_owners',return_value=(types.SimpleNamespace(read_ephemeral_frame=lost),Writer)),patch.object(S.time,'time',side_effect=lambda:f.clock[0]):
            first=S.run(f.selected_runtime)
            before={str(p):p.read_bytes() for p in f.journal.rglob('*') if p.is_file()}
            second=S.run(f.selected_runtime)
            after={str(p):p.read_bytes() for p in f.journal.rglob('*') if p.is_file()}
        self.assertEqual(first['status'],'REFUSED_OR_UNCERTAIN_NO_RETRY')
        self.assertEqual(second['status'],'REFUSED_OR_UNCERTAIN_NO_RETRY')
        self.assertEqual(frames,[1]);self.assertEqual(before,after)
        self.assertEqual(len(list(f.journal.glob('*/UNKNOWN.json'))),1)
        self.assertNotIn('INERT_UNTRUSTED_EXCEPTION_TEXT',json.dumps([first,second])+b''.join(after.values()).decode())

    def test_original_tree_duplicate_guard_survives_optimized_import(self):
        code="""import sys
sys.path.insert(0,sys.argv[1])
import semantic_receiver as S
row={'path':'fixture.txt','mode':'100644','git_blob':'1'*40}
try:S.original_tree_id([row,row])
except AssertionError:print('ORIGINAL_DUPLICATE_GUARD_RETAINED')
else:print('DUPLICATE_ACCEPTED')
"""
        p=subprocess.run([sys.executable,'-I','-O','-B','-c',code,str(SOURCE)],capture_output=True,text=True,timeout=10)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(p.stdout,'ORIGINAL_DUPLICATE_GUARD_RETAINED\n')

    def test_optimized_production_entry_refuses_before_selection(self):
        p=subprocess.run([sys.executable,'-I','-O','-B',str(SOURCE/'semantic_receiver.py'),'{}'],capture_output=True,text=True,timeout=10)
        self.assertEqual(p.returncode,1)
        self.assertEqual(json.loads(p.stdout),{'status':'REFUSED_OR_UNCERTAIN_NO_RETRY','authority':'NONE','automatic_retry':False,'original_acceptance':False})
        self.assertEqual(p.stderr,'')

if __name__=='__main__':unittest.main(verbosity=2)
