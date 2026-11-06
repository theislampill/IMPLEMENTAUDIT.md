#!/usr/bin/env python3
"""DG17-only hosted episode. No local execution route or original awards.

Maintained claim/activation/continuity owners supply all custody authority.
Command capture and child containment reuse the unchanged reviewed host utility.
"""
import argparse, ctypes, errno, hashlib, json, os, platform, re, stat, sys, tarfile, time, types, urllib.request
from pathlib import Path

REPO = 'theislampill/IMPLEMENTAUDIT.md'
BRANCH = 'pro/dg17-isolated-episode-01-20261106'
SOURCE = '0d57929be5bd15682b4e9da2c0209d5dff307843'
TREE = 'ee316c27250ec422d35a1ea965182ebddf7a5da0'
PARENT = '481e529b691ed3d21169b07f376e357ae51f1f03'
MANIFEST_SHA = 'ed6a601d3a66997218195202cb5513363b5410b98489762324095a9030c261b4'
UTILITY_SHA = '429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c'
PINS_SHA = 'b40720c76942d03e4fa807c5888e065fafd4f7c6534e75c5dbd6ceacda192ffc'
CLAIM = 'skills/implementaudit/scripts/claim-run.sh'
AUTHOR = 'fixtures/controller-initialization/author_checkpoint.py'
DOCS = ('STATE.md', 'PROTOCOL.md', 'ROADMAP.md', 'THINKING.md', 'sidecars.md', 'tools.md', 'context.md', 'phases/phase-1.md')
STEPS = ('prepare', 'initialize', 'discover', 'invalidate', 'read-state', 'read-roadmap', 'resume', 'verify', 'require', 'runtime', 'claude', 'receive')
PUBLIC = ('RESULT.json', 'SOURCE.json', 'HOST.json', 'CURRENTNESS.json', 'PREDICATES.json', 'CLAUDE.json', 'CLEANUP.json', 'FAILURE.json', 'ARTIFACT_MANIFEST.json')
PURPOSE = 'Observe only the frozen-source Claude source-candidate metadata with exactly plugin validate, session plugin list and plugin details, under the inherited fresh controller, offline private filesystem view and owned capture/cleanup. Preserve prior independently received component references without replay or original acceptance.'
NEXT = 'Receive the pinned Claude archive as data, run only the three separately admitted metadata commands, retain their separate recognition and custody results, and verify source, currentness, private seals and unchanged outside identities.'
ARCHIVE_URL = 'https://github.com/anthropics/claude-code/releases/download/v2.1.318/claude-linux-x64.tar.gz'
ARCHIVE_SHA = 'e6d426ca0c123f61fad58a361da0329f2a93cd206bc87040ed8d9576dd9eb583'
ARCHIVE_BYTES = 155477886
BINARY_SHA = '708c77b204db30086ff6f1ed34577bda03e1be74ced80557cbf7b54249ebf0bd'
BINARY_BYTES = 337814032
PREDICATE_SCOPE = {
    'direct_source_applicability': ['T06', 'T08', 'Y04', 'BINDING_POSITIVE'],
    'component_only': ['T12'],
    'indirect_inherited_scope_only': ['NESTED/P01'],
    'narrow_receiving_input_only': ['T14'],
    'ceiling': 'SYNTHETIC_IDENTITY_PREDICATES_ONLY_NO_NATIVE_OR_ORIGINAL_AWARD',
}

CAPSULE_TARGETS = ('/opt', '/usr/local/bin', '/etc/gitconfig')
CAPSULE_SCRIPT = 'set -eu\nset -o noclobber\numask 022\n[ "$EUID" -eq 0 ]\n[ "$#" -eq 23 ]\n[ -d /opt ] && [ ! -L /opt ]\n[ -d /usr/local/bin ] && [ ! -L /usr/local/bin ]\n[ -f /etc/gitconfig ] && [ ! -L /etc/gitconfig ]\n/usr/bin/mount --internal-only --no-mtab -t tmpfs -o rw,nodev,nosuid,noexec,size=4096,uid=0,gid=0,mode=0755 tmpfs /opt\n: > /opt/dg17-empty-system-gitconfig\n/usr/bin/mount --internal-only --no-mtab -t tmpfs -o remount,ro,nodev,nosuid,noexec,size=4096,uid=0,gid=0,mode=0755 tmpfs /opt\n/usr/bin/mount --internal-only --no-mtab -o bind,ro,nodev,nosuid,noexec /opt/dg17-empty-system-gitconfig /etc/gitconfig\n/usr/bin/mount --internal-only --no-mtab -t tmpfs -o ro,nodev,nosuid,noexec,size=4096,uid=0,gid=0,mode=0755 tmpfs /usr/local/bin\nexec /usr/bin/setpriv --reuid "$1" --regid "$2" --clear-groups --no-new-privs /usr/bin/python3 -I -S -B -c "$3" "$1" "$2" "$4" "$5" "$6" "$7" "${@:8}"\n'
CAPSULE_SCRIPT_SHA = '3a5ab95387971e1116064f296cffac801ce2314eb668c9d8b6283eded6c8ab7a'
CAPSULE_CODE = "import hashlib,json,os,re,stat,subprocess,sys\nTARGETS=('/opt','/usr/local/bin','/etc/gitconfig')\nCONFIG_SOURCE='/opt/dg17-empty-system-gitconfig'\nEMPTY_SHA='e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'\ndef need(ok,code):\n    if not ok: raise RuntimeError(code)\ndef encode(value):return (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\\n').encode()\ndef sha(raw):return hashlib.sha256(raw).hexdigest()\ndef parse_mounts(raw):\n    need(type(raw) is bytes and len(raw)<=1048576,'MOUNTINFO_BOUND')\n    lines=raw.decode('ascii').splitlines();need(1<=len(lines)<=4096,'MOUNTINFO_POPULATION')\n    rows={};private=True\n    for line in lines:\n        fields=line.split();need('-' in fields,'MOUNTINFO_SHAPE');split=fields.index('-')\n        need(split>=6 and len(fields)>=split+4,'MOUNTINFO_SHAPE')\n        if any(x.startswith(('shared:','master:','propagate_from:')) for x in fields[6:split]):private=False\n        if fields[4] not in TARGETS:continue\n        path=fields[4];need(path not in rows,'DUPLICATE_TARGET_MOUNT')\n        opts=fields[5].split(',');superopts=fields[split+3].split(',')\n        size=[x[5:] for x in superopts if x.startswith('size=')]\n        need(len(size)==1 and re.fullmatch(r'[0-9]+[kKmMgG]?',size[0]),'TMPFS_SIZE')\n        token=size[0];suffix=token[-1].lower();factor={'k':1024,'m':1048576,'g':1073741824}.get(suffix,1)\n        number=int(token[:-1]) if suffix in 'kmg' else int(token)\n        need(all(re.fullmatch(r'[0-9]{1,12}',fields[i]) for i in (0,1)),'MOUNT_ID')\n        rows[path]={'path':path,'mount_id':int(fields[0]),'parent_mount_id':int(fields[1]),'mount_root':fields[3],\n                    'filesystem':fields[split+1],'mount_source':fields[split+2],\n                    'readonly':'ro' in opts and 'rw' not in opts and 'ro' in superopts and 'rw' not in superopts,\n                    'nodev':'nodev' in opts,'nosuid':'nosuid' in opts,'noexec':'noexec' in opts,\n                    'size_bytes':number*factor,'mount_options_sha256':sha(fields[5].encode()),\n                    'super_options_sha256':sha(fields[split+3].encode())}\n    need(set(rows)==set(TARGETS),'TARGET_MOUNTS_MISSING')\n    return private,len(lines),[rows[path] for path in TARGETS]\ndef file_snapshot(path):\n    before=os.lstat(path)\n    need(os.path.realpath(path)==path and stat.S_ISREG(before.st_mode) and\n         before.st_uid==0 and before.st_gid==0 and stat.S_IMODE(before.st_mode)==0o644 and\n         before.st_nlink==1 and before.st_size==0,'EMPTY_CONFIG_FILE')\n    with open(path,'rb') as stream:raw=stream.read(1)\n    after=os.lstat(path)\n    identity=lambda x:(x.st_dev,x.st_ino,x.st_mode,x.st_uid,x.st_gid,x.st_nlink,x.st_size,x.st_mtime_ns,x.st_ctime_ns)\n    need(identity(before)==identity(after) and raw==b'','EMPTY_CONFIG_FILE_CHANGED')\n    return {'file_uid':before.st_uid,'file_gid':before.st_gid,'mode':stat.S_IMODE(before.st_mode),\n            'regular':True,'symlink':False,'nlink':before.st_nlink,'bytes':len(raw),'sha256':sha(raw),\n            'device':before.st_dev,'inode':before.st_ino}\ndef snapshot(uid,gid,parent):\n    namespace=os.readlink('/proc/self/ns/mnt')\n    raw=open('/proc/self/mountinfo','rb').read(1048577)\n    private,count,rows=parse_mounts(raw)\n    fields={}\n    for line in open('/proc/self/status',encoding='ascii'):\n        if ':' in line:\n            key,value=line.split(':',1);fields[key]=value.strip()\n    uids=[int(x) for x in fields['Uid'].split()];gids=[int(x) for x in fields['Gid'].split()]\n    caps={key:int(fields[key],16) for key in ('CapEff','CapPrm','CapAmb')}\n    for row in rows[:2]:\n        path=row['path'];info=os.lstat(path);entries=sorted(os.listdir(path))\n        expected=['dg17-empty-system-gitconfig'] if path=='/opt' else []\n        need(entries==expected,'TARGET_DIRECTORY_POPULATION')\n        row.update(directory_uid=info.st_uid,directory_gid=info.st_gid,mode=stat.S_IMODE(info.st_mode),\n                   directory=stat.S_ISDIR(info.st_mode),symlink=stat.S_ISLNK(info.st_mode),\n                   entries=len(entries),device=info.st_dev,inode=info.st_ino)\n    source=file_snapshot(CONFIG_SOURCE);target=file_snapshot('/etc/gitconfig');rows[2].update(target)\n    need(source==target and source['device']==rows[0]['device'],'EMPTY_CONFIG_BIND_IDENTITY')\n    result={'mount_namespace_sha256':sha(namespace.encode()),'namespace_distinct':namespace!=parent,\n            'private_propagation':private,'mountinfo_sha256':sha(raw),'mount_count':count,\n            'uids':uids,'gids':gids,'groups':os.getgroups(),'capabilities':caps,\n            'no_new_privileges':int(fields['NoNewPrivs']),'mounts':rows,\n            'gitconfig_source':{'path':CONFIG_SOURCE,**source},'source_target_same_file':True}\n    need(result['namespace_distinct'] and private and uids==[uid]*4 and gids==[gid]*4 and\n         not result['groups'] and all(v==0 for v in caps.values()) and result['no_new_privileges']==1,'PRIVILEGE_OR_NAMESPACE')\n    need(len({row['mount_id'] for row in rows})==3 and all(row['filesystem']=='tmpfs' and row['mount_source']=='tmpfs' and\n             row['mount_root']==('/dg17-empty-system-gitconfig' if row['path']=='/etc/gitconfig' else '/') and\n             row['mount_id']>0 and row['parent_mount_id']>0 and row['mount_id']!=row['parent_mount_id'] and\n             all(row[key] is True for key in ('readonly','nodev','nosuid','noexec')) and row['size_bytes']==4096 for row in rows),'TARGET_MOUNT_VIEW')\n    need(all(row['directory'] is True and row['symlink'] is False and row['directory_uid']==0 and\n             row['directory_gid']==0 and row['mode']==0o755 and row['entries']==(1 if row['path']=='/opt' else 0)\n             for row in rows[:2]),'TARGET_DIRECTORY_VIEW')\n    return result\ndef write(path,value,uid):\n    parent=os.path.dirname(path);info=os.lstat(parent)\n    need(os.path.realpath(parent)==parent and stat.S_ISDIR(info.st_mode) and info.st_uid==uid,'PROOF_PARENT')\n    raw=encode(value);need(len(raw)<=16384,'PROOF_BOUND')\n    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)\n    with os.fdopen(fd,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())\n    return sha(raw)\ndef run():\n    need(len(sys.argv)==23,'ARGUMENT_POPULATION')\n    uid=int(sys.argv[1]);gid=int(sys.argv[2]);before_path=sys.argv[3];result_path=sys.argv[4];parent=sys.argv[5]\n    need(uid>0 and gid>0 and re.fullmatch(r'mnt:\\[[0-9]+\\]',parent),'ARGUMENT_VALUE')\n    need(os.path.basename(before_path)=='CAPSULE_ADMISSION.json' and\n         os.path.basename(result_path)=='CAPSULE_RESULT.json' and\n         os.path.dirname(before_path)==os.path.dirname(result_path),'PROOF_PATHS')\n    argv=['/usr/bin/python3','-I','-S','-B',*sys.argv[6:]]\n    argv_sha=sha(encode(argv));before=snapshot(uid,gid,parent)\n    proof={'schema':'dg17.private-view-admission.v2','child_argv_sha256':argv_sha,'snapshot':before}\n    before_sha=write(before_path,proof,uid)\n    child_rc=None;after=None;failure=None\n    try:\n        child=subprocess.Popen(argv,stdin=subprocess.DEVNULL,close_fds=True)\n        child_rc=child.wait()\n    except BaseException:\n        failure='CHILD_START_OR_WAIT_REFUSED'\n    try:after=snapshot(uid,gid,parent)\n    except BaseException:\n        failure=failure or 'AFTER_VIEW_REFUSED'\n    result={'schema':'dg17.private-view-result.v2','before_sha256':before_sha,'child_argv_sha256':argv_sha,\n            'before':before,'after':after,'child_returncode':child_rc,'failure':failure}\n    write(result_path,result,uid)\n    return 0 if failure is None and child_rc==0 and before==after else 1\nif __name__=='__main__':\n    try:sys.exit(run())\n    except BaseException as exc:\n        if isinstance(exc,SystemExit):raise\n        sys.stderr.write('DG17_CAPSULE_ADMISSION_REFUSED\\n');sys.exit(1)\n"
CAPSULE_CODE_SHA = '7782b42246fadeed702a5e42198dac3229ced22a00133ca85fbf7058ca5e3210'
PRIOR_COMPONENT = {'run_id': 42210454718, 'attempt': 1, 'artifact_id': 13497879213, 'artifact_sha256': '9a285ea3756238ac689669782b690a5aa05dfdbbe14a2c285694085ce3b70847', 'predicate_member_sha256': '9028d6711dc1e02b2babf6fc5e4e70974a99a3ed54b547d391ded3f8033af73a', 'source_commit': '0d57929be5bd15682b4e9da2c0209d5dff307843', 'source_tree': 'ee316c27250ec422d35a1ea965182ebddf7a5da0', 'test_path': 'tests/shell_companion_source_custody.py', 'test_source_sha256': '22ffd31ff45e1f439759c45bb5c67bde5e8390b69b54030833476e80aaee7f08', 'independent_receipt_sha256': '9ba49dfeb1ec8e7ac3c4fe122e5c89227340405fa729d48c0c651b8fa12bf07f', 'root_receipt_sha256': 'a63dc54e1812ddf4a57091360d09753fc3b0c9dae90d6cddd4bcc757bc550a64', 'scope': 'SYNTHETIC_IDENTITY_PREDICATES_ONLY_NO_NATIVE_OR_ORIGINAL_AWARD'}

