#!/usr/bin/env python3
"""One maintained positive case; bounded observation of actual failure frames.

No owner hook is replaced and no call is replayed. The only local-value access
is the exact source-pinned compiler frame declared in DIAGNOSTIC_PROFILE.json.
Raw messages, paths, arguments, closure records and stderr never become public.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import types
import unittest

PROFILE_SHA = 'edfa27e59a5f2313500177a0310531cec23cffb5083f2ad2cbc4106291a351cc'
TEST = 'test_native_intake_uses_current_original14_not_retired_root'
SOURCE_COMMIT = '0d57929be5bd15682b4e9da2c0209d5dff307843'
SOURCE_TREE = 'ee316c27250ec422d35a1ea965182ebddf7a5da0'
OUTCOMES = ('PASS','FAIL','ERROR','SKIP','EXPECTED_FAILURE','UNEXPECTED_SUCCESS')
EXCEPTIONS = ('AssertionError','RuntimeError','ValueError','OSError','TimeoutError',
    'WorkGraphError','ContinuityTransportError','FileNotFoundError','PermissionError',
    'ImportError','ModuleNotFoundError','TypeError','KeyError','UnicodeError',
    'UnicodeDecodeError','JSONDecodeError','Refusal','KeyboardInterrupt','SystemExit','OTHER')
LITERALS = (
    ('OWNER_COMPANION_SOURCE',b'claim-run.sh: companion source'),
    ('OWNER_GIT_REV_PARSE',b'claim-run.sh: Git operation failed: rev-parse'),
    ('OWNER_GIT_UNKNOWN_EFFECT',b'claim-run.sh: Git operation has unknown effect'),
    ('OWNER_PYTHON_SELECTION',b'a supported physical Python 3 interpreter is required'),
    ('NATIVE_OWNER_REFUSED',b'native continuity owner refused or changed'),
    ('NATIVE_SOURCE_CLOSURE_CHANGED',b'native continuity executed source closure changed'),
    ('CANONICAL_WORK_GRAPH',b'canonical WORK_GRAPH'),
    ('NETLINK_ROUTE',b'NETLINK_ROUTE'),
    ('OS_OPERATION_NOT_PERMITTED',b'Operation not permitted'),
    ('OS_PERMISSION_DENIED',b'Permission denied'),
    ('OS_REQUIRED_PATH_UNAVAILABLE',b'No such file or directory'))


class Refusal(Exception):
    pass


def need(value, code):
    if not value:
        raise Refusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),
                       ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')


def strict(raw):
    def pairs(items):
        out={}
        for key,value in items:
            need(key not in out,'DUPLICATE_KEY')
            out[key]=value
        return out
    return json.loads(raw,object_pairs_hook=pairs,
        parse_constant=lambda _:(_ for _ in ()).throw(Refusal('NONFINITE_JSON')))


def stamp(info):
    return (info.st_dev,info.st_ino,info.st_mode,info.st_nlink,info.st_size,
            info.st_mtime_ns,info.st_ctime_ns,info.st_uid,info.st_gid)


def read_regular(path,maximum):
    before=path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1
         and 0<=before.st_size<=maximum,'SOURCE_FILE_SHAPE')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        need(stamp(os.fstat(fd))==stamp(before) and not os.listxattr(fd),'SOURCE_OPEN_CHANGED')
        with os.fdopen(fd,'rb',closefd=False) as stream:raw=stream.read(maximum+1)
        need(len(raw)==before.st_size and stamp(os.fstat(fd))==stamp(before)
             and stamp(path.lstat())==stamp(before),'SOURCE_READ_CHANGED')
        return raw
    finally:
        os.close(fd)


def profile():
    raw=read_regular(Path(__file__).with_name('DIAGNOSTIC_PROFILE.json'),1024*1024)
    need(sha(raw)==PROFILE_SHA,'PROFILE_PIN')
    value=strict(raw)
    need(value['schema']=='dg16.native-intake-diagnostic-profile.v1'
         and value['source_commit']==SOURCE_COMMIT and value['source_tree']==SOURCE_TREE
         and value['test']==TEST,'PROFILE_SCOPE')
    return value


def codes(code):
    yield code
    for value in code.co_consts:
        if isinstance(value,types.CodeType):
            yield from codes(value)


def function_rows(code):
    rows=[]
    for item in codes(code):
        lines=[n for _,_,n in item.co_lines() if n is not None]
        row=[item.co_qualname,item.co_firstlineno,min(lines or [item.co_firstlineno]),
             max(lines or [item.co_firstlineno])]
        if row not in rows:rows.append(row)
    return rows


def bind_sources(root,p):
    result={}
    need(len(p['sources'])==8,'SOURCE_ROLE_POPULATION')
    total=0
    for row in p['sources']:
        path=root/row['path'];raw=read_regular(path,1024*1024);total+=len(raw)
        need(total<=2*1024*1024 and len(raw)==row['bytes'] and sha(raw)==row['sha256'],'SOURCE_PIN')
        compiled=compile(raw,str(path),'exec',dont_inherit=True,optimize=sys.flags.optimize)
        need(function_rows(compiled)==row['functions'],'SOURCE_FUNCTION_DERIVATION')
        result[str(path)]=dict(row=row,raw=raw,code=compiled,codes=tuple(codes(compiled)))
    return result


def source_files_unchanged(bindings):
    return all(read_regular(Path(path),1024*1024)==entry['raw'] for path,entry in bindings.items())


def descriptor(raw):
    need(type(raw) is bytes,'STREAM_TYPE')
    return dict(bytes=len(raw),sha256=sha(raw))


def literal_codes(raw,p):
    # These are literal-presence observations, not inferred refusal phases.
    found=[code for code,needle in LITERALS if needle in raw]
    found += [code for code in p['transport_codes'] if code.encode('ascii') in raw]
    return found


def scalar_message(exc,p):
    args=exc.args
    if type(args) is not tuple or not args or type(args[0]) not in (str,bytes):
        return dict(status='NONSCALAR_OR_ABSENT',bytes=None,sha256=None,known_literals=[])
    raw=args[0].encode('utf-8','replace') if type(args[0]) is str else args[0]
    if len(raw)>p['raw_message_bytes']:
        return dict(status='BYTE_BOUND_REFUSED',bytes=len(raw),sha256=None,known_literals=[])
    return dict(status='COMPLETE_BOUNDED_FIRST_ARGUMENT',**descriptor(raw),known_literals=literal_codes(raw,p))


def frame_binding(tb,bindings):
    code=tb.tb_frame.f_code
    selected=bindings.get(code.co_filename)
    if selected is None:
        return None
    for actual in selected['codes']:
        if code==actual and code.co_filename==actual.co_filename:
            lines={n for _,_,n in actual.co_lines() if n is not None}
            if tb.tb_lineno in lines:
                return dict(kind='PINNED_SOURCE',role=selected['row']['role'],
                    function=code.co_qualname,first_line=code.co_firstlineno,line=tb.tb_lineno)
    return None


def argument_role(arguments):
    if type(arguments) not in (tuple,list) or not arguments or type(arguments[0]) is not str:
        return 'UNESTABLISHED'
    first=arguments[0]
    if first=='--current-controller' and len(arguments)==1:return 'CURRENT_CONTROLLER'
    if first=='--require-current-continuity' and len(arguments)==2:return 'REQUIRE_CURRENT'
    if first=='--verify-resume-receipt' and len(arguments)==2:return 'VERIFY_RECEIPT'
    return 'UNESTABLISHED'


def observe_allowed_local(tb,site,p):
    gate=p['observed_slot']
    if not (site is not None and site['role']==gate['role']
            and site['function']==gate['function'] and site['first_line']==gate['first_line']
            and site['line'] in gate['traceback_lines']):
        return None
    # No enumeration, recursion, closure/ref, path or receipt-value inspection.
    values=tb.tb_frame.f_locals
    observed=values.get(gate['local'])
    role=argument_role(values.get(gate['arguments_local']))
    if type(observed) is not dict:
        return dict(status='OBSERVED_NOT_PRESENT_OR_NOT_DICT',argument_role=role,
                    returncode=None,stdout=None,stderr=None,known_stderr_literals=[],
                    compiler_stdout_bound_exceeded=None,compiler_stderr_bound_exceeded=None)
    rc=observed.get('returncode');out=observed.get('stdout');err=observed.get('stderr')
    if not (type(rc) is int and -255<=rc<=255 and type(out) is bytes and type(err) is bytes
            and len(out)<=gate['stdout_bound'] and len(err)<=gate['stderr_bound']):
        return dict(status='OBSERVED_CLOSED_SHAPE_REFUSED',argument_role=role,
                    returncode=None,stdout=None,stderr=None,known_stderr_literals=[],
                    compiler_stdout_bound_exceeded=None,compiler_stderr_bound_exceeded=None)
    return dict(status='ACTUAL_FRAME_LOCAL_CAPTURED',argument_role=role,returncode=rc,
        stdout=descriptor(out),stderr=descriptor(err),known_stderr_literals=literal_codes(err,p),
        compiler_stdout_bound_exceeded=len(out)>8192,
        compiler_stderr_bound_exceeded=len(err)>gate['compiler_stderr_acceptance_bound'])


def failure_record(err,bindings,p):
    original=err[1];chain=[];seen=set();frames=[];locals_rows=[];truncated=False
    exc=original
    while exc is not None:
        if id(exc) in seen or len(chain)>=p['max_exception_chain']:
            truncated=True;break
        seen.add(id(exc));kind=type(exc).__name__
        chain.append(dict(exception_type=kind if kind in EXCEPTIONS else 'OTHER',
                          message=scalar_message(exc,p)))
        tb=err[2] if exc is original else exc.__traceback__
        while tb is not None:
            if len(frames)>=p['max_traceback_frames']:
                truncated=True;break
            site=frame_binding(tb,bindings)
            if site is None:
                code=tb.tb_frame.f_code
                frame=dict(kind='OUTSIDE_DECLARED_SOURCE',
                    filename_sha256=sha(code.co_filename.encode('utf-8','replace')),
                    function_sha256=sha(code.co_qualname.encode('utf-8','replace')))
            else:
                frame=site
            frame=dict(frame,exception_ordinal=len(chain)-1)
            frames.append(frame)
            observed=observe_allowed_local(tb,site,p)
            if observed is not None:
                locals_rows.append(dict(frame_ordinal=len(frames)-1,**observed))
            tb=tb.tb_next
        next_exc=exc.__cause__
        if next_exc is None and not exc.__suppress_context__:next_exc=exc.__context__
        exc=next_exc
    return dict(exception_chain=chain,frames=frames,observed_results=locals_rows,
                traceback_or_chain_truncated=truncated)


class HashedRunnerStream:
    def __init__(self):
        self.bytes=0;self.hash=hashlib.sha256()

    def write(self,text):
        need(type(text) is str,'RUNNER_TEXT_TYPE')
        raw=text.encode('utf-8','replace')
        need(self.bytes+len(raw)<=262144,'RUNNER_TEXT_BOUND')
        self.bytes+=len(raw);self.hash.update(raw)

    def flush(self):
        pass


def run_one(root,p,bindings):
    selected=next(v for v in bindings.values() if v['row']['role']=='SELECTED_TEST')
    path=root/selected['row']['path']
    module=types.ModuleType('hosted_one_native_intake_case');module.__file__=str(path)
    sys.modules[module.__name__]=module
    exec(compile(selected['raw'],str(path),'exec',dont_inherit=True,optimize=sys.flags.optimize),module.__dict__)
    cls=module.Original14GraphReceiving
    method=cls.__dict__[TEST]
    need(type(method) is types.FunctionType and any(method.__code__==c for c in selected['codes']),
         'SELECTED_CASE_CODE_BINDING')
    case=cls(TEST);events=[]
    class Record(unittest.TextTestResult):
        def record(self,test,outcome,err=None):
            need(type(test) is cls and test._testMethodName==TEST,'ONE_CASE_POPULATION')
            need(len(events)<p['max_terminal_events'],'CASE_EVENT_BOUND')
            value=dict(outcome=outcome,failure=None if err is None else failure_record(err,bindings,p))
            events.append(value)
        def addSuccess(self,test):
            self.record(test,'PASS');super().addSuccess(test)
        def addFailure(self,test,err):
            self.record(test,'FAIL',err);super().addFailure(test,err)
        def addError(self,test,err):
            self.record(test,'ERROR',err);super().addError(test,err)
        def addSkip(self,test,reason):
            self.record(test,'SKIP');super().addSkip(test,reason)
        def addExpectedFailure(self,test,err):
            self.record(test,'EXPECTED_FAILURE',err);super().addExpectedFailure(test,err)
        def addUnexpectedSuccess(self,test):
            self.record(test,'UNEXPECTED_SUCCESS');super().addUnexpectedSuccess(test)
        def addSubTest(self,test,subtest,err):
            raise Refusal('UNDECLARED_SUBTEST')
    stream=HashedRunnerStream()
    result=unittest.TextTestRunner(stream=stream,verbosity=2,resultclass=Record).run(unittest.TestSuite([case]))
    return dict(tests_run=result.testsRun,unittest_success=result.wasSuccessful(),events=events,
                runner_text=dict(bytes=stream.bytes,sha256=stream.hash.hexdigest()))


def validate_descriptor(value,maximum):
    need(type(value) is dict and set(value)=={'bytes','sha256'},'DESCRIPTOR_FIELDS')
    need(type(value['bytes']) is int and 0<=value['bytes']<=maximum
         and type(value['sha256']) is str and re.fullmatch('[0-9a-f]{64}',value['sha256']),
         'DESCRIPTOR_SHAPE')


def validate_failure(value,p):
    need(type(value) is dict and set(value)=={'exception_chain','frames','observed_results',
         'traceback_or_chain_truncated'},'FAILURE_FIELDS')
    need(type(value['traceback_or_chain_truncated']) is bool,'FAILURE_TRUNCATION_TYPE')
    chain=value['exception_chain'];frames=value['frames'];observed=value['observed_results']
    need(type(chain) is list and 1<=len(chain)<=p['max_exception_chain']
         and type(frames) is list and len(frames)<=p['max_traceback_frames']
         and type(observed) is list and len(observed)<=len(frames),'FAILURE_POPULATION')
    known={x for x,_ in LITERALS}|set(p['transport_codes'])
    def literals(values):
        need(type(values) is list and len(values)==len(set(values)) and all(x in known for x in values),
             'LITERAL_POPULATION')
    for row in chain:
        need(type(row) is dict and set(row)=={'exception_type','message'} and row['exception_type'] in EXCEPTIONS,
             'EXCEPTION_FIELDS')
        msg=row['message']
        need(type(msg) is dict and set(msg)=={'status','bytes','sha256','known_literals'}
             and msg['status'] in ('NONSCALAR_OR_ABSENT','BYTE_BOUND_REFUSED','COMPLETE_BOUNDED_FIRST_ARGUMENT'),
             'MESSAGE_FIELDS')
        literals(msg['known_literals'])
        if msg['status']=='COMPLETE_BOUNDED_FIRST_ARGUMENT':
            validate_descriptor({k:msg[k] for k in ('bytes','sha256')},p['raw_message_bytes'])
        else:
            need(msg['sha256'] is None and not msg['known_literals'],'MESSAGE_UNOBSERVED_HASH')
            need(msg['bytes'] is None if msg['status']=='NONSCALAR_OR_ABSENT'
                 else type(msg['bytes']) is int and p['raw_message_bytes']<msg['bytes']<=2**63-1,
                 'MESSAGE_BYTE_BOUND')
    roles={r['role']:r for r in p['sources']}
    for row in frames:
        need(type(row) is dict and type(row.get('exception_ordinal')) is int
             and 0<=row['exception_ordinal']<len(chain),'FRAME_EXCEPTION_BINDING')
        if row.get('kind')=='PINNED_SOURCE':
            need(set(row)=={'kind','role','function','first_line','line','exception_ordinal'}
                 and row['role'] in roles and type(row['first_line']) is int and type(row['line']) is int,
                 'SOURCE_FRAME_FIELDS')
            need(any(row['function']==name and row['first_line']==first and low<=row['line']<=high
                 for name,first,low,high in roles[row['role']]['functions']),'SOURCE_FRAME_SITE')
        else:
            need(set(row)=={'kind','filename_sha256','function_sha256','exception_ordinal'}
                 and row['kind']=='OUTSIDE_DECLARED_SOURCE','OTHER_FRAME_FIELDS')
            for key in ('filename_sha256','function_sha256'):
                need(type(row[key]) is str and re.fullmatch('[0-9a-f]{64}',row[key]),'OTHER_FRAME_HASH')
    seen=set();gate=p['observed_slot']
    for row in observed:
        need(type(row) is dict and set(row)=={'frame_ordinal','status','argument_role','returncode','stdout','stderr',
             'known_stderr_literals','compiler_stdout_bound_exceeded','compiler_stderr_bound_exceeded'},'OBSERVED_FIELDS')
        index=row['frame_ordinal']
        need(type(index) is int and 0<=index<len(frames) and index not in seen,'OBSERVED_FRAME_ORDINAL');seen.add(index)
        frame=frames[index]
        need(frame.get('kind')=='PINNED_SOURCE' and frame['role']==gate['role']
             and frame['function']==gate['function'] and frame['first_line']==gate['first_line']
             and frame['line'] in gate['traceback_lines'],'OBSERVED_SLOT_BINDING')
        need(row['status'] in ('ACTUAL_FRAME_LOCAL_CAPTURED','OBSERVED_NOT_PRESENT_OR_NOT_DICT','OBSERVED_CLOSED_SHAPE_REFUSED')
             and row['argument_role'] in (*gate['allowed_argument_roles'],'UNESTABLISHED'),'OBSERVED_ENUMS')
        literals(row['known_stderr_literals'])
        if row['status']=='ACTUAL_FRAME_LOCAL_CAPTURED':
            need(type(row['returncode']) is int and -255<=row['returncode']<=255,'OBSERVED_RETURNCODE')
            validate_descriptor(row['stdout'],gate['stdout_bound']);validate_descriptor(row['stderr'],gate['stderr_bound'])
            need(type(row['compiler_stdout_bound_exceeded']) is bool
                 and row['compiler_stdout_bound_exceeded']==(row['stdout']['bytes']>8192)
                 and type(row['compiler_stderr_bound_exceeded']) is bool
                 and row['compiler_stderr_bound_exceeded']==(row['stderr']['bytes']>16384),'OBSERVED_BOUND_RELATION')
        else:
            need(all(row[k] is None for k in ('returncode','stdout','stderr','compiler_stdout_bound_exceeded',
                 'compiler_stderr_bound_exceeded')) and not row['known_stderr_literals'],'OBSERVED_UNESTABLISHED_FIELDS')


def validate_record(value,p):
    need(type(value) is dict and set(value)=={'schema','authority','scope','test','source_commit','source_tree',
         'profile_sha256','phase','tests_run','unittest_success','positive_case_pass','events','runner_text','source_closure_unchanged',
         'bootstrap_failure','bank_acceptance','original_G1_award','original_G3_award'},'RESULT_FIELDS')
    need(value['schema']=='dg16.native-intake-one-case-diagnostic.v1' and value['authority']=='NONE'
         and value['scope']=='ONE_MAINTAINED_POSITIVE_CASE_DIAGNOSTIC_ONLY' and value['test']==TEST
         and value['source_commit']==SOURCE_COMMIT and value['source_tree']==SOURCE_TREE
         and value['profile_sha256']==PROFILE_SHA,'RESULT_BINDING')
    need(value['bank_acceptance'] is False and value['original_G1_award'] is False
         and value['original_G3_award'] is False,'RESULT_AUTHORITY')
    need(value['phase'] in ('CASE_COMPLETED','BOOTSTRAP_OR_HARNESS_REFUSED')
         and type(value['tests_run']) is int and value['tests_run'] in (0,1)
         and type(value['unittest_success']) is bool and type(value['positive_case_pass']) is bool
         and type(value['source_closure_unchanged']) is bool,'RESULT_STATE')
    need(type(value['events']) is list and len(value['events'])<=p['max_terminal_events'],'EVENT_POPULATION')
    for event in value['events']:
        need(type(event) is dict and set(event)=={'outcome','failure'} and event['outcome'] in OUTCOMES,'EVENT_FIELDS')
        if event['failure'] is not None:validate_failure(event['failure'],p)
        need((event['failure'] is None)==(event['outcome'] in ('PASS','SKIP','UNEXPECTED_SUCCESS')),'EVENT_FAILURE_RELATION')
    validate_descriptor(value['runner_text'],262144)
    if value['bootstrap_failure'] is not None:validate_failure(value['bootstrap_failure'],p)
    if value['phase']=='CASE_COMPLETED':
        need(value['tests_run']==1 and value['bootstrap_failure'] is None and value['events'],'COMPLETE_CASE_RELATION')
    else:
        need(value['bootstrap_failure'] is not None and value['unittest_success'] is False,'BOOTSTRAP_RELATION')
    need(value['positive_case_pass'] is (value['phase']=='CASE_COMPLETED' and value['tests_run']==1
         and value['unittest_success'] and value['events']==[{'outcome':'PASS','failure':None}]
         and value['source_closure_unchanged'] is True),'POSITIVE_PASS_RELATION')
    need(len(canonical(value))<=p['case_record_bytes'],'CASE_RECORD_BYTE_BOUND')
    return value


def main(argv=None):
    args=sys.argv[1:] if argv is None else argv
    need(len(args)==1,'FIXED_ENTRY_ARGUMENT')
    root=Path(args[0]).absolute();need(root.resolve(strict=True)==root,'SOURCE_ROOT_CANONICAL')
    p=profile();bindings={};os.chdir(root);sys.dont_write_bytecode=True
    record=dict(schema='dg16.native-intake-one-case-diagnostic.v1',authority='NONE',
        scope='ONE_MAINTAINED_POSITIVE_CASE_DIAGNOSTIC_ONLY',test=TEST,source_commit=SOURCE_COMMIT,
        source_tree=SOURCE_TREE,profile_sha256=PROFILE_SHA,phase='BOOTSTRAP_OR_HARNESS_REFUSED',
        tests_run=0,unittest_success=False,positive_case_pass=False,events=[],runner_text=descriptor(b''),
        source_closure_unchanged=False,bootstrap_failure=None,bank_acceptance=False,
        original_G1_award=False,original_G3_award=False)
    try:
        bindings=bind_sources(root,p)
        record.update(run_one(root,p,bindings));record['phase']='CASE_COMPLETED'
        record['source_closure_unchanged']=source_files_unchanged(bindings)
        need(record['source_closure_unchanged'],'SOURCE_CLOSURE_CHANGED_AFTER_CASE')
        record['positive_case_pass']=(record['tests_run']==1 and record['unittest_success']
            and record['events']==[{'outcome':'PASS','failure':None}])
    except BaseException:
        record.update(phase='BOOTSTRAP_OR_HARNESS_REFUSED',unittest_success=False,positive_case_pass=False,
                      bootstrap_failure=failure_record(sys.exc_info(),bindings,p))
    validate_record(record,p)
    sys.stdout.buffer.write(canonical(record));sys.stdout.buffer.flush()
    return 0 if record['positive_case_pass'] else 1


if __name__=='__main__':
    raise SystemExit(main())
