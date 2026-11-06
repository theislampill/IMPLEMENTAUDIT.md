#!/usr/bin/env python3
"""Bounded compile-only admission of eight exact public source files.

Maintained code is compiled as data and never executed or imported here. The
retained author line tables are diagnostic provenance. Executed-frame binding
still requires exact code equality against compilation in the executing runtime.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import types

PROFILE_SHA = 'bd0240ba590c424b44037818e4cae0504b2e0a4be60c7f78077644b23debb01d'
SOURCE_COMMIT = '0d57929be5bd15682b4e9da2c0209d5dff307843'
SOURCE_TREE = 'ee316c27250ec422d35a1ea965182ebddf7a5da0'
ROLES = ('SELECTED_TEST','NATIVE_FIXTURE','CANONICAL_READER_FIXTURE','CLAIM_TRANSACTION_FIXTURE',
         'COMPILER','TRANSPORT','OPERATIONAL_OWNER','CLAIM_COMPANION')
FAILURES = ('RUNTIME_NOT_ADMITTED','SOURCE_PIN','SOURCE_ROLE_POPULATION','SOURCE_SITE_DERIVATION',
            'COMPILED_NAMED_SITE','SOURCE_FILE_SHAPE','SOURCE_OPEN_CHANGED','SOURCE_READ_CHANGED',
            'SOURCE_CLOSURE_CHANGED','SOURCE_COMPILE_REFUSED','UNCLASSIFIED_ADMISSION_REFUSAL')
# The unchanged, pinned host_utility.capture retains 32768 bytes per stream.
# Six source-bound differences per role keep the maximal closed record below
# that ceiling; counts and full table hashes remain complete when truncated.
RECORD_LIMIT = 32768
DIFFERENCE_LIMIT = 6
ROW_LIMIT = 4096


class Refusal(Exception):
    pass


def need(value,code):
    if not value: raise Refusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')


def strict(raw):
    def pairs(items):
        out={}
        for key,value in items:
            need(key not in out,'DUPLICATE_KEY');out[key]=value
        return out
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:(_ for _ in ()).throw(Refusal('NONFINITE_JSON')))


def stamp(info):
    return (info.st_dev,info.st_ino,info.st_mode,info.st_nlink,info.st_size,info.st_mtime_ns,
            info.st_ctime_ns,info.st_uid,info.st_gid)


def read_regular(path,maximum):
    before=path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and 0<=before.st_size<=maximum,'SOURCE_FILE_SHAPE')
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        need(stamp(os.fstat(fd))==stamp(before) and not os.listxattr(fd),'SOURCE_OPEN_CHANGED')
        with os.fdopen(fd,'rb',closefd=False) as stream: raw=stream.read(maximum+1)
        need(len(raw)==before.st_size and stamp(os.fstat(fd))==stamp(before)
             and stamp(path.lstat())==stamp(before),'SOURCE_READ_CHANGED')
        return raw
    finally: os.close(fd)


def profile():
    raw=read_regular(Path(__file__).with_name('DIAGNOSTIC_PROFILE.json'),1024*1024)
    need(sha(raw)==PROFILE_SHA,'PROFILE_PIN')
    value=strict(raw)
    need(value['schema']=='dg16.native-intake-diagnostic-profile.v2'
         and value['source_commit']==SOURCE_COMMIT and value['source_tree']==SOURCE_TREE,'PROFILE_SCOPE')
    return value


def codes(code):
    yield code
    for item in code.co_consts:
        if type(item) is types.CodeType: yield from codes(item)


def function_rows(code):
    rows=[]
    for item in codes(code):
        lines=[line for _,_,line in item.co_lines() if line is not None]
        row=[item.co_qualname,item.co_firstlineno,min(lines or [item.co_firstlineno]),max(lines or [item.co_firstlineno])]
        if row not in rows: rows.append(row)
    need(len(rows)<=ROW_LIMIT,'SOURCE_COMPILE_REFUSED')
    return rows


def source_sites(raw):
    """Source spelling and spans only; no bytecode line-table endpoints."""
    class Visitor(ast.NodeVisitor):
        def __init__(self):
            self.stack=[];self.rows=[['<module>',1,0,len(raw.splitlines())]]
        def definition(self,node,function):
            prefix=''.join(name+('.<locals>.' if isfunction else '.') for name,isfunction in self.stack)
            first=min([node.lineno]+[item.lineno for item in node.decorator_list])
            self.rows.append([prefix+node.name,first,first,node.end_lineno])
            self.stack.append((node.name,function));self.generic_visit(node);self.stack.pop()
        def visit_FunctionDef(self,node): self.definition(node,True)
        def visit_AsyncFunctionDef(self,node): self.definition(node,True)
        def visit_ClassDef(self,node): self.definition(node,False)
    visitor=Visitor();visitor.visit(ast.parse(raw,mode='exec',feature_version=(3,12)))
    need(len(visitor.rows)<=ROW_LIMIT,'SOURCE_SITE_DERIVATION')
    need(len({(r[0],r[1]) for r in visitor.rows})==len(visitor.rows),'SOURCE_SITE_DERIVATION')
    return visitor.rows


def runtime_metadata():
    version=list(sys.version_info[:3])
    return dict(implementation=sys.implementation.name if sys.implementation.name=='cpython' else 'OTHER',
        version=version,releaselevel=sys.version_info.releaselevel if sys.version_info.releaselevel in ('alpha','beta','candidate','final') else 'OTHER',
        serial=sys.version_info.serial,cache_tag=sys.implementation.cache_tag if sys.implementation.cache_tag=='cpython-312' else 'OTHER',
        flags=dict(isolated=sys.flags.isolated,no_site=sys.flags.no_site,dont_write_bytecode=int(sys.dont_write_bytecode),
                   optimize=sys.flags.optimize),compile=dict(mode='exec',dont_inherit=True,optimize=0))


def runtime_admitted(runtime):
    return (runtime['implementation']=='cpython' and runtime['version'][:2]==[3,12]
        and runtime['releaselevel']=='final' and runtime['serial']==0 and runtime['cache_tag']=='cpython-312'
        and runtime['flags']==dict(isolated=1,no_site=1,dont_write_bytecode=1,optimize=0)
        and runtime['compile']==dict(mode='exec',dont_inherit=True,optimize=0))


def row_public(row,source):
    if row is None: return None
    name,first,low,high=row
    known={r[0] for r in source['functions']}|{r[0] for r in source['source_sites']}
    return dict(function=name if name in known else None,function_sha256=sha(name.encode('utf-8','strict')),
                first_line=first,low=low,high=high)


def table_observation(actual,source):
    expected=source['functions'];differences=[];count=0
    for index in range(max(len(expected),len(actual))):
        old=expected[index] if index<len(expected) else None
        new=actual[index] if index<len(actual) else None
        if old!=new:
            count+=1
            if len(differences)<DIFFERENCE_LIMIT:
                differences.append(dict(ordinal=index,author=row_public(old,source),runtime=row_public(new,source)))
    return dict(author_count=len(expected),runtime_count=len(actual),author_sha256=sha(canonical(expected)),
        runtime_sha256=sha(canonical(actual)),equal=expected==actual,difference_count=count,
        differences=differences,differences_truncated=count>DIFFERENCE_LIMIT)


def named_site_binding(compiled,sites):
    lookup={(name,first):(low,high) for name,first,low,high in sites}
    named=[];anonymous=0
    for item in codes(compiled):
        if item.co_name.startswith('<') and item.co_name!='<module>': anonymous+=1;continue
        key=(item.co_qualname,item.co_firstlineno)
        need(key in lookup,'COMPILED_NAMED_SITE')
        low,high=lookup[key]
        lines=[line for _,_,line in item.co_lines() if line is not None]
        need(all(low<=line<=high for line in lines),'COMPILED_NAMED_SITE')
        if list(key) not in named: named.append(list(key))
    # A source site need not survive constant folding; every runtime named code
    # object must nevertheless have exactly one source definition site.
    return dict(named_sites_match=True,named_count=len(named),named_sha256=sha(canonical(named)),anonymous_code_count=anonymous)


def admit_sources(root,p):
    runtime=runtime_metadata();bindings={};total=0;current_role=None
    record=dict(schema='dg16.native-intake-source-admission.v1',authority='NONE',scope='COMPILE_ONLY_NO_MAINTAINED_EXECUTION',
        source_commit=SOURCE_COMMIT,source_tree=SOURCE_TREE,profile_sha256=PROFILE_SHA,runtime=runtime,
        runtime_admitted=runtime_admitted(runtime),rows=[],source_bytes=0,source_closure_unchanged=False,
        admitted=False,phase='ADMISSION_REFUSED',failure_code=None,failure_role=None,
        maintained_source_executed=False,maintained_modules_imported=False,tests_run=0,
        author_table_equality_required=False,same_runtime_code_equality_required=True,
        anonymous_frames_publicly_named=False,original_awards=False)
    try:
        need(record['runtime_admitted'],'RUNTIME_NOT_ADMITTED')
        need(type(p['sources']) is list and tuple(row['role'] for row in p['sources'])==ROLES,'SOURCE_ROLE_POPULATION')
        for row in p['sources']:
            current_role=row['role'];path=root/row['path'];raw=read_regular(path,1024*1024);total+=len(raw)
            need(total<=2*1024*1024 and len(raw)==row['bytes'] and sha(raw)==row['sha256'],'SOURCE_PIN')
            sites=source_sites(raw)
            compiled=compile(raw,str(path),'exec',dont_inherit=True,optimize=0)
            actual=function_rows(compiled)
            try: named=named_site_binding(compiled,row['source_sites'])
            except Refusal as exc:
                if str(exc)!='COMPILED_NAMED_SITE': raise
                named=dict(named_sites_match=False,named_count=None,named_sha256=None,
                    anonymous_code_count=sum(item.co_name.startswith('<') and item.co_name!='<module>' for item in codes(compiled)))
            # Retain the exact bounded table comparison before either site gate
            # can refuse. The failing role is therefore still discriminating.
            record['rows'].append(dict(role=row['role'],bytes=len(raw),sha256=sha(raw),source_site_count=len(sites),
                source_sites_sha256=sha(canonical(sites)),source_sites_match=sites==row['source_sites'],
                functions=table_observation(actual,row),**named))
            need(sites==row['source_sites'],'SOURCE_SITE_DERIVATION')
            need(named['named_sites_match'],'COMPILED_NAMED_SITE')
            bindings[str(path)]=dict(row=row,raw=raw,code=compiled,codes=tuple(codes(compiled)))
        record['source_closure_unchanged']=all(read_regular(Path(path),1024*1024)==entry['raw'] for path,entry in bindings.items())
        need(record['source_closure_unchanged'],'SOURCE_CLOSURE_CHANGED')
        record.update(admitted=True,phase='ADMISSION_COMPLETED')
    except BaseException as exc:
        code=str(exc) if isinstance(exc,Refusal) and str(exc) in FAILURES else 'SOURCE_COMPILE_REFUSED' if isinstance(exc,(SyntaxError,UnicodeError)) else 'UNCLASSIFIED_ADMISSION_REFUSAL'
        record.update(failure_code=code,failure_role=current_role)
    record['source_bytes']=sum(row['bytes'] for row in record['rows'])
    validate_record(record,p)
    return bindings,record


def validate_record(value,p):
    fields={'schema','authority','scope','source_commit','source_tree','profile_sha256','runtime','runtime_admitted','rows',
        'source_bytes','source_closure_unchanged','admitted','phase','failure_code','failure_role','maintained_source_executed',
        'maintained_modules_imported','tests_run','author_table_equality_required','same_runtime_code_equality_required',
        'anonymous_frames_publicly_named','original_awards'}
    need(type(value) is dict and set(value)==fields,'ADMISSION_FIELDS')
    need(value['schema']=='dg16.native-intake-source-admission.v1' and value['authority']=='NONE'
        and value['scope']=='COMPILE_ONLY_NO_MAINTAINED_EXECUTION' and value['source_commit']==SOURCE_COMMIT
        and value['source_tree']==SOURCE_TREE and value['profile_sha256']==PROFILE_SHA,'ADMISSION_BINDING')
    for key in ('maintained_source_executed','maintained_modules_imported','author_table_equality_required',
                'anonymous_frames_publicly_named','original_awards'): need(value[key] is False,'ADMISSION_AUTHORITY')
    need(value['same_runtime_code_equality_required'] is True and type(value['tests_run']) is int and value['tests_run']==0,'ADMISSION_AUTHORITY')
    runtime=value['runtime']
    need(type(runtime) is dict and set(runtime)=={'implementation','version','releaselevel','serial','cache_tag','flags','compile'},'RUNTIME_FIELDS')
    need(runtime['implementation'] in ('cpython','OTHER') and runtime['releaselevel'] in ('alpha','beta','candidate','final','OTHER')
        and runtime['cache_tag'] in ('cpython-312','OTHER') and type(runtime['version']) is list and len(runtime['version'])==3
        and all(type(n) is int and 0<=n<=10000 for n in runtime['version']) and type(runtime['serial']) is int
        and 0<=runtime['serial']<=10000,'RUNTIME_TYPES')
    need(type(runtime['flags']) is dict and set(runtime['flags'])=={'isolated','no_site','dont_write_bytecode','optimize'}
        and all(type(n) is int and 0<=n<=2 for n in runtime['flags'].values())
        and type(runtime['compile']) is dict and set(runtime['compile'])=={'mode','dont_inherit','optimize'}
        and runtime['compile']['mode']=='exec' and runtime['compile']['dont_inherit'] is True
        and type(runtime['compile']['optimize']) is int and runtime['compile']['optimize']==0,'RUNTIME_FLAGS')
    need(type(value['runtime_admitted']) is bool and value['runtime_admitted']==runtime_admitted(runtime),'RUNTIME_RELATION')
    sources={row['role']:row for row in p['sources']};rows=value['rows']
    need(type(rows) is list and len(rows)<=8 and [r.get('role') for r in rows]==list(ROLES[:len(rows)]),'ADMISSION_POPULATION')
    def integer(number,maximum=2*1024*1024): return type(number) is int and 0<=number<=maximum
    def hashvalue(token): return type(token) is str and re.fullmatch('[0-9a-f]{64}',token) is not None
    def tablerow(row,source):
        if row is None: return
        need(type(row) is dict and set(row)=={'function','function_sha256','first_line','low','high'},'FUNCTION_ROW_FIELDS')
        names={r[0] for r in source['functions']}|{r[0] for r in source['source_sites']}
        need(row['function'] is None or row['function'] in names,'FUNCTION_NAME_ALLOWLIST')
        need(hashvalue(row['function_sha256']) and (row['function'] is None or sha(row['function'].encode())==row['function_sha256'])
            and all(integer(row[k]) for k in ('first_line','low','high')) and row['low']<=row['high'],'FUNCTION_ROW_TYPES')
    for row in rows:
        need(type(row) is dict and set(row)=={'role','bytes','sha256','source_site_count','source_sites_sha256',
            'source_sites_match','functions','named_sites_match','named_count','named_sha256','anonymous_code_count'},'ADMISSION_ROW_FIELDS')
        source=sources[row['role']]
        need(row['bytes']==source['bytes'] and row['sha256']==source['sha256'] and type(row['bytes']) is int
            and integer(row['source_site_count'],ROW_LIMIT) and hashvalue(row['source_sites_sha256'])
            and type(row['source_sites_match']) is bool
            and row['source_sites_match']==(row['source_site_count']==len(source['source_sites'])
                and row['source_sites_sha256']==sha(canonical(source['source_sites']))),'ADMISSION_SOURCE_ROW')
        need(type(row['named_sites_match']) is bool and integer(row['anonymous_code_count'],ROW_LIMIT),'ADMISSION_NAMED_ROW')
        if row['named_sites_match']:
            need(integer(row['named_count'],ROW_LIMIT) and 1<=row['named_count']<=len(source['source_sites'])
                and hashvalue(row['named_sha256']),'ADMISSION_NAMED_ROW')
        else: need(row['named_count'] is None and row['named_sha256'] is None,'ADMISSION_NAMED_ROW')
        table=row['functions']
        need(type(table) is dict and set(table)=={'author_count','runtime_count','author_sha256','runtime_sha256','equal',
            'difference_count','differences','differences_truncated'},'FUNCTION_TABLE_FIELDS')
        need(type(table['author_count']) is int and table['author_count']==len(source['functions'])
            and table['author_sha256']==sha(canonical(source['functions'])) and integer(table['runtime_count'],ROW_LIMIT)
            and hashvalue(table['runtime_sha256']) and type(table['equal']) is bool
            and type(table['differences_truncated']) is bool and integer(table['difference_count'],ROW_LIMIT),'FUNCTION_TABLE_TYPES')
        diffs=table['differences'];count=table['difference_count']
        need(type(diffs) is list and len(diffs)==min(count,DIFFERENCE_LIMIT)
            and count<=max(table['author_count'],table['runtime_count'])
            and table['differences_truncated']==(count>DIFFERENCE_LIMIT)
            and table['equal']==(count==0) and table['equal']==(table['author_count']==table['runtime_count']
                and table['author_sha256']==table['runtime_sha256']),'FUNCTION_TABLE_RELATION')
        previous=-1
        for difference in diffs:
            need(type(difference) is dict and set(difference)=={'ordinal','author','runtime'}
                and integer(difference['ordinal'],ROW_LIMIT-1) and previous<difference['ordinal']
                and difference['ordinal']<max(table['author_count'],table['runtime_count']),'FUNCTION_DIFFERENCE_ORDINAL')
            previous=difference['ordinal'];index=difference['ordinal']
            for key in ('author','runtime'): tablerow(difference[key],source)
            expected=source['functions'][index] if index<len(source['functions']) else None
            need(difference['author']==row_public(expected,source) and difference['author']!=difference['runtime']
                and (difference['runtime'] is None)==(index>=table['runtime_count']),'FUNCTION_DIFFERENCE_BINDING')
    need(type(value['source_bytes']) is int and value['source_bytes']==sum(row['bytes'] for row in rows)
        and value['source_bytes']<=2*1024*1024 and type(value['source_closure_unchanged']) is bool
        and type(value['admitted']) is bool,'ADMISSION_TOTALS')
    if value['admitted']:
        need(value['phase']=='ADMISSION_COMPLETED' and value['runtime_admitted'] and len(rows)==8
            and value['source_closure_unchanged'] and all(row['source_sites_match'] and row['named_sites_match'] for row in rows)
            and value['failure_code'] is None and value['failure_role'] is None,'ADMISSION_COMPLETE_RELATION')
    else:
        need(value['phase']=='ADMISSION_REFUSED' and value['failure_code'] in FAILURES
            and (value['failure_role'] is None or value['failure_role'] in ROLES),'ADMISSION_REFUSAL_RELATION')
    need(len(canonical(value))<=RECORD_LIMIT,'ADMISSION_BYTE_BOUND')
    return value


def main(argv=None):
    args=sys.argv[1:] if argv is None else argv
    need(len(args)==2 and args[0]=='--compile-only','FIXED_COMPILE_ONLY_ARGUMENTS')
    root=Path(args[1]).absolute();need(root.resolve(strict=True)==root,'SOURCE_ROOT_CANONICAL')
    p=profile();_,record=admit_sources(root,p)
    sys.stdout.buffer.write(canonical(record));sys.stdout.buffer.flush()
    return 0 if record['admitted'] else 1


if __name__=='__main__': raise SystemExit(main())
