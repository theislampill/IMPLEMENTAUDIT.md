"""INERT fixture producer for the new Python-to-recovered-V8 interface tests.

No real tool invocation or bound-positive semantic claim is emitted. This test
worker keeps new run(), original journal and original control-prefix checks
real, while explicitly replacing the unavailable authentic bound receiver and
TTY input boundaries. The complete production driver is otherwise unchanged.
"""
import importlib.util
import json
from pathlib import Path
import sys
import types
from unittest.mock import patch

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import test_support as F

spec=importlib.util.spec_from_file_location('new_semantic_fixture_worker',HERE/'semantic_receiver.py')
S=importlib.util.module_from_spec(spec);spec.loader.exec_module(S)
workspace=Path(sys.argv[1])
mode=sys.argv[2]
f=F.runtime_fixture(S,workspace,mode=mode,live_seconds=30)
_,writer=S.source_owners()
resolver=types.SimpleNamespace(read_ephemeral_frame=lambda maximum,seconds:f.frame)
with patch.object(S,'load_receiver',return_value=f.R),patch.object(S,'source_owners',return_value=(resolver,writer)):
    if mode=='control':
        with patch.object(S,'load_control_preparer',return_value=F.control_preparer_fixture(S,f)):
            outcome=S.run(f.selected_runtime)
    else:
        outcome=S.run(f.selected_runtime)
assert outcome['status'] in ('PUBLIC_SEMANTIC_RECEIVING_COMPLETE_DATA_ONLY',
    'LOCAL_CONTROL_PREPARATION_REQUIRES_SEPARATE_PUBLICATION_AUTHORITY'),outcome
print(json.dumps({'fixture_scope':'SIMULATED_EXTERNAL_PROVENANCE_AND_BOUND_RECEIVER_ONLY',
    'runtime':f.selected_runtime,'frame':f.frame.decode(),'outcome':outcome,'now_ms':int(S.time.time()*1000)}))
