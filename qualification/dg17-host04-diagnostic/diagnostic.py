#!/usr/bin/env python3
"""Isolated Host04 read-only helper diagnostic. No native, controller or installation route."""
import errno, hashlib, json, os, re, signal, stat, sys, time, types
from pathlib import Path

REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
BRANCH_REF = 'refs/heads/pro/dg17-isolated-episode-01-20261106'
PREDECESSOR = '51e6479a563a2d243a7fcfc9af7e61353f6edeb3'
DEADLINE_EXPIRED = False
FIRST_ORIGINAL_REFUSAL = None
TERMINAL_STAGE = 'TIMER_SETUP'
TERMINAL_PREFIX = 'DG17_HOST04_TERMINAL '
PINS_SHA = '8e90bb3c72c22d4261a56b21da21e5b2a78fb6c887e1b87e7d08b7f51623f8b7'
PUBLIC = ('RESULT.json', 'SOURCE.json', 'HOST.json', 'CURRENTNESS.json', 'PREDICATES.json', 'CONTENT.json', 'CLEANUP.json', 'FAILURE.json', 'ARTIFACT_MANIFEST.json')
ORIGINAL_REFUSALS = ('CONTENT_BIN_ALIAS_PROFILE', 'CONTENT_SYSTEM_ANCESTRY', 'CONTENT_SYSTEM_HELPER_REFUSED', 'CONTENT_PYTHON_CANONICAL_PROFILE', 'CONTENT_PYTHON_ALIAS_PROFILE', 'CONTENT_SYSTEM_HELPER_ALIAS', 'CONTENT_SYSTEM_HELPER_SHAPE', 'CONTENT_SYSTEM_HELPER_OPEN_DRIFT', 'CONTENT_SYSTEM_HELPER_ELF', 'CONTENT_SYSTEM_HELPER_READ_BOUND', 'CONTENT_SYSTEM_HELPER_DRIFT', 'CONTENT_SYSTEM_HELPER_IDENTITY_JOIN', 'CONTENT_BIN_ALIAS_DRIFT')

class Refusal(Exception): pass


def need(test, code):
    if not test: raise Refusal(code)


def digest(raw): return hashlib.sha256(raw).hexdigest()


def encoded(value): return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()


def catalogue_schema_matches(value, schema):
    # The pinned result schema uses only this small, closed keyword set.
    allowed = {'$schema', 'title', 'type', 'additionalProperties', 'required', 'properties', 'const', 'enum', 'anyOf', 'minimum', 'maximum', 'maxItems', 'items', 'pattern'}
    need(type(schema) is dict and set(schema) <= allowed, 'CATALOGUE_SCHEMA_KEYWORD')
    if 'anyOf' in schema:
        need(set(schema) == {'anyOf'}, 'CATALOGUE_SCHEMA_COMBINATION')
        return any(catalogue_schema_matches(value, part) for part in schema['anyOf'])
    expected = {'object': dict, 'array': list, 'string': str, 'integer': int, 'boolean': bool, 'null': type(None)}
    if 'type' in schema:
        need(schema['type'] in expected, 'CATALOGUE_SCHEMA_TYPE')
        if type(value) is not expected[schema['type']]: return False
    if 'const' in schema and (type(value) is not type(schema['const']) or value != schema['const']): return False
    if 'enum' in schema and not any(type(value) is type(item) and value == item for item in schema['enum']): return False
    if type(value) is dict:
        need(schema.get('additionalProperties') is False, 'CATALOGUE_SCHEMA_OBJECT_NOT_CLOSED')
        props = schema['properties']
        if not set(schema['required']) <= set(value) <= set(props): return False
        if not all(catalogue_schema_matches(item, props[key]) for key, item in value.items()): return False
    if type(value) is list:
        if 'maxItems' in schema and len(value) > schema['maxItems']: return False
        if 'items' in schema and not all(catalogue_schema_matches(item, schema['items']) for item in value): return False
    if 'minimum' in schema and (type(value) is not int or value < schema['minimum']): return False
    if 'maximum' in schema and (type(value) is not int or value > schema['maximum']): return False
    if 'pattern' in schema and (type(value) is not str or re.search(schema['pattern'], value) is None): return False
    return True


def content_fs_identity(info):
    return {'device':info.st_dev,'inode':info.st_ino,'mode':info.st_mode,
            'uid':info.st_uid,'gid':info.st_gid,'nlink':info.st_nlink,
            'bytes':info.st_size,'mtime_ns':info.st_mtime_ns,'ctime_ns':info.st_ctime_ns}


