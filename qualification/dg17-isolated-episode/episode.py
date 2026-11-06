#!/usr/bin/env python3
"""DG17-only hosted episode. No local execution route or original awards.

Maintained claim/activation/continuity owners supply all custody authority.
Command capture and child containment reuse the unchanged reviewed host utility.
"""
import argparse, ctypes, errno, hashlib, json, os, platform, re, stat, sys, tarfile, time, types, urllib.request, tomllib
from pathlib import Path

REPO = 'theislampill/IMPLEMENTAUDIT.md'
BRANCH = 'pro/dg17-isolated-episode-01-20261106'
SOURCE = '0d57929be5bd15682b4e9da2c0209d5dff307843'
TREE = 'ee316c27250ec422d35a1ea965182ebddf7a5da0'
PARENT = '481e529b691ed3d21169b07f376e357ae51f1f03'
MANIFEST_SHA = 'ed6a601d3a66997218195202cb5513363b5410b98489762324095a9030c261b4'
UTILITY_SHA = '429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c'
PINS_SHA = 'b52f5f088069bbac8f23884943bd355424fbd6c2f01abfef3153c0b53e8273b7'
CLAIM = 'skills/implementaudit/scripts/claim-run.sh'
AUTHOR = 'fixtures/controller-initialization/author_checkpoint.py'
DOCS = ('STATE.md', 'PROTOCOL.md', 'ROADMAP.md', 'THINKING.md', 'sidecars.md', 'tools.md', 'context.md', 'phases/phase-1.md')
STEPS = ('prepare', 'initialize', 'discover', 'invalidate', 'read-state', 'read-roadmap', 'resume', 'verify', 'require', 'runtime', 'activation', 'receive')
PUBLIC = ('RESULT.json', 'SOURCE.json', 'HOST.json', 'CURRENTNESS.json', 'PREDICATES.json', 'ACTIVATION.json', 'CLEANUP.json', 'FAILURE.json', 'ARTIFACT_MANIFEST.json')
PURPOSE = 'Observe exact local source-candidate plugin installation, enabling and cache-backed five-skill discovery through the separately admitted Codex version command and one app-server process with five fixed RPCs, under the inherited fresh controller, offline private view and unchanged cleanup owner. Preserve prior component receipts without replay or original awards.'
NEXT = 'Acquire and receive the pinned Codex runtime as data, run the retained bounded version command, then initialize/plugin-install/plugin-read/skills-list/hooks-list only. Independently receive the full frozen source image/cache, sole enabled config, exact protocol, private metadata and cleanup. No thread, turn, provider, model, config-read, authentication or lifecycle trigger request.'
ARCHIVE_URL = 'https://github.com/openai/codex/releases/download/rust-v0.167.0-alpha.4/codex-x86_64-unknown-linux-musl.tar.gz'
ARCHIVE_SHA = 'c4fd6fdeedf0ae78cc4d1d9dde4282c57a4a67c38319e3575b9a1e4d46c9ccc6'
ARCHIVE_BYTES = 123815356
BINARY_SHA = '57c94ea520df28beb76955316c5c48f672550fe42c6cff7003badb76e1ee10d8'
BINARY_BYTES = 324012616
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
def receive_activation(state, packet, raw):
    schema_raw = read(packet/'PUBLIC_RESULT_SCHEMA.json')
    state['activation_validation'] = {'valid': False, 'schema_sha256': digest(schema_raw), 'result_sha256': digest(raw), 'result_bytes': len(raw)}
    value = json.loads(raw, object_pairs_hook=unique_object)
    need(catalogue_schema_matches(value, json.loads(schema_raw, object_pairs_hook=unique_object)), 'ACTIVATION_RESULT_SCHEMA')
    state['activation'] = value
    state['activation_validation']['valid'] = True