class Refusal(Exception): pass
def need(test, code):
    if not test: raise Refusal(code)
def digest(raw): return hashlib.sha256(raw).hexdigest()
def encoded(value): return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode()
def read(path, limit=1048576):
    path = Path(path); before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size <= limit, 'FILE_SHAPE')
    with path.open('rb') as stream: raw = stream.read(limit+1)
    after = path.lstat()
    need((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) == (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns) and len(raw) == before.st_size, 'FILE_CHANGED')
    return raw
def save(path, value):
    path = Path(path); tmp = path.with_name(path.name+'.next')
    with tmp.open('xb') as out: out.write(encoded(value)); out.flush(); os.fsync(out.fileno())
    os.chmod(tmp, 0o600); os.replace(tmp, path)
def stream_hash(path):
    h = hashlib.sha256(); size = 0
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1048576), b''): size += len(chunk); h.update(chunk)
    return size, h.hexdigest()
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
def unique_object(pairs):
    result = {}
    for key, value in pairs:
        need(key not in result, 'CATALOGUE_DUPLICATE_KEY'); result[key] = value
    return result
def receive_claude(state, packet, raw):
    schema_raw = read(packet/'PUBLIC_RESULT_SCHEMA.json')
    state['claude_validation'] = {'valid': False, 'schema_sha256': digest(schema_raw), 'result_sha256': digest(raw), 'result_bytes': len(raw)}
    value = json.loads(raw, object_pairs_hook=unique_object)
    need(catalogue_schema_matches(value, json.loads(schema_raw, object_pairs_hook=unique_object)), 'CLAUDE_RESULT_SCHEMA')
    state['claude'] = value
    state['claude_validation']['valid'] = True
def claude_validation_observation(raw, source):
    """Independently derive the child08 projections from complete private bytes."""
    canonical = lambda value:(json.dumps(value,sort_keys=True,ensure_ascii=True,allow_nan=False,
                                        separators=(',',':'))+'\n').encode('ascii')
    shape = identity = None
    try:
        need(type(raw) is bytes and len(raw) <= 32768,'JSON_BYTE_BOUND_REFUSED')
        def pairs(items):
            result = {}
            for key,value in items:
                need(key not in result,'JSON_DUPLICATE_KEY_UNRECEIVED'); result[key] = value
            return result
        def nonfinite(unused): raise Refusal('JSON_NONFINITE_UNRECEIVED')
        try:
            value = json.loads(raw.decode('utf-8'),object_pairs_hook=pairs,parse_constant=nonfinite)
        except (UnicodeError,ValueError,RecursionError):
            raise Refusal('JSON_PARSE_UNRECEIVED') from None
        queue = [(value,0)]; nodes = 0
        while queue:
            item,depth = queue.pop(); nodes += 1
            need(nodes <= 2048 and depth <= 12,'JSON_COMPLEXITY_UNRECEIVED')
            kind = type(item)
            if kind is dict:
                need(len(item) <= 128 and all(type(key) is str and len(key) <= 256 for key in item),
                     'JSON_SHAPE_UNRECEIVED')
                queue.extend((entry,depth+1) for entry in item.values())
            elif kind is list:
                need(len(item) <= 256,'JSON_SHAPE_UNRECEIVED')
                queue.extend((entry,depth+1) for entry in item)
            elif kind is str: need(len(item) <= 8192,'JSON_SHAPE_UNRECEIVED')
            elif kind is int: need(abs(item) <= 2**53,'JSON_SHAPE_UNRECEIVED')
            else: need(item is None or kind is bool,'JSON_SHAPE_UNRECEIVED')
        names = ('success','strict','target','manifest','contents','advice','gatingHooks','directory')
        kinds = {type(None):'NULL',bool:'BOOLEAN',int:'INTEGER',str:'STRING',list:'ARRAY',dict:'OBJECT'}
        fields = {}
        for name in names:
            present = type(value) is dict and name in value
            item = value[name] if present else None
            fields[name] = {'present':present,'type':kinds[type(item)] if present else 'ABSENT',
                            'count':len(item) if present and type(item) in (dict,list) else None}
        unknown = sorted(key for key in value if key not in names) if type(value) is dict else None
        shape = {'status':'PUBLIC_SAFE_TOP_LEVEL_SHAPE_ONLY','root_type':kinds[type(value)],
                 'root_count':len(value) if type(value) in (dict,list) else None,
                 'unknown_key_count':len(unknown) if unknown is not None else None,
                 'unknown_key_names_sha256':digest(canonical(unknown)) if unknown is not None else None,
                 'fields':fields}
        record = value if type(value) is dict else {}
        target = record.get('target')
        target_raw = None
        relation = 'NON_STRING_OR_ABSENT'
        if type(target) is str:
            try:
                target_raw = target.encode('utf-8')
            except UnicodeError:
                relation = 'NON_UTF8_STRING'
            else:
                exact_targets = {
                    str(source): 'EXACT_SOURCE_DIRECTORY',
                    str(source/'.claude-plugin/marketplace.json'): 'EXACT_SELECTED_MARKETPLACE_MANIFEST',
                    str(source/'.claude-plugin/plugin.json'): 'EXACT_PLUGIN_MANIFEST'}
                relation = exact_targets.get(target, 'OTHER_STRING')
        source_bound = relation in ('EXACT_SOURCE_DIRECTORY', 'EXACT_SELECTED_MARKETPLACE_MANIFEST')
        identity = {'status': 'PUBLIC_SAFE_IDENTITY_AND_VERDICT_ONLY',
                    'success_is_true': record.get('success') is True,
                    'strict_is_false': record.get('strict') is False,
                    'target_relation': relation,
                    'target_bytes': len(target_raw) if target_raw is not None else None,
                    'target_sha256': digest(target_raw) if target_raw is not None else None,
                    'target_is_source_bound': source_bound}
        required = set(names[:6])
        need(type(value) is dict and required <= set(value) <= set(names) and
             type(value['success']) is bool and type(value['strict']) is bool and
             type(value['target']) is str and (value['manifest'] is None or type(value['manifest']) is dict) and
             type(value['contents']) is list and type(value['advice']) is list and
             ('directory' not in value or value['directory'] is None or type(value['directory']) is dict),
             'VALIDATION_SHAPE_UNRECEIVED')
        need(identity['success_is_true'] and identity['strict_is_false'] and source_bound,
             'VALIDATION_IDENTITY_OR_VERDICT_REFUSED')
        counts = {'errors':0,'warnings':0,'notes':0}
        for item in value['contents']:
            need(type(item) is dict and {'file',*counts} <= set(item) <= {'file',*counts,'gatingHooks'} and
                 type(item['file']) is str and all(type(item[key]) is list and
                 all(type(message) is str for message in item[key]) for key in counts),
                 'VALIDATION_CONTENTS_UNRECEIVED')
            need(item.get('gatingHooks',[]) == [],'UNEXPECTED_GATING_HOOKS_REFUSED')
            for key in counts: counts[key] += len(item[key])
        need(value.get('gatingHooks',[]) == [],'UNEXPECTED_GATING_HOOKS_REFUSED')
        for item in value['advice']:
            need(type(item) is dict and set(item) == {'file','message','installLine'} and
                 all(type(item[key]) is str for key in item),'VALIDATION_ADVICE_UNRECEIVED')
        need(counts['errors'] == 0,'VALIDATION_CONTENT_ERRORS_REFUSED')
        directory_present = 'directory' in value
        projection = {'status':'DOCUMENTED_OUTER_VALIDATION_OBSERVED','success':True,'strict':False,
                      'target_matches_source_directory':relation == 'EXACT_SOURCE_DIRECTORY',
                      'target_is_source_bound':True,'target_relation':relation,'error_count':counts['errors'],
                      'warning_count':counts['warnings'],'note_count':counts['notes'],
                      'diagnostic_count_scope':'CONTENTS_ONLY_MANIFEST_OPAQUE',
                      'contents_count':len(value['contents']),'advice_count':len(value['advice']),
                      'manifest_semantics':'UNRECEIVED_OPAQUE_OBJECT','manifest_is_null':value['manifest'] is None,
                      'manifest_json_sha256':digest(canonical(value['manifest'])),
                      'directory_state':'ABSENT' if not directory_present else 'NULL' if value['directory'] is None else 'OPAQUE_OBJECT',
                      'directory_json_sha256':digest(canonical(value['directory'])) if directory_present else None,
                      'directory_semantics':'UNRECEIVED_OPAQUE_METADATA','directory_validation_received':False,
                      'native_five_skill_inventory_received':False}
        return shape,identity,projection,None
    except Refusal as exc:
        return shape,identity,None,str(exc)

