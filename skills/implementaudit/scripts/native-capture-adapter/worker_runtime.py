"""Claim-specific bounded preparation and same-process readback checks.

No process creation here. Capture owns execution and custody. Caller-owned
adoption/selection pins are not interpreted as invented governor authority.
"""
import copy
import hashlib
import importlib.util
import json
import os
import re
from pathlib import Path, PureWindowsPath
import shlex
import tomllib

WORKER_PROFILE_SHA256 = '0b1bc8d879f128df59200d4f22167d063e1f56c802cc7088113267417e9f8b82'


def worker_profile():
    """Execute only this runtime source's selected, once-verified profile bytes."""
    expected = WORKER_PROFILE_SHA256
    require(isinstance(expected, str) and re.fullmatch(r'[0-9a-f]{64}', expected) is not None,
        'Selected worker profile source is unbound')
    path = Path(__file__).parent / 'worker_profile.py'
    for node in (path, *path.parents):
        require(not node.is_symlink() and not (node.exists() and
            getattr(node.lstat(), 'st_file_attributes', 0) & 0x400), 'Aliased worker profile source')
    require(path.is_file(), 'Selected worker profile source is missing')
    raw = path.read_bytes()
    require(hashlib.sha256(raw).hexdigest() == expected, 'Selected worker profile source differs')
    spec = importlib.util.spec_from_file_location('bound_worker_profile', path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(raw, str(path), 'exec'), module.__dict__)
    return module