def activation_success(value, uid, gid, receipt):
    if type(value) is not dict:return False
    flags=('source_identity_verified','source_after_verified','runtime_identity_verified','runtime_reported_version_matches',
           'native_process_started','currentness_before','currentness_after','executable_route_sound')
    if value.get('schema')!='dg17.t12.local-source-activation.v1' or value.get('status')!='OBSERVED_LOCAL_INSTALL_AND_CACHE_DISCOVERY' or not all(value.get(key) is True for key in flags):return False
    if value.get('source_commit')!=SOURCE or value.get('source_tree')!=TREE or value.get('runtime_version')!='0.167.0-alpha.4' or value.get('runtime_bytes')!=BINARY_BYTES or value.get('runtime_sha256')!=BINARY_SHA:return False
    if value.get('selector')!='.claude-plugin/marketplace.json:implementaudit:./' or value.get('plugin_id')!='implementaudit@implementaudit' or value.get('cache_relative_root')!='plugins/cache/implementaudit/implementaudit/0.4.0':return False
    if value.get('failure') is not None or value.get('supplemental_failures')!=[] or type(value.get('additional_failure_count')) is not int or value['additional_failure_count']!=0:return False
    ceilings=('original_acceptance_awarded','built_archive_binding_proven','canonical_git_marketplace_qualified',
              'model_inference_proven','prompt_independent_routing_proven','thread_content_loaded','lifecycle_trigger_delivery_proven')
    if not all(value.get(key) is False for key in ceilings) or value.get('independent_receiving')!='NOT_PERFORMED':return False
    methods=('initialize','plugin/install','plugin/read','skills/list','hooks/list')
    if value.get('calls')!=[{'method':method,'status':'OBSERVED'} for method in methods]:return False
    offline=value.get('offline') or {}
    if type(offline) is not dict or offline.get('uid')!=uid or offline.get('gid')!=gid or offline.get('external_routes')!=0 or not all(offline.get(key) is True for key in ('verified','namespace_differs_from_parent','only_loopback','effective_permitted_ambient_capabilities_zero','no_new_privileges')):return False
    git=value.get('git_startup_admission') or {}
    if type(git) is not dict or git.get('profile')!='LINUX_STANDARD_GIT_EMPTY_OR_SAFE_DIRECTORY_V1' or not all(git.get(key) is True for key in ('before_passed','after_passed','identities_unchanged','global_config_paths_absent','source_store_owned_physical','source_common_dir_matches','source_redirections_absent')):return False
    if git.get('system_config_state')!='EMPTY' or git.get('system_config_entries')!=0 or git.get('system_config_bytes')!=0 or git.get('system_config_sha256')!=digest(b'') or git.get('includes_expanded') is not False or git.get('selected_helper_count')!=3:return False
    if not git.get('before_identity_sha256') or git.get('before_identity_sha256')!=git.get('after_identity_sha256') or git.get('source_config_profile')!='OWNED_CHECKOUT_CORE_ORIGIN_V1' or git.get('source_git_config_entries') not in (6,7) or git.get('source_active_hook_count')!=0:return False
    if value.get('install')!={'status':'LOCAL_INSTALL_RESPONSE_OBSERVED','auth_policy':'ON_INSTALL','apps_needing_auth_count':0}:return False
    catalog=value.get('catalog') or {};effective=value.get('configured_skills') or {}
    names={'implementaudit','audit-state','audit-assess','audit-implement','audit-andon'}
    if catalog.get('status')!='SOURCE_CANDIDATE_INSTALLED_ENABLED' or catalog.get('id')!='implementaudit@implementaudit' or not all(catalog.get(key) is True for key in ('installed','enabled','source_image_path_bound','five_exact_skill_paths')) or any(catalog.get(key)!=0 for key in ('other_skill_count','declared_hook_count','declared_app_count','declared_mcp_count')):return False
    if effective.get('status')!='CACHE_BACKED_ENABLED_SKILL_METADATA' or effective.get('other_skills_attributed_to_candidate') is not False or effective.get('error_count')!=0 or effective.get('thread_content_loaded') is not False:return False
    for group,cached in ((catalog,False),(effective,True)):
        rows=group.get('skills')
        if type(rows) is not list or len(rows)!=5 or not all(type(row) is dict for row in rows) or {row.get('name') for row in rows}!=names:return False
        if not all(row.get('path')=='skills/'+row['name']+'/SKILL.md' and row.get('enabled') is True and row.get('exact_selected_root') is True and row.get('plugin_attribution_matches') is cached for row in rows):return False
    if value.get('configured_hooks')!={'status':'EMPTY_CONFIGURED_HOOK_METADATA','hook_count':0,'error_count':0,'warning_count':0,'loaded_thread_hooks_observed':False,'hook_delivery_exercised':False}:return False
    notifications=value.get('notifications') or {}
    if notifications.get('wire_complete') is not True or notifications.get('response_count')!=5 or any(notifications.get(key)!=0 for key in ('unknown_frames','server_requests','nonadmitted_outbound')):return False
    if type(notifications.get('remote_control_payload_sha256')) is not list or len(notifications['remote_control_payload_sha256'])!=notifications.get('remote_control_disabled_count'):return False
    payloads=value.get('payloads') or {}
    if payloads.get('declared_full_payload_bytes')!=331711908 or not all(payloads.get(key) is True for key in ('source_image_unchanged','cache_unchanged','after_seal_unchanged')):return False
    for before,after in (('source_image_before','source_image_after_close'),('native_cache_after_install','native_cache_after_close')):
        row=payloads.get(before) or {}
        if row!=payloads.get(after) or row.get('files')!=1755 or row.get('directories')!=418 or row.get('bytes')!=165855954 or row.get('manifest_sha256')!=MANIFEST_SHA or row.get('complete_exact_population') is not True:return False
    config=value.get('config') or {}
    if not all(config.get(key) is True for key in ('absent_before_install','unchanged','after_seal_unchanged')) or config.get('after_install')!=config.get('after_close'):return False
    installed=config.get('after_install') or {}
    if installed.get('profile')!='SOLE_LOCAL_PLUGIN_ENABLED_V1' or installed.get('enabled') is not True or installed.get('entry_count')!=1:return False
    metadata=value.get('metadata') or {}
    if metadata.get('unchanged') is not True or not metadata.get('seal_sha256') or metadata.get('per_file_bound')!=8388608 or metadata.get('aggregate_bound')!=33554432 or metadata.get('entry_bound')!=512:return False
    cleanup=value.get('cleanup') or {}
    if not all(cleanup.get(key) is True for key in ('close_returned','reader_joined','global_quiescence_after_close','global_quiescence_after_seal')) or type(cleanup.get('parent_returncode')) is not int or cleanup['parent_returncode']!=0 or cleanup.get('transport_remaining_owned_count')!=0 or cleanup.get('close_error_type') is not None or cleanup.get('containment') is not None:return False
    for key in ('after_close','after_seal'):
        row=cleanup.get(key) or {}
        if row.get('full_session_scope_available') is not True or row.get('launch_directory_empty') is not True or any(type(row.get(field)) is not int or row[field]!=0 for field in ('living_owned_processes','owned_zombies','uncertain_owned_candidates')):return False
    return True

def activation_capture_base_shape(row, name):
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
def activation_identity(info):
    return {'device':info.st_dev,'inode':info.st_ino,'mode':stat.S_IMODE(info.st_mode),
            'uid':info.st_uid,'gid':info.st_gid,'links':info.st_nlink,'bytes':info.st_size,
            'mtime_ns':info.st_mtime_ns,'ctime_ns':info.st_ctime_ns}

def activation_directory(path, private=False):
    info=path.lstat()
    need(stat.S_ISDIR(info.st_mode) and path.is_absolute() and path.resolve(strict=True)==path and
         info.st_uid==os.getuid() and info.st_gid==os.getgid() and not info.st_mode&0o022 and
         (not private or stat.S_IMODE(info.st_mode)==0o700),'ACTIVATION_DIRECTORY_SHAPE')
    return activation_identity(info)

def activation_file(path, limit, collect=False):
    before=path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_uid==os.getuid() and
         before.st_gid==os.getgid() and not before.st_mode&0o022 and
         0<=before.st_size<=limit,'ACTIVATION_FILE_SHAPE')
    fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW);total=0;hashed=hashlib.sha256();parts=[]
    try:
        need(activation_identity(os.fstat(fd))==activation_identity(before),'ACTIVATION_FILE_OPEN_CHANGED')
        while True:
            chunk=os.read(fd,1048576)
            if not chunk:break
            total+=len(chunk);need(total<=before.st_size,'ACTIVATION_FILE_READ_BOUND');hashed.update(chunk)
            if collect:parts.append(chunk)
        need(total==before.st_size and activation_identity(os.fstat(fd))==activation_identity(before) and
             activation_identity(path.lstat())==activation_identity(before),'ACTIVATION_FILE_CHANGED')
    finally:os.close(fd)
    return b''.join(parts),{'bytes':total,'sha256':hashed.hexdigest(),'identity':activation_identity(before)}