def content_helper_refusal_observation(name, inherited):
    """Closed metadata from the existing refusal; no raw path, code or exception."""
    helpers = ('bash','cat','bwrap','true','python3','env')
    codes = ('TOOL_NOT_EXECUTABLE','TOOL_CUSTODY_REFUSED','PRIVILEGED_TOOL_REFUSED',
             'TOOL_CAPABILITY_UNKNOWN','FILE_SHAPE_REFUSED','FILE_CHANGED','TOOL_OS_REFUSAL')
    helper = name if type(name) is str and name in helpers else None
    received = (helper is not None and type(inherited) is dict and
                set(inherited) == {'available','requested','code','errno'} and
                inherited['available'] is False and
                type(inherited['requested']) is str and inherited['requested'] == '/usr/bin/'+helper and
                type(inherited['code']) is str and inherited['code'] in codes and
                (inherited['errno'] is None or
                 (inherited['code'] == 'TOOL_OS_REFUSAL' and type(inherited['errno']) is int and
                  0 <= inherited['errno'] <= 4096)))
    return {'schema':'dg17.codex.system-helper-refusal.v1','scope':'FIRST_HELPER_REFUSAL_ONLY',
            'helper_id':helper,'inherited_refusal_received':received,
            'inherited_code':inherited['code'] if received else None,
            'inherited_errno':inherited['errno'] if received else None}


def require(condition, code):
    if not condition:
        raise Refusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked_file(path, maximum=64*1024*1024, single_link=True):
    path = Path(path)
    before = path.lstat()
    require(stat.S_ISREG(before.st_mode) and (not single_link or before.st_nlink == 1)
            and before.st_size <= maximum, 'FILE_SHAPE_REFUSED')
    with path.open('rb') as stream:
        raw = stream.read(maximum+1)
    after = path.lstat()
    require((before.st_dev,before.st_ino,before.st_size,before.st_mtime_ns,before.st_ctime_ns)==
            (after.st_dev,after.st_ino,after.st_size,after.st_mtime_ns,after.st_ctime_ns) and len(raw)<=maximum, 'FILE_CHANGED')
    return raw


def trusted(name):
    requested = Path('/usr/bin')/name
    try:
        path = requested.resolve(strict=True)
        require(path.is_file() and os.access(path,os.X_OK), 'TOOL_NOT_EXECUTABLE')
        for item in (path,*path.parents):
            info = item.lstat()
            require(info.st_uid==0 and not info.st_mode & 0o022, 'TOOL_CUSTODY_REFUSED')
        info = path.stat()
        require(not info.st_mode & 0o6000, 'PRIVILEGED_TOOL_REFUSED')
        try: cap = os.getxattr(path,'security.capability')
        except OSError as exc:
            require(exc.errno in (errno.ENODATA,errno.ENOTSUP), 'TOOL_CAPABILITY_UNKNOWN')
            cap = b''
        require(not cap, 'PRIVILEGED_TOOL_REFUSED')
        raw = checked_file(path, single_link=False)
        return str(path), {'available':True,'requested':'/usr/bin/'+name,'canonical':str(path),
                           'bytes':len(raw),'sha256':sha(raw),'root_owned_nonwritable_chain':True,
                           'setid_or_file_capabilities':False}
    except (OSError,Refusal) as exc:
        code=str(exc) if isinstance(exc,Refusal) else 'TOOL_OS_REFUSAL'
        return None, {'available':False,'requested':'/usr/bin/'+name,'code':code,
                      'errno':getattr(exc,'errno',None)}