def load(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    exec(compile(Path(path).read_bytes(),str(path),'exec'),module.__dict__)
    return module


def exact(a,b):
    if type(a) is not type(b):return False
    if isinstance(b,dict):return set(a)==set(b) and all(exact(a[k],b[k]) for k in b)
    if isinstance(b,list):return len(a)==len(b) and all(exact(x,y) for x,y in zip(a,b))
    return a==b


def require(test,why):
    if not test:raise ValueError(why)


def pin(path):
    p=Path(path); raw=p.read_bytes()
    return {'path':str(p),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}


def schema_result(plan,name,value):
    import jsonschema
    try:
        jsonschema.Draft7Validator(json.loads(Path(plan['schemas'][name]['path']).read_bytes())).validate(value)
    except jsonschema.ValidationError as exc:
        raise ValueError(name+' schema rejected: '+str(exc.validator)) from None


def skill_config_representation(actual, expected, breadcrumb):
    """Only the selected ordered path/False rules admit separator differences."""
    require(type(actual) is list and type(expected) is list and len(actual) == len(expected),
        'Effective config differs: ' + breadcrumb)
    def path_identity(value, where):
        require(isinstance(value, str) and not any(c in value for c in ('\x00', '\n', '\r', '*', '?')),
            'Effective config differs: ' + where)
        path = value.replace('\\', '/')
        if re.match(r'^[A-Za-z]:/', path):
            parts = path[3:].split('/')
        elif path.startswith('//'):
            parts = path[2:].split('/')
            require(len(parts) >= 3, 'Effective config differs: ' + where)
        else:
            raise ValueError('Effective config differs: ' + where)
        require(all(part not in ('', '.', '..') for part in parts), 'Effective config differs: ' + where)
        return path
    seen_actual, seen_expected = set(), set()
    for index, (row, wanted) in enumerate(zip(actual, expected)):
        where = breadcrumb + '[' + str(index) + ']'
        require(type(row) is dict and type(wanted) is dict and set(row) == set(wanted) == {'path', 'enabled'},
            'Effective config differs: ' + where)
        require(row['enabled'] is False and wanted['enabled'] is False, 'Effective config differs: ' + where + '.enabled')
        observed = path_identity(row['path'], where + '.path')
        approved = path_identity(wanted['path'], where + '.path')
        require(observed == approved and observed not in seen_actual and approved not in seen_expected,
            'Effective config differs: ' + where + '.path')
        seen_actual.add(observed); seen_expected.add(approved)
    return copy.deepcopy(actual)


def project_config(config, expected, breadcrumb='config'):
    """Only selected fields; do not copy unrelated credentials into summaries."""
    require(isinstance(config,dict),'Effective config object unavailable: ' + breadcrumb)
    result={}
    for key,wanted in expected.items():
        label = key if isinstance(key, str) and re.fullmatch(r'[A-Za-z_][A-Za-z0-9_-]*', key) else '[selected_key]'
        where = breadcrumb + '.' + label
        require(key in config,'Effective config field missing: ' + where)
        actual=config[key]
        if where == 'config.skills.config':
            result[key]=skill_config_representation(actual,wanted,where)
        elif isinstance(wanted,dict):
            result[key]=project_config(actual,wanted,where)
        else:
            require(exact(actual,wanted),'Effective config differs: ' + where)
            result[key]=copy.deepcopy(actual)
    return result


def declared_mcp_names(plan):
    names = plan['binding']['mcp_names']
    require(type(names) is list and all(type(name) is str and re.fullmatch(r'[A-Za-z0-9_-]+', name) for name in names),
        'Declared MCP names are not typed exact names')
    require(len(names) == len(set(names)) == len({name.casefold() for name in names}),
        'Declared MCP names contain duplicates or case aliases')
    return list(names)


def validate_config(plan,result):
    schema_result(plan,'ConfigReadResponse',result)
    require(result.get('layers') is None,'Unexpected unrequested configuration layers')
    expected=plan['profile_proposal']['effective_config_projection']
    projection=project_config(result['config'],expected)
    for name,profile in expected['permissions'].items():
        actual=result['config']['permissions'][name]
        require(actual.get('extends') in (None,[]),'Unexpected permission inheritance')
        fs=dict(actual.get('filesystem',{}))
        if fs.get('glob_scan_max_depth','ABSENT') is None:fs.pop('glob_scan_max_depth')
        require(exact(fs,profile['filesystem']),'Extra/missing filesystem grants')
        require(actual['network'].get('enabled') is False,'Network exclusion differs')
    names=declared_mcp_names(plan)
    require('mcp_servers' in result['config'],'Effective MCP registry is missing')
    servers=result['config']['mcp_servers']
    require(type(servers) is dict and set(servers)==set(names),'Effective MCP registered-name scope differs')
    require(all(type(v) is dict and v.get('enabled') is False for v in servers.values()),
        'Additional effective enabled MCP server')
    toolenv=result['config'].get('shell_environment_policy',{})
    profiles=worker_profile()
    complete=profiles.complete_environment(plan['binding'],expected['shell_environment_policy']['set'],plan['config_source_pins'],purpose=plan.get('purpose'))
    require(exact(toolenv.get('set'),complete),
        'Effective config differs: config.shell_environment_policy.set')
    return {'kind':'WHITELISTED_CONFIG_PROJECTION','projection':projection,
        'mcp_registry':{'registered_names':names,'registered_count':len(names),'all_enabled_false':True},
        'not_raw_response':True,'raw_custody':'Bounded private stdout.bin; locator and exact raw frame digest retained separately'}


def validate_startup(plan,response,facts):
    """Same owned process; returns only corroborated selected facts, not PASS."""
    config=response(plan['readbacks']['config'])
    require('result' in config,'config/read rejected')
    facts['effective_selection']=validate_config(plan,config['result'])
    models=[]; request=copy.deepcopy(plan['readbacks']['models'])
    for page in range(4):
        msg=response(request); result=msg.get('result')
        schema_result(plan,'ModelListResponse',result)
        models.extend(result['data'])
        if result['nextCursor'] is None:break
        require(isinstance(result['nextCursor'],str) and result['nextCursor'],'Invalid model cursor')
        request={'id':210+page,'method':'model/list','params':dict(request['params'],cursor=result['nextCursor'])}
    else:raise ValueError('Model pagination bound')
    matches=[m for m in models if m['model']==plan['binding']['model']]
    require(len(matches)==1 and any(x['reasoningEffort']==plan['binding']['effort'] for x in matches[0]['supportedReasoningEfforts']),
        'Exact model/effort catalog binding unavailable')
    hooks=response(plan['readbacks']['hooks']).get('result')
    schema_result(plan,'HooksListResponse',hooks)
    require(hooks['data']==[{'cwd':plan['server_cwd'],'hooks':[],'errors':[],'warnings':[]}],
        'Hook discovery is not exactly empty at bound cwd')
    facts['hook_selection_basis']='Source-pinned plugins/hooks/executor exclusions plus actual effective config and empty discovery; not a complete engine instrumentation claim'


def validate_thread_selection(plan,response,thread_id,facts):
    """Qualify a complete disabled registry snapshot, not an empty inventory."""
    names=declared_mcp_names(plan)
    template={'id':13,'method':'mcpServerStatus/list','params':{'limit':100,'detail':'full'}}
    require(exact(plan['readbacks']['mcp'],template),'Exact MCP request scope differs')
    require(len(names)<=template['params']['limit'],'MCP registry exceeds the supported complete-page bound')
    require(type(facts) is dict,'MCP config/thread corroboration is missing')
    thread=facts.get('thread_metadata')
    require(type(thread_id) is str and bool(thread_id) and type(thread) is dict and
        type(thread.get('thread_id')) is str and thread['thread_id']==thread_id,'MCP request thread differs')
    effective=facts.get('effective_selection')
    require(type(effective) is dict and effective.get('kind')=='WHITELISTED_CONFIG_PROJECTION',
        'Validated MCP config corroboration is missing')
    registry=effective.get('mcp_registry')
    require(type(registry) is dict and set(registry)=={'registered_names','registered_count','all_enabled_false'} and
        exact(registry['registered_names'],names) and type(registry['registered_count']) is int and
        registry['registered_count']==len(names) and registry['all_enabled_false'] is True,
        'Declared and config-disabled MCP registry differ')
    request=copy.deepcopy(template)
    request['params']['threadId']=thread_id
    reply=response(request)
    require(type(reply) is dict and set(reply)=={'id','result'} and type(reply['id']) is int and reply['id']==request['id'],
        'MCP response identity or envelope differs')
    result=reply['result']
    schema_result(plan,'ListMcpServerStatusResponse',result)
    require(type(result) is dict and set(result)=={'data','nextCursor'} and result['nextCursor'] is None and
        type(result['data']) is list,'Incomplete or unsupported full MCP response')
    rows=result['data']
    require(len(rows)==len(names),'MCP status registry count differs')
    expected=set(names); seen=set()
    fields={'name','runtimeStatus','pluginId','serverInfo','tools','resources','resourceTemplates','authStatus'}
    for row in rows:
        require(type(row) is dict and set(row)==fields,'MCP status row fields differ')
        name=row['name']
        require(type(name) is str and name in expected and name not in seen,'MCP status name differs or repeats')
        require(type(row['runtimeStatus']) is str and row['runtimeStatus']=='disabled' and
            row['pluginId'] is None and row['serverInfo'] is None and
            type(row['tools']) is dict and not row['tools'] and
            type(row['resources']) is list and not row['resources'] and
            type(row['resourceTemplates']) is list and not row['resourceTemplates'] and
            type(row['authStatus']) is str and row['authStatus']=='unsupported',
            'MCP status is not an explicit capability-empty disabled record')
        seen.add(name)
    require(seen==expected,'MCP status registry is incomplete')
    facts['mcp_runtime_selection']={'selection':'NO_ACTIVE_MCP_SELECTION',
        'registered_disabled_names':names,'registered_disabled_count':len(names),
        'response_identity':{'id':request['id'],'method':request['method'],'thread_id':thread_id,
            'detail':'full','limit':100,'canonical_response_sha256':hashlib.sha256(
                json.dumps(reply,sort_keys=True,separators=(',',':')).encode()).hexdigest()},
        'complete_tool_inventory_observed':False}


def command_matches(item_command,expected_argv):
    if not isinstance(item_command,str):return False
    try:argv=shlex.split(item_command,posix=True)
    except ValueError:return False
    # No case/alias substitution or redacted-byte reconstruction earns identity.
    return exact(argv,expected_argv)


def preflight(here,plan_sha,owner,owner_sha,pins_sha,source_root):
    here=Path(here)
    source_root=Path(source_root)
    require(source_root == Path(__file__).parent, 'Selected adapter source root differs')
    require(pin(owner)['sha256']==owner_sha,'Pinned c86 owner changed')
    helper=load(owner,'retained_c86_owner')
    helper.no_reparse(here)
    for path in (here/'THREAD_METADATA_PLAN.json',here/'INPUT_PINS.json'):
        helper.no_reparse(path)
    plan_raw=(here/'THREAD_METADATA_PLAN.json').read_bytes()
    pins_raw=(here/'INPUT_PINS.json').read_bytes()
    require(hashlib.sha256(plan_raw).hexdigest()==plan_sha,'Plan hash differs')
    require(hashlib.sha256(pins_raw).hexdigest()==pins_sha,'Input manifest hash differs')
    plan=json.loads(plan_raw)
    require(plan.get('purpose') in ('OFFLINE_FIXTURE','NATURALLY_WARRANTED_WORKER','ISOLATED_QUALIFICATION'),'Worker purpose differs')
    pins=json.loads(pins_raw)['files']
    listed={str(Path(row['path'])) for row in pins}
    for name in ('worker_profile.py','worker_runtime.py','canary_protocol.py','load_visibility.py','notification_policy.py','NOTIFICATION_DISPOSITIONS.json','HOOK_OBSERVATION_CONTRACT.json','JSONSCHEMA_RUNTIME.json'):
        require(str((source_root if name.endswith('.py') else here)/name) in listed,'Current module/data not pinned: '+name)
    for row in pins:
        helper.no_reparse(Path(row['path']))
        require(helper.file_record(Path(row['path']))==row,'Pinned input differs: '+row['path'])
    if plan.get('purpose')=='ISOLATED_QUALIFICATION':
        load(source_root/'load_visibility.py','exact_qualification_visibility').validate_isolated_qualification_plan(plan)
    profiles=worker_profile()
    if 'complete_environment_policy' in plan['binding']:
        require(plan['binding']['complete_environment_policy'] in pins,'Complete environment policy is not pinned')
    prepared=profiles.prepare(plan['binding'],json.loads(Path(plan['schemas']['ConfigSchema']['path']).read_bytes()),
        json.loads(Path(plan['schemas']['ClientRequest']['path']).read_bytes()),purpose=plan.get('purpose'))
    require(exact(prepared,plan['profile_proposal']),'Profile regeneration differs')
    require(exact(plan.get('visibility',{}).get('load_spec',{}).get('context_contract'),prepared['context_contract']),
        'Policy/observer context expectations differ from independently derived factory input')
    require(plan['binding'].get('context_input')==prepared['context_contract']['source_input'],
        'Context expectation source/input pin differs')
    for context_pin in prepared['context_contract']['custody']:
        require(context_pin in pins,'Independent context source/render/input custody is missing from the input manifest')
    for key in ('server_argv','server_cwd','thread_start','turn_start','use_turn_start'):
        require(exact(plan[key],prepared[key]),'Bound worker plan differs: '+key)
    cwd=plan['server_cwd']
    requests={
        'initialize':{'id':1,'method':'initialize','params':{'clientInfo':{'name':'bounded-worker-load-use','version':'1'},'capabilities':{'experimentalApi':True}}},
        'after_successful_initialize':{'method':'initialized','params':{}},
        'profile_list':{'id':2,'method':'permissionProfile/list','params':{'cwd':cwd}}}
    unknown=copy.deepcopy(plan['thread_start']);unknown['id']=3;unknown['params']['permissions']='worker_absent_ae1209'
    requests['unknown_thread_start']=unknown
    for key,wanted in requests.items():require(exact(plan[key],wanted),'Exact RPC binding differs: '+key)
    require(exact(plan['readbacks'],{
        'config':{'id':10,'method':'config/read','params':{'cwd':cwd,'includeLayers':False}},
        'models':{'id':11,'method':'model/list','params':{'limit':100}},
        'hooks':{'id':12,'method':'hooks/list','params':{'cwds':[cwd]}},
        'mcp':{'id':13,'method':'mcpServerStatus/list','params':{'limit':100,'detail':'full'}}}), 'Exact readback RPC set differs')
    require(plan['binding']['native']['sha256']==plan['native_identity']['sha256']=='081e4de4be8e38fac6ed4d95e3b1a0b9f6d31c090ddc36e1696b349fe406f575' and plan['native_version']=='0.154.0-alpha.6.2',
        'Native identity/version binding differs')
    require(plan['forbidden_markers'] and len(plan['forbidden_markers'])<=8,'Witness population missing/exceeds bound')
    for row in plan['forbidden_markers']:
        raw=Path(row['path']).read_bytes()
        require(8<=len(raw)<=128 and raw.isascii() and raw.strip(), 'Forbidden witness bytes malformed')
    cfg=plan['visibility']; b=plan['binding']
    require(not any(name in os.environ for name in ('CODEX_MANAGED_BY_VITE_PLUS','CODEX_MANAGED_BY_PNPM',
        'CODEX_MANAGED_BY_NPM','CODEX_MANAGED_BY_BUN')),'Unreviewed code-mode install-context override')
    for source in plan['expected_metadata']['instructionSources']:
        require(str(Path(source)) in listed,'Instruction source lacks current caller pin')
    # LOAD pin/reader/custody entries may not be detached from the manifest.
    for row in [b['native'],b['code_mode_host']]+list(b['load_pins'].values())+[b['loader']]+b['use_pins']+plan['config_source_pins']+plan['forbidden_markers']+list(plan['schemas'].values()):
        require(row in pins,'Required source/read/config pin absent from manifest')
    mcp_layers = []
    inherited_environment = {}
    for row in plan['config_source_pins']:
        raw = Path(row['path']).read_bytes()
        require(len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256'],
                'Pinned MCP configuration changed before transport validation')
        try:
            parsed = tomllib.loads(raw.decode('utf-8'))
        except (ValueError, UnicodeDecodeError):
            raise ValueError('Pinned MCP configuration source cannot be parsed') from None
        mcp_layers.append(parsed.get('mcp_servers', {}))
        environment = parsed.get('shell_environment_policy', {})
        require(isinstance(environment,dict),'Pinned environment policy is not a table')
        entries = environment.get('set', {})
        require(isinstance(entries,dict) and all(isinstance(k,str) and isinstance(v,str) for k,v in entries.items()),
            'Pinned environment set is not a string map')
        inherited_environment.update(entries)
    profiles.validate_mcp_transports(prepared['effective_config_projection'], b['mcp_names'], mcp_layers)
    prescribed = prepared['effective_config_projection']['shell_environment_policy']['set']
    complete = profiles.complete_environment(b,prescribed,plan['config_source_pins'],purpose=plan.get('purpose'))
    inherited_environment.update(prescribed)
    require(exact(inherited_environment,complete),'Pinned complete tool environment differs')
    require(exact(cfg['load_input'],b['load_input']) and exact(cfg['use_input'],b['use_input']),'LOAD/USE input custody differs')
    require(cfg['load_spec']['command']==b['load_command'] and cfg['load_spec']['cwd']==plan['server_cwd'],'Reader command/cwd differs')
    loaded={k:{'pin':v,'text':Path(v['path']).read_bytes().decode('utf-8')} for k,v in sorted(b['load_pins'].items())}
    expected=json.dumps({'identity':cfg['identity'],'loaded':loaded},sort_keys=True,separators=(',',':'),ensure_ascii=True)+'\n'
    require(cfg['load_spec']['expected_output']==expected and len(expected.encode('ascii'))<=65536,'Exact LOAD output binding differs')
    require(cfg['load_spec']['ready_text']=='LOAD_READY_ONLY '+hashlib.sha256(expected.encode('ascii')).hexdigest(),'Exact ready text differs')
    require(exact(cfg['load_input'],profiles.silent_load_input(b,cfg['load_spec']['ready_text'])),
        'Silent LOAD prompt differs from exact output/readiness binding')
    contract=plan['qualification_contract']
    require(all(b[key]==contract[owner] for key,owner in (
        ('use_command','USE_expected_command'),('use_expected_output','USE_expected_output'),
        ('use_terminal_text','USE_expected_terminal_text'))),'Exact USE command/output/terminal owner differs')
    selected_code_mode={
        'LOAD':profiles.code_mode_spec(b,b['load_command'],expected,cfg['load_spec']['ready_text']),
        'USE':profiles.code_mode_spec(b,b['use_command'],b['use_expected_output'],b['use_terminal_text'])}
    require(exact(cfg['load_spec'].get('code_mode'),selected_code_mode),'Literal LOAD/USE custody selection differs')
    require(exact(cfg['use_input'],profiles.silent_use_input(b)),'Silent USE prompt differs')
    raw_schema_identity={
        'RawResponseItemCompletedNotification':(32472,'808fe739fc46130292a0a8c1969ff4e63dff856fc241ff78ce207a8eb1a67f46'),
        'RawResponseCompletedNotification':(1998,'aba140e87952c900f96e0308a8849d3e313d985de1f1aa2b77f193884a76357c')}
    for name,(size,sha256) in raw_schema_identity.items():
        require(name in plan['schemas'] and plan['schemas'][name] in pins,'Required raw-response schema custody missing')
        require((plan['schemas'][name]['bytes'],plan['schemas'][name]['sha256'])==(size,sha256),
                'Raw-response schema does not match the selected current binary export')
    require(cfg['load_spec']['expected_argv']==[b['powershell']['path'],'-NoProfile','-Command',b['load_command']],
        'Exact native PowerShell command vector differs')
    require(cfg['load_spec']['loader_pin']==b['loader'],'Reader pin differs')
    # The model-provided path selects type only. Process-local discovery must
    # deterministically find the pinned pwsh, before fallback/other shell routes.
    shell=Path(b['powershell']['path'])
    require(shell.name.lower()=='pwsh.exe','This bounded selection requires pwsh.exe')
    require(not (Path(plan['server_cwd'])/'pwsh.exe').exists() or (Path(plan['server_cwd'])/'pwsh.exe')==shell,
        'Cwd shell shadowing')
    require(plan['process_environment']=={'PATH':str(shell.parent),'PATHEXT':'.EXE'},'Process shell discovery environment differs')
    require(0<cfg['ack_timeout_seconds']<=50,'ACK wait exceeds the retained 60 second protocol deadline')
    # Provenance membership is not semantic qualification or adoption.
    for name in ('phase_capable_source_adoption','runtime_selection_acceptance'):
        require(cfg[name] in pins,'Caller custody pin absent from pinned inputs')
    require(Path(cfg['parent_rollout']).is_file() and type(cfg['parent_launch_offset']) is int and cfg['parent_launch_offset']>=0,
        'Parent rollout/launch offset unavailable')
    helper.no_reparse(Path(cfg['parent_rollout']))
    require(str(PureWindowsPath(cfg['parent_rollout'])).lower() in
        [str(PureWindowsPath(p)).lower() for p in b['excluded_paths']], 'Parent rollout must be explicitly excluded from worker reads')
    require(set(plan['expected_turn_settings'])=={'LOAD','USE'},'Two exact phase settings required')
    policy=load(source_root/'notification_policy.py','bound_worker_policy')
    require(policy.runtime_identity()==json.loads((here/'JSONSCHEMA_RUNTIME.json').read_bytes()),'Existing jsonschema runtime identity differs')
    matrix=json.loads((here/'NOTIFICATION_DISPOSITIONS.json').read_bytes())
    require(all(row['disposition']=='ABORT' for row in matrix['rows'] if row['method'].startswith('hook/')), 'Worker hook notification admission is forbidden')
    notification_validator=policy.NotificationPolicy(plan,matrix,Path(matrix['schema_pin']['path']),{}).validator
    for phase,profile in [('LOAD','worker_load'),('USE','worker_use')]:
        expected=plan['expected_turn_settings'][phase]
        require(expected['activePermissionProfile']=={'id':profile,'extends':None},'Phase profile provenance differs')
        require(expected['cwd']==plan['server_cwd'] and expected['approvalPolicy']=='never' and expected['sandboxPolicy']=={'type':'readOnly','networkAccess':False},
            'Phase permission semantics differ')
        require((expected['model'],expected['modelProvider'],expected['effort'])==(b['model'],b['provider'],b['effort']),
            'Phase model binding differs')
        try:notification_validator.validate({'method':'thread/settings/updated','params':{'threadId':'__PREFLIGHT__','threadSettings':expected}})
        except Exception:raise ValueError('Expected phase settings native schema differs') from None
    return plan,pins,helper