def activation_frozen_snapshot(root, manifest, source=False):
    expected={row['path']:row for row in manifest['members']}
    expected_dirs={str(parent) for name in expected for parent in Path(name).parents if parent!=Path('.')}
    need(len(expected)==1755 and len(expected_dirs)==418 and
         sum(row['bytes'] for row in expected.values())==165855954,'ACTIVATION_MANIFEST_POPULATION')
    root_row=activation_directory(root);population={};directories={};pending=[root]
    while pending:
        parent=pending.pop();observed=activation_directory(parent)
        directories[parent]=observed
        with os.scandir(parent) as stream:
            entries=list(stream)
        need(activation_identity(parent.lstat())==observed,'ACTIVATION_DIRECTORY_CHANGED')
        for entry in entries:
            item=parent/entry.name;info=item.lstat();relative=item.relative_to(root).as_posix()
            if source and parent==root and entry.name in ('.git','.IMPLEMENTAUDIT'):
                activation_directory(item);continue
            need(relative not in population and len(population)<2173,'ACTIVATION_PAYLOAD_POPULATION_BOUND')
            population[relative]=(item,info)
            if stat.S_ISDIR(info.st_mode):pending.append(item)
            else:need(stat.S_ISREG(info.st_mode),'ACTIVATION_PAYLOAD_NONREGULAR')
    files={name for name,(path,info) in population.items() if stat.S_ISREG(info.st_mode)}
    dirs=set(population)-files
    need(files==set(expected) and dirs==expected_dirs,'ACTIVATION_PAYLOAD_EXACT_POPULATION')
    rows=[]
    for name in sorted(population):
        item,info=population[name]
        need(info.st_uid==os.getuid() and info.st_gid==os.getgid(),'ACTIVATION_PAYLOAD_OWNER')
        if name in dirs:
            need(stat.S_IMODE(info.st_mode)==0o755,'ACTIVATION_PAYLOAD_DIRECTORY_MODE')
            rows.append({'path':name,'kind':'DIRECTORY','identity':activation_identity(info)})
        else:
            wanted=expected[name]
            need(stat.S_IMODE(info.st_mode)==(0o755 if wanted['mode']=='100755' else 0o644),
                 'ACTIVATION_PAYLOAD_MODE')
            unused,observed=activation_file(item,wanted['bytes'])
            need(observed['bytes']==wanted['bytes'] and observed['sha256']==wanted['sha256'] and
                 observed['identity']==activation_identity(info),'ACTIVATION_PAYLOAD_BYTES')
            rows.append({'path':name,'kind':'REGULAR',**observed})
    need(activation_identity(root.lstat())==root_row and
         all(activation_identity(path.lstat())==row for path,row in directories.items()),
         'ACTIVATION_PAYLOAD_DIRECTORY_BOOKEND')
    return {'root':root_row,'rows':rows}

def activation_store_join(snapshot, independent):
    need(type(snapshot) is dict and set(snapshot)=={'root','rows'} and type(snapshot['rows']) is list and
         len(snapshot['rows'])<=65536,'ACTIVATION_STORE_SNAPSHOT')
    fields={'device','inode','mode','uid','gid','links','bytes','mtime_ns','ctime_ns'}
    def converted(row, kind):
        need(type(row) is dict and set(row)==fields and all(type(value) is int for value in row.values()) and
             row['uid']==os.getuid() and row['gid']==os.getgid() and 0<=row['mode']<=0o7777 and
             not row['mode']&0o022,'ACTIVATION_STORE_IDENTITY')
        value={('nlink' if name=='links' else name):item for name,item in row.items()}
        value['mode']|=stat.S_IFDIR if kind=='DIRECTORY' else stat.S_IFREG
        return value
    rows=[];names=[];total=0;files=0
    for row in snapshot['rows']:
        need(type(row) is dict and row.get('kind') in ('REGULAR','DIRECTORY') and
             set(row)==({'path','kind','identity','sha256'} if row['kind']=='REGULAR' else {'path','kind','identity'}),
             'ACTIVATION_STORE_MEMBER_SHAPE')
        name=row['path'];path=Path(name)
        need(type(name) is str and path.as_posix()==name and not path.is_absolute() and
             len(path.parts)<=32 and len(name)<=4096 and all(x not in ('','..','.') for x in path.parts),
             'ACTIVATION_STORE_PATH')
        converted_row={'path':name,'kind':row['kind'],'identity':converted(row['identity'],row['kind'])}
        if row['kind']=='REGULAR':
            need(re.fullmatch('[0-9a-f]{64}',row['sha256']) is not None and row['identity']['links']==1,
                 'ACTIVATION_STORE_FILE')
            converted_row['sha256']=row['sha256'];files+=1;total+=row['identity']['bytes']
        rows.append(converted_row);names.append(name)
    need(names==sorted(set(names)) and 0<=total<=536870912 and
         len(rows)==independent['entries'] and files==independent['regular_files'] and total==independent['bytes'] and
         digest(encoded({'root':converted(snapshot['root'],'DIRECTORY'),'members':rows}))==independent['population_sha256'],
         'ACTIVATION_STORE_INDEPENDENT_BINDING')

def activation_metadata_snapshot(private, home, cache):
    rows=[];total=0
    for owner,root in (('evidence',private),('native-home',home)):
        activation_directory(root,True);pending=[root]
        while pending:
            parent=pending.pop();before=activation_identity(parent.lstat())
            with os.scandir(parent) as stream:
                entries=list(stream)
            need(activation_identity(parent.lstat())==before,'ACTIVATION_METADATA_DIRECTORY_CHANGED')
            for entry in entries:
                item=parent/entry.name
                if item==private/'PRIVATE_EVIDENCE_SEAL.json':continue
                info=item.lstat();name=owner+'/'+item.relative_to(root).as_posix()
                need(len(rows)<512 and len(Path(name).parts)<=18 and info.st_uid==os.getuid() and
                     info.st_gid==os.getgid() and (not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)) or
                     not info.st_mode&0o022),'ACTIVATION_METADATA_POPULATION')
                if item==cache:
                    activation_directory(item)
                    rows.append({'path':name,'kind':'EXACT_PAYLOAD_OWNER','identity':activation_identity(info)})
                elif stat.S_ISDIR(info.st_mode):
                    rows.append({'path':name,'kind':'DIRECTORY','identity':activation_identity(info)});pending.append(item)
                elif stat.S_ISREG(info.st_mode):
                    unused,observed=activation_file(item,8388608)
                    total+=observed['bytes'];need(total<=33554432,'ACTIVATION_METADATA_TOTAL')
                    rows.append({'path':name,'kind':'REGULAR',**observed})
                else:
                    rows.append({'path':name,'kind':'NONREGULAR','identity':activation_identity(info)})
    return sorted(rows,key=lambda row:row['path'])

def activation_expected_requests(image, neutral):
    return [
      {'id':1,'method':'initialize','params':{'clientInfo':{'name':'dg17_t12_activation','version':'1.0.0'},
                                          'capabilities':{'experimentalApi':True}}},
      {'method':'initialized'},
      {'id':2,'method':'plugin/install','params':{'pluginName':'implementaudit','marketplacePath':str(image/'.claude-plugin/marketplace.json')}},
      {'id':3,'method':'plugin/read','params':{'pluginName':'implementaudit','marketplacePath':str(image/'.claude-plugin/marketplace.json')}},
      {'id':4,'method':'skills/list','params':{'cwds':[str(neutral)],'forceReload':True}},
      {'id':5,'method':'hooks/list','params':{'cwds':[str(neutral)]}},
    ]