def content_system_helpers(u, state):
    """Data-only physical system identities; never run a capability probe."""
    names = ('bash','cat','bwrap','true','python3','env')
    rows = []
    bin_alias = Path('/bin'); alias_info = bin_alias.lstat()
    need(stat.S_ISLNK(alias_info.st_mode) and alias_info.st_uid == 0 and
         os.readlink(bin_alias) in ('usr/bin','/usr/bin') and
         bin_alias.resolve(strict=True) == Path('/usr/bin'), 'CONTENT_BIN_ALIAS_PROFILE')
    for directory in (Path('/'),Path('/usr'),Path('/usr/bin')):
        info = directory.lstat()
        need(stat.S_ISDIR(info.st_mode) and info.st_uid == 0 and not info.st_mode & 0o022 and
             directory.resolve(strict=True) == directory, 'CONTENT_SYSTEM_ANCESTRY')
    for name in names:
        requested = Path('/usr/bin')/name
        canonical, inherited = u.trusted(name)
        if canonical is None:
            state.setdefault('content_helper_refusal', content_helper_refusal_observation(name, inherited))
        need(canonical is not None, 'CONTENT_SYSTEM_HELPER_REFUSED')
        path = Path(canonical); link_info = requested.lstat()
        if name == 'python3':
            need(re.fullmatch(r'/usr/bin/python3(?:\.[0-9]{1,2})?',canonical) is not None,
                 'CONTENT_PYTHON_CANONICAL_PROFILE')
            need((stat.S_ISREG(link_info.st_mode) or stat.S_ISLNK(link_info.st_mode)) and
                 link_info.st_uid == 0, 'CONTENT_PYTHON_ALIAS_PROFILE')
        else:
            if not (path == requested and stat.S_ISREG(link_info.st_mode)):
                remember_policy_refusal(state, name, canonical, link_info.st_mode, path == requested)
            need(path == requested and stat.S_ISREG(link_info.st_mode),
                 'CONTENT_SYSTEM_HELPER_ALIAS')
        info = path.lstat(); identity = content_fs_identity(info)
        need(stat.S_ISREG(info.st_mode) and info.st_uid == 0 and
             not info.st_mode & 0o6022 and info.st_mode & 0o111 and
             64 <= info.st_size <= 67108864, 'CONTENT_SYSTEM_HELPER_SHAPE')
        fd = os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
        try:
            need(content_fs_identity(os.fstat(fd)) == identity, 'CONTENT_SYSTEM_HELPER_OPEN_DRIFT')
            header = os.read(fd,64)
            need(len(header) == 64 and header[:7] == b'\x7fELF\x02\x01\x01' and
                 int.from_bytes(header[16:18],'little') in (2,3) and
                 int.from_bytes(header[18:20],'little') == 62, 'CONTENT_SYSTEM_HELPER_ELF')
            hashed = hashlib.sha256(); hashed.update(header); count = len(header)
            while True:
                chunk = os.read(fd,1048576)
                if not chunk: break
                count += len(chunk); need(count <= info.st_size, 'CONTENT_SYSTEM_HELPER_READ_BOUND')
                hashed.update(chunk)
            need(count == info.st_size and content_fs_identity(os.fstat(fd)) == identity and
                 content_fs_identity(path.lstat()) == identity and
                 content_fs_identity(requested.lstat()) == content_fs_identity(link_info),
                 'CONTENT_SYSTEM_HELPER_DRIFT')
        finally:
            os.close(fd)
        need(inherited['bytes'] == count and inherited['sha256'] == hashed.hexdigest() and
             (Path('/bin')/name).resolve(strict=True) == path,
             'CONTENT_SYSTEM_HELPER_IDENTITY_JOIN')
        rows.append({'name':name,'requested':str(requested),'canonical':canonical,
                     'identity':identity,'requested_identity':content_fs_identity(link_info),
                     'bytes':count,'sha256':hashed.hexdigest(),'elf':'ELF64_LSB_X86_64',
                     'bin_alias_same_file':True,'inherited_admission':inherited})
    need(content_fs_identity(bin_alias.lstat()) == content_fs_identity(alias_info) and
         bin_alias.resolve(strict=True) == Path('/usr/bin'), 'CONTENT_BIN_ALIAS_DRIFT')
    return {'profile':'PHYSICAL_SYSTEM_HELPERS_ONLY_V1','helpers':rows,
            'bin_alias':{'target':os.readlink(bin_alias),'identity':content_fs_identity(alias_info)},
            'capability_probe_executed':False}

class DiagnosticDeadline(BaseException):
    pass


def policy_refusal_observation(name, canonical, requested_mode, same_as_requested):
    """Pure fixed-literal projection of already available observations; no path lookup."""
    try:
        roles = ('bash','cat','bwrap','true','env')
        if not (type(name) is str and name in roles and type(canonical) is str and
                1 <= len(canonical) <= 4096 and canonical.startswith('/') and
                all(33 <= ord(c) <= 126 for c in canonical) and
                type(requested_mode) is int and 0 <= requested_mode <= 4294967295 and
                type(same_as_requested) is bool and
                same_as_requested == (canonical == '/usr/bin/'+name)):
            return None
        regular = stat.S_ISREG(requested_mode)
        if same_as_requested and regular:
            return None
        value = {
            'schema':'dg17.codex.system-helper-policy-refusal.v1',
            'scope':'FIRST_LOCAL_ALIAS_REFUSAL_ONLY',
            'helper_id':name,
            'policy_code':'CONTENT_SYSTEM_HELPER_ALIAS',
            'requested_kind':'REGULAR' if regular else 'SYMLINK' if stat.S_ISLNK(requested_mode) else 'OTHER',
            'canonical_relation':'SAME_AS_REQUESTED' if same_as_requested else 'DIFFERENT_FROM_REQUESTED',
            'canonical_literal_class':('REQUESTED_ROLE_PATH' if canonical == '/usr/bin/'+name else
                                       'USR_LIB_CARGO_COREUTILS_ROLE_LITERAL' if canonical == '/usr/lib/cargo/bin/coreutils/'+name else
                                       'OTHER_PATH'),
            'admission_completed':False,
        }
        return value if len(encoded(value)) <= 1024 else None
    except BaseException:
        return None