def receive_claude_validation(state, source, output):
    value = state['claude']; rows = [row for row in value['commands'] if row['name'] == 'validate']
    need(len(rows) <= 1,'CLAUDE_VALIDATION_CAPTURE_POPULATION')
    flags = state['claude_validation']
    flags['validation_shape_private_binding_verified'] = False
    flags['validation_identity_private_binding_verified'] = False
    flags['validation_projection_private_binding_verified'] = False
    if not rows or rows[0]['streams_complete'] is not True or rows[0]['returncode'] != 0:
        need(value['validation_shape'] is None and value['validation_identity'] is None and value['validation'] is None,
             'CLAUDE_VALIDATION_WITHOUT_COMPLETE_CAPTURE')
        flags['private_validation_recognition'] = 'NOT_AVAILABLE'
        return
    row = rows[0]; raw = read(output/'private/claude-source-candidate/validate.stdout',32768)
    need(len(raw) == row['stdout_bytes'] and digest(raw) == row['stdout_sha256'],
         'CLAUDE_VALIDATION_PRIVATE_BYTES')
    shape,identity,projection,code = claude_validation_observation(raw,source)
    need(shape == value['validation_shape'] and identity == value['validation_identity'] and projection == value['validation'],
         'CLAUDE_VALIDATION_PRIVATE_PROJECTION')
    need(row['recognition_status'] == ('RECEIVED_JSON' if code is None else 'UNRECEIVED') and
         row['recognition_code'] == code,'CLAUDE_VALIDATION_PRIVATE_RECOGNITION')
    flags['validation_shape_private_binding_verified'] = True
    flags['validation_identity_private_binding_verified'] = True
    flags['validation_projection_private_binding_verified'] = True
    flags['private_validation_recognition'] = 'RECEIVED_OUTER_VERDICT' if code is None else 'REFUSAL_CONFIRMED'

def claude_success(value, uid, gid, receipt):
    if type(value) is not dict: return False
    flags = ('managed_policy_absent', 'currentness_before', 'currentness_after',
             'consumed_source_before', 'consumed_source_after', 'runtime_before',
             'runtime_after', 'git_admission_unchanged')
    if value.get('status') != 'OBSERVED_SOURCE_CANDIDATE_METADATA_WITH_DETAILS_UNRECEIVED' or not all(value.get(k) is True for k in flags): return False
    if value.get('schema') != 'dg17.claude.source-candidate.v1' or value.get('source_commit') != SOURCE or value.get('source_tree') != TREE: return False
    if value.get('archive_bytes') != ARCHIVE_BYTES or value.get('archive_sha256') != ARCHIVE_SHA or value.get('runtime_bytes') != BINARY_BYTES or value.get('runtime_sha256') != BINARY_SHA or value.get('runtime_release_tag_declared') != 'v2.1.318': return False
    if value.get('currentness_receipt_sha256') != digest((receipt+'\n').encode()) or value.get('failure') is not None or value.get('supplemental_failures') != []: return False
    false_flags = ('runtime_version_self_reported', 'native_five_skill_inventory_received',
                   'original_acceptance_awarded', 'persistent_installation_proven',
                   'model_inference_proven', 'prompt_independent_routing_proven')
    if not all(value.get(k) is False for k in false_flags) or value.get('parent_full_source_admission_required') is not True or value.get('independent_receiving') != 'NOT_PERFORMED': return False
    if value.get('expected_source_skills') != ['implementaudit','audit-state','audit-assess','audit-implement','audit-andon'] or value.get('fresh_context_count') != 3 or value.get('product_commands_started') != 3 or value.get('planned_commands') != ['validate','list','details'] or value.get('unstarted_commands') != []: return False
    offline = value.get('offline') or {}
    if type(offline) is not dict or offline.get('uid') != uid or offline.get('gid') != gid or offline.get('external_routes') != 0 or not all(offline.get(k) is True for k in ('verified','namespace_differs_from_parent','only_loopback','effective_permitted_ambient_capabilities_zero','no_new_privileges')): return False
    commands = value.get('commands')
    if type(commands) is not list or not all(type(row) is dict for row in commands) or [row.get('name') for row in commands] != ['validate','list','details']: return False
    for row in commands:
        if not all(row.get(k) is True for k in ('process_started','streams_complete','pidfd_acquired','private_streams_retained','owned_cleanup_echild','source_before','source_after','runtime_before','runtime_after','startup_before','startup_after')): return False
        if not all(row.get(k) is False for k in ('timeout','output_bound_exceeded','internal_failure','retention_failure')) or type(row.get('returncode')) is not int or row['returncode'] != 0: return False
        if row.get('recognition_code') is not None or row.get('recognition_status') != ('TEXT_UNRECEIVED' if row['name'] == 'details' else 'RECEIVED_JSON'): return False
        if any(type(row.get(k+'_bytes')) is not int or not 0 <= row[k+'_bytes'] <= 32768 or type(row.get(k+'_sha256')) is not str or re.fullmatch('[0-9a-f]{64}',row[k+'_sha256']) is None for k in ('stdout','stderr')): return False
        if row.get('stderr_present') is not (row['stderr_bytes'] > 0): return False
        if type(row.get('owned_reaped_status_count')) is not int or row['owned_reaped_status_count'] < 0 or type(row.get('owned_statuses_sha256')) is not str or re.fullmatch('[0-9a-f]{64}',row['owned_statuses_sha256']) is None: return False
    validation = value.get('validation') or {}
    if type(validation) is not dict or validation.get('status') != 'DOCUMENTED_OUTER_VALIDATION_OBSERVED' or validation.get('success') is not True or validation.get('strict') is not False or validation.get('target_is_source_bound') is not True or validation.get('error_count') != 0 or validation.get('manifest_semantics') != 'UNRECEIVED_OPAQUE_OBJECT' or validation.get('native_five_skill_inventory_received') is not False: return False
    if validation.get('directory_semantics') != 'UNRECEIVED_OPAQUE_METADATA' or validation.get('directory_validation_received') is not False: return False
    directory = validation.get('directory_state'); directory_sha = validation.get('directory_json_sha256')
    if directory not in ('ABSENT','NULL','OPAQUE_OBJECT') or (directory == 'ABSENT' and directory_sha is not None) or (directory != 'ABSENT' and (type(directory_sha) is not str or re.fullmatch('[0-9a-f]{64}',directory_sha) is None)): return False
    shape = value.get('validation_shape') or {}
    if type(shape) is not dict or shape.get('status') != 'PUBLIC_SAFE_TOP_LEVEL_SHAPE_ONLY' or shape.get('root_type') != 'OBJECT' or shape.get('unknown_key_count') != 0: return False
    identity = value.get('validation_identity') or {}
    if type(identity) is not dict or identity.get('status') != 'PUBLIC_SAFE_IDENTITY_AND_VERDICT_ONLY': return False
    if not all(identity.get(key) is True for key in ('success_is_true','strict_is_false','target_is_source_bound')): return False
    relation = identity.get('target_relation')
    if relation not in ('EXACT_SOURCE_DIRECTORY','EXACT_SELECTED_MARKETPLACE_MANIFEST') or validation.get('target_relation') != relation: return False
    if validation.get('target_matches_source_directory') is not (relation == 'EXACT_SOURCE_DIRECTORY'): return False
    if type(identity.get('target_bytes')) is not int or not 0 <= identity['target_bytes'] <= 32768: return False
    if type(identity.get('target_sha256')) is not str or re.fullmatch('[0-9a-f]{64}',identity['target_sha256']) is None: return False
    listed = value.get('plugin_list') or {}
    if type(listed) is not dict or listed.get('status') != 'EXACT_SESSION_CANDIDATE_OBSERVED' or listed.get('id') != 'implementaudit@inline' or listed.get('version') != '0.4.0' or listed.get('scope') != 'session' or listed.get('enabled') is not True or listed.get('effective_path_matches_source') is not True or listed.get('plugin_count') != 1 or listed.get('load_error_count') != 0 or listed.get('native_five_skill_inventory_received') is not False: return False
    details = value.get('details') or {}
    if details != {'status':'TEXT_FORMAT_UNRECEIVED','exit_zero_observed':True,'native_five_skill_inventory_received':False}: return False
    cleanup = value.get('cleanup') or {}
    if type(cleanup) is not dict or cleanup.get('private_seal_unchanged') is not True or cleanup.get('private_plaintext_policy') != 'RETAIN_UNTIL_HOST_TEARDOWN' or cleanup.get('host_teardown_observed') is not False: return False
    if type(cleanup.get('private_evidence_seal_sha256')) is not str or re.fullmatch('[0-9a-f]{64}',cleanup['private_evidence_seal_sha256']) is None: return False
    for key in ('after_close','after_seal'):
        if cleanup.get(key) != {'no_owned_children_listed':True,'wait_echild':True,'verified':True}: return False
    return True

def claude_capture_base_shape(row, name):
    keys = {'name','process_started','returncode','timeout','output_bound_exceeded',
            'pidfd_acquired','internal_failure','reason_code','stream_digest_scope',
            'streams_complete','stdout_bytes','stderr_bytes','stdout_sha256','stderr_sha256',
            'cleanup','private_streams_retained','retention_failure'}
    if type(row) is not dict or set(row) != keys or row['name'] != name: return False
    if not all(type(row[k]) is bool for k in ('process_started','timeout','output_bound_exceeded','pidfd_acquired','streams_complete','private_streams_retained','retention_failure')): return False
    if type(row['returncode']) is not int or row['internal_failure'] is not None or type(row['reason_code']) is not str or not 1 <= len(row['reason_code']) <= 96 or row['stream_digest_scope'] != 'CAPTURED_BYTES_ONLY': return False
    if any(type(row[k+'_bytes']) is not int or not 0 <= row[k+'_bytes'] <= 32768 or type(row[k+'_sha256']) is not str or re.fullmatch('[0-9a-f]{64}',row[k+'_sha256']) is None for k in ('stdout','stderr')): return False
    cleanup = row['cleanup']
    if type(cleanup) is not dict or set(cleanup) != {'echild','pidfd_signals','retained_status_count','retained_statuses_sha256','reaped_statuses','reaped_statuses_truncated'}: return False
    if type(cleanup['echild']) is not bool or type(cleanup['reaped_statuses_truncated']) is not bool or any(type(cleanup[k]) is not int or cleanup[k] < 0 for k in ('pidfd_signals','retained_status_count')): return False
    if type(cleanup['retained_statuses_sha256']) is not str or re.fullmatch('[0-9a-f]{64}',cleanup['retained_statuses_sha256']) is None: return False
    statuses = cleanup['reaped_statuses']; count = cleanup['retained_status_count']
    if type(statuses) is not list or len(statuses) != min(count,8) or cleanup['reaped_statuses_truncated'] is not (count > 8): return False
    if any(type(item) is not dict or set(item) != {'pid','returncode'} or type(item['pid']) is not int or item['pid'] <= 0 or type(item['returncode']) is not int for item in statuses): return False
    return True