def activation_protocol_readback(raw, image, home, neutral, private, binary):
    need(len(raw)<=8388608,'ACTIVATION_PROTOCOL_BOUND')
    def reject_nonfinite(unused):raise Refusal('ACTIVATION_PROTOCOL_NONFINITE')
    def parse(data):return json.loads(data,object_pairs_hook=unique_object,parse_constant=reject_nonfinite)
    lines=raw.splitlines();need(1<=len(lines)<=64,'ACTIVATION_PROTOCOL_POPULATION')
    records=[parse(line) for line in lines];outbound=[];responses={};starts=[];ends=[];notifications=[]
    sent_ids=set();skills_changed=0;remote=[]
    expected=activation_expected_requests(image,neutral)
    for position,event in enumerate(records,1):
        need(type(event) is dict and set(event)=={'sequence','monotonic_ns','direction','value'} and
             type(event['sequence']) is int and event['sequence']==position and
             type(event['monotonic_ns']) is int and event['monotonic_ns']>=0,'ACTIVATION_PROTOCOL_EVENT')
        direction=event['direction'];value=event['value']
        if direction=='send':
            need(len(outbound)<len(expected) and value==expected[len(outbound)],'ACTIVATION_OUTBOUND_NOT_ADMITTED')
            outbound.append(value)
            if 'id' in value:sent_ids.add(value['id'])
        elif direction=='recv_raw':
            need(type(value) is str and len(value.encode())<=65536,'ACTIVATION_NATIVE_FRAME_BOUND')
            message=parse(value);need(type(message) is dict,'ACTIVATION_NATIVE_FRAME_SHAPE')
            if 'id' in message:
                need(set(message)=={'id','result'} and type(message['id']) is int and
                     message['id'] in sent_ids and message['id'] not in responses,'ACTIVATION_NATIVE_REQUEST_OR_RESPONSE')
                responses[message['id']]=message['result']
            else:
                need(set(message)=={'method','params'},'ACTIVATION_NOTIFICATION_SHAPE')
                method=message['method'];params=message['params']
                if method=='skills/changed':
                    need(type(params) is dict and params=={},'ACTIVATION_SKILLS_CHANGED_SHAPE');skills_changed+=1
                elif method=='remoteControl/status/changed':
                    need(type(params) is dict and {'status','installationId','serverName'}<=set(params)<=
                         {'status','installationId','serverName','environmentId'} and params['status']=='disabled' and
                         params.get('environmentId') is None and all(type(params[x]) is str and
                         1<=len(params[x].encode())<=256 for x in ('installationId','serverName')),
                         'ACTIVATION_REMOTE_CONTROL_NOT_DISABLED')
                    remote.append(digest(encoded(params)))
                else:raise Refusal('ACTIVATION_UNADMITTED_NOTIFICATION')
                need(skills_changed<=16 and len(remote)<=16,'ACTIVATION_NOTIFICATION_COUNT')
        elif direction=='lifecycle':
            need(type(value) is dict,'ACTIVATION_LIFECYCLE_SHAPE')
            if value.get('event')=='started':starts.append(value)
            elif value.get('event')=='terminated':ends.append(value)
            else:raise Refusal('ACTIVATION_LIFECYCLE_NOT_ADMITTED')
        else:raise Refusal('ACTIVATION_PROTOCOL_DIRECTION')
    need(outbound==expected and set(responses)=={1,2,3,4,5} and len(starts)==len(ends)==1 and
         records[0]['direction']==records[-1]['direction']=='lifecycle' and
         records[0]['value']==starts[0] and records[-1]['value']==ends[0],'ACTIVATION_PROTOCOL_COMPLETE_POPULATION')
    start=starts[0];end=ends[0]
    extra=['--strict-config','-c','features.plugins=true','-c','features.plugin_discovery_prefetch=false',
           '-c','features.remote_plugin=false','-c','cli_auth_credentials_store="ephemeral"',
           '-c','mcp_oauth_credentials_store="file"','-c','analytics.enabled=false','-c','feedback.enabled=false']
    need(set(start)=={'namespace_identity','event','pid','argv','cwd','home','environment_keys',
                     'original_binary','binary_sha256','launch_copy_is_hardlink'} and
         type(start['pid']) is int and start['pid']>0 and type(start['namespace_identity']) is dict and
         start['argv']==[str(private/'transport/owned-binary/codex'),'app-server','--listen','stdio://',*extra] and
         start['cwd']==str(neutral) and start['home']==str(home) and start['original_binary']==str(binary) and
         start['binary_sha256']==BINARY_SHA and start['launch_copy_is_hardlink'] is False and
         start['environment_keys']==['CODEX_HOME','HOME','LANG','PATH','PYTHONDONTWRITEBYTECODE','TMPDIR'],
         'ACTIVATION_NATIVE_LAUNCH_BINDING')
    need(set(end)=={'event','pid','returncode','reader_joined','escalations','residual_signal_attempts',
                   'remaining_owned_processes','launch_directory_empty'} and end['pid']==start['pid'] and
         type(end['returncode']) is int and end['returncode']==0 and end['reader_joined'] is True and
         end['remaining_owned_processes']==[] and end['launch_directory_empty'] is True and
         type(end['residual_signal_attempts']) is list and type(end['escalations']) is list and
         all(item in ('SIGTERM_OWN_PROCESS_GROUP','SIGKILL_OWN_PROCESS_GROUP','SIGTERM_OWN_RESIDUALS_PIDFD',
                      'SIGKILL_OWN_RESIDUALS_PIDFD') for item in end['escalations']),'ACTIVATION_NATIVE_CLOSE_BINDING')
    return {'skills_changed_count':skills_changed,'remote_control_disabled_count':len(remote),
            'remote_control_payload_sha256':remote,'unknown_frames':0,'server_requests':0,
            'nonadmitted_outbound':0,'response_count':5,'wire_complete':True},responses