def policy_refusal_received(value):
    """Closed structural/consistency check; it never establishes observation truth."""
    try:
        if type(value) is not dict or set(value) != {'schema','scope','helper_id','policy_code',
                'requested_kind','canonical_relation','canonical_literal_class','admission_completed'}:
            return False
        if not (value['schema'] == 'dg17.codex.system-helper-policy-refusal.v1' and
                value['scope'] == 'FIRST_LOCAL_ALIAS_REFUSAL_ONLY' and
                type(value['helper_id']) is str and value['helper_id'] in ('bash','cat','bwrap','true','env') and
                value['policy_code'] == 'CONTENT_SYSTEM_HELPER_ALIAS' and
                type(value['requested_kind']) is str and value['requested_kind'] in ('REGULAR','SYMLINK','OTHER') and
                type(value['canonical_relation']) is str and value['canonical_relation'] in ('SAME_AS_REQUESTED','DIFFERENT_FROM_REQUESTED') and
                type(value['canonical_literal_class']) is str and value['canonical_literal_class'] in ('REQUESTED_ROLE_PATH','USR_LIB_CARGO_COREUTILS_ROLE_LITERAL','OTHER_PATH') and
                value['admission_completed'] is False):
            return False
        if value['canonical_relation'] == 'SAME_AS_REQUESTED':
            if value['canonical_literal_class'] != 'REQUESTED_ROLE_PATH' or value['requested_kind'] == 'REGULAR':
                return False
        elif value['canonical_literal_class'] == 'REQUESTED_ROLE_PATH':
            return False
        return len(encoded(value)) <= 1024
    except BaseException:
        return False


def remember_policy_refusal(state, name, canonical, requested_mode, same_as_requested):
    """Keep the first valid local record; projection must never mask the original refusal."""
    try:
        if type(state) is not dict or policy_refusal_received(state.get('content_helper_policy_refusal')):
            return
        value = policy_refusal_observation(name, canonical, requested_mode, same_as_requested)
        if value is not None:
            state['content_helper_policy_refusal'] = value
    except BaseException:
        pass



def latch_original_refusal(code):
    """Retain only the first captured original allowlisted Refusal, never arbitrary text."""
    global FIRST_ORIGINAL_REFUSAL
    if FIRST_ORIGINAL_REFUSAL is None and type(code) is str and code in ORIGINAL_REFUSALS:
        FIRST_ORIGINAL_REFUSAL = code


def terminal_line(context, original_code, stage, reason, returncode, deadline_observed, timer_cleanup_failed):
    """Closed pure metadata for the existing stderr channel; not proof of process exit."""
    run_id = None; attempt = None; commit = None
    if (type(context) is dict and type(context.get('run_id')) is str and
            re.fullmatch(r'[1-9][0-9]{0,19}',context['run_id']) is not None and
            type(context.get('run_attempt')) is int and context['run_attempt'] == 1 and
            type(context.get('source_commit')) is str and
            re.fullmatch(r'[0-9a-f]{40}',context['source_commit']) is not None):
        run_id = context['run_id']; attempt = 1; commit = context['source_commit']
    known = original_code if type(original_code) is str and original_code in ORIGINAL_REFUSALS else None
    need(type(stage) is str and stage in ('TIMER_SETUP','CONTEXT','SOURCE','CENSUS','PROJECTION','ENCODING','EXPORT','RETURNED'),
         'DIAGNOSTIC_TERMINAL_STAGE')
    need(type(reason) is str and reason in ('RETURNED','FAILURE','DEADLINE','TIMER_FAILURE') and
         type(returncode) is int and returncode in (0,1,2) and
         type(deadline_observed) is bool and type(timer_cleanup_failed) is bool,
         'DIAGNOSTIC_TERMINAL_SHAPE')
    need((reason == 'DEADLINE') == deadline_observed, 'DIAGNOSTIC_TERMINAL_DEADLINE_JOIN')
    if reason != 'RETURNED' or deadline_observed or timer_cleanup_failed:
        need(returncode == 2, 'DIAGNOSTIC_TERMINAL_FAILURE_JOIN')
    if returncode == 1:
        need(known is not None and reason == 'RETURNED' and stage == 'RETURNED',
             'DIAGNOSTIC_TERMINAL_REFUSAL_JOIN')
    if returncode == 0:
        need(known is None and reason == 'RETURNED' and stage == 'RETURNED' and
             not deadline_observed and not timer_cleanup_failed, 'DIAGNOSTIC_TERMINAL_PASS_JOIN')
    packet_state = ('RETURNED_WITHIN_BUDGET' if stage == 'RETURNED' and reason == 'RETURNED' and
                    not deadline_observed and not timer_cleanup_failed else
                    'INCOMPLETE_OR_UNKNOWN' if stage in ('EXPORT','RETURNED') else 'NOT_EXPORTED')
    value = {'schema':'dg17.host04.terminal.v1','scope':'BEST_EFFORT_RECORD_NOT_PROCESS_OUTCOME',
             'run_id':run_id,'run_attempt':attempt,'source_commit':commit,
             'first_original_refusal_code':known,'terminal_stage':stage,'terminal_reason':reason,
             'deadline_observed':deadline_observed,'timer_cleanup_failed':timer_cleanup_failed,
             'returncode':returncode,'packet_state':packet_state}
    line = TERMINAL_PREFIX + json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False) + '\n'
    need(len(line.encode('ascii')) <= 1024, 'DIAGNOSTIC_TERMINAL_BOUND')
    return line


