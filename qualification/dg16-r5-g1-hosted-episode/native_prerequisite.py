"""Exact maintained bank03 wrapper/validator only; no primitive probe."""
import re

TESTS = (
 'test_actual_later_invalidation_prevents_return',
 'test_derivative_snapshot_change_after_use_prevents_return',
 'test_native_intake_later_boundary_prevents_return',
 'test_native_intake_rejects_opaque_fixture_work_graph',
 'test_native_intake_rejects_unowned_nested_record',
 'test_native_intake_uses_current_original14_not_retired_root',
 'test_protected_document_change_after_use_prevents_return',
 'test_real_original14_documents_reach_unchanged_graph_parser',
 'test_valid_original14_owner_does_not_supply_missing_graph_document',
)

KNOWN_CODES = ('CONTINUITY_TRANSPORT_NAMESPACE_REFUSED','CONTINUITY_TRANSPORT_TIMEOUT','CANONICAL_WORK_GRAPH','SOURCE_PROFILE_REFUSED','NATIVE_CHECKPOINT','NETLINK_ROUTE','OS_OPERATION_NOT_PERMITTED','OS_PERMISSION_DENIED','OS_REQUIRED_PATH_UNAVAILABLE')

EXCEPTIONS = ('AssertionError','RuntimeError','ValueError','OSError','TimeoutError','WorkGraphError','ContinuityTransportError','FileNotFoundError','PermissionError','OTHER')

CHILD = r'''import hashlib,importlib.util,io,json,os,pathlib,sys,traceback,unittest
sys.dont_write_bytecode=True
root=pathlib.Path(sys.argv[1]); path=root/'tests/work-graph-original14-receiving-cases.py'
os.chdir(root)
spec=importlib.util.spec_from_file_location('hosted_original14',path)
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
expected=json.loads(sys.argv[2]); suite=unittest.defaultTestLoader.loadTestsFromTestCase(module.Original14GraphReceiving)
names=[test._testMethodName for test in suite]
if names!=expected:raise RuntimeError('BANK_POPULATION_REFUSED')
class Record(unittest.TextTestResult):
    def __init__(self,*a,**kw):super().__init__(*a,**kw);self.rows=[]
    def record(self,test,outcome,err=None):
        row={'test':test._testMethodName,'outcome':outcome,'exception_type':None,
             'diagnostic_bytes':0,'diagnostic_sha256':hashlib.sha256(b'').hexdigest(),'known_codes':[]}
        if err is not None:
            raw=''.join(traceback.format_exception(*err)).encode('utf-8','replace')
            kind=err[0].__name__
            row.update(exception_type=kind if kind in ('AssertionError','RuntimeError','ValueError','OSError',
                       'TimeoutError','WorkGraphError','ContinuityTransportError','FileNotFoundError','PermissionError') else 'OTHER',
                       diagnostic_bytes=len(raw),diagnostic_sha256=hashlib.sha256(raw).hexdigest())
            needles=(('CONTINUITY_TRANSPORT_NAMESPACE_REFUSED',b'CONTINUITY_TRANSPORT_NAMESPACE_REFUSED'),
                     ('CONTINUITY_TRANSPORT_TIMEOUT',b'CONTINUITY_TRANSPORT_TIMEOUT'),
                     ('CANONICAL_WORK_GRAPH',b'canonical WORK_GRAPH'),
                     ('SOURCE_PROFILE_REFUSED',b'SOURCE_REFUSED'),
                     ('NATIVE_CHECKPOINT',b'native checkpoint'),
                     ('NETLINK_ROUTE',b'NETLINK_ROUTE'),
                     ('OS_OPERATION_NOT_PERMITTED',b'Operation not permitted'),
                     ('OS_PERMISSION_DENIED',b'Permission denied'),
                     ('OS_REQUIRED_PATH_UNAVAILABLE',b'No such file or directory'))
            row['known_codes']=[name for name,needle in needles if needle in raw]
        self.rows.append(row)
    def addSuccess(self,test):super().addSuccess(test);self.record(test,'PASS')
    def addFailure(self,test,err):super().addFailure(test,err);self.record(test,'FAIL',err)
    def addError(self,test,err):super().addError(test,err);self.record(test,'ERROR',err)
    def addSkip(self,test,reason):super().addSkip(test,reason);self.record(test,'SKIP')
    def addExpectedFailure(self,test,err):super().addExpectedFailure(test,err);self.record(test,'EXPECTED_FAILURE',err)
    def addUnexpectedSuccess(self,test):super().addUnexpectedSuccess(test);self.record(test,'UNEXPECTED_SUCCESS')
stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Record).run(suite)
raw=stream.getvalue().encode('utf-8','replace')
record={'schema':'dg16.linux-native-bank.v1','test_population':names,'tests_run':result.testsRun,
        'success':result.wasSuccessful(),'rows':result.rows,'runner_text_bytes':len(raw),
        'runner_text_sha256':hashlib.sha256(raw).hexdigest()}
print(json.dumps(record,sort_keys=True,separators=(',',':')),flush=True)
raise SystemExit(0 if result.wasSuccessful() else 1)
'''

class Refusal(Exception): pass

def need(value, code):
    if not value: raise Refusal(code)

def validate_bank(v):
    need(type(v) is dict and set(v)=={'schema','test_population','tests_run','success','rows','runner_text_bytes','runner_text_sha256'} and
         v['schema']=='dg16.linux-native-bank.v1' and v['test_population']==list(TESTS) and
         type(v['tests_run']) is int and v['tests_run']==9 and type(v['success']) is bool and
         type(v['rows']) is list and len(v['rows'])==9 and type(v['runner_text_bytes']) is int and v['runner_text_bytes']>=0 and
         re.fullmatch('[0-9a-f]{64}',v['runner_text_sha256']),'BANK_RESULT_SHAPE_REFUSED')
    seen=[]
    for row in v['rows']:
        need(type(row) is dict and set(row)=={'test','outcome','exception_type','diagnostic_bytes','diagnostic_sha256','known_codes'} and
             row['test'] in TESTS and row['outcome'] in ('PASS','FAIL','ERROR','SKIP','EXPECTED_FAILURE','UNEXPECTED_SUCCESS') and
             (row['exception_type'] is None or row['exception_type'] in EXCEPTIONS) and
             type(row['diagnostic_bytes']) is int and row['diagnostic_bytes']>=0 and
             re.fullmatch('[0-9a-f]{64}',row['diagnostic_sha256']) and type(row['known_codes']) is list and
             len(row['known_codes'])==len(set(row['known_codes'])) and all(x in KNOWN_CODES for x in row['known_codes']),'BANK_ROW_REFUSED')
        seen.append(row['test'])
    need(seen==list(TESTS),'BANK_RESULT_POPULATION_REFUSED')
    return v