def activation_rpc_projection(responses, image, home, cache, neutral, manifest):
    methods=('initialize','plugin/install','plugin/read','skills/list','hooks/list')
    need(type(responses) is dict and set(responses)==set(range(1,6)),'ACTIVATION_RPC_POPULATION')
    init=responses[1]
    need(type(init) is dict and set(init)=={'userAgent','codexHome','platformFamily','platformOs'} and
         init['codexHome']==str(home) and init['platformFamily']=='unix' and init['platformOs']=='linux' and
         type(init['userAgent']) is str and '0.167.0-alpha.4' in init['userAgent'] and
         len(init['userAgent'])<=1024,'ACTIVATION_INITIALIZE_BINDING')
    install=responses[2]
    need(type(install) is dict and set(install)=={'authPolicy','appsNeedingAuth'} and
         install['authPolicy']=='ON_INSTALL' and type(install['appsNeedingAuth']) is list and
         install['appsNeedingAuth']==[],'ACTIVATION_INSTALL_TYPED_RESPONSE')
    names=('implementaudit','audit-state','audit-assess','audit-implement','audit-andon')
    expected={'implementaudit:'+name:name for name in names}
    files={row['path']:row for row in manifest['members']}
    def selected(item, root, cached):
        need(type(item) is dict and type(item.get('name')) is str and type(item.get('enabled')) is bool,
             'ACTIVATION_SKILL_ROW')
        name=expected.get(item['name'])
        if name is None:return None
        relative='skills/'+name+'/SKILL.md'
        need(item.get('path')==str(root/relative) and item['enabled'] is True and
             (not cached or item.get('pluginId')=='implementaudit@implementaudit'),'ACTIVATION_SKILL_ROOT_OR_ATTRIBUTION')
        return {'name':name,'path':relative,'sha256':files[relative]['sha256'],'enabled':True,
                'exact_selected_root':True,'plugin_attribution_matches':cached}
    detail=responses[3]
    need(type(detail) is dict and set(detail)=={'plugin'} and type(detail['plugin']) is dict,'ACTIVATION_PLUGIN_READ')
    detail=detail['plugin'];summary=detail.get('summary')
    need(type(summary) is dict and summary.get('id')=='implementaudit@implementaudit' and
         summary.get('name')=='implementaudit' and summary.get('installed') is True and
         summary.get('enabled') is True and summary.get('authPolicy')=='ON_INSTALL' and
         summary.get('source')=={'type':'local','path':str(image)} and
         detail.get('marketplacePath')==str(image/'.claude-plugin/marketplace.json') and
         detail.get('marketplaceName')=='implementaudit','ACTIVATION_LOCAL_PLUGIN_STATE')
    need(all(type(detail.get(key)) is list and detail[key]==[] for key in ('apps','appTemplates','mcpServers','hooks')) and
         type(detail.get('skills')) is list and len(detail['skills'])==5,'ACTIVATION_PLUGIN_COMPONENTS')
    candidate=[selected(row,image,False) for row in detail['skills']]
    need(all(row is not None for row in candidate) and {row['name'] for row in candidate}==set(names),
         'ACTIVATION_CANDIDATE_FIVE_SKILLS')
    effective=responses[4]
    need(type(effective) is dict and set(effective)=={'data'} and type(effective['data']) is list and
         len(effective['data'])==1,'ACTIVATION_EFFECTIVE_SKILLS')
    effective=effective['data'][0]
    need(type(effective) is dict and set(effective)=={'cwd','skills','errors'} and effective['cwd']==str(neutral) and
         type(effective['skills']) is list and len(effective['skills'])<=128 and
         type(effective['errors']) is list and effective['errors']==[],'ACTIVATION_EFFECTIVE_SKILL_SCOPE')
    cached=[];other_count=0
    for item in effective['skills']:
        row=selected(item,cache,True)
        if row is None:
            need(item.get('pluginId')!='implementaudit@implementaudit' and type(item.get('path')) is str and
                 not Path(item['path']).is_relative_to(cache),'ACTIVATION_UNATTRIBUTED_CACHE_MEMBER')
            other_count+=1
        else:cached.append(row)
    need(len(cached)==5 and {row['name'] for row in cached}==set(names),'ACTIVATION_EFFECTIVE_FIVE_SKILLS')
    hooks=responses[5]
    need(type(hooks) is dict and set(hooks)=={'data'} and type(hooks['data']) is list and len(hooks['data'])==1,
         'ACTIVATION_HOOKS_RESPONSE')
    hooks=hooks['data'][0]
    need(type(hooks) is dict and set(hooks)=={'cwd','hooks','errors','warnings'} and hooks['cwd']==str(neutral) and
         all(type(hooks[key]) is list and hooks[key]==[] for key in ('hooks','errors','warnings')),
         'ACTIVATION_HOOK_METADATA_SCOPE')
    return {
      'install':{'status':'LOCAL_INSTALL_RESPONSE_OBSERVED','auth_policy':'ON_INSTALL','apps_needing_auth_count':0},
      'catalog':{'status':'SOURCE_CANDIDATE_INSTALLED_ENABLED','id':'implementaudit@implementaudit','installed':True,
                 'enabled':True,'source_image_path_bound':True,'five_exact_skill_paths':True,
                 'skills':sorted(candidate,key=lambda row:row['name']),'other_skill_count':0,
                 'declared_hook_count':0,'declared_app_count':0,'declared_mcp_count':0},
      'configured_skills':{'status':'CACHE_BACKED_ENABLED_SKILL_METADATA','skills':sorted(cached,key=lambda row:row['name']),
                           'other_skill_count':other_count,'other_skills_attributed_to_candidate':False,
                           'error_count':0,'thread_content_loaded':False},
      'configured_hooks':{'status':'EMPTY_CONFIGURED_HOOK_METADATA','hook_count':0,'error_count':0,'warning_count':0,
                          'loaded_thread_hooks_observed':False,'hook_delivery_exercised':False},
    }

