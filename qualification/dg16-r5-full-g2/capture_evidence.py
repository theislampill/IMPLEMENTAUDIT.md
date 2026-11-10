"""Closed supplementary observations of one failed full-pair leg; authority NONE.

No maintained code is patched, traced or redirected through a substitute.
Unsealed files are diagnostic data. Neither a matching source literal nor a
post-failure directory census is represented as a missing earlier observation.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import types

SOURCE_COMMIT = 'e61ead4284e8c8a58948fb9c0b128fd933482d69'
SOURCE_TREE = '1df9ff643f5b5564ebb6b17c51254f4e9faf4b7a'
OWNER_PATH='scripts/qualify-work-graph-verifier.py'
OWNER_SHA = '79e3250a654abff1c5c326908875da1fea575686bdfb0c1a291c73bc525ed33b'
CATALOG_SHA = 'fe7b912693034b0e1c48ad4b8f2a32aa202891b0baf5d96c1ab32118f46359d1'
RECORD_LIMIT=24576
PRETTY_RECORD_LIMIT=32768
PROJECTION_LIMIT=28672
PROJECTION_LINE_LIMIT=1024
STREAM_LIMIT=128*1024*1024
CLASSIFY_BYTES=4*1024*1024
CLASSIFY_LINES=50000
MATCH_SAMPLES=12
UNKNOWN_SAMPLES=8
NAMESPACE_LIMIT=68*4096
CAPTURE_NAMES=('child-environment.json','commands.bin','dist-after','dist-before','dist-namespace.json','exit-code.txt',
               'mapping.json','nodes.tsv','portal-events','repro-artifacts.json','repro-assets','repro-events',
               'result.json','stderr.log','stdin.bin','stdin.json','stdout.log')
STAGES=('RESERVED','OWNER_RETURNED','OWNER_RAISED','PRIMARY_RETAINED','OBSERVATION_COMPLETE','DIAGNOSTIC_REFUSED')
ERROR_STAGES=('PRIMARY_EXIT','SOURCE_FRAMES','SIDECARS','FIRST_CENSUS','STREAMS','CLOSING_CENSUS','BOOKENDS','FINAL_READBACK')
EXCEPTIONS=('AssertionError','RuntimeError','ValueError','OSError','TimeoutError','WorkGraphError','ContinuityTransportError',
            'FileNotFoundError','PermissionError','Refusal','KeyboardInterrupt','SystemExit','OTHER')
GUARD_MESSAGE_SHA='d0c75ab4634e062895eef76e93cf2dc02a2c2bc495d2081ec8e37ce2ed0994c8'

class Refusal(ValueError):pass
def need(value,code):
    if not value:raise Refusal(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def canonical(value):return (json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')
def desc(raw):return {'bytes':len(raw),'sha256':sha(raw)}
def strict(raw):
    def pairs(items):
        result={}
        for key,value in items:
            need(key not in result,'DUPLICATE_DIAGNOSTIC_KEY');result[key]=value
        return result
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(Refusal('NONFINITE_DIAGNOSTIC_VALUE')))
def shape(value,keys):need(type(value) is dict and set(value)==set(keys.split()),'DIAGNOSTIC_SHAPE')
def integer(value,maximum,minimum=0):return type(value) is int and minimum<=value<=maximum
def digest(value):return type(value) is str and re.fullmatch('[0-9a-f]{64}',value) is not None
def descriptor(value,maximum):
    shape(value,'bytes sha256');need(integer(value['bytes'],maximum) and digest(value['sha256']),'DIAGNOSTIC_DESCRIPTOR')
def exit_value(value,nullable=False):
    return value is None and nullable or integer(value,255,-255)
def stamp(info):return (info.st_dev,info.st_ino,info.st_mode,info.st_nlink,info.st_size,info.st_mtime_ns,info.st_ctime_ns,info.st_uid,info.st_gid)

def owned_bytes(path,maximum):
    """Stable bounded no-follow read; never repairs an owner, mode or path."""
    before=path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_uid==os.geteuid()
         and 0<=before.st_size<=maximum,'DIAGNOSTIC_FILE_SHAPE')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        need(stamp(os.fstat(fd))==stamp(before),'DIAGNOSTIC_FILE_OPEN_CHANGED')
        with os.fdopen(fd,'rb',closefd=False) as stream:raw=stream.read(maximum+1)
        need(len(raw)==before.st_size and stamp(os.fstat(fd))==stamp(before) and stamp(path.lstat())==stamp(before),
             'DIAGNOSTIC_FILE_READ_CHANGED')
        return raw
    finally:os.close(fd)

def private_directory(path):
    need(path.resolve(strict=True)==path,'DIAGNOSTIC_DIRECTORY_CANONICAL')
    info=path.lstat()
    need(stat.S_ISDIR(info.st_mode) and info.st_uid==os.geteuid() and stat.S_IMODE(info.st_mode)==0o700,
         'DIAGNOSTIC_DIRECTORY_CUSTODY')
    fd=os.open(path,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        need(stamp(os.fstat(fd))==stamp(info),'DIAGNOSTIC_DIRECTORY_OPEN_CHANGED')
        return fd
    except BaseException:
        os.close(fd);raise

def capture_bytes(directory,name,maximum):
    need(name in ('exit-code.txt','result.json','stdout.log','stderr.log','refusal.json','custody.json'),'DIAGNOSTIC_FIXED_MEMBER')
    root=private_directory(directory)
    try:
        before_root=stamp(os.fstat(root));before=os.stat(name,dir_fd=root,follow_symlinks=False)
        need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_uid==os.geteuid()
             and 0<=before.st_size<=maximum,'DIAGNOSTIC_CAPTURE_FILE_SHAPE')
        fd=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=root)
        try:
            need(stamp(os.fstat(fd))==stamp(before),'DIAGNOSTIC_CAPTURE_FILE_OPEN_CHANGED')
            with os.fdopen(fd,'rb',closefd=False) as stream:raw=stream.read(maximum+1)
            need(len(raw)==before.st_size and stamp(os.fstat(fd))==stamp(before)
                 and stamp(os.stat(name,dir_fd=root,follow_symlinks=False))==stamp(before)
                 and stamp(os.fstat(root))==before_root and stamp(directory.lstat())==before_root,'DIAGNOSTIC_CAPTURE_FILE_READ_CHANGED')
            return raw
        finally:os.close(fd)
    finally:os.close(root)

def write_exclusive(path,raw,maximum):
    need(type(raw) is bytes and len(raw)<=maximum,'DIAGNOSTIC_WRITE_BOUND')
    directory=private_directory(path.parent)
    try:
        fd=os.open(path.name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=directory)
        with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
        os.fsync(directory)
    finally:os.close(directory)
    need(owned_bytes(path,maximum)==raw,'DIAGNOSTIC_WRITE_READBACK')

def load_catalog():
    path=Path(__file__).with_name('CAPTURE_DIAGNOSTIC_CATALOG.json')
    raw=owned_bytes(path,1024*1024);need(sha(raw)==CATALOG_SHA,'DIAGNOSTIC_CATALOG_PIN')
    value=strict(raw)
    need(value['schema']=='dg16.g2-failed-capture-closed-catalog.v1' and value['source_commit']==SOURCE_COMMIT
         and value['source_tree']==SOURCE_TREE and value['owner_sha256']==OWNER_SHA,'DIAGNOSTIC_CATALOG_SCOPE')
    return value

def compiled_owner(source,catalog):
    path=source/OWNER_PATH;raw=owned_bytes(path,1024*1024)
    need(sha(raw)==OWNER_SHA,'DIAGNOSTIC_OWNER_SOURCE_PIN')
    module=compile(raw,str(path),'exec',dont_inherit=True,optimize=0)
    def walk(code):
        yield code
        for value in code.co_consts:
            if type(value) is types.CodeType:yield from walk(value)
    codes=tuple(walk(module));selected={};observations={}
    for site in catalog['owner_frames']+catalog['observation_calls']:
        found=[code for code in codes if code.co_qualname==site['name'] and code.co_firstlineno==site['first']]
        need(len(found)==1,'DIAGNOSTIC_OWNER_SITE_DERIVATION')
        destination=selected if site in catalog['owner_frames'] else observations
        destination[site['name']]={'code':found[0],'site':site,'lines':{line for _,_,line in found[0].co_lines() if line is not None}}
    return {'path':str(path),'raw':raw,'sites':selected,'observation_calls':observations}

def admit_owner(owner,compiled):
    functions={'run':owner.run,'_CaptureRetention.seal':owner._CaptureRetention.seal,
               '_capture_record_contract':owner._capture_record_contract,'_capture_population':owner._capture_population,
               '_capture_census':owner._capture_census}
    declared=dict(compiled['sites'],**compiled['observation_calls'])
    need(set(functions)==set(declared),'DIAGNOSTIC_OWNER_CALL_POPULATION')
    for name,function in functions.items():
        need(type(function) is types.FunctionType and function.__code__==declared[name]['code']
             and function.__code__.co_filename==compiled['path'],'DIAGNOSTIC_OWNER_CALL_CODE_CHANGED')

def checked_census(owner,path,compiled):
    function=owner._capture_census;declared=compiled['observation_calls']['_capture_census']
    need(type(function) is types.FunctionType and function.__code__==declared['code']
         and function.__code__.co_filename==compiled['path'],'DIAGNOSTIC_CENSUS_CALL_CODE_CHANGED')
    return function(path)

def bound_frame(frame,line,compiled):
    code=frame.f_code;selected=compiled['sites'].get(code.co_qualname)
    if selected is None or code.co_filename!=compiled['path']:return None
    need(code==selected['code'] and line in selected['lines']
         and selected['site']['first']<=line<=selected['site']['last'],'DIAGNOSTIC_OWNER_CODE_OR_LINE_CHANGED')
    return selected['site']

def exception_observation(error):
    name=type(error).__name__
    args=error.args if isinstance(error,BaseException) else ()
    result={'type':name if name in EXCEPTIONS else 'OTHER','message':None,'message_kind':'NON_SCALAR','errno':None}
    if type(args) is tuple and len(args)==1 and type(args[0]) is str:
        if len(args[0])<=32768:
            raw=args[0].encode('utf-8','backslashreplace')
            if len(raw)<=131072:result.update(message=desc(raw),message_kind='HASHED_SCALAR')
            else:result['message_kind']='OVER_BOUND_SCALAR'
        else:result['message_kind']='OVER_BOUND_SCALAR'
    if isinstance(error,OSError) and integer(error.errno,4096):result['errno']=error.errno
    return result

def failure_frames(traceback,compiled,workspace,owner):
    frames=[];locals_by_name={};seen=0
    slots={'_capture_population':('path','expected'),'_CaptureRetention.seal':('self','before'),
           '_capture_record_contract':('path','record'),'run':('retention','code')}
    while traceback is not None:
        need(type(traceback) is types.TracebackType and seen<64,'DIAGNOSTIC_TRACEBACK_BOUND');seen+=1
        site=bound_frame(traceback.tb_frame,traceback.tb_lineno,compiled)
        if site is not None:
            frames.append({'id':site['id'],'line':traceback.tb_lineno})
            need(site['name'] not in locals_by_name,'DIAGNOSTIC_DUPLICATE_OWNER_FRAME')
            # No locals are accessed until same-runtime code, exact filename,
            # named source site and actual executable line have all bound.
            local=traceback.tb_frame.f_locals
            locals_by_name[site['name']]={key:local[key] for key in slots[site['name']] if key in local}
        traceback=traceback.tb_next
    expected=None;before=None;source_record=None;retention=None;run_code=None
    population=locals_by_name.get('_capture_population')
    if population is not None:
        need(type(population.get('path')) is type(workspace) and population['path']==workspace,'DIAGNOSTIC_GUARD_PATH')
        expected=population.get('expected')
        need(type(expected) is set and all(type(name) is str and name in CAPTURE_NAMES for name in expected),
             'DIAGNOSTIC_GUARD_EXPECTED_SET')
        expected=sorted(expected)
    seal=locals_by_name.get('_CaptureRetention.seal')
    if seal is not None:
        retention=seal.get('self')
        need(type(retention) is owner._CaptureRetention and retention.workspace==workspace,'DIAGNOSTIC_RETENTION_FRAME')
        before=seal.get('before')
    contract=locals_by_name.get('_capture_record_contract')
    if contract is not None:
        need(type(contract.get('path')) is type(workspace) and contract['path']==workspace,'DIAGNOSTIC_RECORD_FRAME_PATH')
        source_record=contract.get('record');need(type(source_record) is dict,'DIAGNOSTIC_RECORD_FRAME')
    run=locals_by_name.get('run')
    if run is not None:
        candidate=run.get('retention')
        if candidate is not None:
            need(type(candidate) is owner._CaptureRetention and candidate.workspace==workspace,'DIAGNOSTIC_RUN_RETENTION')
            if retention is not None:need(candidate is retention,'DIAGNOSTIC_RETENTION_FRAME_JOIN')
            retention=candidate
        if 'code' in run:
            run_code=run['code'];need(integer(run_code,383),'DIAGNOSTIC_RUN_RETURN_CODE')
    return {'frames':frames,'expected':expected,'before':before,'source_record':source_record,'retention':retention,'run_code':run_code}

def names_observation(names):
    need(type(names) in (list,set,tuple) and len(names)<=NAMESPACE_LIMIT and all(type(name) is str and len(os.fsencode(name))<=4096 for name in names),
         'DIAGNOSTIC_NAMESPACE_BOUND')
    ordered=sorted(names);need(len(set(ordered))==len(ordered),'DIAGNOSTIC_NAMESPACE_DUPLICATE')
    known=[name for name in ordered if name in CAPTURE_NAMES];unknown=[name for name in ordered if name not in CAPTURE_NAMES]
    return {'count':len(ordered),'sha256':sha(canonical(ordered)),'known':known,'unknown_count':len(unknown),
            'unknown_sha256':sha(canonical(unknown)),'unknown_samples':[desc(os.fsencode(name)) for name in unknown[:UNKNOWN_SAMPLES]],
            'unknown_truncated':len(unknown)>UNKNOWN_SAMPLES}

def census_observation(value,phase):
    shape(value,'entries total_bytes limits');need(type(value['entries']) is dict,'DIAGNOSTIC_CENSUS_ENTRIES')
    need(value['limits']==dict(file_bytes=STREAM_LIMIT,total_bytes=2*1024**3,entries=NAMESPACE_LIMIT,depth=64,manifest_bytes=STREAM_LIMIT),
         'DIAGNOSTIC_MAINTAINED_CENSUS_LIMITS')
    root=value['entries'].get('.')
    need(type(root) is dict and root.get('kind')=='DIRECTORY','DIAGNOSTIC_CENSUS_ROOT')
    raw=canonical(value);need(len(raw)<=STREAM_LIMIT,'DIAGNOSTIC_CENSUS_MANIFEST_BOUND')
    return {'phase':phase,'census':desc(raw),'entry_count':len(value['entries']),'total_bytes':value['total_bytes'],
            'root_stamp':desc(canonical(root['stamp'])),'members':names_observation(root['members'])}

def difference(expected,names,phase):
    return {'phase':phase,'missing':sorted(set(expected)-set(names)),'extra':names_observation(sorted(set(names)-set(expected)))}

def primary_file(path):
    raw=capture_bytes(path.parent,path.name,64)
    need(re.fullmatch(rb'-?(?:0|[1-9][0-9]{0,2})\n',raw) is not None,'DIAGNOSTIC_PRIMARY_EXIT_SHAPE')
    value=int(raw);need(exit_value(value) and raw==(str(value)+'\n').encode(),'DIAGNOSTIC_PRIMARY_EXIT_RANGE')
    return dict(value=value,**desc(raw))

def refusal_file(path):
    raw=capture_bytes(path.parent,path.name,1024*1024);value=strict(raw)
    need(type(value) is dict and value.get('schema')=='implementaudit.capture-retention-refusal.v1'
         and value.get('status')=='UNSEALED' and value.get('authority')=='NONE' and exit_value(value.get('primary_exit'),True),
         'DIAGNOSTIC_REFUSAL_SIDECAR')
    need(value.get('renamed') is None or type(value['renamed']) is bool,'DIAGNOSTIC_REFUSAL_RENAME')
    return {'file':desc(raw),'primary_exit':value['primary_exit'],'renamed':value['renamed'],
            'cleanup_error_present':value.get('cleanup_error') is not None}

def record_file(path,source_record=None,mode='legacy'):
    need(type(mode) is str and mode in ('legacy','dag'),'DIAGNOSTIC_LEG_MODE')
    raw=capture_bytes(path.parent,path.name,STREAM_LIMIT);value=strict(raw)
    need(type(value) is dict and value.get('schema')=='implementaudit.verifier-run.v4' and value.get('mode')==mode
         and exit_value(value.get('exit')) and digest(value.get('stdout_sha256')) and digest(value.get('stderr_sha256')),
         'DIAGNOSTIC_CAPTURE_RECORD')
    wrapper=value.get('repro_events')
    need(wrapper is None or type(wrapper) is dict,'DIAGNOSTIC_REPRO_WRAPPER')
    if wrapper is not None:need('record' in wrapper and (wrapper['record'] is None or type(wrapper['record']) is dict),'DIAGNOSTIC_REPRO_INNER')
    return {'file':desc(raw),'primary_exit':value['exit'],'stdout_sha256':value['stdout_sha256'],'stderr_sha256':value['stderr_sha256'],
            'repro_wrapper':'ABSENT' if wrapper is None else 'PRESENT_INNER_ABSENT' if wrapper['record'] is None else 'PRESENT_INNER_RECORD',
            'matches_bound_source_checked_record':None if source_record is None else source_record==value}

def custody_observation(retention,owner):
    if retention is None:return None
    child=retention.children
    need(type(child) is owner._CaptureChildren,'DIAGNOSTIC_CHILD_OWNER_TYPE')
    return custody_fields(child.status)

def custody_fields(value):
    need(type(value) is dict,'DIAGNOSTIC_CHILD_STATUS')
    need(exit_value(value.get('primary_exit'),True) and type(value.get('flag_restored')) is bool
         and type(value.get('live_children_refused')) is bool and integer(value.get('owned_pidfd_signals'),NAMESPACE_LIMIT)
         and type(value.get('other_child_exits')) is list and len(value['other_child_exits'])<=4096,'DIAGNOSTIC_CHILD_STATUS_FIELDS')
    quiescence=value.get('quiescence')
    return {'primary_exit':value['primary_exit'],'quiescence':quiescence if quiescence in ('ECHILD_ALL_CHILDREN','LIVE_CHILDREN','UNPROVED') else 'OTHER',
            'flag_restored':value['flag_restored'],'live_children_refused':value['live_children_refused'],
            'owned_pidfd_signals':value['owned_pidfd_signals'],'other_child_exit_count':len(value['other_child_exits'])}

def stream_observation(raw,source,catalog):
    need(type(raw) is bytes and len(raw)<=STREAM_LIMIT,'DIAGNOSTIC_STREAM_BOUND')
    literals={(row['bytes'],row['sha256']):row['id'] for row in catalog['literals']}
    tests={(row['bytes'],row['sha256']):row['id'] for row in catalog['tests']}
    prefixes={}
    for row in catalog['prefixes']:prefixes.setdefault(row['bytes'],{}).setdefault(row['sha256'],[]).append(row['id'])
    files={row['path']:row for row in catalog['files']}
    source_prefix=(str(source)+'/').encode()
    line_count=raw.count(b'\n')+(1 if raw and not raw.endswith(b'\n') else 0)
    whole=len(raw)<=CLASSIFY_BYTES and line_count<=CLASSIFY_LINES
    side=min(CLASSIFY_BYTES//2,len(raw)//2)
    windows=[(0,len(raw))] if whole else [(0,side),(len(raw)-side,len(raw))]
    samples=[];tail_samples=[];match_hash=hashlib.sha256();match_count=0;classified_lines=0;classified_bytes=0;long_lines=0;limited=False
    for window_number,(start,end) in enumerate(windows):
        quota=CLASSIFY_LINES if whole else CLASSIFY_LINES//2
        if not whole and window_number==1:
            # Retain the last complete lines as well as the first. An early
            # verbose prefix must not consume the tail's diagnostic budget.
            cut=end
            for _ in range(quota):
                found=raw.rfind(b'\n',start,max(start,cut-1))
                if found<start:cut=start;break
                cut=found+1
            if cut>start:start=cut;limited=True
        if start and raw[start-1:start]!=b'\n':
            found=raw.find(b'\n',start,end);start=end if found<0 else found+1
        line_number=raw.count(b'\n',0,start)+1;offset=start;window_lines=0
        while offset<end:
            if window_lines>=quota:limited=True;break
            next_line=raw.find(b'\n',offset,end)
            if next_line<0 and end<len(raw):break
            stop=end if next_line<0 else next_line+1
            content_end=stop-(1 if next_line>=0 else 0)
            amount=stop-offset;classified_lines+=1;window_lines+=1;classified_bytes+=amount
            matches=[]
            if content_end-offset<=65536:
                line=raw[offset:content_end]
                exact=literals.get((len(line),sha(line)))
                if exact:matches.append(('LITERAL',exact,None))
                for length,lookup in prefixes.items():
                    if len(line)>=length:
                        for identity in lookup.get(sha(line[:length]),[]):matches.append(('EMITTER_PREFIX',identity,None))
                for prefix,kind in ((b'FAIL: ','TEST_FAIL'),(b'ERROR: ','TEST_ERROR')):
                    if line.startswith(prefix):
                        tail=line[len(prefix):];identity=tests.get((len(tail),sha(tail)))
                        if identity:matches.append((kind,identity,None))
                match=re.fullmatch(rb'\s*File "([^"]+)", line ([1-9][0-9]{0,6})(?:, in [^\r\n]*)?',line)
                if match and match.group(1).startswith(source_prefix):
                    relative=match.group(1)[len(source_prefix):]
                    try:name=relative.decode('utf-8','strict')
                    except UnicodeError:name=None
                    file=files.get(name);number=int(match.group(2))
                    if file and 1<=number<=file['lines']:matches.append(('SOURCE_TRACEBACK_TEXT',file['id'],number))
            else:long_lines+=1
            for kind,identity,source_line in matches:
                row={'kind':kind,'id':identity,'stream_line':line_number,'stream_offset':offset,'source_line':source_line}
                match_hash.update(canonical(row));match_count+=1
                if len(samples)<MATCH_SAMPLES//2:samples.append(row)
                else:
                    tail_samples.append(row)
                    if len(tail_samples)>MATCH_SAMPLES//2:tail_samples.pop(0)
            offset=stop;line_number+=1
    complete=whole and not limited and classified_bytes==len(raw) and long_lines==0
    return {'file':desc(raw),'line_count':line_count,
            'classification_scope':'WHOLE_STREAM' if whole else 'FIRST_AND_LAST_BOUNDED_COMPLETE_LINES',
            'classification_complete':complete,'classified_lines':classified_lines,'classified_bytes':classified_bytes,
            'overlong_classified_lines':long_lines,'classification_line_limit_reached':limited,
            'match_count':match_count,'matches_sha256':match_hash.hexdigest(),'samples':samples+tail_samples,'samples_truncated':match_count>MATCH_SAMPLES,
            'sample_policy':'FIRST_SIX_AND_LAST_SIX_MATCH_ROWS',
            'match_hash_scope':'ORDERED_CANONICAL_MATCH_ROWS_WITH_NEWLINES','matched_text_is_execution_proof':False}

def initial_record(mode='legacy'):
    need(type(mode) is str and mode in ('legacy','dag'),'DIAGNOSTIC_LEG_MODE')
    return {'schema':'dg16.g2-failed-capture-diagnostic.v1','authority':'NONE','source_commit':SOURCE_COMMIT,'source_tree':SOURCE_TREE,
            'owner_sha256':OWNER_SHA,'catalog_sha256':CATALOG_SHA,'scope':'ONE_FULL_PAIR_LEG_FAILURE_DIAGNOSTIC_ONLY','mode':mode,
            'phase':'RESERVED','reserved':True,'attempts':0,'owner_return':None,'owner_exception':None,'owner_frames':[],
            'attempt_counter_scope':'RESERVED_CALL_BOUNDARY_NOT_COMPLETION',
            'population_guard_observed':False,'guard_inline_list_observation_available':False,'expected_names':None,
            'primary_file':None,'primary_receipt':None,'refusal_file':None,'capture_record':None,'run_frame_code':None,
            'custody':None,'custody_source':'UNESTABLISHED','custody_file':None,'primary_raw_values_agree':None,'raw_to_return_code_agrees':None,
            'capture_location':'UNESTABLISHED','censuses':[],'differences':[],
            'preseal_equals_after_owner':None,'closing_censuses_equal':None,'stream_hashes_match_record':None,'streams':{'stdout':None,'stderr':None},
            'source_status_unchanged':None,'ordinary_runtime_unchanged':None,'currentness_unchanged':None,
            'diagnostic_errors':[],'maintained_guard_modified':False,'missing_directory_created':False,
            'sealed_capture_acceptance':False,'full_G2':False,'Q02':False,'original_acceptance':False,'automatic_retry':False}

def validate_names(value):
    shape(value,'count sha256 known unknown_count unknown_sha256 unknown_samples unknown_truncated')
    need(integer(value['count'],NAMESPACE_LIMIT) and digest(value['sha256']) and type(value['known']) is list
         and value['known']==sorted(set(value['known'])) and all(name in CAPTURE_NAMES for name in value['known'])
         and integer(value['unknown_count'],NAMESPACE_LIMIT) and value['count']==len(value['known'])+value['unknown_count']
         and digest(value['unknown_sha256']) and type(value['unknown_samples']) is list
         and len(value['unknown_samples'])==min(value['unknown_count'],UNKNOWN_SAMPLES)
         and type(value['unknown_truncated']) is bool and value['unknown_truncated']==(value['unknown_count']>UNKNOWN_SAMPLES),'DIAGNOSTIC_NAMES')
    for sample in value['unknown_samples']:descriptor(sample,4096)
    if value['unknown_count']==0:need(value['sha256']==sha(canonical(value['known'])) and value['unknown_sha256']==sha(canonical([])),'DIAGNOSTIC_KNOWN_NAMES_HASH')

def validate_exception(value):
    shape(value,'type message message_kind errno')
    need(value['type'] in EXCEPTIONS and value['message_kind'] in ('NON_SCALAR','OVER_BOUND_SCALAR','HASHED_SCALAR')
         and (value['errno'] is None or integer(value['errno'],4096)),'DIAGNOSTIC_EXCEPTION')
    if value['message_kind']=='HASHED_SCALAR':descriptor(value['message'],131072)
    else:need(value['message'] is None,'DIAGNOSTIC_EXCEPTION_MESSAGE')

def validate_record(value,catalog):
    need(type(value) is dict and set(value)==set(initial_record()),'DIAGNOSTIC_RECORD_FIELDS')
    need(type(value['mode']) is str and value['mode'] in ('legacy','dag'),'DIAGNOSTIC_LEG_MODE')
    base=initial_record(value['mode'])
    fixed=('schema','authority','source_commit','source_tree','owner_sha256','catalog_sha256','scope','mode','reserved',
           'guard_inline_list_observation_available','maintained_guard_modified','missing_directory_created','sealed_capture_acceptance',
           'full_G2','Q02','original_acceptance','automatic_retry','attempt_counter_scope')
    need(all(type(value[k]) is type(base[k]) and value[k]==base[k] for k in fixed),'DIAGNOSTIC_AUTHORITY_OR_SCOPE')
    need(value['phase'] in STAGES and integer(value['attempts'],1) and (value['owner_return'] is None or integer(value['owner_return'],383)),
         'DIAGNOSTIC_OPERATION')
    if value['owner_exception'] is not None:validate_exception(value['owner_exception'])
    need(not(value['owner_return'] is not None and value['owner_exception'] is not None),'DIAGNOSTIC_OUTCOME_CONFLICT')
    sites={site['id']:site for site in catalog['owner_frames']}
    need(type(value['owner_frames']) is list and len(value['owner_frames'])<=4 and len({r['id'] for r in value['owner_frames']})==len(value['owner_frames']),
         'DIAGNOSTIC_FRAME_POPULATION')
    for frame in value['owner_frames']:
        shape(frame,'id line');need(frame['id'] in sites and integer(frame['line'],sites[frame['id']]['last'],sites[frame['id']]['first']),'DIAGNOSTIC_FRAME_SITE')
    expected=value['expected_names']
    need(expected is None or type(expected) is list and expected==sorted(set(expected)) and all(n in CAPTURE_NAMES for n in expected),'DIAGNOSTIC_EXPECTED_NAMES')
    need(type(value['population_guard_observed']) is bool and (not value['population_guard_observed'] or expected is not None),'DIAGNOSTIC_GUARD_FLAG')
    if expected is not None:need(any(sites[f['id']]['name']=='_capture_population' for f in value['owner_frames']),'DIAGNOSTIC_EXPECTED_FRAME_BINDING')
    if value['population_guard_observed']:
        need(value['owner_exception'] is not None and value['owner_exception']['type']=='WorkGraphError'
             and value['owner_exception']['message']=={'bytes':36,'sha256':GUARD_MESSAGE_SHA}
             and any(sites[f['id']]['name']=='_capture_population' and f['line']==1598 for f in value['owner_frames']),
             'DIAGNOSTIC_POPULATION_GUARD_BINDING')
    if value['primary_file'] is not None:
        shape(value['primary_file'],'value bytes sha256');need(exit_value(value['primary_file']['value']),'DIAGNOSTIC_EXIT_VALUE')
        descriptor({k:value['primary_file'][k] for k in ('bytes','sha256')},64)
        need({k:value['primary_file'][k] for k in ('bytes','sha256')}==desc((str(value['primary_file']['value'])+'\n').encode()),'DIAGNOSTIC_EXIT_BYTES')
        descriptor(value['primary_receipt'],4096)
    else:need(value['primary_receipt'] is None,'DIAGNOSTIC_PRIMARY_RECEIPT')
    if value['refusal_file'] is not None:
        row=value['refusal_file'];shape(row,'file primary_exit renamed cleanup_error_present');descriptor(row['file'],1024*1024)
        need(exit_value(row['primary_exit'],True) and (row['renamed'] is None or type(row['renamed']) is bool)
             and type(row['cleanup_error_present']) is bool,'DIAGNOSTIC_REFUSAL_FIELDS')
    if value['capture_record'] is not None:
        row=value['capture_record'];shape(row,'file primary_exit stdout_sha256 stderr_sha256 repro_wrapper matches_bound_source_checked_record')
        descriptor(row['file'],STREAM_LIMIT)
        need(exit_value(row['primary_exit']) and digest(row['stdout_sha256']) and digest(row['stderr_sha256'])
             and row['repro_wrapper'] in ('ABSENT','PRESENT_INNER_ABSENT','PRESENT_INNER_RECORD')
             and (row['matches_bound_source_checked_record'] is None or type(row['matches_bound_source_checked_record']) is bool),'DIAGNOSTIC_CAPTURE_RECORD_FIELDS')
    need(value['run_frame_code'] is None or integer(value['run_frame_code'],383),'DIAGNOSTIC_RUN_FRAME_CODE')
    if value['custody'] is not None:
        row=value['custody'];shape(row,'primary_exit quiescence flag_restored live_children_refused owned_pidfd_signals other_child_exit_count')
        need(exit_value(row['primary_exit'],True) and row['quiescence'] in ('ECHILD_ALL_CHILDREN','LIVE_CHILDREN','UNPROVED','OTHER')
             and type(row['flag_restored']) is bool and type(row['live_children_refused']) is bool
             and integer(row['owned_pidfd_signals'],NAMESPACE_LIMIT) and integer(row['other_child_exit_count'],4096),'DIAGNOSTIC_CUSTODY')
    need(value['custody_source'] in ('UNESTABLISHED','BOUND_SOURCE_FRAME','MAINTAINED_REFUSAL_SIDECAR','MAINTAINED_SEAL_SIDECAR')
         and (value['custody'] is None)==(value['custody_source']=='UNESTABLISHED'),'DIAGNOSTIC_CUSTODY_SOURCE')
    if value['custody_file'] is not None:descriptor(value['custody_file'],STREAM_LIMIT)
    need(value['capture_location'] in ('UNESTABLISHED','ORIGINAL_WORKSPACE','RENAMED_CAPTURE'),'DIAGNOSTIC_CAPTURE_LOCATION')
    phases=('PRE_SEAL','AFTER_OWNER','AFTER_STREAMS')
    need(type(value['censuses']) is list and len(value['censuses'])<=3 and len({r['phase'] for r in value['censuses']})==len(value['censuses']),'DIAGNOSTIC_CENSUS_POPULATION')
    for row in value['censuses']:
        shape(row,'phase census entry_count total_bytes root_stamp members');descriptor(row['census'],STREAM_LIMIT);descriptor(row['root_stamp'],4096)
        need(row['phase'] in phases and integer(row['entry_count'],NAMESPACE_LIMIT,1) and integer(row['total_bytes'],2*1024**3),'DIAGNOSTIC_CENSUS_FIELDS')
        validate_names(row['members']);need(row['members']['count']<row['entry_count'],'DIAGNOSTIC_CENSUS_MEMBER_COUNT')
    need(type(value['differences']) is list and len(value['differences'])<=2
         and len({r['phase'] for r in value['differences']})==len(value['differences']),'DIAGNOSTIC_DIFFERENCE_POPULATION')
    for row in value['differences']:
        shape(row,'phase missing extra');need(expected is not None and row['phase'] in phases[:2] and type(row['missing']) is list
            and row['missing']==sorted(set(row['missing'])) and all(n in expected for n in row['missing']),'DIAGNOSTIC_DIFFERENCE_FIELDS');validate_names(row['extra'])
        census=next((r for r in value['censuses'] if r['phase']==row['phase']),None);need(census is not None,'DIAGNOSTIC_DIFFERENCE_CENSUS')
        members=census['members']
        need(row['missing']==sorted(set(expected)-set(members['known'])) and row['extra']['known']==sorted(set(members['known'])-set(expected))
             and all(row['extra'][k]==members[k] for k in ('unknown_count','unknown_sha256','unknown_samples','unknown_truncated')),
             'DIAGNOSTIC_DIFFERENCE_BINDING')
    for key in ('primary_raw_values_agree','raw_to_return_code_agrees','preseal_equals_after_owner','closing_censuses_equal',
                'source_status_unchanged','ordinary_runtime_unchanged','currentness_unchanged','stream_hashes_match_record'):
        need(value[key] is None or type(value[key]) is bool,'DIAGNOSTIC_BOOLEAN')
    shape(value['streams'],'stdout stderr')
    ids={kind:{r['id'] for r in catalog[table]} for kind,table in (('LITERAL','literals'),('EMITTER_PREFIX','prefixes'),('TEST_FAIL','tests'),('TEST_ERROR','tests'),('SOURCE_TRACEBACK_TEXT','files'))}
    file_ids={r['id']:r for r in catalog['files']}
    for row in value['streams'].values():
        if row is None:continue
        shape(row,'file line_count classification_scope classification_complete classified_lines classified_bytes overlong_classified_lines classification_line_limit_reached match_count matches_sha256 samples samples_truncated sample_policy match_hash_scope matched_text_is_execution_proof')
        descriptor(row['file'],STREAM_LIMIT)
        need(integer(row['line_count'],STREAM_LIMIT) and row['classification_scope'] in ('WHOLE_STREAM','FIRST_AND_LAST_BOUNDED_COMPLETE_LINES')
             and type(row['classification_complete']) is bool and integer(row['classified_lines'],CLASSIFY_LINES)
             and integer(row['classified_bytes'],CLASSIFY_BYTES) and integer(row['overlong_classified_lines'],CLASSIFY_LINES)
             and type(row['classification_line_limit_reached']) is bool and integer(row['match_count'],CLASSIFY_LINES*(len(catalog['prefixes'])+3))
             and digest(row['matches_sha256']) and type(row['samples']) is list and len(row['samples'])==min(row['match_count'],MATCH_SAMPLES)
             and type(row['samples_truncated']) is bool and row['samples_truncated']==(row['match_count']>MATCH_SAMPLES)
             and row['sample_policy']=='FIRST_SIX_AND_LAST_SIX_MATCH_ROWS'
             and row['match_hash_scope']=='ORDERED_CANONICAL_MATCH_ROWS_WITH_NEWLINES' and row['matched_text_is_execution_proof'] is False,
             'DIAGNOSTIC_STREAM_FIELDS')
        for sample in row['samples']:
            shape(sample,'kind id stream_line stream_offset source_line')
            need(sample['kind'] in ids and sample['id'] in ids[sample['kind']] and integer(sample['stream_line'],row['line_count'],1)
                 and integer(sample['stream_offset'],row['file']['bytes']),'DIAGNOSTIC_MATCH_ID')
            if sample['kind']=='SOURCE_TRACEBACK_TEXT':need(integer(sample['source_line'],file_ids[sample['id']]['lines'],1),'DIAGNOSTIC_SOURCE_LINE')
            else:need(sample['source_line'] is None,'DIAGNOSTIC_MATCH_SOURCE_LINE')
    need(type(value['diagnostic_errors']) is list and len(value['diagnostic_errors'])<=len(ERROR_STAGES),'DIAGNOSTIC_ERRORS')
    need(len({r['stage'] for r in value['diagnostic_errors']})==len(value['diagnostic_errors']),'DIAGNOSTIC_FIRST_ERROR_PER_STAGE')
    for row in value['diagnostic_errors']:
        shape(row,'stage exception');need(row['stage'] in ERROR_STAGES,'DIAGNOSTIC_ERROR_STAGE');validate_exception(row['exception'])
    expected_relations=derived_relations(value)
    need(all(value[k]==v and type(value[k]) is type(v) for k,v in expected_relations.items()),'DIAGNOSTIC_OBSERVATION_RELATION')
    if value['phase']=='OBSERVATION_COMPLETE':need(complete_eligible(value),'DIAGNOSTIC_COMPLETION_RELATION')
    need(len(canonical(value))<=RECORD_LIMIT and len((json.dumps(value,sort_keys=True,indent=2,ensure_ascii=True)+'\n').encode('ascii'))<=PRETTY_RECORD_LIMIT,
         'DIAGNOSTIC_RECORD_BOUND')
    return value

def derived_relations(value):
    numbers=[]
    if value['primary_file'] is not None:numbers.append(value['primary_file']['value'])
    for key in ('refusal_file','capture_record','custody'):
        if value[key] is not None and value[key]['primary_exit'] is not None:numbers.append(value[key]['primary_exit'])
    returns=[n for n in (value['run_frame_code'],value['owner_return']) if n is not None]
    raw=value['primary_file']['value'] if value['primary_file'] is not None else None
    by_phase={row['phase']:row['census'] for row in value['censuses']}
    streams=value['streams'];record=value['capture_record']
    return {'primary_raw_values_agree':None if len(numbers)<2 else len(set(numbers))==1,
            'raw_to_return_code_agrees':None if raw is None or not returns else all(n==(raw if raw>=0 else 128-raw) for n in returns),
            'preseal_equals_after_owner':None if not {'PRE_SEAL','AFTER_OWNER'}<=set(by_phase) else by_phase['PRE_SEAL']==by_phase['AFTER_OWNER'],
            'closing_censuses_equal':None if not {'AFTER_OWNER','AFTER_STREAMS'}<=set(by_phase) else by_phase['AFTER_OWNER']==by_phase['AFTER_STREAMS'],
            'stream_hashes_match_record':None if record is None or any(s is None for s in streams.values()) else all(streams[name]['file']['sha256']==record[name+'_sha256'] for name in streams)}

def save_record(evidence,value,catalog):
    value.update(derived_relations(value))
    raw=canonical(validate_record(value,catalog));target=evidence/'DIAGNOSTIC.json';temporary=evidence/'DIAGNOSTIC.next'
    write_exclusive(temporary,raw,RECORD_LIMIT)
    if target.exists():owned_bytes(target,RECORD_LIMIT)
    os.replace(temporary,target)
    directory=private_directory(evidence)
    try:os.fsync(directory)
    finally:os.close(directory)
    need(owned_bytes(target,RECORD_LIMIT)==raw,'DIAGNOSTIC_RECORD_READBACK')

def save_primary(evidence,value,mode):
    need(type(mode) is str and mode in ('legacy','dag'),'DIAGNOSTIC_LEG_MODE')
    raw=canonical({'schema':'dg16.g2-diagnostic-durable-primary-exit.v1','authority':'NONE','source_commit':SOURCE_COMMIT,
                   'source_tree':SOURCE_TREE,'owner_sha256':OWNER_SHA,'mode':mode,'observation':value,'unsealed_data_is_acceptance':False})
    write_exclusive(evidence/'PRIMARY_EXIT.json',raw,4096)
    return desc(raw)

def record_error(value,stage,error):
    need(stage in ERROR_STAGES,'DIAGNOSTIC_ERROR_STAGE')
    if not any(row['stage']==stage for row in value['diagnostic_errors']):
        value['diagnostic_errors'].append({'stage':stage,'exception':exception_observation(error)})

def complete_eligible(value):
    return (value['attempts']==1 and (value['owner_return'] is not None or value['owner_exception'] is not None)
            and value['primary_file'] is not None and value['primary_receipt'] is not None
            and value['capture_record'] is not None and value['primary_raw_values_agree'] is True
            and value['capture_record']['matches_bound_source_checked_record'] is not False
            and value['custody'] is not None and value['custody']['quiescence']=='ECHILD_ALL_CHILDREN'
            and value['custody']['flag_restored'] is True
            and value['raw_to_return_code_agrees'] is not False and value['closing_censuses_equal'] is True
            and value['stream_hashes_match_record'] is True and value['source_status_unchanged'] is True
            and value['ordinary_runtime_unchanged'] is True and value['currentness_unchanged'] is True
            and not value['diagnostic_errors']
            and (not value['population_guard_observed'] or value['preseal_equals_after_owner'] is True))

def observe_operation(value,evidence,captures,source,owner,compiled,catalog,*,code=None,error=None,traceback=None):
    """Observe only after the one actual owner call has returned or raised."""
    need(value['attempts']==1 and value['phase']=='RESERVED','DIAGNOSTIC_OPERATION_REPLAY')
    need((error is None)!=(code is None),'DIAGNOSTIC_ACTUAL_OUTCOME_REQUIRED')
    value['owner_return']=code
    value['owner_exception']=None if error is None else exception_observation(error)
    value['phase']='OWNER_RETURNED' if error is None else 'OWNER_RAISED'
    save_record(evidence,value,catalog)
    mode=value['mode'];workspace=captures/'work';renamed=captures/mode/'capture';root=None;observed_frames=None;first_census=None

    # This minimal durable receipt precedes all frame, census and stream work.
    # It is a separate file so a later journal interruption cannot erase it.
    try:
        present=[path for path in (workspace,renamed) if os.path.lexists(path)]
        need(len(present)==1,'DIAGNOSTIC_CAPTURE_LOCATION_UNESTABLISHED')
        root=present[0];fd=private_directory(root);os.close(fd)
        value['capture_location']='ORIGINAL_WORKSPACE' if root==workspace else 'RENAMED_CAPTURE'
        primary=primary_file(root/'exit-code.txt')
        receipt=save_primary(evidence,primary,mode)
        value['primary_file']=primary;value['primary_receipt']=receipt;value['phase']='PRIMARY_RETAINED'
    except BaseException as exc:record_error(value,'PRIMARY_EXIT',exc)
    save_record(evidence,value,catalog)

    if traceback is not None:
        try:
            observed_frames=failure_frames(traceback,compiled,workspace,owner)
            value['owner_frames']=observed_frames['frames'];value['expected_names']=observed_frames['expected']
            value['run_frame_code']=observed_frames['run_code']
            if observed_frames['retention'] is not None:
                value['custody']=custody_observation(observed_frames['retention'],owner)
                value['custody_source']='BOUND_SOURCE_FRAME'
            if observed_frames['before'] is not None:
                before=observed_frames['before'];value['censuses'].append(census_observation(before,'PRE_SEAL'))
                if value['expected_names'] is not None:value['differences'].append(difference(value['expected_names'],before['entries']['.']['members'],'PRE_SEAL'))
            site_by_id={r['id']:r for r in catalog['owner_frames']}
            value['population_guard_observed']=(value['owner_exception'] is not None
                and value['owner_exception']['type']=='WorkGraphError' and value['owner_exception']['message']=={'bytes':36,'sha256':GUARD_MESSAGE_SHA}
                and any(site_by_id[r['id']]['name']=='_capture_population' and r['line']==1598 for r in value['owner_frames'])
                and value['expected_names'] is not None)
        except BaseException as exc:record_error(value,'SOURCE_FRAMES',exc)
    save_record(evidence,value,catalog)

    try:
        if root is not None and os.path.lexists(root/'result.json'):
            value['capture_record']=record_file(root/'result.json',None if observed_frames is None else observed_frames['source_record'],mode)
        refusal=captures/mode/'refusal.json';custody=captures/mode/'custody.json'
        if os.path.lexists(refusal):
            value['refusal_file']=refusal_file(refusal)
            if value['custody'] is None:
                raw=capture_bytes(refusal.parent,refusal.name,1024*1024);private=strict(raw)
                if private.get('process_custody') is not None:
                    value['custody']=custody_fields(private['process_custody']);value['custody_source']='MAINTAINED_REFUSAL_SIDECAR';value['custody_file']=desc(raw)
        if os.path.lexists(custody) and value['custody'] is None:
            raw=capture_bytes(custody.parent,custody.name,STREAM_LIMIT);private=strict(raw)
            need(private.get('schema')=='implementaudit.capture-retention-custody.v1','DIAGNOSTIC_SEAL_SIDECAR')
            value['custody']=custody_fields(private['process_custody']);value['custody_source']='MAINTAINED_SEAL_SIDECAR';value['custody_file']=desc(raw)
    except BaseException as exc:record_error(value,'SIDECARS',exc)
    save_record(evidence,value,catalog)

    try:
        need(root is not None and value['custody'] is not None and value['custody']['quiescence']=='ECHILD_ALL_CHILDREN'
             and value['custody']['flag_restored'] is True,'DIAGNOSTIC_QUIESCENCE_UNESTABLISHED')
        first_census=checked_census(owner,root,compiled)
        value['censuses'].append(census_observation(first_census,'AFTER_OWNER'))
        if value['expected_names'] is not None:value['differences'].append(difference(value['expected_names'],first_census['entries']['.']['members'],'AFTER_OWNER'))
    except BaseException as exc:record_error(value,'FIRST_CENSUS',exc)
    save_record(evidence,value,catalog)

    if first_census is not None:
        try:
            for stream in ('stdout','stderr'):
                raw=capture_bytes(root,stream+'.log',STREAM_LIMIT)
                member=first_census['entries'].get(stream+'.log')
                need(type(member) is dict and member.get('kind')=='FILE' and member['sha256']==sha(raw)
                     and member['stamp']['bytes']==len(raw),'DIAGNOSTIC_STREAM_CENSUS_BINDING')
                value['streams'][stream]=stream_observation(raw,source,catalog)
                save_record(evidence,value,catalog)
        except BaseException as exc:record_error(value,'STREAMS',exc)
        try:
            closing=checked_census(owner,root,compiled)
            value['censuses'].append(census_observation(closing,'AFTER_STREAMS'))
        except BaseException as exc:record_error(value,'CLOSING_CENSUS',exc)
    save_record(evidence,value,catalog)
    return value

def finish_record(value,evidence,catalog):
    value.update(derived_relations(value))
    value['phase']='OBSERVATION_COMPLETE' if complete_eligible(value) else 'DIAGNOSTIC_REFUSED'
    save_record(evidence,value,catalog)
    return value

def validate_primary(value):
    shape(value,'schema authority source_commit source_tree owner_sha256 mode observation unsealed_data_is_acceptance')
    need(type(value['mode']) is str and value['mode'] in ('legacy','dag'),'DIAGNOSTIC_LEG_MODE')
    need(value['schema']=='dg16.g2-diagnostic-durable-primary-exit.v1' and value['authority']=='NONE'
         and value['source_commit']==SOURCE_COMMIT and value['source_tree']==SOURCE_TREE and value['owner_sha256']==OWNER_SHA
         and value['unsealed_data_is_acceptance'] is False,'DIAGNOSTIC_PRIMARY_SCOPE')
    row=value['observation'];shape(row,'value bytes sha256')
    need(exit_value(row['value']) and {k:row[k] for k in ('bytes','sha256')}==desc((str(row['value'])+'\n').encode()),'DIAGNOSTIC_PRIMARY_OBSERVATION')
    return value

def validate_projection(value,catalog):
    shape(value,'schema authority record record_file retained_primary primary_file primary_precedes_journal pending_journal_update diagnostic_complete original_acceptance')
    need(value['schema']=='dg16.g2-diagnostic-retained-projection.v1' and value['authority']=='NONE' and value['original_acceptance'] is False,
         'DIAGNOSTIC_PROJECTION_SCOPE')
    descriptor(value['record_file'],RECORD_LIMIT);validate_record(value['record'],catalog)
    need(desc(canonical(value['record']))==value['record_file'],'DIAGNOSTIC_PROJECTION_RECORD_BINDING')
    if value['retained_primary'] is not None:
        validate_primary(value['retained_primary']);descriptor(value['primary_file'],4096)
        need(value['retained_primary']['mode']==value['record']['mode'],'DIAGNOSTIC_PRIMARY_LEG_BINDING')
        need(desc(canonical(value['retained_primary']))==value['primary_file'],'DIAGNOSTIC_PROJECTION_PRIMARY_BINDING')
        if value['record']['primary_file'] is not None:
            need(value['retained_primary']['observation']==value['record']['primary_file'] and value['primary_file']==value['record']['primary_receipt'],
                 'DIAGNOSTIC_JOURNAL_PRIMARY_BINDING')
    else:need(value['primary_file'] is None and value['record']['primary_file'] is None,'DIAGNOSTIC_PRIMARY_NOT_RETAINED')
    need(type(value['primary_precedes_journal']) is bool and value['primary_precedes_journal']==(value['retained_primary'] is not None and value['record']['primary_file'] is None)
         and type(value['pending_journal_update']) is bool and type(value['diagnostic_complete']) is bool
         and value['diagnostic_complete']==(value['record']['phase']=='OBSERVATION_COMPLETE' and not value['pending_journal_update']
            and not value['primary_precedes_journal']),'DIAGNOSTIC_PROJECTION_COMPLETENESS')
    rendered=(json.dumps(value,sort_keys=True,indent=2,ensure_ascii=True)+'\n').encode('ascii')
    need(len(rendered)<=PROJECTION_LIMIT and rendered.count(b'\n')<=PROJECTION_LINE_LIMIT,'DIAGNOSTIC_PROJECTION_BOUND')
    return value



def readback(evidence,catalog):
    raw=owned_bytes(evidence/'DIAGNOSTIC.json',RECORD_LIMIT);record=validate_record(strict(raw),catalog)
    need(canonical(record)==raw,'DIAGNOSTIC_CANONICAL_READBACK')
    value={'schema':'dg16.g2-diagnostic-retained-projection.v1','authority':'NONE','record':record,'record_file':desc(raw),
           'retained_primary':None,'primary_file':None,'primary_precedes_journal':False,
           'pending_journal_update':os.path.lexists(evidence/'DIAGNOSTIC.next'),'diagnostic_complete':False,'original_acceptance':False}
    if os.path.lexists(evidence/'PRIMARY_EXIT.json'):
        primary=owned_bytes(evidence/'PRIMARY_EXIT.json',4096);value['retained_primary']=validate_primary(strict(primary));value['primary_file']=desc(primary)
        need(canonical(value['retained_primary'])==primary,'DIAGNOSTIC_PRIMARY_CANONICAL')
        value['primary_precedes_journal']=record['primary_file'] is None
    value['diagnostic_complete']=record['phase']=='OBSERVATION_COMPLETE' and not value['pending_journal_update'] and not value['primary_precedes_journal']
    return validate_projection(value,catalog)