def emit_terminal(context, original_code, stage, reason, returncode, deadline_observed, timer_cleanup_failed):
    """One best-effort bounded write/flush, with no retry, new file or new budget."""
    try:
        line = terminal_line(context,original_code,stage,reason,returncode,deadline_observed,timer_cleanup_failed)
        written = sys.stderr.write(line)
        if type(written) is not int or written != len(line):
            return False
        sys.stderr.flush()
        return True
    except BaseException:
        return False


def diagnostic_census():
    """The entire census effect boundary: exactly one original fixed helper collector."""
    state = {}
    result = {'diagnostic_status':'FAILED','helper_admission':'UNKNOWN','exit_code':2,
              'snapshot':None,'state':state,'failure_kind':'UNEXPECTED_EXCEPTION',
              'original_refusal_code':None,'errno':None}
    try:
        snapshot = content_system_helpers(types.SimpleNamespace(trusted=trusted), state)
    except DiagnosticDeadline:
        raise
    except Refusal as exc:
        code = str(exc)
        if code in ORIGINAL_REFUSALS:
            latch_original_refusal(code)
            result.update(diagnostic_status='COMPLETE',helper_admission='REFUSED',exit_code=1,
                          failure_kind='ORIGINAL_HELPER_REFUSAL',original_refusal_code=code)
    except BaseException as exc:
        if isinstance(exc, OSError):
            result['failure_kind'] = 'OS_ERROR'
            if type(exc.errno) is int and 0 <= exc.errno <= 4096:
                result['errno'] = exc.errno
    else:
        result.update(diagnostic_status='COMPLETE',helper_admission='ADMITTED',exit_code=0,
                      snapshot=snapshot,failure_kind=None)
    return result


def public_documents(observation, source, context):
    complete = observation['diagnostic_status'] == 'COMPLETE'
    admitted = complete and observation['helper_admission'] == 'ADMITTED'
    snapshot = observation['snapshot'] if admitted else None
    state = observation['state']
    policy = state.get('content_helper_policy_refusal')
    if not policy_refusal_received(policy):
        policy = None
    inherited = state.get('content_helper_refusal')
    if inherited is not None:
        # This value is produced only by the unchanged inherited-refusal projector.
        need(type(inherited) is dict, 'DIAGNOSTIC_INHERITED_SHAPE')
    result = {'schema':'dg17.host04.diagnostic-result.v1','scope':'FIXED_HELPER_DIAGNOSTIC_ONLY',
              'diagnostic_status':observation['diagnostic_status'],
              'helper_admission':observation['helper_admission'],'exit_code':observation['exit_code'],
              'original_acceptance':False,'native_route_qualified':False,
              'run_id':context['run_id'],'run_attempt':context['run_attempt'],
              'source_commit':context['source_commit'],'predecessor':context['predecessor']}
    source = dict(source)
    source['source_commit'] = context['source_commit']
    host = {'schema':'dg17.host04.helper-observation.v1',
            'system_helpers':({'profile':'PHYSICAL_SYSTEM_HELPERS_ONLY_V1','count':6,
                               'sha256':digest(encoded(snapshot))} if snapshot is not None else None),
            'system_helper_refusal':inherited,'system_helper_policy_refusal':policy}
    skipped = {'status':'NOT_RUN_DIAGNOSTIC_ONLY'}
    return {'RESULT.json':result,'SOURCE.json':source,'HOST.json':host,
            'CURRENTNESS.json':dict(skipped),'PREDICATES.json':dict(skipped),'CONTENT.json':dict(skipped),
            'CLEANUP.json':{'scope':'NO_CHILD_OR_NATIVE_OPERATION','child_resources_created':False,
                            'native_cleanup_executed':False},
            'FAILURE.json':{'kind':observation['failure_kind'],'original_refusal_code':observation['original_refusal_code'],
                            'errno':observation['errno']}}