def receive_activation_private(state, output, source):
    packet=Path(__file__).absolute().parent
    manifest_raw=read(packet/'SOURCE_MANIFEST.json')
    need(digest(manifest_raw)==MANIFEST_SHA,'ACTIVATION_PARENT_MANIFEST_PIN')
    manifest=json.loads(manifest_raw,object_pairs_hook=unique_object)
    private=output/'private/native-activation';payloads=output/'payloads'
    image=payloads/'source-image';home=payloads/'native-home';neutral=payloads/'neutral'
    cache=home/'plugins/cache/implementaudit/implementaudit/0.4.0'
    value=state['activation'];flags=state['activation_validation']
    activation_directory(payloads,True);activation_directory(private,True)
    with os.scandir(payloads) as stream:children=list(stream)
    need({entry.name for entry in children}=={'source-image','native-home','neutral'},'ACTIVATION_PAYLOAD_OWNERS')
    owners={}
    for name,path in (('source-image',image),('native-home',home),('neutral',neutral)):
        observed=activation_directory(path,name!='source-image')
        owners[name]={key:observed[key] for key in ('device','inode','mode','uid','gid')}
    with os.scandir(neutral) as stream:need(list(stream)==[],'ACTIVATION_NEUTRAL_NOT_EMPTY')
    def private_json(name,limit=8388608):
        raw,unused=activation_file(private/name,limit,True)
        return json.loads(raw,object_pairs_hook=unique_object)
    need(private_json('PAYLOAD_OWNERS_BEFORE.json')==owners,'ACTIVATION_OWNER_IDENTITY_CHANGED')
    for root in (source,image,neutral):
        for ancestor in (root,*root.parents):
            for name in ('config.toml','hooks.json','managed_config.toml','requirements.toml'):
                need(not os.path.lexists(ancestor/'.codex'/name),'ACTIVATION_UNREVIEWED_ANCESTOR_CONFIG')
    for name in ('config.toml','managed_config.toml','requirements.toml','hooks.json'):
        need(not os.path.lexists(Path('/etc/codex')/name),'ACTIVATION_UNREVIEWED_SYSTEM_CONFIG')
    for name in ('auth.json','auth.json.tmp','managed_config.toml','requirements.toml','hooks.json','.gitconfig','.config/git/config'):
        need(not os.path.lexists(home/name),'ACTIVATION_UNREVIEWED_NATIVE_HOME_LAYER')
    for relative in ('plugin.json','.mcp.json','.app.json','hooks/hooks.json','commands','.codex-plugin/migrated-command-skills'):
        need(not os.path.lexists(image/relative),'ACTIVATION_UNREVIEWED_PLUGIN_COMPONENT')
    observed_source=activation_frozen_snapshot(source,manifest,True)
    need(observed_source==private_json('SOURCE_BEFORE.json')==private_json('SOURCE_AFTER.json'),
         'ACTIVATION_FULL_SOURCE_PRIVATE_BOOKENDS')
    independent_store=currentness_store_snapshot(source,packet)
    need(independent_store==state['currentness_store_before'],'ACTIVATION_PARENT_STORE_BASELINE_DRIFT')
    store_before=private_json('SOURCE_STORE_BEFORE.json')
    need(store_before==private_json('SOURCE_STORE_AFTER.json'),'ACTIVATION_STORE_PRIVATE_BOOKENDS')
    activation_store_join(store_before,independent_store)
    image_now=activation_frozen_snapshot(image,manifest)
    cache_now=activation_frozen_snapshot(cache,manifest)
    need(image_now==private_json('IMAGE_BEFORE.json')==private_json('IMAGE_AFTER_CLOSE.json') and
         cache_now==private_json('CACHE_AFTER_INSTALL.json')==private_json('CACHE_AFTER_CLOSE.json'),
         'ACTIVATION_FULL_PAYLOAD_BOOKENDS')
    def summary(snapshot):
        regular=[row for row in snapshot['rows'] if row['kind']=='REGULAR']
        return {'files':len(regular),'directories':len(snapshot['rows'])-len(regular),
                'bytes':sum(row['bytes'] for row in regular),'manifest_sha256':MANIFEST_SHA,
                'physical_census_sha256':digest(encoded(snapshot)),'complete_exact_population':True}
    need(value['payloads']['source_image_before']==value['payloads']['source_image_after_close']==summary(image_now) and
         value['payloads']['native_cache_after_install']==value['payloads']['native_cache_after_close']==summary(cache_now),
         'ACTIVATION_PUBLIC_PAYLOAD_BINDING')
    config_raw,config_file=activation_file(home/'config.toml',4096,True)
    configuration=tomllib.loads(config_raw.decode('utf-8'))
    need(configuration=={'plugins':{'implementaudit@implementaudit':{'enabled':True}}} and
         configuration['plugins']['implementaudit@implementaudit']['enabled'] is True and
         config_file['identity']['mode'] in (0o600,0o644),'ACTIVATION_SOLE_ENABLED_CONFIGURATION')
    config={'profile':'SOLE_LOCAL_PLUGIN_ENABLED_V1','bytes':config_file['bytes'],'sha256':config_file['sha256'],
            'identity':config_file['identity'],'enabled':True,'entry_count':1}
    need(config==private_json('CONFIG_AFTER_INSTALL.json')==private_json('CONFIG_AFTER_CLOSE.json') and
         value['config']['after_install']==value['config']['after_close']=={key:item for key,item in config.items() if key!='identity'},
         'ACTIVATION_CONFIG_PRIVATE_PUBLIC_BINDING')
    flags['full_source_image_cache_config_independently_received']=True
    git_before=private_json('GIT_ADMISSION_BEFORE.json');git_after=private_json('GIT_ADMISSION_AFTER.json')
    need(type(git_before) is dict and set(git_before)=={'resolver','git','libexec','helpers','system_config','home','source_store'} and
         git_before==git_after and git_before['source_store']==independent_store['guard'],
         'ACTIVATION_GIT_PRIVATE_BOOKENDS')
    selected=git_before['git'];admitted=state['host']['tools']['git'];system=git_before['system_config']
    need(selected.get('resolved')=='/usr/bin/git' and selected.get('sha256')==admitted['sha256'] and
         selected.get('bytes')==admitted['bytes'] and system.get('present') is True and
         system.get('bytes')==0 and system.get('sha256')==digest(b'') and
         value['git_startup_admission']['before_identity_sha256']==value['git_startup_admission']['after_identity_sha256']==digest(json.dumps(git_before,sort_keys=True,separators=(',',':')).encode()),
         'ACTIVATION_GIT_PARENT_BINDING')
    records=private_json('GATE_COMMANDS.json')
    need(type(records) is list and len(records)==2,'ACTIVATION_GATE_POPULATION')
    for name,row in zip(('gate-before','gate-after'),records):
        need(activation_capture_base_shape(row,name),'ACTIVATION_GATE_CAPTURE_FIELDS')
        captured=private_json(name+'.capture.json',65536)
        need(type(captured) is list and captured==[row] and
             row['process_started'] is True and type(row['returncode']) is int and row['returncode']==0 and
             row['streams_complete'] is True and row['timeout'] is False and row['output_bound_exceeded'] is False and
             row['pidfd_acquired'] is True and row['internal_failure'] is None and
             row['private_streams_retained'] is True and row['retention_failure'] is False and
             row['cleanup']['echild'] is True,'ACTIVATION_GATE_CUSTODY')
        stdout,unused=activation_file(private/(name+'.stdout'),32768,True)
        stderr,unused=activation_file(private/(name+'.stderr'),32768,True)
        need(stdout==(state['receipt']+'\n').encode() and stderr==b'' and
             row['stdout_bytes']==len(stdout) and row['stdout_sha256']==digest(stdout) and
             row['stderr_bytes']==0 and row['stderr_sha256']==digest(b''),'ACTIVATION_GATE_RECEIPT_BINDING')
    flags['same_receipt_private_readbacks_verified']=True
    protocol_raw,unused=activation_file(private/'transport/protocol.jsonl',8388608,True)
    notifications,responses=activation_protocol_readback(protocol_raw,image,home,neutral,private,output/'private/codex-input')
    expected=activation_rpc_projection(responses,image,home,cache,neutral,manifest)
    need(all(value[name]==projection for name,projection in expected.items()) and value['notifications']==notifications,
         'ACTIVATION_RPC_PUBLIC_PROJECTION')
    methods=('initialize','plugin/install','plugin/read','skills/list','hooks/list')
    need(private_json('RPC_RESULTS.json')=={method:responses[index+1] for index,method in enumerate(methods)},
         'ACTIVATION_RPC_MEMORY_WIRE_BINDING')
    effects=private_json('transport/NATIVE_EXECUTABLE_EFFECTS.json')
    launch=private/'transport/owned-binary'
    with os.scandir(launch) as stream:need(list(stream)==[],'ACTIVATION_LAUNCH_DIRECTORY_NOT_EMPTY')
    need(effects.get('original_binary')==str(output/'private/codex-input') and effects.get('original_sha256')==BINARY_SHA and
         effects.get('launch_root')==str(launch) and effects.get('remaining_owned_processes')==[] and
         effects.get('deleted_regular_files')==['codex'] and effects.get('files_after_cleanup')==[] and
         effects.get('files_after_process_exit')==[{'path':'codex','mode':0o755,'bytes':BINARY_BYTES,'links':1,'kind':'file','sha256':BINARY_SHA}],
         'ACTIVATION_UNCHANGED_CLEANUP_OWNER_BINDING')
    before_resources=private_json('transport/RESOURCE_BEFORE.json')
    need(before_resources.get('roots')=={str(home):[],str(private/'transport/owned-tmp'):[]},
         'ACTIVATION_NATIVE_HOME_TMP_NOT_FRESH')
    flags['exact_five_rpc_and_cleanup_owner_received']=True
    seal_path=private/'PRIVATE_EVIDENCE_SEAL.json';seal_raw,seal_file=activation_file(seal_path,8388608,True)
    need(seal_file['sha256']==value['metadata']['seal_sha256'],'ACTIVATION_METADATA_SEAL_BINDING')
    declared=json.loads(seal_raw,object_pairs_hook=unique_object)
    need(type(declared) is dict and set(declared)=={'schema','files','separate_payload_owners','full_payload_manifest_sha256'} and
         declared['schema']=='dg17.activation.small-evidence-seal.v1' and
         declared['separate_payload_owners']==['source-image','plugins/cache/implementaudit/implementaudit/0.4.0'] and
         declared['full_payload_manifest_sha256']==MANIFEST_SHA,'ACTIVATION_METADATA_SEAL_SHAPE')
    observed=activation_metadata_snapshot(private,home,cache)
    regular=[row for row in observed if row['kind']=='REGULAR'];total=sum(row['bytes'] for row in regular)+len(seal_raw)
    need(observed==declared['files'] and total<=33554432 and value['metadata']['files']==len(regular) and
         value['metadata']['entries']==len(observed) and value['metadata']['bytes']==total and
         activation_file(seal_path,8388608,True)[0]==seal_raw,'ACTIVATION_METADATA_INDEPENDENT_CENSUS')
    flags['private_seal_verified_after_child_reaping']=True
    flags['private_member_count']=len(observed)
    flags['payload_files_independently_received']=3510
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
                      'after-runtime-acquisition':'runtime','before-activation':'activation',
                      'after-activation':'activation','before-receiving':'receive',
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
    late = label in ('after-activation','before-receiving','after-receiving','final-currentness')
    if label == 'final-currentness':
        need(state.get('completed') == list(STEPS) and state.get('bounded_receiving_complete') is True,
             'FINAL_CURRENTNESS_INCOMPLETE_RECEIVING')
    packet = Path(__file__).absolute().parent
    if late:
        need(any(row.get('name') == 'offline-native-activation' for row in state['commands']),
             'CURRENTNESS_NATIVE_CAPTURE_MISSING')
        need(state.get('activation_validation',{}).get('valid') is True and
             state['activation_validation'].get('captured_result_matches') is True and
             activation_success(state.get('activation',{}),os.getuid(),os.getgid(),state['receipt']),
             'CURRENTNESS_CHILD_ROUTE_UNSOUND')
        raw = read(output/'private/ACTIVATION_RESULT.json',32768)
        need(digest(raw) == state['activation_validation']['result_sha256'] and
             json.loads(raw,object_pairs_hook=unique_object) == state['activation'], 'CURRENTNESS_CHILD_RESULT_CHANGED')
        receive_activation_private(state,output,source)
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
        received_git = json.loads(read(output/'private/native-activation/GIT_ADMISSION_BEFORE.json',262144),
                                  object_pairs_hook=unique_object)
        need(store['guard'] == received_git.get('source_store'), 'CURRENTNESS_RECEIVED_STORE_DRIFT')
    for name in ('bash','env','git','python3'):
        path,observed_tool = u.trusted(name)
        need(path is not None and observed_tool == state['host']['tools'][name], 'CURRENTNESS_TOOL_CHANGED')
    if 'runtime' in state:
        binary = output/'private/codex-input'; info = binary.lstat()
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
    archive = output/'private/codex.tar.gz'; started = time.monotonic(); count = 0; h = hashlib.sha256()
    with urllib.request.urlopen(ARCHIVE_URL, timeout=30) as response, archive.open('xb') as f:
        while True:
            chunk = response.read(1048576)
            if not chunk: break
            count += len(chunk); need(count <= ARCHIVE_BYTES and time.monotonic()-started < 180, 'ARCHIVE_BOUND')
            h.update(chunk); f.write(chunk)
    need(count == ARCHIVE_BYTES and h.hexdigest() == ARCHIVE_SHA, 'ARCHIVE_PIN')
    binary = output/'private/codex-input'
    with tarfile.open(archive, 'r:gz') as tar:
        members = tar.getmembers()
        need(len(members) == 1 and members[0].isreg() and members[0].name == 'codex-x86_64-unknown-linux-musl' and members[0].size == BINARY_BYTES, 'ARCHIVE_MEMBERS')
        with tar.extractfile(members[0]) as inp, binary.open('xb') as out:
            while True:
                chunk = inp.read(1048576)
                if not chunk: break
                out.write(chunk)
    need(stream_hash(binary) == (BINARY_BYTES, BINARY_SHA), 'BINARY_PIN')
    os.chmod(binary, 0o700)
    return {'archive_sha256': ARCHIVE_SHA, 'archive_bytes': ARCHIVE_BYTES, 'binary_sha256': BINARY_SHA, 'binary_bytes': BINARY_BYTES, 'version_subject': 'codex-cli 0.167.0-alpha.4', 'input_retained_until_host_teardown': True}

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
def launch_activation(state, source, output, packet, u):
    need(digest(CAPSULE_SCRIPT.encode()) == CAPSULE_SCRIPT_SHA and digest(CAPSULE_CODE.encode()) == CAPSULE_CODE_SHA, 'CAPSULE_LITERAL_PIN')
    host = capsule_host_snapshot(state, u)
    netns = os.readlink('/proc/self/ns/net')
    probe_args = ['--source',str(source),'--episode',str(output),'--binary',str(output/'private/codex-input'),
                  '--controller',state['controller'],'--receipt',state['receipt'],'--expected-uid',str(os.getuid()),
                  '--expected-gid',str(os.getgid()),'--parent-netns',netns]
    child_argv = ['/usr/bin/python3','-I','-S','-B',str(packet/'activation_probe.py'),*probe_args]
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
            host['parent_mount_namespace'],str(packet/'activation_probe.py'),*probe_args]
    failure = None
    try: command(state, output, u, 'offline-native-activation', argv, seconds=180)
    except BaseException as exc: failure = exc
    for label, action in (('capsule-outside-after',lambda:capsule_recheck(state,u,'after-command')),
                          ('capsule-proof-after',lambda:receive_capsule(state,output))):
        try: action()
        except BaseException as exc:
            observe_capsule_failure(state,label,exc)
            if failure is None: failure = exc
    try:
        if (output/'private/ACTIVATION_RESULT.json').exists():
            receive_activation(state, packet, read(output/'private/ACTIVATION_RESULT.json', 32768))
            record = state['commands'][-1]
            state['activation_validation']['captured_result_matches'] = False
            if record.get('name') == 'offline-native-activation' and record.get('streams_complete') is True:
                captured_raw = read(output/'private'/f'{len(state["commands"]):03d}-offline-native-activation.stdout',32768)
                need(captured_raw == read(output/'private/ACTIVATION_RESULT.json',32768), 'ACTIVATION_CAPTURE_DIFFERS')
                captured = json.loads(captured_raw, object_pairs_hook=unique_object)
                need(catalogue_schema_matches(captured, json.loads(read(packet/'PUBLIC_RESULT_SCHEMA.json'), object_pairs_hook=unique_object)) and captured == state['activation'], 'ACTIVATION_CAPTURE_DIFFERS')
                state['activation_validation']['captured_result_matches'] = True
    except BaseException as exc:
        observe_capsule_failure(state,'activation-receiving',exc)
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
        version = command(state, output, u, 'codex-version', [str(output/'private/codex-input'), '--version']).decode().strip()
        need(version == 'codex-cli 0.167.0-alpha.4', 'CODEX_VERSION'); state['runtime']['observed_version'] = version
        current(state, source, output, u, 'after-runtime-acquisition')
    elif step == 'activation':
        current(state, source, output, u, 'before-activation')
        launch_activation(state, source, output, packet, u)
        current(state, source, output, u, 'after-activation')
    elif step == 'receive':
        current(state, source, output, u, 'before-receiving')
        prior_component(state, source, 'receive')
        receive_capsule(state, output)
        capsule_recheck(state, u, 'receive')
        need(state.get('activation_validation', {}).get('valid') is True and state['activation_validation'].get('captured_result_matches') is True and activation_success(state.get('activation', {}),os.getuid(),os.getgid(),state['receipt']), 'ACTIVATION_NOT_RECEIVED')
        need(stream_hash(output/'private/codex-input') == (BINARY_BYTES,BINARY_SHA), 'RECEIVED_RUNTIME_CHANGED')
        receive_activation_private(state,output,source)
        state['activation_validation']['semantic_receiving_passed'] = True
        state['source_after'] = source_check(source, packet)
        need(state['source_after'] == state['source_before'] and canonical_hashes(source, state) == state['canonical_before'], 'FINAL_SOURCE_OR_STATE_DRIFT')
        current(state, source, output, u, 'after-receiving')
        state['bounded_receiving_complete'] = True
    else: raise Refusal('UNKNOWN_STEP')

