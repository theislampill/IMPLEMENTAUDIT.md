#!/usr/bin/env python3
"""One maintained positive case; bounded observation of actual failure frames.

No owner hook is replaced and no call is replayed. Local-value access is limited to the exact
source-pinned compiler and failed transport frames declared in DIAGNOSTIC_PROFILE.json.
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

PROFILE_SHA = 'ed837c7ecbff50d0f7049ffdfbeba9035b8d056c7d7472e9bb605fda2d4b1eb8'
ADMISSION_SHA = '34be181961cfcb5c9e18b0036124dce37efa5e36bf6a51a86afbdd031e71635d'
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
    need(value['schema']=='dg16.native-intake-diagnostic-profile.v2'
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


def admission_module():
    path=Path(__file__).with_name('source_admission.py')
    raw=read_regular(path,1024*1024)
    need(sha(raw)==ADMISSION_SHA,'ADMISSION_MODULE_PIN')
    value=types.ModuleType('hosted_source_admission');value.__file__=str(path)
    exec(compile(raw,str(path),'exec',dont_inherit=True,optimize=0),value.__dict__)
    return value


def bind_sources(root,p):
    admission=admission_module();bindings,record=admission.admit_sources(root,p)
    need(record['admitted'],'SOURCE_ADMISSION_REFUSED')
    return bindings


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
            sites=selected['row']['source_sites']
            admitted=any(code.co_qualname==name and code.co_firstlineno==first and low<=tb.tb_lineno<=high
                         for name,first,low,high in sites)
            if admitted and tb.tb_lineno in lines:
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


# Pure diagnostic language. This context is populated before the maintained case.
# No filesystem access, object coercion or owner calls occur in the observer.
_FORMATTER_CONTEXT = None


def formatter_gate(condition, code):
    if not condition:
        raise Refusal(code)


def formatter_sha(value):
    return sha(canonical(value))


def formatter_keys(value, keys):
    return type(value) is dict and all(type(k) is str for k in value) and set(value)==set(keys)


def formatter_path(value):
    return (type(value) is str and 1<len(value)<=4096 and value.startswith('/')
            and all(ord(c)>=32 for c in value) and not any(x in ('','.','..') for x in value.split('/')[1:]))


def formatter_context(value,p):
    f=p['formatter_observed_slot'];b=f['binary']
    formatter_gate(formatter_keys(value,('available','requested','canonical','bytes','sha256',
        'root_owned_nonwritable_chain','setid_or_file_capabilities')),'FORMATTER_TOOL_CONTEXT_REFUSED')
    formatter_gate(all(type(value[k]) is str for k in ('requested','canonical','sha256'))
        and value['available'] is True and value['requested']=='/usr/bin/bwrap'
        and formatter_path(value['canonical']) and type(value['bytes']) is int and value['bytes']==b['bytes']
        and type(value['sha256']) is str and value['sha256']==b['sha256']
        and value['root_owned_nonwritable_chain'] is True and value['setid_or_file_capabilities'] is False,
        'FORMATTER_TOOL_CONTEXT_REFUSED')
    return dict(value)


def formatter_prepare_context(value,p):
    # Deliberate pre-case content read outside the pure frame observer.
    value=formatter_context(value,p)
    raw=read_regular(Path(value['canonical']),p['formatter_observed_slot']['binary']['bytes'])
    formatter_gate(len(raw)==value['bytes'] and sha(raw)==value['sha256'],'FORMATTER_PRECASE_TOOL_BYTES_REFUSED')
    return value


def formatter_argv(values,p,context):
    f=p['formatter_observed_slot'];t=f['transport'];lim=f['limits']
    formatter_gate(type(values) is dict and all(type(k) is str for k in values),'FORMATTER_LOCALS_TYPE_REFUSED')
    names=('command','bindings','descriptors','roots','manifests','startup_members','environment',
           'arguments','bwrap','python','bash','child','request','repository','common','source_dir','overlay')
    formatter_gate(all(k in values for k in names),'FORMATTER_LOCALS_POPULATION_REFUSED')
    v={k:values[k] for k in names}
    command=v['command'];bindings=v['bindings'];fds=v['descriptors'];roots=v['roots']
    formatter_gate(type(command) is list and 1<=len(command)<=lim['argv_tokens']
        and all(type(x) is str and '\0' not in x and len(x)<=lim['argv_utf8_bytes'] for x in command),
        'FORMATTER_ARGV_TYPE_REFUSED')
    command_bytes=sum(len(x.encode('utf-8','strict')) for x in command)
    formatter_gate(command_bytes<=lim['argv_utf8_bytes'],'FORMATTER_ARGV_BYTE_BOUND_REFUSED')
    formatter_gate(type(roots) is list and len(roots)==2 and all(formatter_path(x) for x in roots),
        'FORMATTER_ROOT_STRINGS_REFUSED')
    formatter_gate(type(bindings) is dict and 1<=len(bindings)<=2
        and all(type(x) is int and 0<=x<4096 for x in bindings.values()),'FORMATTER_BINDINGS_TYPE_REFUSED')
    # Keys are opaque: only identity is inspected. No key hashing/equality or Path methods.
    pairs=list(bindings.items())
    formatter_gate(all(k is v['repository'] or k is v['common'] for k,_ in pairs)
        and len(set(x for _,x in pairs))==len(pairs),'FORMATTER_BINDING_IDENTITY_REFUSED')
    if len(pairs)==1:
        formatter_gate(pairs[0][0] is v['repository'] and roots[0]==roots[1],
            'FORMATTER_BINDING_IDENTITY_REFUSED')
    else:
        formatter_gate(any(k is v['repository'] for k,_ in pairs)
            and any(k is v['common'] for k,_ in pairs) and roots[0]!=roots[1],
            'FORMATTER_BINDING_IDENTITY_REFUSED')
    formatter_gate(type(fds) is list and 1<=len(fds)<=16
        and all(type(x) is int and 0<=x<4096 for x in fds) and len(set(fds))==len(fds)
        and not set(fds)&{x for _,x in pairs},'FORMATTER_SEALED_FDS_REFUSED')
    for name in ('bwrap','python','bash'):
        formatter_gate(formatter_path(v[name]),'FORMATTER_TOOL_STRING_REFUSED')
    formatter_gate(v['bwrap']==context['canonical'],'FORMATTER_SELECTED_TOOL_JOIN_REFUSED')
    args=v['arguments']
    formatter_gate(type(args) is tuple and all(type(x) is str for x in args)
        and (args==('--current-controller',) or len(args)==2 and (
          args[0]=='--require-current-continuity' and re.fullmatch('[a-z0-9][a-z0-9-]{0,47}',args[1])
          or args[0]=='--verify-resume-receipt' and re.fullmatch('refs/implementaudit/continuity-receipts/[a-z0-9][a-z0-9-]{0,47}/G[0-9A-F]{4}@[0-9a-f]{40}',args[1]))),
        'FORMATTER_ARGUMENT_ROLE_REFUSED')
    manifests=v['manifests'];startup=v['startup_members'];environment=v['environment'];request=v['request']
    formatter_gate(type(manifests) is list and 1<=len(manifests)<=14,'FORMATTER_MANIFEST_SHAPE_REFUSED')
    for row in manifests:
        formatter_gate(formatter_keys(row,('name','path','bytes','sha256','mode'))
            and type(row['name']) is str and re.fullmatch('[A-Za-z0-9_.-]{1,80}',row['name'])
            and formatter_path(row['path']) and type(row['bytes']) is int and 0<=row['bytes']<=8388608
            and type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}',row['sha256'])
            and type(row['mode']) is int and row['mode'] in (0o644,0o755),'FORMATTER_MANIFEST_SHAPE_REFUSED')
    identity=[[r['name'],r['bytes'],r['sha256'],r['mode']] for r in manifests]
    formatter_gate(identity in t['source_profiles'],'FORMATTER_MANIFEST_SOURCE_JOIN_REFUSED')
    wrapper=('#!'+v['bash']+'\nexec '+t['python_alias']+' -I -S -B "$@"\n').encode('utf-8','strict')
    expected_startup=[dict(name=n,path=t['python_directory']+'/'+n,bytes=len(wrapper),sha256=sha(wrapper),mode=0o755)
                      for n in ('python','python3')]
    formatter_gate(type(startup) is list and len(startup)==2,'FORMATTER_STARTUP_SHAPE_REFUSED')
    for row in startup:
        formatter_gate(formatter_keys(row,('name','path','bytes','sha256','mode'))
            and all(type(row[k]) is str for k in ('name','path','sha256'))
            and type(row['bytes']) is int and type(row['mode']) is int,'FORMATTER_STARTUP_SHAPE_REFUSED')
    formatter_gate(startup==expected_startup and len(fds)==len(manifests)+2,'FORMATTER_STARTUP_JOIN_REFUSED')
    formatter_gate(type(environment) is dict and all(type(k) is str and type(x) is str for k,x in environment.items())
        and environment==t['environment'],'FORMATTER_ENVIRONMENT_REFUSED')
    formatter_gate(type(v['child']) is str and sha(v['child'].encode('utf-8','strict'))==t['embedded_child_sha256'],
        'FORMATTER_CHILD_SOURCE_JOIN_REFUSED')
    formatter_gate(formatter_keys(request,('repository','members','bash','arguments','startup','startup_members','python','host_python')),
        'FORMATTER_REQUEST_SHAPE_REFUSED')
    formatter_gate(all(type(request[k]) is str for k in ('repository','bash','python','host_python'))
        and request['repository']==roots[0] and request['bash']==v['bash'] and request['python']==t['python_alias']
        and request['host_python']==v['python'] and request['members'] is manifests
        and request['startup_members'] is startup and request['arguments'] is args,
        'FORMATTER_REQUEST_JOIN_REFUSED')
    start=request['startup']
    formatter_gate(formatter_keys(start,('profile','isolated','no_site','dont_write_bytecode'))
        and type(start['profile']) is str and start['profile']=='ISOLATED_CPYTHON_V1'
        and all(start[k] is True for k in ('isolated','no_site','dont_write_bytecode')),'FORMATTER_REQUEST_JOIN_REFUSED')
    roles={}
    def role(raw,name):
        formatter_gate(type(raw) is str,'FORMATTER_ROLE_TYPE_REFUSED')
        key=raw.encode('utf-8','strict');roles.setdefault(key,set()).add(name)
    def take(expected,index):
        formatter_gate(command[index:index+len(expected)]==expected,'FORMATTER_ARGV_GRAMMAR_REFUSED')
        return index+len(expected)
    i=take([v['bwrap'],'--unshare-user','--unshare-net','--cap-drop','ALL','--die-with-parent','--clearenv'],0)
    previous=-1
    while i<len(command) and command[i]=='--ro-bind':
        formatter_gate(i+2<len(command),'FORMATTER_ARGV_GRAMMAR_REFUSED')
        root=command[i+1]
        formatter_gate(root in t['host_roots'] and root!='/dev','FORMATTER_ARGV_GRAMMAR_REFUSED')
        number=t['host_roots'].index(root)
        formatter_gate(number>previous,'FORMATTER_ARGV_GRAMMAR_REFUSED');previous=number
        i=take(['--ro-bind',root,root],i);role(root,'BYTE_EQUALS_HOST_RO_BIND_OPERAND')
    i=take(['--dev-bind','/dev/null','/dev/null','--symlink','/proc/self/fd','/dev/fd'],i)
    role('/dev/null','BYTE_EQUALS_NULL_DEVICE_BIND');role('/proc/self/fd','BYTE_EQUALS_DEV_FD_SYMLINK_SOURCE')
    role('/dev/fd','BYTE_EQUALS_DEV_FD_SYMLINK_DEST')
    pending={str(fd):(key,fd) for key,fd in pairs}
    for _ in pairs:
        formatter_gate(i+2<len(command) and command[i]=='--ro-bind-fd' and command[i+1] in pending,
            'FORMATTER_ARGV_GRAMMAR_REFUSED')
        key,fd=pending.pop(command[i+1]);dest=command[i+2]
        expected=roots[0] if key is v['repository'] else roots[1]
        formatter_gate(dest==expected,'FORMATTER_BINDING_DEST_JOIN_REFUSED')
        role(dest,'BYTE_EQUALS_BOUND_DATA_DEST')
        if key is v['repository'] or len(pairs)==1:role(dest,'BYTE_EQUALS_REPOSITORY_BIND_DEST')
        if key is v['common'] or len(pairs)==1:role(dest,'BYTE_EQUALS_COMMON_BIND_DEST')
        role(str(fd),'BYTE_EQUALS_ISSUED_BIND_FD_NUMBER')
        role('/proc/self/fd/'+str(fd),'BYTE_EQUALS_ISSUED_BIND_FD_PROC_SOURCE');i+=3
    overlay=None
    if v['overlay'] is not None:
        formatter_gate(i+1<len(command) and command[i]=='--tmpfs' and formatter_path(command[i+1]),
            'FORMATTER_ARGV_GRAMMAR_REFUSED')
        overlay=command[i+1];role(overlay,'BYTE_EQUALS_SOURCE_OVERLAY_DEST');i+=2
    formatter_gate(i+1<len(command) and command[i]=='--dir' and formatter_path(command[i+1]),
        'FORMATTER_ARGV_GRAMMAR_REFUSED')
    source_dir=command[i+1]
    formatter_gate(all(r['path']==source_dir+'/'+r['name'] for r in manifests),'FORMATTER_SOURCE_DIR_JOIN_REFUSED')
    i=take(['--dir',source_dir,'--dir',t['python_directory'],'--ro-bind',v['python'],t['python_alias']],i)
    role(source_dir,'BYTE_EQUALS_SOURCE_DIRECTORY_DEST');role(t['python_directory'],'BYTE_EQUALS_PYTHON_DIRECTORY_DEST')
    role(v['python'],'BYTE_EQUALS_HOST_PYTHON_SOURCE');role(t['python_alias'],'BYTE_EQUALS_PRIVATE_PYTHON_ALIAS')
    for fd,row in zip(fds,manifests+startup):
        i=take(['--perms',format(row['mode'],'04o'),'--file',str(fd),row['path']],i)
        role(row['path'],'BYTE_EQUALS_SEALED_SOURCE_DEST' if row in manifests else 'BYTE_EQUALS_STARTUP_WRAPPER_DEST')
        role(str(fd),'BYTE_EQUALS_ISSUED_SEALED_FD_NUMBER');role('/proc/self/fd/'+str(fd),'BYTE_EQUALS_ISSUED_SEALED_FD_PROC_TEXT')
    if overlay is not None:i=take(['--remount-ro',overlay],i)
    i=take(['--remount-ro','/','--chdir',roots[0]],i);role('/','BYTE_EQUALS_FINAL_ROOT_REMOUNT_DEST')
    role(roots[0],'BYTE_EQUALS_REPOSITORY_CHDIR')
    for k,val in sorted(environment.items()):i=take(['--setenv',k,val],i)
    i=take([t['python_alias'],'-I','-S','-B','-c',v['child'],json.dumps(request,separators=(',',':'))],i)
    formatter_gate(i==len(command),'FORMATTER_ARGV_GRAMMAR_REFUSED')
    return dict(tokens=len(command),utf8_bytes=command_bytes,sha256=formatter_sha(command),
                binding_fd_count=len(pairs),sealed_fd_count=len(fds),
                scope='SOURCE_SHAPE_AND_LOCAL_CONSISTENCY_OPAQUE_PATHS_NOT_REEVALUATED'),roles


def formatter_number(raw,conversion):
    if conversion=='%s':return b'\0' not in raw and b'\n' not in raw
    if len(raw)>21:return False
    if conversion in ('%d','%ld','%zu'):
        if re.fullmatch(b'-?(?:0|[1-9][0-9]*)',raw) is None:return False
        n=int(raw)
        low,high=(0,2**64-1) if conversion=='%zu' else ((-2**31,2**31-1) if conversion=='%d' else (-2**63,2**63-1))
        return low<=n<=high and str(n).encode('ascii')==raw
    if conversion=='%#o':
        if re.fullmatch(b'0(?:[1-7][0-7]*)?',raw) is None:return False
        return int(raw,8)<=2**32-1
    return False


def formatter_parses(raw,row,budget,limit):
    literals=[x.encode('utf-8') for x in row['literals']];conversions=row['conversions'];out=[]
    if not raw.startswith(literals[0]):return out
    def walk(n,offset,parts):
        if n==len(conversions):
            if offset==len(raw):
                budget['population']+=1
                formatter_gate(budget['population']<=limit['parse_population'],'FORMATTER_PARSE_POPULATION_REFUSED')
                out.append(parts)
            return
        literal=literals[n+1];pos=offset
        while True:
            budget['work']+=1
            formatter_gate(budget['work']<=limit['parse_work'],'FORMATTER_PARSE_WORK_REFUSED')
            end=raw.find(literal,pos)
            if end<0:break
            part=raw[offset:end]
            if formatter_number(part,conversions[n]):walk(n+1,end+len(literal),parts+[part])
            pos=end+1
    walk(0,len(literals[0]),[])
    return out


def formatter_observe(values,raw,p,context):
    f=p['formatter_observed_slot'];lim=f['limits']
    result=dict(schema='dg16.g1-bwrap-formatter-observation.v1',status='FORMATTER_NOT_CLASSIFIED',
        scope='WHOLE_LINE_COMPATIBILITY_NOT_EMITTER_OR_CAUSE',catalog_sha256=f['catalog_sha256'],
        stream=descriptor(raw),binary=None,argv=None,candidate_count=None,candidate_sha256=None,
        parse_count=None,parse_sha256=None,candidates=[],candidates_omitted=None,
        issued_fd_roles_do_not_assert_live_descriptors=True)
    try:
        context=formatter_context(context,p)
        argv,roles=formatter_argv(values,p,context)
        result['argv']=argv
        result['binary']=dict(bytes=context['bytes'],sha256=context['sha256'],
            canonical_path_sha256=sha(context['canonical'].encode('utf-8','strict')),
            pre_case_content_checked=True,frame_selected_path_equal=True,
            source_metadata_is_not_build_or_install_provenance=True)
        formatter_gate(0<len(raw)<=lim['line_bytes'] and raw.endswith(b'\n') and raw.count(b'\n')==1 and b'\0' not in raw,
            'FORMATTER_WHOLE_LINE_SCOPE_REFUSED')
        full=[];all_parses=[];budget={'work':0,'population':0}
        for row in f['catalog']:
            parses=formatter_parses(raw,row,budget,lim)
            if not parses:continue
            described=[[dict(bytes=len(x),sha256=sha(x),roles=sorted(roles.get(x,set()))) for x in parse] for parse in parses]
            record=dict(id=row['id'],parse_count=len(described),parse_sha256=formatter_sha(described),
                substitution_samples=described[:lim['parse_samples_per_candidate']],
                parses_omitted=len(described)-min(len(described),lim['parse_samples_per_candidate']))
            full.append(record);all_parses.append(dict(id=row['id'],parses=described))
        result.update(status='COMPLETE_FINITE_FORMAT_COMPARISON',candidate_count=len(full),
            candidate_sha256=formatter_sha(full),parse_count=budget['population'],parse_sha256=formatter_sha(all_parses),
            candidates=full[:lim['candidate_samples']],candidates_omitted=max(0,len(full)-lim['candidate_samples']))
        formatter_gate(len(canonical(result))<=lim['observation_bytes'],'FORMATTER_OBSERVATION_BYTE_BOUND_REFUSED')
    except (Refusal,UnicodeError) as exc:
        # Only our closed refusal symbols can be emitted. No arbitrary repr/str.
        code=exc.args[0] if type(exc) is Refusal and type(exc.args) is tuple and len(exc.args)==1 and type(exc.args[0]) is str else 'FORMATTER_UTF8_REFUSED'
        allowed=f['refusal_codes'];code=code if code in allowed else 'FORMATTER_INTERNAL_REFUSED'
        result.update(status=code,candidate_count=None,candidate_sha256=None,parse_count=None,
                      parse_sha256=None,candidates=[],candidates_omitted=None)
    return result


def validate_formatter_observation(value,transport,p):
    f=p['formatter_observed_slot'];lim=f['limits']
    fields=('schema','status','scope','catalog_sha256','stream','binary','argv','candidate_count',
            'candidate_sha256','parse_count','parse_sha256','candidates','candidates_omitted',
            'issued_fd_roles_do_not_assert_live_descriptors')
    need(formatter_keys(value,fields),'FORMATTER_RECORD_FIELDS')
    need(value['schema']=='dg16.g1-bwrap-formatter-observation.v1'
        and value['scope']=='WHOLE_LINE_COMPATIBILITY_NOT_EMITTER_OR_CAUSE'
        and value['catalog_sha256']==f['catalog_sha256']
        and value['stream']==transport['stderr']
        and value['issued_fd_roles_do_not_assert_live_descriptors'] is True,'FORMATTER_RECORD_BINDING')
    complete=value['status']=='COMPLETE_FINITE_FORMAT_COMPARISON'
    need(complete or value['status'] in f['refusal_codes'],'FORMATTER_RECORD_STATUS')
    b=value['binary'];a=value['argv']
    need((b is None)==(a is None),'FORMATTER_BINDING_RELATION')
    if b is not None:
        need(formatter_keys(b,('bytes','sha256','canonical_path_sha256','pre_case_content_checked',
             'frame_selected_path_equal','source_metadata_is_not_build_or_install_provenance'))
             and type(b['bytes']) is int and b['bytes']==f['binary']['bytes'] and b['sha256']==f['binary']['sha256']
             and type(b['canonical_path_sha256']) is str and re.fullmatch('[0-9a-f]{64}',b['canonical_path_sha256'])
             and b['pre_case_content_checked'] is True and b['frame_selected_path_equal'] is True
             and b['source_metadata_is_not_build_or_install_provenance'] is True,'FORMATTER_BINARY_FIELDS')
        need(formatter_keys(a,('tokens','utf8_bytes','sha256','binding_fd_count','sealed_fd_count','scope'))
             and type(a['tokens']) is int and 1<=a['tokens']<=lim['argv_tokens']
             and type(a['utf8_bytes']) is int and 1<=a['utf8_bytes']<=lim['argv_utf8_bytes']
             and type(a['sha256']) is str and re.fullmatch('[0-9a-f]{64}',a['sha256'])
             and type(a['binding_fd_count']) is int and 1<=a['binding_fd_count']<=2
             and type(a['sealed_fd_count']) is int and 3<=a['sealed_fd_count']<=16
             and a['scope']=='SOURCE_SHAPE_AND_LOCAL_CONSISTENCY_OPAQUE_PATHS_NOT_REEVALUATED','FORMATTER_ARGV_FIELDS')
    rows=value['candidates']
    need(type(rows) is list and len(rows)<=lim['candidate_samples'],'FORMATTER_CANDIDATE_POPULATION')
    if not complete:
        need(all(value[k] is None for k in ('candidate_count','candidate_sha256','parse_count','parse_sha256','candidates_omitted'))
             and not rows,'FORMATTER_INCOMPLETE_COUNTS')
    else:
        need(b is not None and 0<value['stream']['bytes']<=lim['line_bytes'],'FORMATTER_COMPLETE_BINDING')
        # Complete producer comparisons require exactly one terminal LF. Join
        # the existing retained partition, without reading a private stream.
        partition=transport.get('marker_observation')
        need(formatter_keys(partition,('separator_present','first_line','remainder',
             'first_line_starts_marker','marker_in_remainder','marker_occurrences')),
             'FORMATTER_COMPLETE_TERMINAL_LF_RELATION')
        validate_descriptor(partition['first_line'],lim['line_bytes'])
        need(partition['separator_present'] is True and partition['remainder']==descriptor(b'')
             and partition['first_line']['bytes']+1==value['stream']['bytes']
             and partition['first_line_starts_marker'] is False and partition['marker_in_remainder'] is False,
             'FORMATTER_COMPLETE_TERMINAL_LF_RELATION')
        # Only source-public operands are recoverable from these descriptors.
        # Private paths and actual issued descriptor numbers remain opaque.
        t=f['transport']
        public_operands={
            'BYTE_EQUALS_NULL_DEVICE_BIND':(b'/dev/null',),
            'BYTE_EQUALS_DEV_FD_SYMLINK_SOURCE':(b'/proc/self/fd',),
            'BYTE_EQUALS_DEV_FD_SYMLINK_DEST':(b'/dev/fd',),
            'BYTE_EQUALS_FINAL_ROOT_REMOUNT_DEST':(b'/',),
            'BYTE_EQUALS_PYTHON_DIRECTORY_DEST':(t['python_directory'].encode('utf-8'),),
            'BYTE_EQUALS_PRIVATE_PYTHON_ALIAS':(t['python_alias'].encode('utf-8'),),
            'BYTE_EQUALS_STARTUP_WRAPPER_DEST':tuple((t['python_directory']+'/'+n).encode('utf-8') for n in ('python','python3')),
            'BYTE_EQUALS_HOST_RO_BIND_OPERAND':tuple(n.encode('utf-8') for n in t['host_roots'] if n!='/dev')}
        numeric_widths={'%d':(1,11),'%ld':(1,20),'%zu':(1,20),'%#o':(1,12)}
        count=value['candidate_count'];pc=value['parse_count'];om=value['candidates_omitted']
        need(type(count) is int and 0<=count<=len(f['catalog']) and type(pc) is int
             and count<=pc<=lim['parse_population'] and type(om) is int and om==count-len(rows)
             and len(rows)==min(count,lim['candidate_samples']),'FORMATTER_COMPLETE_COUNTS')
        for k in ('candidate_sha256','parse_sha256'):
            need(type(value[k]) is str and re.fullmatch('[0-9a-f]{64}',value[k]),'FORMATTER_COMPLETE_HASH')
        catalog={r['id']:r for r in f['catalog']};previous='';sample_parses=0
        for row in rows:
            need(formatter_keys(row,('id','parse_count','parse_sha256','substitution_samples','parses_omitted'))
                 and type(row['id']) is str and row['id'] in catalog and row['id']>previous,'FORMATTER_CANDIDATE_FIELDS')
            previous=row['id'];n=row['parse_count'];samples=row['substitution_samples'];sample_parses+=n
            need(type(n) is int and 1<=n<=pc and type(samples) is list
                 and len(samples)==min(n,lim['parse_samples_per_candidate']) and type(row['parses_omitted']) is int
                 and row['parses_omitted']==n-len(samples) and type(row['parse_sha256']) is str
                 and re.fullmatch('[0-9a-f]{64}',row['parse_sha256']),'FORMATTER_PARSE_COUNTS')
            for subs in samples:
                need(type(subs) is list and len(subs)==len(catalog[row['id']]['conversions']),'FORMATTER_SUBSTITUTION_POPULATION')
                known=[]
                for sub,conversion in zip(subs,catalog[row['id']]['conversions']):
                    need(formatter_keys(sub,('bytes','sha256','roles')),'FORMATTER_SUBSTITUTION_FIELDS')
                    validate_descriptor({k:sub[k] for k in ('bytes','sha256')},lim['line_bytes'])
                    need(sub['bytes']!=0 or sub['sha256']==sha(b''),'FORMATTER_EMPTY_SUBSTITUTION')
                    roles=sub['roles']
                    need(type(roles) is list and all(type(x) is str and x in f['role_codes'] for x in roles)
                         and roles==sorted(set(roles)),'FORMATTER_ROLE_CODES')
                    if conversion in numeric_widths:
                        low,high=numeric_widths[conversion]
                        need(low<=sub['bytes']<=high,'FORMATTER_NUMERIC_WIDTH_RELATION')
                    public_raw=b'' if sub['bytes']==0 else None
                    for role in roles:
                        if role not in public_operands:continue
                        matches=[raw for raw in public_operands[role]
                                 if descriptor(raw)=={k:sub[k] for k in ('bytes','sha256')}
                                 and formatter_number(raw,conversion)]
                        need(matches and (public_raw is None or public_raw==matches[0]),
                             'FORMATTER_PUBLIC_ROLE_DESCRIPTOR_RELATION')
                        public_raw=matches[0]
                    known.append(public_raw)
                need(sum(s['bytes'] for s in subs)+sum(len(s.encode('utf-8')) for s in catalog[row['id']]['literals'])
                     ==value['stream']['bytes'],'FORMATTER_SUBSTITUTION_BYTE_CONSERVATION')
                if all(raw is not None for raw in known):
                    literals=catalog[row['id']]['literals'];public_raw=literals[0].encode('utf-8')
                    for raw,literal in zip(known,literals[1:]):public_raw+=raw+literal.encode('utf-8')
                    need(value['stream']==descriptor(public_raw)
                         and partition['first_line']==descriptor(public_raw[:-1]),
                         'FORMATTER_KNOWN_STREAM_RELATION')
            if n==len(samples):need(row['parse_sha256']==formatter_sha(samples),'FORMATTER_PARSE_HASH_RELATION')
        need(sample_parses+om<=pc and (om!=0 or sample_parses==pc),
             'FORMATTER_TOTAL_PARSE_CONSERVATION')
        if om==0:need(value['candidate_sha256']==formatter_sha(rows),'FORMATTER_CANDIDATE_HASH_RELATION')
        if count==0:
            need(pc==0 and value['candidate_sha256']==formatter_sha([])
                 and value['parse_sha256']==formatter_sha([]),'FORMATTER_EMPTY_CANDIDATES')
        elif om==0 and all(r['parses_omitted']==0 for r in rows):
            need(value['parse_sha256']==formatter_sha([dict(id=r['id'],parses=r['substitution_samples']) for r in rows]),
                 'FORMATTER_ALL_PARSE_HASH_RELATION')
    need(len(canonical(value))<=lim['observation_bytes'],'FORMATTER_OBSERVATION_BYTE_BOUND_REFUSED')


def observe_transport_capture(tb,site,p):
    gate=p['transport_observed_slot']
    if not (site is not None and site['role']==gate['role']
            and site['function']==gate['function'] and site['first_line']==gate['first_line']
            and site['line'] in gate['traceback_lines']):
        return None
    # Existing capture fields, then the separately declared pure formatter locals.
    values=tb.tb_frame.f_locals
    role=argument_role(values.get(gate['arguments_local']))
    empty=dict(argument_role=role,returncode=None,stdout=None,stderr=None,
               marker_observation=None,known_stderr_literals=[],source_literal_ids=[],formatter_observation=None)
    if values.get(gate['canonical_route_local'],True) is not None:
        return dict(status='TRANSPORT_OPERATION_SCOPE_REFUSED',**empty)
    captured=values.get(gate['local'])
    if not (type(captured) is tuple and len(captured)==3):
        return dict(status='TRANSPORT_CAPTURE_ABSENT_OR_NOT_TUPLE',**empty)
    rc,out,err=captured
    if not (type(rc) is int and -255<=rc<=255 and type(out) is bytes and type(err) is bytes
            and len(out)<=gate['stdout_bound'] and len(err)<=gate['stderr_bound']):
        return dict(status='TRANSPORT_CAPTURE_SHAPE_REFUSED',**empty)
    first,separator,remainder=err.partition(b'\n');marker=gate['marker_ascii'].encode('ascii')
    observation=dict(separator_present=bool(separator),first_line=descriptor(first),
        remainder=descriptor(remainder),first_line_starts_marker=first.startswith(marker),
        marker_in_remainder=marker in remainder,marker_occurrences=err.count(marker))
    refused=not separator or not first.startswith(marker) or marker in remainder
    if not refused:
        return dict(status='TRANSPORT_GUARD_RELATION_REFUSED',**empty)
    hits=[r['id'] for r in gate['stderr_literals']
          if r['text'].encode('ascii') in (err.lower() if r['casefold'] else err)]
    return dict(status='ACTUAL_PINNED_TRANSPORT_CAPTURE',argument_role=role,
        returncode=rc,stdout=descriptor(out),stderr=descriptor(err),
        marker_observation=observation,known_stderr_literals=literal_codes(err,p),
        source_literal_ids=hits,formatter_observation=formatter_observe(values,err,p,_FORMATTER_CONTEXT))


def validate_transport_observations(rows,frames,p):
    gate=p['transport_observed_slot'];seen=set()
    need(type(rows) is list and len(rows)<=gate['max_records'],'TRANSPORT_OBSERVATION_POPULATION')
    literal_ids={r['id'] for r in gate['stderr_literals']}
    known={x for x,_ in LITERALS}|set(p['transport_codes'])
    fields={'frame_ordinal','status','argument_role','returncode','stdout','stderr',
            'marker_observation','known_stderr_literals','source_literal_ids','formatter_observation'}
    statuses=('ACTUAL_PINNED_TRANSPORT_CAPTURE','TRANSPORT_OPERATION_SCOPE_REFUSED',
              'TRANSPORT_CAPTURE_ABSENT_OR_NOT_TUPLE','TRANSPORT_CAPTURE_SHAPE_REFUSED',
              'TRANSPORT_GUARD_RELATION_REFUSED')
    for row in rows:
        need(type(row) is dict and set(row)==fields,'TRANSPORT_OBSERVATION_FIELDS')
        index=row['frame_ordinal']
        need(type(index) is int and 0<=index<len(frames) and index not in seen,
             'TRANSPORT_OBSERVATION_ORDINAL');seen.add(index)
        frame=frames[index]
        need(frame.get('kind')=='PINNED_SOURCE' and frame['role']==gate['role']
             and frame['function']==gate['function'] and frame['first_line']==gate['first_line']
             and frame['line'] in gate['traceback_lines'],'TRANSPORT_OBSERVATION_SITE')
        need(row['status'] in statuses and row['argument_role'] in (*gate['allowed_argument_roles'],'UNESTABLISHED'),
             'TRANSPORT_OBSERVATION_ENUMS')
        for key,allowed in [('known_stderr_literals',known),('source_literal_ids',literal_ids)]:
            data=row[key]
            need(type(data) is list and all(type(x) is str for x in data)
                 and len(data)==len(set(data)) and all(x in allowed for x in data),
                 'TRANSPORT_LITERAL_POPULATION')
        if row['status']!='ACTUAL_PINNED_TRANSPORT_CAPTURE':
            need(all(row[k] is None for k in ('returncode','stdout','stderr','marker_observation'))
                 and not row['known_stderr_literals'] and not row['source_literal_ids'] and row['formatter_observation'] is None,
                 'TRANSPORT_UNOBSERVED_FIELDS')
            continue
        need(type(row['returncode']) is int and -255<=row['returncode']<=255,
             'TRANSPORT_OBSERVATION_EXIT')
        validate_descriptor(row['stdout'],gate['stdout_bound'])
        validate_descriptor(row['stderr'],gate['stderr_bound'])
        m=row['marker_observation']
        need(type(m) is dict and set(m)=={'separator_present','first_line','remainder',
             'first_line_starts_marker','marker_in_remainder','marker_occurrences'},'TRANSPORT_MARKER_FIELDS')
        for key in ('separator_present','first_line_starts_marker','marker_in_remainder'):
            need(type(m[key]) is bool,'TRANSPORT_MARKER_BOOLEAN')
        validate_descriptor(m['first_line'],gate['stderr_bound'])
        validate_descriptor(m['remainder'],gate['stderr_bound'])
        # Empty bytes have one exact digest, including when a separator exists.
        for value in (row['stdout'],row['stderr'],m['first_line'],m['remainder']):
            need(value['bytes']!=0 or value==descriptor(b''),
                 'TRANSPORT_EMPTY_DESCRIPTOR_RELATION')
        size=len(gate['marker_ascii'].encode('ascii'))
        need(type(m['marker_occurrences']) is int
             and int(m['first_line_starts_marker'])+int(m['marker_in_remainder'])<=m['marker_occurrences']
             <=row['stderr']['bytes']//size,'TRANSPORT_MARKER_COUNT')
        need(m['first_line']['bytes']+int(m['separator_present'])+m['remainder']['bytes']==row['stderr']['bytes'],
             'TRANSPORT_MARKER_BYTE_RELATION')
        # The source-pinned marker has no newline and cannot cross the separator.
        # A non-prefix occurrence must leave at least one leading byte.
        first_capacity=max(0,(m['first_line']['bytes']-int(not m['first_line_starts_marker']))//size)
        remainder_capacity=m['remainder']['bytes']//size if m['marker_in_remainder'] else 0
        need(m['marker_occurrences']<=first_capacity+remainder_capacity,
             'TRANSPORT_MARKER_SEGMENT_CAPACITY')
        if not m['separator_present']:
            need(m['first_line']==row['stderr'] and m['remainder']==descriptor(b'')
                 and m['marker_in_remainder'] is False,'TRANSPORT_NO_SEPARATOR_RELATION')
        need((not m['first_line_starts_marker'] or m['first_line']['bytes']>=size)
             and (not m['marker_in_remainder'] or m['remainder']['bytes']>=size),
             'TRANSPORT_MARKER_SIZE_RELATION')
        need(not m['separator_present'] or not m['first_line_starts_marker'] or m['marker_in_remainder'],
             'TRANSPORT_NAMESPACE_GUARD_RELATION')
        validate_formatter_observation(row['formatter_observation'],row,p)


def failure_record(err,bindings,p):
    original=err[1];chain=[];seen=set();frames=[];locals_rows=[];transport_rows=[];truncated=False
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
            transport=observe_transport_capture(tb,site,p)
            if transport is not None:
                need(len(transport_rows)<p['transport_observed_slot']['max_records'],'TRANSPORT_OBSERVATION_POPULATION')
                transport_rows.append(dict(frame_ordinal=len(frames)-1,**transport))
            tb=tb.tb_next
        next_exc=exc.__cause__
        if next_exc is None and not exc.__suppress_context__:next_exc=exc.__context__
        exc=next_exc
    return dict(exception_chain=chain,frames=frames,observed_results=locals_rows,
                transport_observations=transport_rows,traceback_or_chain_truncated=truncated)


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
    exec(selected['code'],module.__dict__)
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
         'transport_observations','traceback_or_chain_truncated'},'FAILURE_FIELDS')
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
                 for name,first,low,high in roles[row['role']]['source_sites']),'SOURCE_FRAME_SITE')
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

    validate_transport_observations(value['transport_observations'],frames,p)


def validate_record(value,p):
    need(type(value) is dict and set(value)=={'schema','authority','scope','test','source_commit','source_tree',
         'profile_sha256','phase','tests_run','unittest_success','positive_case_pass','events','runner_text','source_closure_unchanged',
         'bootstrap_failure','source_admission_sha256','source_admission_passed',
         'bank_acceptance','original_G1_award','original_G3_award'},'RESULT_FIELDS')
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
    need(type(value['source_admission_passed']) is bool and (value['source_admission_sha256'] is None
         or type(value['source_admission_sha256']) is str and re.fullmatch('[0-9a-f]{64}',value['source_admission_sha256'])),
         'CASE_ADMISSION_FIELDS')
    need(not value['source_admission_passed'] or value['source_admission_sha256'] is not None,'CASE_ADMISSION_RELATION')
    need(type(value['events']) is list and len(value['events'])<=p['max_terminal_events'],'EVENT_POPULATION')
    for event in value['events']:
        need(type(event) is dict and set(event)=={'outcome','failure'} and event['outcome'] in OUTCOMES,'EVENT_FIELDS')
        if event['failure'] is not None:validate_failure(event['failure'],p)
        need((event['failure'] is None)==(event['outcome'] in ('PASS','SKIP','UNEXPECTED_SUCCESS')),'EVENT_FAILURE_RELATION')
    validate_descriptor(value['runner_text'],262144)
    if value['bootstrap_failure'] is not None:validate_failure(value['bootstrap_failure'],p)
    if value['phase']=='CASE_COMPLETED':
        need(value['tests_run']==1 and value['bootstrap_failure'] is None and value['events']
             and value['source_admission_passed'],'COMPLETE_CASE_RELATION')
    else:
        need(value['bootstrap_failure'] is not None and value['unittest_success'] is False,'BOOTSTRAP_RELATION')
    need(value['positive_case_pass'] is (value['phase']=='CASE_COMPLETED' and value['tests_run']==1
         and value['unittest_success'] and value['events']==[{'outcome':'PASS','failure':None}]
         and value['source_closure_unchanged'] is True),'POSITIVE_PASS_RELATION')
    need(len(canonical(value))<=p['case_record_bytes'],'CASE_RECORD_BYTE_BOUND')
    return value


def main(argv=None):
    global _FORMATTER_CONTEXT
    args=sys.argv[1:] if argv is None else argv
    need(len(args)==3 and re.fullmatch('[0-9a-f]{64}',args[1]) and len(args[2])<=8192,'FIXED_ENTRY_ARGUMENT')
    root=Path(args[0]).absolute();need(root.resolve(strict=True)==root,'SOURCE_ROOT_CANONICAL')
    p=profile();bindings={};os.chdir(root);sys.dont_write_bytecode=True
    record=dict(schema='dg16.native-intake-one-case-diagnostic.v1',authority='NONE',
        scope='ONE_MAINTAINED_POSITIVE_CASE_DIAGNOSTIC_ONLY',test=TEST,source_commit=SOURCE_COMMIT,
        source_tree=SOURCE_TREE,profile_sha256=PROFILE_SHA,phase='BOOTSTRAP_OR_HARNESS_REFUSED',
        tests_run=0,unittest_success=False,positive_case_pass=False,events=[],runner_text=descriptor(b''),
        source_closure_unchanged=False,bootstrap_failure=None,source_admission_sha256=None,
        source_admission_passed=False,bank_acceptance=False,
        original_G1_award=False,original_G3_award=False)
    try:
        admission=admission_module();bindings,admitted=admission.admit_sources(root,p)
        record['source_admission_sha256']=sha(admission.canonical(admitted))
        need(admitted['admitted'],'SOURCE_ADMISSION_REFUSED')
        need(record['source_admission_sha256']==args[1],'SOURCE_ADMISSION_CHANGED_SINCE_COMPILE_ONLY')
        record['source_admission_passed']=True
        _FORMATTER_CONTEXT=formatter_prepare_context(strict(args[2]),p)
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