def encode_packet(documents, schema):
    need(type(documents) is dict and set(documents) == set(PUBLIC[:-1]), 'DIAGNOSTIC_DOCUMENT_POPULATION')
    result = documents['RESULT.json']; host = documents['HOST.json']; failure = documents['FAILURE.json']
    outcome = (result['diagnostic_status'],result['helper_admission'],result['exit_code'])
    need(outcome in (('COMPLETE','ADMITTED',0),('COMPLETE','REFUSED',1),('FAILED','UNKNOWN',2)), 'DIAGNOSTIC_OUTCOME_JOIN')
    need((host['system_helpers'] is not None) == (outcome == ('COMPLETE','ADMITTED',0)), 'DIAGNOSTIC_SNAPSHOT_JOIN')
    need((failure['kind'] == 'ORIGINAL_HELPER_REFUSAL') == (outcome == ('COMPLETE','REFUSED',1)), 'DIAGNOSTIC_REFUSAL_JOIN')
    if outcome == ('COMPLETE','ADMITTED',0):
        need(failure == {'kind':None,'original_refusal_code':None,'errno':None} and
             host['system_helper_refusal'] is None and host['system_helper_policy_refusal'] is None,
             'DIAGNOSTIC_SUCCESS_JOIN')
    if host['system_helper_policy_refusal'] is not None:
        need(policy_refusal_received(host['system_helper_policy_refusal']) and
             failure['original_refusal_code'] == 'CONTENT_SYSTEM_HELPER_ALIAS' and
             host['system_helper_refusal'] is None, 'DIAGNOSTIC_POLICY_JOIN')
    need(documents['SOURCE.json']['source_commit'] == result['source_commit'], 'DIAGNOSTIC_SOURCE_JOIN')
    raw = {name:encoded(documents[name]) for name in PUBLIC[:-1]}
    need(all(len(value) <= 65536 for value in raw.values()) and sum(map(len,raw.values())) <= 262144,
         'DIAGNOSTIC_PUBLIC_BOUND')
    manifest = {'schema':'dg17.host04.public-packet.v1','scope':'PACKET_INTEGRITY_ONLY_NOT_PROVIDER_TRANSPORT',
                'run_id':result['run_id'],'run_attempt':result['run_attempt'],'source_commit':result['source_commit'],
                'diagnostic_status':result['diagnostic_status'],
                'files':[{'name':name,'bytes':len(raw[name]),'sha256':digest(raw[name])} for name in PUBLIC[:-1]]}
    values = dict(documents); values[PUBLIC[-1]] = manifest
    need(catalogue_schema_matches(values,schema), 'DIAGNOSTIC_PUBLIC_SCHEMA')
    raw[PUBLIC[-1]] = encoded(manifest)
    need(len(raw[PUBLIC[-1]]) <= 65536, 'DIAGNOSTIC_MANIFEST_BOUND')
    return raw


def unique_source_pairs(pairs):
    value = {}
    for key,item in pairs:
        need(key not in value, 'DIAGNOSTIC_SOURCE_DUPLICATE_KEY')
        value[key] = item
    return value


def parse_source_json(raw):
    def reject(value):
        raise Refusal('DIAGNOSTIC_SOURCE_NONFINITE')
    return json.loads(raw.decode('utf-8'),object_pairs_hook=unique_source_pairs,parse_constant=reject)


def receive_source_bytes(raws, expected_entry_sha256):
    """Pure source closure receiving; caller supplies only fixed member bytes."""
    names = ('diagnostic.py','INPUT_PINS.json','SOURCE_BINDING.json','PUBLIC_RESULT_SCHEMA.json')
    need(type(raws) is dict and set(raws) == set(names) and
         all(type(raws[name]) is bytes and 0 < len(raws[name]) <= 1048576 for name in names),
         'DIAGNOSTIC_SOURCE_POPULATION')
    need(type(expected_entry_sha256) is str and re.fullmatch(r'[0-9a-f]{64}',expected_entry_sha256) is not None and
         digest(raws['diagnostic.py']) == expected_entry_sha256, 'DIAGNOSTIC_ENTRYPOINT_HASH')
    need(digest(raws['INPUT_PINS.json']) == PINS_SHA, 'DIAGNOSTIC_INPUT_PINS_HASH')
    pins = parse_source_json(raws['INPUT_PINS.json'])
    need(type(pins) is dict and set(pins) == {'SOURCE_BINDING.json','PUBLIC_RESULT_SCHEMA.json'},
         'DIAGNOSTIC_PIN_POPULATION')
    for name in pins:
        need(type(pins[name]) is str and re.fullmatch(r'[0-9a-f]{64}',pins[name]) is not None and
             digest(raws[name]) == pins[name], 'DIAGNOSTIC_DEPENDENCY_HASH')
    binding = parse_source_json(raws['SOURCE_BINDING.json'])
    need(type(binding) is dict and binding.get('schema') == 'dg17.host04.source-derivation.v1' and
         binding.get('admission_profile') == 'PHYSICAL_SYSTEM_HELPERS_ONLY_V1' and
         binding.get('whole_original_module_execution') is False, 'DIAGNOSTIC_SOURCE_BINDING')
    schema = parse_source_json(raws['PUBLIC_RESULT_SCHEMA.json'])
    return ({'schema':'dg17.host04.source-binding-receipt.v1','input_pins_sha256':PINS_SHA,
             'source_binding_sha256':pins['SOURCE_BINDING.json'],
             'entrypoint_sha256':expected_entry_sha256,'source_bytes_received':True},schema)