def export(state, output, packet):
    if 'activation' in state:
        try:
            need(catalogue_schema_matches(state['activation'], json.loads(read(packet/'PUBLIC_RESULT_SCHEMA.json'))), 'ACTIVATION_EXPORT_SCHEMA')
        except BaseException as exc:
            state.pop('activation', None); state.setdefault('activation_validation',{})['valid'] = False; state['failed'] = True; state['bounded_receiving_complete'] = False
            state['failures'].append({'step': 'export', 'exception_type': type(exc).__name__, 'message_sha256': digest(str(exc).encode()), 'message_bytes': len(str(exc).encode())})
    docs = {
        'RESULT.json': {'schema': 'dg17.isolated-codex-activation-hosted-result.v1', 'context': state['context'], 'completed': state['completed'], 'failed': state['failed'], 'bounded_receiving_complete': state.get('bounded_receiving_complete', False), 'activation_validation': state.get('activation_validation'), 'local_currentness_transfer': False, 'original_acceptance': False, 'whole_T12': False, 'whole_T14': False, 'new_original_awards': []},
        'SOURCE.json': {'before': state.get('source_before'), 'after': state.get('source_after'), 'canonical_unchanged': state.get('canonical_unchanged')},
        'HOST.json': {'host': state.get('host'), 'runtime': state.get('runtime'), 'capsule': state.get('capsule')},
        'CURRENTNESS.json': {'checks': state['currentness'], 'reads': state['reads'], 'local_or_future_transfer': False},
        'PREDICATES.json': state.get('predicates', {'status':'PRIOR_COMPONENT_NOT_REPLAYED','reference':PRIOR_COMPONENT,'fresh_execution':False,'fresh_method_count':0,'native_windows_qualification':False,'new_original_awards':[],'source_closure':{'prepare':False,'receive':False,'final':False}}),
        'ACTIVATION.json': state.get('activation', {'status': 'INVALID_RESULT_SCHEMA' if state.get('activation_validation',{}).get('valid') is False else 'NOT_COMPLETED'}),
        'CLEANUP.json': {'commands': state['commands'], 'active_step': state.get('active_step'), 'active_command': state.get('active_command'), 'all_recorded_commands_reaped': all(x.get('cleanup', {}).get('echild') is True for x in state['commands']), 'private_roots_retained_until_disposable_host_teardown': True, 'declared_large_payload_owners_retained_until_disposable_host_teardown': True},
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
                    need(digest(read(output/'private/ACTIVATION_RESULT.json',32768)) == state['activation_validation']['result_sha256'] and activation_success(state['activation'],os.getuid(),os.getgid(),state['receipt']), 'FINAL_ACTIVATION_RESULT_DRIFT')
                    receive_activation_private(state,output,source)
                    state['activation_validation']['final_private_seal_verified'] = True
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