def receive_claude_private(state, output, source):
    root = output/'private/claude-source-candidate'
    root_info = root.lstat()
    need(stat.S_ISDIR(root_info.st_mode) and root_info.st_uid == os.getuid() and not root_info.st_mode & 0o077 and root.resolve(strict=True) == root, 'CLAUDE_PRIVATE_ROOT')
    path = root/'PRIVATE_EVIDENCE_SEAL.json'; seal_info = path.lstat()
    need(stat.S_ISREG(seal_info.st_mode) and seal_info.st_uid == os.getuid() and not seal_info.st_mode & 0o077 and seal_info.st_nlink == 1, 'CLAUDE_PRIVATE_SEAL_OWNER')
    raw = read(path,262144)
    need(digest(raw) == state['claude']['cleanup']['private_evidence_seal_sha256'], 'CLAUDE_PRIVATE_SEAL_BINDING')
    declared = json.loads(raw, object_pairs_hook=unique_object)
    need(type(declared) is dict and set(declared) == {'schema','members'} and declared['schema'] == 'dg17.claude.private-seal.v1' and type(declared['members']) is list and len(declared['members']) <= 512, 'CLAUDE_PRIVATE_SEAL_SHAPE')
    population = []; pending = [root]
    try:
        while pending:
            directory = pending.pop()
            with os.scandir(directory) as stream:
                entries = list(stream)
            for entry in entries:
                item = directory/entry.name
                if item == path: continue
                mode = item.lstat().st_mode
                need(len(population) < 512 and len(item.relative_to(root).parts) <= 16, 'CLAUDE_PRIVATE_MEMBER_SHAPE')
                population.append(item)
                if stat.S_ISDIR(mode): pending.append(item)
    except OSError:
        raise Refusal('CLAUDE_PRIVATE_ENUMERATION_REFUSED') from None
    observed = []; total = 0
    for item in sorted(population, key=lambda value: value.relative_to(root).as_posix()):
        info = item.lstat()
        need(item.resolve(strict=True) == item and info.st_uid == os.getuid(), 'CLAUDE_PRIVATE_MEMBER_OWNER')
        if stat.S_ISREG(info.st_mode):
            need(info.st_nlink == 1 and not info.st_mode & 0o022 and info.st_size <= 8388608, 'CLAUDE_PRIVATE_MEMBER_SHAPE')
            size, sha = stream_hash(item); after = item.lstat()
            identity = lambda x:(x.st_dev,x.st_ino,x.st_mode,x.st_uid,x.st_gid,x.st_nlink,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
            need(identity(info) == identity(after) and size == info.st_size, 'CLAUDE_PRIVATE_MEMBER_CHANGED')
            total += size; need(total <= 33554432, 'CLAUDE_PRIVATE_TOTAL_BOUND')
            observed.append({'path':item.relative_to(root).as_posix(),'kind':'REGULAR','bytes':size,'sha256':sha})
        else:
            need(stat.S_ISDIR(info.st_mode) and not info.st_mode & 0o077, 'CLAUDE_PRIVATE_NONREGULAR_OR_MODE')
            observed.append({'path':item.relative_to(root).as_posix(),'kind':'DIRECTORY'})
    need(observed == declared['members'] and read(path,262144) == raw, 'CLAUDE_PRIVATE_SEAL_READBACK')
    state['claude_validation']['private_seal_verified_after_child_reaping'] = True
    state['claude_validation']['private_member_count'] = len(observed)
    for name in ('currentness-before','currentness-after'):
        need(read(root/(name+'.stdout'),32768) == (state['receipt']+'\n').encode() and read(root/(name+'.stderr'),32768) == b'', 'CLAUDE_EXACT_RECEIPT_BINDING')
    state['claude_validation']['same_receipt_private_readbacks_verified'] = True
    git_before = json.loads(read(root/'GIT_ADMISSION_BEFORE.json',262144), object_pairs_hook=unique_object)
    git_after = json.loads(read(root/'GIT_ADMISSION_AFTER.json',262144), object_pairs_hook=unique_object)
    need(type(git_before) is dict and set(git_before) == {'resolver','git','libexec','helpers','system_config','home','source_store'} and git_before == git_after, 'CLAUDE_GIT_PRIVATE_BOOKENDS')
    selected = git_before['git']; admitted = state['host']['tools']['git']
    need(type(selected) is dict and selected.get('resolved') == '/usr/bin/git' and selected.get('sha256') == admitted['sha256'] and selected.get('bytes') == admitted['bytes'], 'CLAUDE_GIT_HOST_BINDING')
    system = git_before['system_config']
    need(type(system) is dict and system.get('present') is True and system.get('bytes') == 0 and system.get('sha256') == digest(b''), 'CLAUDE_EMPTY_SYSTEM_CONFIG_BINDING')
    state['claude_validation']['git_private_bookends_verified'] = True
    state['claude_validation']['git_admission_identity_sha256'] = digest(encoded(git_before))
    records = json.loads(read(root/'COMMANDS.json',262144), object_pairs_hook=unique_object)
    names = ['currentness-before','validate','list','details','currentness-after']
    need(type(records) is list and len(records) == len(names) and all(type(row) is dict for row in records) and [row.get('name') for row in records] == names, 'CLAUDE_PRIVATE_COMMAND_POPULATION')
    products = []; flags = ('source_before','source_after','runtime_before','runtime_after','startup_before','startup_after')
    for name,row in zip(names,records):
        captures = json.loads(read(root/(name+'.capture.json'),65536), object_pairs_hook=unique_object)
        need(type(captures) is list and len(captures) == 1 and claude_capture_base_shape(captures[0],name), 'CLAUDE_PRIVATE_CAPTURE_REQUIRED_FIELDS')
        base = captures[0]; extras = {'recognition_status','recognition_code',*flags} if name in ('validate','list','details') else set()
        need(set(row) == set(base) | extras and claude_capture_base_shape({key:row[key] for key in base},name) and all(row[key] == value for key,value in base.items()), 'CLAUDE_PRIVATE_CAPTURE_BINDING')
        if extras:
            need(type(row['recognition_status']) is str and (row['recognition_code'] is None or type(row['recognition_code']) is str) and all(type(row[key]) is bool for key in flags), 'CLAUDE_PRIVATE_ENRICHMENT_SHAPE')
        for stream in ('stdout','stderr'):
            content = read(root/(name+'.'+stream),32768)
            need(row[stream+'_bytes'] == len(content) and row[stream+'_sha256'] == digest(content), 'CLAUDE_PRIVATE_STREAM_BINDING')
        need(row['process_started'] is True and row['returncode'] == 0 and row['streams_complete'] is True and row['timeout'] is False and row['output_bound_exceeded'] is False and row['pidfd_acquired'] is True and row['internal_failure'] is None and row['private_streams_retained'] is True and row['retention_failure'] is False and row['cleanup']['echild'] is True, 'CLAUDE_PRIVATE_CAPTURE_CUSTODY')
        if extras:
            public = {key:row[key] for key in ('name','returncode','stdout_bytes','stdout_sha256','stderr_bytes','stderr_sha256','recognition_status','recognition_code')}
            for key in ('process_started','streams_complete','timeout','output_bound_exceeded','pidfd_acquired','private_streams_retained','retention_failure',*flags):
                public[key] = row[key] is True
            public.update(internal_failure=row['internal_failure'] is not None,stderr_present=row['stderr_bytes'] > 0,
                          owned_cleanup_echild=row['cleanup']['echild'] is True,
                          owned_reaped_status_count=row['cleanup']['retained_status_count'],
                          owned_statuses_sha256=row['cleanup']['retained_statuses_sha256'])
            products.append(public)
    need(products == state['claude']['commands'], 'CLAUDE_PRIVATE_PUBLIC_COMMAND_BINDING')
    state['claude_validation']['private_public_stream_and_command_bindings_verified'] = True
    receive_claude_validation(state,source,output)
def utility(packet):
    raw = read(packet/'host_utility.py'); need(digest(raw) == UTILITY_SHA, 'UTILITY_PIN')
    module = types.ModuleType('dg17_retained_host_utility'); module.__file__ = str(packet/'host_utility.py')
    exec(compile(raw, module.__file__, 'exec'), module.__dict__)
    return module
def packet_check(packet):
    raw = read(packet/'INPUT_PINS.json'); need(digest(raw) == PINS_SHA, 'PACKET_UNSEALED_OR_CHANGED')
    pins = json.loads(raw)
    for name, row in pins.items():
        need(re.fullmatch(r'[A-Za-z0-9_.-]+', name) is not None, 'INPUT_PATH')
        content = read(packet/name)
        need(len(content) == row['bytes'] and digest(content) == row['sha256'], 'INPUT_PIN')
    return pins
def source_check(source, packet):
    raw = read(packet/'SOURCE_MANIFEST.json'); need(digest(raw) == MANIFEST_SHA, 'MANIFEST_PIN')
    manifest = json.loads(raw); need(manifest['expected_tree'] == TREE and manifest['file_count'] == 1755 and manifest['total_bytes'] == 165855954, 'MANIFEST_SUBJECT')
    members = manifest['members']; seen = set(); total = 0
    for row in members:
        path = source/row['path']; info = path.lstat()
        need(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and stat.S_IMODE(info.st_mode) == (0o755 if row['mode'] == '100755' else 0o644), 'SOURCE_FILE_SHAPE')
        size, sha = stream_hash(path)
        need(size == row['bytes'] and sha == row['sha256'], 'SOURCE_BYTES')
        seen.add(row['path']); total += size
    need(len(seen) == 1755 and total == 165855954, 'SOURCE_POPULATION')
    observed = set(); pending = [source]
    try:
        while pending:
            here = pending.pop()
            with os.scandir(here) as stream:
                entries = list(stream)
            for entry in entries:
                path = here/entry.name; mode = path.lstat().st_mode
                need(not stat.S_ISLNK(mode), 'SOURCE_DIRECTORY_ALIAS')
                if stat.S_ISDIR(mode):
                    if here == source and entry.name in ('.git', '.IMPLEMENTAUDIT'): continue
                    pending.append(path)
                else: observed.add(path.relative_to(source).as_posix())
    except OSError:
        raise Refusal('SOURCE_ENUMERATION_REFUSED') from None
    need(observed == seen, 'SOURCE_EXTRA_OR_MISSING_MEMBER')
    return {'commit': SOURCE, 'tree': TREE, 'parent': PARENT, 'files': len(seen), 'bytes': total, 'all_manifest_members_match': True}
def canonical_hashes(source, state):
    return {name: digest(read(source/state['run_root']/name)) for name in DOCS}
def command(state, output, u, label, argv, seconds=60):
    env_args = ['/usr/bin/env', 'HOME='+str(output/'home'), 'CODEX_HOME='+str(output/'home/codex'), 'TMPDIR='+str(output/'tmp')]
    state['active_command'] = label; save(output/'private/episode.json', state)
    try:
        try:
            rc, stdout, stderr = u.capture(label, env_args+argv, state['commands'], time.monotonic()+seconds+5, seconds=seconds)
        except BaseException as exc:
            captured = getattr(exc, 'captured', None)
            if captured is not None:
                for suffix in ('stdout', 'stderr'):
                    raw = captured[suffix]; need(type(raw) is bytes and len(raw) <= 32768, 'FAILURE_CAPTURE_SHAPE')
                    with (output/'private'/f'{len(state["commands"]):03d}-{label}.{suffix}').open('xb') as f: f.write(raw)
            raise
        for suffix, raw in (('stdout', stdout), ('stderr', stderr)):
            with (output/'private'/f'{len(state["commands"]):03d}-{label}.{suffix}').open('xb') as f: f.write(raw)
        state['active_command'] = None
        need(rc == 0, 'COMMAND_NONZERO_'+label)
        return stdout
    finally:
        save(output/'private/episode.json', state)
def owner(state, source, output, u, label, *args):
    need(Path.cwd() == source, 'OWNER_CWD')
    return command(state, output, u, label, ['/usr/bin/bash', str(source/CLAIM), *args])
def currentness_store_snapshot(source, packet):
    """Data-only post-resume Git-store admission; no Git or custody subprocess."""
    helper_raw = read(packet/'catalogue_probe.py')
    need(digest(helper_raw) == '9456e39cf3be3254b4c25c74716a1b87ba5f2accd6bf196db061e326c7a50277',
         'CURRENTNESS_STORE_HELPER_PIN')
    helper = types.ModuleType('dg17_parent_source_store_admission')
    helper.__file__ = str(packet/'catalogue_probe.py')
    exec(compile(helper_raw,helper.__file__,'exec'),helper.__dict__)
    guard = helper.source_store_guard(source)
    root = source/'.git'; rows = []; pending = [root]; directories = []; total = 0; files = 0
    def identity(info):
        return {'device':info.st_dev,'inode':info.st_ino,'mode':info.st_mode,
                'uid':info.st_uid,'gid':info.st_gid,'nlink':info.st_nlink,
                'bytes':info.st_size,'mtime_ns':info.st_mtime_ns,'ctime_ns':info.st_ctime_ns}
    root_identity = identity(root.lstat())
    try:
        while pending:
            directory = pending.pop(); before = directory.lstat()
            need(stat.S_ISDIR(before.st_mode) and before.st_uid == os.getuid() and
                 not before.st_mode & 0o022 and directory.resolve(strict=True) == directory,
                 'CURRENTNESS_STORE_DIRECTORY')
            directories.append((directory,identity(before)))
            with os.scandir(directory) as stream:
                entries = list(stream)
            need(identity(directory.lstat()) == identity(before), 'CURRENTNESS_STORE_CHANGED')
            for entry in entries:
                path = directory/entry.name; info = path.lstat(); relative = path.relative_to(root)
                need(len(rows) < 65536 and len(relative.parts) <= 32 and len(relative.as_posix()) <= 4096 and
                     info.st_uid == os.getuid() and not info.st_mode & 0o022 and
                     (stat.S_ISDIR(info.st_mode) or (stat.S_ISREG(info.st_mode) and info.st_nlink == 1)),
                     'CURRENTNESS_STORE_MEMBER')
                row = {'path':relative.as_posix(),'identity':identity(info)}
                if stat.S_ISDIR(info.st_mode):
                    row['kind'] = 'DIRECTORY'; pending.append(path)
                else:
                    need(0 <= info.st_size <= 536870912 and total+info.st_size <= 536870912,
                         'CURRENTNESS_STORE_BYTE_BOUND')
                    fd = os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
                    try:
                        need(identity(os.fstat(fd)) == identity(info), 'CURRENTNESS_STORE_OPEN_CHANGED')
                        hashed = hashlib.sha256(); size = 0
                        while True:
                            chunk = os.read(fd,1048576)
                            if not chunk: break
                            size += len(chunk); need(size <= info.st_size, 'CURRENTNESS_STORE_READ_BOUND')
                            hashed.update(chunk)
                        need(size == info.st_size and identity(os.fstat(fd)) == identity(info) and
                             identity(path.lstat()) == identity(info), 'CURRENTNESS_STORE_CHANGED')
                    finally: os.close(fd)
                    row.update(kind='REGULAR',sha256=hashed.hexdigest()); total += size; files += 1
                rows.append(row)
        need(all(identity(path.lstat()) == observed for path,observed in directories) and
             identity(root.lstat()) == root_identity, 'CURRENTNESS_STORE_CHANGED')
    except OSError:
        raise Refusal('CURRENTNESS_STORE_ENUMERATION_OR_READ_REFUSED') from None
    need(len(rows) == guard['entries_checked'] and
         any(row['path'] == 'config' and row.get('sha256') == guard['config_sha256'] for row in rows) and
         helper.source_store_guard(source) == guard, 'CURRENTNESS_STORE_GUARD_JOIN')
    population = encoded({'root':root_identity,'members':sorted(rows,key=lambda row:row['path'])})
    need(len(population) <= 33554432, 'CURRENTNESS_STORE_CENSUS_BOUND')
    return {'profile':'POST_RESUME_PHYSICAL_GIT_STORE_V1','guard':guard,'entries':len(rows),
            'regular_files':files,'bytes':total,'population_sha256':digest(population)}

def currentness_admission(state, source, output, u, label):
    """Data-only re-entry gate. Failure containment is distinct from cleanup."""
    expected_steps = {'initial-currentness':'require','before-runtime-acquisition':'runtime',
                      'after-runtime-acquisition':'runtime','before-claude':'claude',
                      'after-claude':'claude','before-receiving':'receive',
                      'after-receiving':'receive','final-currentness':None}
    need(label in expected_steps and state.get('failed') is False and state.get('failures') == [] and
         state.get('active_command') is None and state.get('active_step') == expected_steps[label],
         'CURRENTNESS_UNSOUND_PRIOR_STATE')
    need(type(state.get('commands')) is list and len(state['commands']) > 0 and all(type(row) is dict and
         row.get('process_started') is True and type(row.get('returncode')) is int and row['returncode'] == 0 and
         row.get('timeout') is False and row.get('output_bound_exceeded') is False and
         row.get('pidfd_acquired') is True and row.get('internal_failure') is None and
         row.get('streams_complete') is True and row.get('cleanup',{}).get('echild') is True
         for row in state['commands']), 'CURRENTNESS_PRIOR_CAPTURE_UNSOUND')
    late = label in ('after-claude','before-receiving','after-receiving','final-currentness')
    if label == 'final-currentness':
        need(state.get('completed') == list(STEPS) and state.get('bounded_receiving_complete') is True,
             'FINAL_CURRENTNESS_INCOMPLETE_RECEIVING')
    packet = Path(__file__).absolute().parent
    if late:
        need(any(row.get('name') == 'offline-claude-source-candidate' for row in state['commands']),
             'CURRENTNESS_NATIVE_CAPTURE_MISSING')
        need(state.get('claude_validation',{}).get('valid') is True and
             state['claude_validation'].get('captured_result_matches') is True and
             claude_success(state.get('claude',{}),os.getuid(),os.getgid(),state['receipt']),
             'CURRENTNESS_CHILD_ROUTE_UNSOUND')
        raw = read(output/'private/CLAUDE_RESULT.json',32768)
        need(digest(raw) == state['claude_validation']['result_sha256'] and
             json.loads(raw,object_pairs_hook=unique_object) == state['claude'], 'CURRENTNESS_CHILD_RESULT_CHANGED')
        receive_claude_private(state,output,source)
    observed = source_check(source,packet)
    need(observed == state.get('source_before') and
         canonical_hashes(source,state) == state.get('canonical_before'), 'CURRENTNESS_SOURCE_OR_STATE_DRIFT')
    store = currentness_store_snapshot(source,packet)
    if label == 'initial-currentness':
        need('currentness_store_before' not in state and state.get('currentness') == [] and
             state.get('completed') == list(STEPS[:STEPS.index('require')]), 'CURRENTNESS_STORE_BASELINE_SEQUENCE')
        state['currentness_store_before'] = store
    else:
        need(store == state.get('currentness_store_before'), 'CURRENTNESS_STORE_DRIFT')
    if late:
        received_git = json.loads(read(output/'private/claude-source-candidate/GIT_ADMISSION_BEFORE.json',262144),
                                  object_pairs_hook=unique_object)
        need(store['guard'] == received_git.get('source_store'), 'CURRENTNESS_RECEIVED_STORE_DRIFT')
    for name in ('bash','env','git','python3'):
        path,observed_tool = u.trusted(name)
        need(path is not None and observed_tool == state['host']['tools'][name], 'CURRENTNESS_TOOL_CHANGED')
    if 'runtime' in state:
        binary = output/'private/claude-input'; info = binary.lstat()
        need(binary.resolve(strict=True) == binary and stat.S_ISREG(info.st_mode) and
             info.st_uid == os.getuid() and info.st_nlink == 1 and stat.S_IMODE(info.st_mode) == 0o700 and
             stream_hash(binary) == (BINARY_BYTES,BINARY_SHA), 'CURRENTNESS_RUNTIME_CHANGED')
    need(u.children() == [], 'CURRENTNESS_OWNED_CHILDREN_REMAIN')
    try:
        os.waitpid(-1,os.WNOHANG|0x40000000)
    except ChildProcessError:
        return {'source_before_execution':True,'canonical_before_execution':True,
                'tools_before_execution':True,'runtime_before_execution':'runtime' in state,
                'child_private_binding_before_execution':late,'global_echild_before_execution':True,
                'git_store_before_execution':True,'git_store_baseline_matches':True,
                'git_store_entries':store['entries'],'git_store_bytes':store['bytes'],
                'git_store_population_sha256':store['population_sha256']}
    raise Refusal('CURRENTNESS_GLOBAL_ECHILD_UNCONFIRMED')

def current(state, source, output, u, label):
    need(state.get('receipt') is not None, 'CURRENTNESS_NOT_ESTABLISHED')
    admission = currentness_admission(state,source,output,u,label)
    raw = owner(state, source, output, u, label, '--require-current-continuity', state['controller'])
    need(raw == (state['receipt']+'\n').encode(), 'CURRENTNESS_RECEIPT_DIFFERS')
    state['currentness'].append({'role': label, 'receipt_sha256': digest(raw), 'same_source_cwd': True, 'verified': True, 'pre_execution_admission':admission})
    save(output/'private/episode.json', state)
def acquire_runtime(output):
    archive = output/'private/claude.tar.gz'; started = time.monotonic(); count = 0; h = hashlib.sha256()
    with urllib.request.urlopen(ARCHIVE_URL, timeout=30) as response, archive.open('xb') as stream:
        while True:
            chunk = response.read(1048576)
            if not chunk: break
            count += len(chunk); need(count <= ARCHIVE_BYTES and time.monotonic()-started < 180, 'ARCHIVE_BOUND')
            h.update(chunk); stream.write(chunk)
    need(count == ARCHIVE_BYTES and h.hexdigest() == ARCHIVE_SHA, 'ARCHIVE_PIN')
    binary = output/'private/claude-input'
    with tarfile.open(archive,'r:gz') as tar:
        members = tar.getmembers()
        need(len(members) == 1, 'ARCHIVE_MEMBERS')
        member = members[0]
        need(member.isreg() and member.name == 'claude' and member.size == BINARY_BYTES and member.mode == 0o755 and member.linkname == '' and member.pax_headers == {}, 'ARCHIVE_MEMBER_IDENTITY')
        count = 0
        with tar.extractfile(member) as inp, binary.open('xb') as out:
            while True:
                chunk = inp.read(1048576)
                if not chunk: break
                count += len(chunk); need(count <= BINARY_BYTES, 'ARCHIVE_BINARY_BOUND')
                out.write(chunk)
    need(stream_hash(binary) == (BINARY_BYTES,BINARY_SHA), 'BINARY_PIN')
    os.chmod(binary,0o700)
    info = binary.lstat()
    need(binary.resolve(strict=True) == binary and stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_uid == os.getuid() and info.st_gid == os.getgid() and stat.S_IMODE(info.st_mode) == 0o700, 'BINARY_OWNED_PHYSICAL_FILE')
    with binary.open('rb') as stream: header = stream.read(64)
    need(len(header) == 64 and header[:6] == b'\x7fELF\x02\x01' and int.from_bytes(header[18:20],'little') == 62, 'BINARY_ELF_X64')
    return {'archive_sha256':ARCHIVE_SHA,'archive_bytes':ARCHIVE_BYTES,'archive_member':'claude',
            'binary_sha256':BINARY_SHA,'binary_bytes':BINARY_BYTES,'release_tag_declared':'v2.1.318',
            'runtime_version_self_reported':False,'elf64_little_endian_x86_64':True,
            'input_retained_until_host_teardown':True,
            'parent_runtime_identity_horizon':'ACQUISITION_RECEIVE_AND_CURRENTNESS_ADMISSION'}

def mount_role():
    path = Path('/usr/bin/mount').resolve(strict=True); info = path.lstat()
    need(stat.S_ISREG(info.st_mode) and os.access(path, os.X_OK) and stat.S_IMODE(info.st_mode) in (0o755, 0o4755), 'MOUNT_ROLE_MODE')
    for node in (path, *path.parents):
        value = node.lstat(); need(value.st_uid == 0 and not value.st_mode & 0o022, 'MOUNT_ROLE_ANCESTRY')
    try: cap = os.getxattr(path, 'security.capability')
    except OSError as exc:
        need(exc.errno in (errno.ENODATA, errno.ENOTSUP), 'MOUNT_ROLE_CAPABILITY_UNKNOWN'); cap = b''
    need(not cap, 'MOUNT_ROLE_FILE_CAPABILITY')
    with path.open('rb') as stream: header = stream.read(64)
    need(len(header) == 64 and header[:6] == b'\x7fELF\x02\x01' and int.from_bytes(header[18:20], 'little') == 62, 'MOUNT_ROLE_ELF_X64')
    size, sha = stream_hash(path); after = path.lstat()
    identity = lambda x: (x.st_dev,x.st_ino,x.st_uid,x.st_gid,x.st_mode,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
    need(identity(info) == identity(after), 'MOUNT_ROLE_CHANGED')
    return {'canonical': str(path), 'bytes': size, 'sha256': sha, 'root_owned_nonwritable_chain': True,
            'mode': oct(stat.S_IMODE(info.st_mode)), 'file_capabilities': False, 'elf64_little_endian_x86_64': True,
            'device':info.st_dev,'inode':info.st_ino,'uid':info.st_uid,'gid':info.st_gid,
            'mtime_ns':info.st_mtime_ns,'ctime_ns':info.st_ctime_ns,
            'admitted_effect': 'ROOT_ONLY_FIXED_TMPFS_AND_CONFIG_BIND_IN_PRIVATE_NAMESPACE'}
def capsule_outside():
    rows = {}
    for name in ('/', '/usr', '/usr/local', '/etc', '/opt', '/usr/local/bin'):
        path = Path(name); info = path.lstat(); mode = stat.S_IMODE(info.st_mode)
        need(path.resolve(strict=True) == path and stat.S_ISDIR(info.st_mode) and info.st_uid == 0 and info.st_gid == 0, 'CAPSULE_OUTSIDE_PHYSICAL_ROOT')
        need(mode in (0o755, 0o777) if name in CAPSULE_TARGETS else not mode & 0o022, 'CAPSULE_OUTSIDE_MODE')
        rows[name] = {'device': info.st_dev, 'inode': info.st_ino, 'uid': info.st_uid, 'gid': info.st_gid,
                      'mode': mode, 'mtime_ns': info.st_mtime_ns, 'ctime_ns': info.st_ctime_ns}
    path = Path('/etc/gitconfig'); info = path.lstat()
    need(path.resolve(strict=True) == path and stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
         info.st_uid == 0 and info.st_gid == 0 and not info.st_mode & 0o022 and info.st_size <= 65536, 'CAPSULE_OUTSIDE_CONFIG_SHAPE')
    size, sha = stream_hash(path); after = path.lstat()
    identity = lambda x:(x.st_dev,x.st_ino,x.st_mode,x.st_uid,x.st_gid,x.st_nlink,x.st_size,x.st_mtime_ns,x.st_ctime_ns)
    need(identity(info) == identity(after) and size == info.st_size, 'CAPSULE_OUTSIDE_CONFIG_CHANGED')
    rows['/etc/gitconfig'] = {'kind':'REGULAR','device':info.st_dev,'inode':info.st_ino,
                            'uid':info.st_uid,'gid':info.st_gid,'mode':stat.S_IMODE(info.st_mode),
                            'nlink':info.st_nlink,'bytes':size,'sha256':sha,
                            'mtime_ns':info.st_mtime_ns,'ctime_ns':info.st_ctime_ns}
    return rows
def capsule_host_snapshot(state, u):
    tools = {}
    for name in ('bash', 'unshare', 'setpriv', 'python3', 'env', 'timeout'):
        path, observed = u.trusted(name)
        need(path is not None and observed == state['host']['tools'][name], 'CAPSULE_ROOT_UTILITY_DRIFT')
        info = Path(path).lstat()
        tools[name] = {'admission': observed, 'device': info.st_dev, 'inode': info.st_ino,
                       'mode': stat.S_IMODE(info.st_mode), 'uid': info.st_uid, 'gid': info.st_gid,
                       'mtime_ns': info.st_mtime_ns, 'ctime_ns': info.st_ctime_ns}
    observed = mount_role(); need(observed == state['host']['tools']['mount'], 'CAPSULE_MOUNT_TOOL_DRIFT')
    tools['mount'] = observed
    sudo = Path('/usr/bin/sudo').resolve(strict=True); info = sudo.lstat()
    for node in (sudo, *sudo.parents):
        item = node.lstat(); need(item.st_uid == 0 and not item.st_mode & 0o022, 'CAPSULE_SUDO_ANCESTRY')
    need(stat.S_ISREG(info.st_mode) and stat.S_IMODE(info.st_mode) == 0o4755 and
         stream_hash(sudo) == (state['host']['tools']['sudo']['bytes'], state['host']['tools']['sudo']['sha256']), 'CAPSULE_SUDO_DRIFT')
    try: cap = os.getxattr(sudo, 'security.capability')
    except OSError as exc:
        need(exc.errno in (errno.ENODATA,errno.ENOTSUP), 'CAPSULE_SUDO_CAPABILITY_UNKNOWN'); cap = b''
    need(not cap, 'CAPSULE_SUDO_FILE_CAPABILITY')
    tools['sudo'] = {'device': info.st_dev, 'inode': info.st_ino, 'mode': stat.S_IMODE(info.st_mode),
                     'uid': info.st_uid, 'gid': info.st_gid, 'mtime_ns': info.st_mtime_ns, 'ctime_ns': info.st_ctime_ns,
                     'sha256': state['host']['tools']['sudo']['sha256']}
    namespace = os.readlink('/proc/self/ns/mnt'); need(re.fullmatch(r'mnt:\[[0-9]+\]', namespace), 'PARENT_MOUNT_NAMESPACE')
    return {'outside': capsule_outside(), 'root_tools': tools, 'parent_mount_namespace': namespace}
def capsule_snapshot_valid(value, uid, gid, parent_namespace):
    keys = {'mount_namespace_sha256','namespace_distinct','private_propagation','mountinfo_sha256','mount_count',
            'uids','gids','groups','capabilities','no_new_privileges','mounts','gitconfig_source','source_target_same_file'}
    if type(value) is not dict or set(value) != keys: return False
    hexsha = lambda x:type(x) is str and re.fullmatch('[0-9a-f]{64}',x) is not None
    if not all(hexsha(value[k]) for k in ('mount_namespace_sha256','mountinfo_sha256')): return False
    if value['mount_namespace_sha256'] == digest(parent_namespace.encode()) or value['namespace_distinct'] is not True or value['private_propagation'] is not True: return False
    if type(value['mount_count']) is not int or not 4 <= value['mount_count'] <= 4096: return False
    for key,expected in (('uids',uid),('gids',gid)):
        if type(value[key]) is not list or len(value[key]) != 4 or not all(type(x) is int and x == expected for x in value[key]): return False
    if type(value['groups']) is not list or value['groups'] != []: return False
    caps = value['capabilities']
    if type(caps) is not dict or set(caps) != {'CapEff','CapPrm','CapAmb'} or not all(type(x) is int and x == 0 for x in caps.values()): return False
    if type(value['no_new_privileges']) is not int or value['no_new_privileges'] != 1: return False
    common = {'path','mount_id','parent_mount_id','mount_root','filesystem','mount_source','readonly','nodev','nosuid','noexec','size_bytes','mount_options_sha256','super_options_sha256'}
    directory = {'directory_uid','directory_gid','mode','directory','symlink','entries','device','inode'}
    filekeys = {'file_uid','file_gid','mode','regular','symlink','nlink','bytes','sha256','device','inode'}
    def file_ok(row):
        if row['regular'] is not True or row['symlink'] is not False or row['sha256'] != 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855': return False
        if not all(type(row[k]) is int and row[k] == n for k,n in (('file_uid',0),('file_gid',0),('mode',0o644),('nlink',1),('bytes',0))): return False
        return all(type(row[k]) is int and row[k] > 0 for k in ('device','inode'))
    rows = value['mounts']
    if type(rows) is not list or len(rows) != 3: return False
    for path,row in zip(CAPSULE_TARGETS,rows):
        expected_keys = common | (filekeys if path == '/etc/gitconfig' else directory)
        if type(row) is not dict or set(row) != expected_keys or row['path'] != path: return False
        root = '/dg17-empty-system-gitconfig' if path == '/etc/gitconfig' else '/'
        if row['filesystem'] != 'tmpfs' or row['mount_source'] != 'tmpfs' or row['mount_root'] != root: return False
        if not all(type(row[k]) is int and row[k] > 0 for k in ('mount_id','parent_mount_id')) or row['mount_id'] == row['parent_mount_id']: return False
        if not all(row[k] is True for k in ('readonly','nodev','nosuid','noexec')) or type(row['size_bytes']) is not int or row['size_bytes'] != 4096: return False
        if not all(hexsha(row[k]) for k in ('mount_options_sha256','super_options_sha256')): return False
        if path == '/etc/gitconfig':
            if not file_ok(row): return False
        else:
            if row['directory'] is not True or row['symlink'] is not False: return False
            for key,expected in (('directory_uid',0),('directory_gid',0),('mode',0o755),('entries',1 if path == '/opt' else 0)):
                if type(row[key]) is not int or row[key] != expected: return False
            if not all(type(row[k]) is int and row[k] > 0 for k in ('device','inode')): return False
    if len({row['mount_id'] for row in rows}) != 3: return False
    source = value['gitconfig_source']
    if type(source) is not dict or set(source) != filekeys | {'path'} or source['path'] != '/opt/dg17-empty-system-gitconfig' or not file_ok(source): return False
    if value['source_target_same_file'] is not True or source['device'] != rows[0]['device'] or any(source[k] != rows[2][k] for k in filekeys): return False
    if rows[0]['super_options_sha256'] != rows[2]['super_options_sha256']: return False
    return True
def capsule_recheck(state, u, phase):
    before = state['capsule_private']['host_before']; after = capsule_host_snapshot(state, u)
    equal = after == before
    state['capsule']['outside_rechecks'][phase] = {'unchanged': equal, 'identity_sha256': digest(encoded(after))}
    need(equal, 'CAPSULE_OUTSIDE_OR_UTILITY_CHANGED')
def receive_capsule(state, output):
    before_raw = read(output/'private/CAPSULE_ADMISSION.json', 16384)
    before = json.loads(before_raw, object_pairs_hook=unique_object)
    expected = state['capsule_private']['child_argv_sha256']; parent = state['capsule_private']['host_before']['parent_mount_namespace']
    need(type(before) is dict and set(before) == {'schema','child_argv_sha256','snapshot'} and
         before['schema'] == 'dg17.private-view-admission.v2' and before['child_argv_sha256'] == expected and
         capsule_snapshot_valid(before['snapshot'], os.getuid(), os.getgid(), parent), 'CAPSULE_BEFORE_PROOF')
    first_sha = digest(before_raw); previous = state['capsule'].get('admission_sha256')
    need(previous is None or previous == first_sha, 'CAPSULE_BEFORE_PROOF_CHANGED')
    state['capsule'].update(admission_sha256=first_sha, before=before['snapshot'], admitted_before=True)
    raw = read(output/'private/CAPSULE_RESULT.json', 16384); value = json.loads(raw, object_pairs_hook=unique_object)
    keys = {'schema','before_sha256','child_argv_sha256','before','after','child_returncode','failure'}
    need(type(value) is dict and set(value) == keys and value['schema'] == 'dg17.private-view-result.v2' and
         value['before_sha256'] == first_sha and value['child_argv_sha256'] == expected and value['before'] == before['snapshot'],
         'CAPSULE_RESULT_BINDING')
    after_ok = capsule_snapshot_valid(value['after'], os.getuid(), os.getgid(), parent)
    rc = value['child_returncode']
    need(type(rc) is int and -128 <= rc <= 255 and value['failure'] in (None,'CHILD_START_OR_WAIT_REFUSED','AFTER_VIEW_REFUSED'), 'CAPSULE_RESULT_VALUE')
    result_sha = digest(raw); previous = state['capsule'].get('result_sha256')
    need(previous is None or previous == result_sha, 'CAPSULE_RESULT_CHANGED')
    state['capsule'].update(result_sha256=result_sha, child_returncode=rc,
                            after=value['after'] if after_ok else None,
                            before_after_equal=after_ok and value['before'] == value['after'])
    need(after_ok and value['before'] == value['after'] and rc == 0 and value['failure'] is None, 'CAPSULE_AFTER_OR_CHILD_REFUSED')
    state['capsule']['status'] = 'OBSERVED_PRIVATE_VIEW_BEFORE_AFTER'
def prior_component(state, source, phase):
    expected = {'status':'PRIOR_COMPONENT_NOT_REPLAYED','reference':PRIOR_COMPONENT,'fresh_execution':False,
                'fresh_method_count':0,'native_windows_qualification':False,'new_original_awards':[],
                'source_closure':{'prepare':False,'receive':False,'final':False}}
    if 'predicates' not in state: state['predicates'] = expected
    row = state['predicates']; closure = row.get('source_closure')
    need(type(row) is dict and set(row) == set(expected) and type(closure) is dict and set(closure) == {'prepare','receive','final'} and
         all(type(x) is bool for x in closure.values()) and {k:v for k,v in row.items() if k!='source_closure'} == {k:v for k,v in expected.items() if k!='source_closure'}, 'PRIOR_COMPONENT_REFERENCE')
    closure[phase] = False
    need(SOURCE == PRIOR_COMPONENT['source_commit'] and TREE == PRIOR_COMPONENT['source_tree'] and
         state.get('source_before', {}).get('commit') == SOURCE and state['source_before'].get('tree') == TREE and
         state['source_before'].get('all_manifest_members_match') is True and
         digest(read(source/PRIOR_COMPONENT['test_path'])) == PRIOR_COMPONENT['test_source_sha256'], 'PRIOR_COMPONENT_SOURCE_CLOSURE')
    closure[phase] = True
def observe_capsule_failure(state, label, exc):
    state['failures'].append({'step':label,'exception_type':type(exc).__name__,
                              'message_sha256':digest(str(exc).encode()),'message_bytes':len(str(exc).encode())})
def launch_claude(state, source, output, packet, u):
    need(digest(CAPSULE_SCRIPT.encode()) == CAPSULE_SCRIPT_SHA and digest(CAPSULE_CODE.encode()) == CAPSULE_CODE_SHA, 'CAPSULE_LITERAL_PIN')
    host = capsule_host_snapshot(state, u)
    netns = os.readlink('/proc/self/ns/net')
    probe_args = ['--source',str(source),'--episode',str(output),'--binary',str(output/'private/claude-input'),
                  '--controller',state['controller'],'--receipt',state['receipt'],'--expected-uid',str(os.getuid()),
                  '--expected-gid',str(os.getgid()),'--parent-netns',netns]
    child_argv = ['/usr/bin/python3','-I','-S','-B',str(packet/'claude_probe.py'),*probe_args]
    state['capsule_private'] = {'host_before':host,'child_argv_sha256':digest(encoded(child_argv))}
    state['capsule'] = {'profile':'PRIVATE_READONLY_TMPFS_AND_EMPTY_SYSTEM_GITCONFIG_V2','status':'PREPARED_NOT_OBSERVED',
                        'qualification_scope':'CONSTRUCTED_PRIVATE_VIEW_NOT_STOCK_INSTALLATION_PATH_QUALIFICATION',
                        'targets':list(CAPSULE_TARGETS),'root_watchdog_seconds':165,'root_kill_after_seconds':5,
                        'root_script_sha256':CAPSULE_SCRIPT_SHA,'inline_code_sha256':CAPSULE_CODE_SHA,
                        'outside_before_sha256':digest(encoded(host)),'outside_rechecks':{},
                        'outside_system_gitconfig':host['outside']['/etc/gitconfig'],
                        'admitted_before':False,'before_after_equal':False,'admission_sha256':None,
                        'result_sha256':None,'before':None,'after':None,'child_returncode':None}
    save(output/'private/episode.json', state)
    argv = ['/usr/bin/sudo','-n','/usr/bin/timeout','--signal=TERM','--kill-after=5s','165s',
            '/usr/bin/unshare','--mount','--net','--propagation','private','--',
            '/usr/bin/bash','--noprofile','--norc','-c',CAPSULE_SCRIPT,'dg17-private-view',
            str(os.getuid()),str(os.getgid()),CAPSULE_CODE,
            str(output/'private/CAPSULE_ADMISSION.json'),str(output/'private/CAPSULE_RESULT.json'),
            host['parent_mount_namespace'],str(packet/'claude_probe.py'),*probe_args]
    failure = None
    try: command(state, output, u, 'offline-claude-source-candidate', argv, seconds=180)
    except BaseException as exc: failure = exc
    for label, action in (('capsule-outside-after',lambda:capsule_recheck(state,u,'after-command')),
                          ('capsule-proof-after',lambda:receive_capsule(state,output))):
        try: action()
        except BaseException as exc:
            observe_capsule_failure(state,label,exc)
            if failure is None: failure = exc
    try:
        if (output/'private/CLAUDE_RESULT.json').exists():
            receive_claude(state, packet, read(output/'private/CLAUDE_RESULT.json', 32768))
            record = state['commands'][-1]
            state['claude_validation']['captured_result_matches'] = False
            if record.get('name') == 'offline-claude-source-candidate' and record.get('streams_complete') is True:
                captured_raw = read(output/'private'/f'{len(state["commands"]):03d}-offline-claude-source-candidate.stdout',32768)
                need(captured_raw == read(output/'private/CLAUDE_RESULT.json',32768), 'CLAUDE_CAPTURE_DIFFERS')
                captured = json.loads(captured_raw, object_pairs_hook=unique_object)
                need(catalogue_schema_matches(captured, json.loads(read(packet/'PUBLIC_RESULT_SCHEMA.json'), object_pairs_hook=unique_object)) and captured == state['claude'], 'CLAUDE_CAPTURE_DIFFERS')
                state['claude_validation']['captured_result_matches'] = True
                receive_claude_validation(state,source,output)
    except BaseException as exc:
        observe_capsule_failure(state,'claude-receiving',exc)
        if failure is None: failure = exc
    if failure is not None: raise failure

def execute(step, state, source, output, packet, u):
    if step == 'prepare':
        need(os.getuid() == os.geteuid() > 0 and os.getgid() == os.getegid() > 0, 'ORDINARY_RUNNER_IDENTITY')
        need(not source.exists(), 'SOURCE_NOT_FRESH')
        for label, args in [('git-init', ['init', '--quiet', '--initial-branch=dg17-bootstrap', str(source)]), ('git-remote', ['-C', str(source), 'remote', 'add', 'origin', 'https://github.com/'+REPO+'.git']), ('git-fetch', ['-c', 'protocol.https.allow=always', '-C', str(source), 'fetch', '--quiet', '--depth=2', '--no-tags', 'origin', SOURCE]), ('git-checkout', ['-C', str(source), 'checkout', '--quiet', '--detach', SOURCE])]:
            command(state, output, u, label, ['/usr/bin/git', *args], seconds=180)
        os.chdir(source)
        head = command(state, output, u, 'head-identity', ['/usr/bin/git', 'rev-parse', 'HEAD', 'HEAD^{tree}'])
        need(head.decode().splitlines() == [SOURCE, TREE], 'HEAD_TREE')
        body = command(state, output, u, 'head-parent', ['/usr/bin/git', 'cat-file', '-p', 'HEAD'])
        need(body.split(b'\n\n', 1)[0].splitlines()[:2] == [('tree '+TREE).encode(), ('parent '+PARENT).encode()], 'PARENT')
        need(command(state, output, u, 'fresh-controller-refs', ['/usr/bin/git', 'for-each-ref', '--format=%(refname)', 'refs/implementaudit']) == b'', 'IMPORTED_CONTROLLER_REFS')
        need(not command(state, output, u, 'fresh-source-clean', ['/usr/bin/git', 'status', '--porcelain=v1', '--untracked-files=all']), 'SOURCE_DIRTY')
        tools = {}
        for name in ('python3', 'git', 'bash', 'env', 'unshare', 'setpriv', 'timeout'):
            path, observed = u.trusted(name); need(path is not None, 'HOST_TOOL_'+name); tools[name] = observed
        tools['mount'] = mount_role()
        sudo = Path('/usr/bin/sudo').resolve(strict=True)
        for path in (sudo, *sudo.parents):
            info = path.lstat(); need(info.st_uid == 0 and not info.st_mode & 0o022, 'SUDO_ANCESTRY')
        need(stat.S_IMODE(sudo.stat().st_mode) == 0o4755, 'SUDO_EXPECTED_SETUID_MODE')
        size, sha = stream_hash(sudo)
        tools['sudo'] = {'canonical': str(sudo), 'bytes': size, 'sha256': sha, 'root_owned_nonwritable_chain': True, 'mode': '04755', 'admitted_effect': 'ROOT_WATCHDOG_PRIVATE_MOUNT_AND_NETWORK_NAMESPACES_FIXED_TMPFS_AND_EMPTY_READONLY_GITCONFIG_BIND_THEN_DROP_UID_GID_NO_NEW_PRIVILEGES'}
        state['host'] = {'platform': platform.system(), 'kernel': platform.release(), 'python': list(sys.version_info[:3]), 'uid': os.getuid(), 'gid': os.getgid(), 'tools': tools, 'provider_calls': 0}
        state['source_before'] = source_check(source, packet)
        prior_component(state, source, 'prepare')
    elif step == 'initialize':
        raw = owner(state, source, output, u, 'fresh-claim', '--controller', state['controller'], 'dg17-isolated-native')
        run = raw.decode('ascii').strip(); need(re.fullmatch(r'\.IMPLEMENTAUDIT/runs/dg17-isolated-native-[A-Za-z0-9]{6}', run), 'RUN_ROOT')
        state['run_root'] = run; save(output/'private/episode.json', state)
        authored = json.loads(command(state, output, u, 'author-task', ['/usr/bin/python3', '-I', '-S', '-B', str(source/AUTHOR), '--repo', str(source), '--run-root', run, '--source', str(source), '--purpose', PURPOSE, '--next-action', NEXT]))
        need(set(authored) == set(DOCS) and authored == canonical_hashes(source, state), 'AUTHOR_READBACK')
        inspected = json.loads(owner(state, source, output, u, 'inspect-initialization', '--inspect-controller-initialization', state['controller'], '--run-root', run))
        init = inspected['initialization_token']; need(re.fullmatch('refs/implementaudit/controller-initializations/'+state['controller']+r'/[0-9a-f]{32}@[0-9a-f]{40}', init), 'PREPARATION_TOKEN')
        activated = json.loads(owner(state, source, output, u, 'activate-initialization', '--activate-controller', state['controller'], '--run-root', run, '--expected-initialization', init))
        need(activated.get('status') == 'BOUND_ELIGIBLE_FOR_NORMAL_CURRENTNESS' and activated.get('authority_ceiling') == 'ELIGIBLE_FOR_NORMAL_CURRENTNESS_ONLY', 'ACTIVATION')
        state['canonical_before'] = canonical_hashes(source, state)
    elif step == 'discover':
        parts = owner(state, source, output, u, 'discover', '--current-controller', state['controller']).decode().strip().split('\t')
        need(len(parts) == 4 and parts[0] == state['controller'] and Path(parts[1]) == source and Path(parts[2]) == source/state['run_root'], 'DISCOVERY')
    elif step == 'invalidate':
        owner(state, source, output, u, 'invalidate', '--invalidate-continuity', state['controller'], '--boundary', 'new-session', '--event', 'dg17-hosted-'+state['context']['run_id']+'-attempt-1')
    elif step in ('read-state', 'read-roadmap'):
        name = 'STATE.md' if step == 'read-state' else 'ROADMAP.md'; raw = read(source/state['run_root']/name)
        with (output/'private'/(step+'.read')).open('xb') as f: f.write(raw)
        state['reads'][name] = {'sha256': digest(raw), 'completed_host_action_ordinal': len(state['completed'])+1}
    elif step == 'resume':
        need(set(state['reads']) == {'STATE.md', 'ROADMAP.md'} and state['reads']['STATE.md']['completed_host_action_ordinal'] < state['reads']['ROADMAP.md']['completed_host_action_ordinal'], 'SEPARATE_READS')
        for name, row in state['reads'].items(): need(digest(read(source/state['run_root']/name)) == row['sha256'], 'READ_CHANGED')
        raw = owner(state, source, output, u, 'resume', '--resume-controller', state['controller'], '--boundary', 'new-session', '--epoch', 'G0001')
        receipt = raw.decode().strip(); need(re.fullmatch('refs/implementaudit/continuity-receipts/'+state['controller']+r'/G0001@[0-9a-f]{40}', receipt), 'RECEIPT')
        state['receipt'] = receipt
    elif step == 'verify':
        need(owner(state, source, output, u, 'verify', '--verify-resume-receipt', state['receipt']) == (state['receipt']+'\n').encode(), 'VERIFY')
    elif step == 'require': current(state, source, output, u, 'initial-currentness')
    elif step == 'runtime':
        current(state, source, output, u, 'before-runtime-acquisition'); state['runtime'] = acquire_runtime(output)
        current(state, source, output, u, 'after-runtime-acquisition')
    elif step == 'claude':
        current(state, source, output, u, 'before-claude')
        launch_claude(state, source, output, packet, u)
        current(state, source, output, u, 'after-claude')
    elif step == 'receive':
        current(state, source, output, u, 'before-receiving')
        prior_component(state, source, 'receive')
        receive_capsule(state, output)
        capsule_recheck(state, u, 'receive')
        need(state.get('claude_validation', {}).get('valid') is True and state['claude_validation'].get('captured_result_matches') is True and claude_success(state.get('claude', {}),os.getuid(),os.getgid(),state['receipt']), 'CLAUDE_NOT_RECEIVED')
        need(stream_hash(output/'private/claude-input') == (BINARY_BYTES,BINARY_SHA), 'RECEIVED_RUNTIME_CHANGED')
        receive_claude_private(state,output,source)
        state['claude_validation']['semantic_receiving_passed'] = True
        state['source_after'] = source_check(source, packet)
        need(state['source_after'] == state['source_before'] and canonical_hashes(source, state) == state['canonical_before'], 'FINAL_SOURCE_OR_STATE_DRIFT')
        current(state, source, output, u, 'after-receiving')
        state['bounded_receiving_complete'] = True
    else: raise Refusal('UNKNOWN_STEP')

def export(state, output, packet):
    if 'claude' in state:
        try:
            need(catalogue_schema_matches(state['claude'], json.loads(read(packet/'PUBLIC_RESULT_SCHEMA.json'))), 'CLAUDE_EXPORT_SCHEMA')
        except BaseException as exc:
            state.pop('claude', None); state.setdefault('claude_validation',{})['valid'] = False; state['failed'] = True; state['bounded_receiving_complete'] = False
            state['failures'].append({'step': 'export', 'exception_type': type(exc).__name__, 'message_sha256': digest(str(exc).encode()), 'message_bytes': len(str(exc).encode())})
    docs = {
        'RESULT.json': {'schema': 'dg17.isolated-claude-hosted-result.v1', 'context': state['context'], 'completed': state['completed'], 'failed': state['failed'], 'bounded_receiving_complete': state.get('bounded_receiving_complete', False), 'claude_validation': state.get('claude_validation'), 'local_currentness_transfer': False, 'original_acceptance': False, 'whole_T12': False, 'whole_T14': False, 'new_original_awards': []},
        'SOURCE.json': {'before': state.get('source_before'), 'after': state.get('source_after'), 'canonical_unchanged': state.get('canonical_unchanged')},
        'HOST.json': {'host': state.get('host'), 'runtime': state.get('runtime'), 'capsule': state.get('capsule')},
        'CURRENTNESS.json': {'checks': state['currentness'], 'reads': state['reads'], 'local_or_future_transfer': False},
        'PREDICATES.json': state.get('predicates', {'status':'PRIOR_COMPONENT_NOT_REPLAYED','reference':PRIOR_COMPONENT,'fresh_execution':False,'fresh_method_count':0,'native_windows_qualification':False,'new_original_awards':[],'source_closure':{'prepare':False,'receive':False,'final':False}}),
        'CLAUDE.json': state.get('claude', {'status': 'INVALID_RESULT_SCHEMA' if state.get('claude_validation',{}).get('valid') is False else 'NOT_COMPLETED'}),
        'CLEANUP.json': {'commands': state['commands'], 'active_step': state.get('active_step'), 'active_command': state.get('active_command'), 'all_recorded_commands_reaped': all(x.get('cleanup', {}).get('echild') is True for x in state['commands']), 'private_roots_retained_until_disposable_host_teardown': True},
        'FAILURE.json': {'failures': state['failures']}}
    files = {name: encoded(value) for name, value in docs.items()}; need(all(len(raw) <= 65536 for raw in files.values()) and sum(map(len, files.values())) <= 262144, 'PUBLIC_BOUND')
    files['ARTIFACT_MANIFEST.json'] = encoded({'schema': 'dg17.public-artifact-manifest.v1', 'members': [{'name': name, 'bytes': len(raw), 'sha256': digest(raw)} for name, raw in sorted(files.items())]})
    public = output/'public'; public.mkdir(exist_ok=True)
    for name, raw in files.items():
        with (public/name).open('xb') as f: f.write(raw)
    print(json.dumps({'status': 'FAILED_RETAINED' if state['failed'] else 'BOUNDED_OBSERVATIONS_RETAINED', 'completed_steps': len(state['completed']), 'original_acceptance': False}))

def main():
    p = argparse.ArgumentParser(); p.add_argument('--step', choices=(*STEPS, 'finalize'), required=True); p.add_argument('--output', required=True); p.add_argument('--source', required=True); a = p.parse_args()
    packet = Path(__file__).absolute().parent; output = Path(a.output).absolute(); source = Path(a.source).absolute(); env = os.environ
    need(env.get('GITHUB_ACTIONS') == 'true' and env.get('RUNNER_ENVIRONMENT') == 'github-hosted' and env.get('GITHUB_REPOSITORY') == REPO and env.get('GITHUB_REF') == 'refs/heads/'+BRANCH and env.get('GITHUB_EVENT_NAME') == 'push' and env.get('GITHUB_RUN_ATTEMPT') == '1', 'ACTUAL_HOSTED_EVENT_REQUIRED')
    run_id = env['GITHUB_RUN_ID']; need(re.fullmatch(r'[0-9]{1,20}', run_id), 'RUN_ID')
    need(re.fullmatch(r'[0-9a-f]{40}', env.get('GITHUB_SHA', '')), 'WORKFLOW_COMMIT')
    need(output == Path(env['RUNNER_TEMP'])/('dg17-episode-'+run_id+'-1') and source == Path(env['GITHUB_WORKSPACE'])/'dg17-qualified-source', 'OWNED_PATHS')
    packet_check(packet); u = utility(packet)
    lib = ctypes.CDLL(None, use_errno=True); need(lib.prctl(36, 1, 0, 0, 0) == 0, 'SUBREAPER')
    if a.step == 'prepare':
        output.mkdir(mode=0o700)
        for name in ('private', 'home', 'tmp'): (output/name).mkdir(mode=0o700)
        state = {'context': {'repository': REPO, 'branch': BRANCH, 'run_id': run_id, 'attempt': 1, 'workflow_commit': env['GITHUB_SHA']}, 'controller': 'dg17-hosted-'+run_id+'-a1', 'run_root': None, 'receipt': None, 'completed': [], 'commands': [], 'currentness': [], 'reads': {}, 'failed': False, 'failures': [], 'active_step': None, 'active_command': None}
    else:
        state = json.loads(read(output/'private/episode.json'))
        need(state['context']['run_id'] == run_id and state['context']['workflow_commit'] == env['GITHUB_SHA'], 'EPISODE_IDENTITY')
    if source.exists(): os.chdir(source)
    if a.step == 'finalize':
        if 'capsule_private' in state:
            try:
                capsule_recheck(state, u, 'final')
                receive_capsule(state, output)
            except BaseException as exc:
                state['failed'] = True; state['bounded_receiving_complete'] = False
                observe_capsule_failure(state, 'capsule-final', exc)
        if state.get('active_step') is not None or state.get('active_command') is not None or state['completed'] != list(STEPS) or not state.get('receipt') or not all(row.get('cleanup', {}).get('echild') is True for row in state['commands']) or state.get('bounded_receiving_complete') is not True:
            state['failed'] = True
            state['bounded_receiving_complete'] = False
            code = 'UNCERTAIN_PREDECESSOR' if state.get('active_step') is not None or state.get('active_command') is not None else 'INCOMPLETE_EPISODE'
            state['failures'].append({'step': 'finalize', 'exception_type': 'Refusal', 'message_sha256': digest(code.encode()), 'message_bytes': len(code)})
        if state.get('failed') is False and state.get('failures') == [] and state.get('bounded_receiving_complete') is True and state.get('completed') == list(STEPS) and state.get('receipt') and state.get('active_step') is None and state.get('active_command') is None and all(x.get('cleanup', {}).get('echild') is True for x in state['commands']):
            try:
                state['canonical_unchanged'] = canonical_hashes(source, state) == state['canonical_before']
                state['source_after'] = source_check(source, packet)
                need(state['canonical_unchanged'] and state['source_after'] == state['source_before'], 'FINAL_SOURCE_OR_STATE_DRIFT')
                prior_component(state, source, 'final')
                if state.get('bounded_receiving_complete') is True:
                    need(digest(read(output/'private/CLAUDE_RESULT.json',32768)) == state['claude_validation']['result_sha256'] and claude_success(state['claude'],os.getuid(),os.getgid(),state['receipt']), 'FINAL_CLAUDE_RESULT_DRIFT')
                    receive_claude_private(state,output,source)
                    state['claude_validation']['final_private_seal_verified'] = True
                current(state, source, output, u, 'final-currentness')
            except BaseException as exc:
                state['failed'] = True; state['bounded_receiving_complete'] = False; state['failures'].append({'step': 'finalize', 'exception_type': type(exc).__name__, 'message_sha256': digest(str(exc).encode()), 'message_bytes': len(str(exc).encode())})
        export(state, output, packet); save(output/'private/episode.json', state); return 1 if state['failed'] else 0
    need(not state['failed'] and state['active_step'] is None and state['active_command'] is None and state['completed'] == list(STEPS[:STEPS.index(a.step)]), 'STEP_SEQUENCE_OR_UNCERTAIN_PREDECESSOR')
    state['active_step'] = a.step; save(output/'private/episode.json', state)
    try:
        execute(a.step, state, source, output, packet, u)
        state['completed'].append(a.step); state['active_step'] = None
    except BaseException as exc:
        state['failed'] = True
        state['failures'].append({'step': a.step, 'exception_type': type(exc).__name__, 'message_sha256': digest(str(exc).encode()), 'message_bytes': len(str(exc).encode())})
        if state['active_command'] is None: state['active_step'] = None
    finally: save(output/'private/episode.json', state)
    print(json.dumps({'step': a.step, 'complete': a.step in state['completed'], 'failed': state['failed']}))
    return 1 if state['failed'] else 0

if __name__ == '__main__':
    try: sys.exit(main())
    except BaseException as exc:
        if isinstance(exc, SystemExit): raise
        print(json.dumps({'status': 'BOOTSTRAP_REFUSED', 'exception_type': type(exc).__name__, 'message_sha256': digest(str(exc).encode())})); sys.exit(1)