def read_source_file(path):
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_uid == os.geteuid() and
         not before.st_mode & 0o022 and 0 < before.st_size <= 1048576, 'DIAGNOSTIC_SOURCE_FILE')
    identity = content_fs_identity(before)
    fd = os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
    try:
        need(content_fs_identity(os.fstat(fd)) == identity, 'DIAGNOSTIC_SOURCE_OPEN_DRIFT')
        chunks=[];count=0
        while True:
            part=os.read(fd,65536)
            if not part:break
            count+=len(part);need(count<=before.st_size,'DIAGNOSTIC_SOURCE_READ_BOUND');chunks.append(part)
        need(count==before.st_size and content_fs_identity(os.fstat(fd))==identity and
             content_fs_identity(path.lstat())==identity,'DIAGNOSTIC_SOURCE_DRIFT')
        return b''.join(chunks)
    finally:
        os.close(fd)


def verify_source(root):
    root = Path(root)
    before = root.lstat()
    need(root.is_absolute() and root.resolve(strict=True)==root and stat.S_ISDIR(before.st_mode) and
         before.st_uid==os.geteuid() and not before.st_mode & 0o022,'DIAGNOSTIC_SOURCE_PARENT')
    raws={name:read_source_file(root/name) for name in
          ('diagnostic.py','INPUT_PINS.json','SOURCE_BINDING.json','PUBLIC_RESULT_SCHEMA.json')}
    need(content_fs_identity(root.lstat())==content_fs_identity(before) and root.resolve(strict=True)==root,
         'DIAGNOSTIC_SOURCE_PARENT_DRIFT')
    return receive_source_bytes(raws,os.environ.get('DG17_ENTRY_SHA256'))


def ensure_budget(deadline):
    if DEADLINE_EXPIRED or time.monotonic() >= deadline:
        raise DiagnosticDeadline()


def export_packet(output, packet, deadline):
    """Only bounded public writes, after census; last-written manifest closes the packet."""
    ensure_budget(deadline)
    need(type(packet) is dict and set(packet)==set(PUBLIC) and
         all(type(packet[name]) is bytes and len(packet[name])<=65536 for name in PUBLIC) and
         sum(len(packet[name]) for name in PUBLIC[:-1])<=262144,'DIAGNOSTIC_EXPORT_BOUND')
    output=Path(output); parent=output.parent
    info=parent.lstat()
    need(output.is_absolute() and parent.resolve(strict=True)==parent and stat.S_ISDIR(info.st_mode) and
         info.st_uid==os.geteuid() and not info.st_mode & 0o022,'DIAGNOSTIC_EXPORT_PARENT')
    os.mkdir(output,0o700)
    root_fd=os.open(output,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    try:
        os.mkdir('public',0o700,dir_fd=root_fd)
        public_fd=os.open('public',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=root_fd)
        try:
            for name in PUBLIC:
                ensure_budget(deadline)
                fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=public_fd)
                try:
                    offset=0
                    while offset<len(packet[name]):
                        ensure_budget(deadline)
                        count=os.write(fd,packet[name][offset:])
                        need(type(count) is int and 0<count<=len(packet[name])-offset,'DIAGNOSTIC_EXPORT_WRITE')
                        offset+=count
                    os.fsync(fd)
                    ensure_budget(deadline)
                finally:
                    os.close(fd)
            os.fsync(public_fd)
        finally:
            os.close(public_fd)
        os.fsync(root_fd)
    finally:
        os.close(root_fd)
    ensure_budget(deadline)



def run_diagnostic(source_root, output, context, deadline):
    global TERMINAL_STAGE
    ensure_budget(deadline)
    TERMINAL_STAGE = 'SOURCE'
    source,schema=verify_source(source_root)
    ensure_budget(deadline)
    TERMINAL_STAGE = 'CENSUS'
    observation=diagnostic_census()
    ensure_budget(deadline)
    TERMINAL_STAGE = 'PROJECTION'
    documents=public_documents(observation,source,context)
    TERMINAL_STAGE = 'ENCODING'
    packet=encode_packet(documents,schema)
    ensure_budget(deadline)
    TERMINAL_STAGE = 'EXPORT'
    export_packet(output,packet,deadline)
    ensure_budget(deadline)
    TERMINAL_STAGE = 'RETURNED'
    return observation['exit_code']


def hosted_context(environment):
    need(environment.get('GITHUB_ACTIONS')=='true' and environment.get('GITHUB_REPOSITORY')==REPOSITORY and
         environment.get('GITHUB_EVENT_NAME')=='push' and environment.get('GITHUB_REF')==BRANCH_REF and
         environment.get('GITHUB_RUN_ATTEMPT')=='1' and environment.get('RUNNER_OS')=='Linux' and
         environment.get('RUNNER_ARCH')=='X64' and environment.get('DG17_EVENT_BEFORE')==PREDECESSOR and
         all(environment.get(key)=='false' for key in ('DG17_EVENT_CREATED','DG17_EVENT_DELETED','DG17_EVENT_FORCED')),
         'DIAGNOSTIC_HOSTED_CONTEXT')
    commit=environment.get('GITHUB_SHA');run_id=environment.get('GITHUB_RUN_ID')
    need(type(commit) is str and re.fullmatch(r'[0-9a-f]{40}',commit) is not None and commit!=PREDECESSOR and
         type(run_id) is str and re.fullmatch(r'[1-9][0-9]{0,19}',run_id) is not None,
         'DIAGNOSTIC_RUN_IDENTITY')
    return {'repository':REPOSITORY,'event_name':'push','ref':BRANCH_REF,'source_commit':commit,
            'predecessor':PREDECESSOR,'run_id':run_id,'run_attempt':1}


def deadline_signal(signum, frame):
    global DEADLINE_EXPIRED
    DEADLINE_EXPIRED = True
    raise DiagnosticDeadline()



def main():
    global DEADLINE_EXPIRED, FIRST_ORIGINAL_REFUSAL, TERMINAL_STAGE
    DEADLINE_EXPIRED=False; FIRST_ORIGINAL_REFUSAL=None; TERMINAL_STAGE='TIMER_SETUP'
    deadline=time.monotonic()+180.0
    previous=None; installed=False; context=None; returncode=2; reason='FAILURE'
    timer_cleanup_failed=False; deadline_observed=False
    try:
        previous=signal.signal(signal.SIGALRM,deadline_signal);installed=True
        signal.setitimer(signal.ITIMER_REAL,180.0)
        TERMINAL_STAGE='CONTEXT'
        need(len(sys.argv)==3 and sys.argv[1]=='--census','DIAGNOSTIC_ARGUMENTS')
        context=hosted_context(os.environ)
        temp=os.environ.get('RUNNER_TEMP')
        need(type(temp) is str and Path(temp).is_absolute(),'DIAGNOSTIC_OUTPUT_ROOT')
        output=Path(temp)/('dg17-host04-'+context['run_id']+'-a1')
        need(sys.argv[2]==str(output),'DIAGNOSTIC_OUTPUT_ARGUMENT')
        returncode=run_diagnostic(Path(__file__).absolute().parent,output,context,deadline)
        reason='RETURNED'
    except DiagnosticDeadline:
        returncode=2; reason='DEADLINE'; deadline_observed=True
    except BaseException:
        returncode=2; reason='TIMER_FAILURE' if TERMINAL_STAGE=='TIMER_SETUP' else 'FAILURE'
    finally:
        if installed:
            try:
                signal.setitimer(signal.ITIMER_REAL,0.0)
                signal.signal(signal.SIGALRM,previous)
            except BaseException:
                returncode=2; reason='TIMER_FAILURE'; timer_cleanup_failed=True
    # Cleanup/terminal handling does not renew the census/source/export budget.
    try:
        ensure_budget(deadline)
    except DiagnosticDeadline:
        returncode=2; reason='DEADLINE'; deadline_observed=True
    except BaseException:
        returncode=2; reason='FAILURE'
    if deadline_observed or DEADLINE_EXPIRED:
        returncode=2; reason='DEADLINE'; deadline_observed=True
    emitted=emit_terminal(context,FIRST_ORIGINAL_REFUSAL,TERMINAL_STAGE,reason,returncode,
                          deadline_observed,timer_cleanup_failed)
    if not emitted:
        return 2
    # A late marker/flush failure or expiry can make its reported returncode stale.
    # Independent numeric process outcome is mandatory; never emit a second line.
    try:
        ensure_budget(deadline)
    except BaseException:
        return 2
    return returncode


if __name__ == '__main__':
    sys.exit(main())
