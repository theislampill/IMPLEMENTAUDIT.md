"""Pure preparation/preflight proposal. No launcher and no runtime acceptance.

Inputs are exact caller-selected bindings, not evidence of adoption/currentness.
The parent owns source selection; plugin exclusion does not replace direct LOAD.
"""
import hashlib
import copy
import re
import json
import math
from pathlib import Path, PureWindowsPath
import tomllib

ROLES = {'child_source', 'shared_transcript_contract', 'frozen_open_envelope'}
DISABLED_FEATURES = ('plugins', 'remote_plugin', 'hooks', 'executor_capability_discovery',
    'apps', 'multi_agent', 'multi_agent_v2', 'shell_zsh_fork', 'unified_exec_zsh_fork',
    'skill_mcp_dependency_install', 'memories')
COMPLETE_ENVIRONMENT_POLICY_SHA256 = 'd2114a8dc618d7405901ebe625d1f08e0c7591d75739bb67c4ddef256940e23c'


def pin(path):
    path = Path(path)
    raw = path.read_bytes()
    return {'path': str(path.resolve()), 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}


def context_basis(binding, proposal):
    """Bind expectations to source inputs and exact generated requests, without a self-hash cycle."""
    selected = {key: proposal[key] for key in ('server_argv','server_cwd','thread_start','turn_start',
        'use_turn_start','effective_config_projection')}
    inputs = {key:value for key,value in binding.items() if key!='context_input'}
    return hashlib.sha256(json.dumps({'binding':inputs,'proposal':selected},sort_keys=True,separators=(',',':')).encode()).hexdigest()


def context_contract_from_input(binding, basis_sha256, *, purpose):
    """Derive grouping and phase deltas from independent, pinned producer render receipts.

    This verifies custody and declared source-branch relationships. The owner
    must independently establish each producer receipt's rendering semantics;
    unknown production renderings remain UNRESOLVED. No observed frame is an
    input to this function or an expectation oracle.
    """
    def require(value, message):
        if not value: raise ValueError(message)
    def digest(value):
        return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    def valid_digest(value): return type(value) is str and re.fullmatch('[0-9a-f]{64}',value) is not None
    custody={}
    def take(record):
        require(type(record) is dict and set(record)=={'path','bytes','sha256'} and
            type(record['path']) is str and Path(record['path']).is_absolute() and
            type(record['bytes']) is int and 0<=record['bytes']<=1048576 and valid_digest(record['sha256']),
            'Malformed independent context input pin')
        require(record['path'] not in custody or custody[record['path']]==record,'Context path has conflicting commitments')
        try:raw=Path(record['path']).read_bytes()
        except OSError:raise ValueError('Independent context source/input is unavailable') from None
        require(len(raw)==record['bytes'] and hashlib.sha256(raw).hexdigest()==record['sha256'],
            'Independent context source/input bytes changed')
        custody[record['path']]=copy.deepcopy(record)
        return raw
    def unique(pairs):
        result={}
        for key,value in pairs:
            require(key not in result,'Duplicate independent context input key')
            result[key]=value
        return result
    def document(record):
        try:
            return json.loads(take(record),object_pairs_hook=unique,
                parse_constant=lambda value: (_ for _ in ()).throw(ValueError('Non-finite context input')))
        except (UnicodeDecodeError,json.JSONDecodeError):
            raise ValueError('Malformed independent context JSON input') from None
    require(type(binding) is dict and 'context_input' in binding and valid_digest(basis_sha256),
        'Independent context input and request/profile basis required')
    source_input=binding['context_input'];record=document(source_input)
    required={'schema','origin','scope','status','unresolved','source_commit','basis_sha256','source_pins','input_pins','population_proof','producers','phases'}
    require(type(record) is dict and set(record)==required and record['schema']=='native-context-input-v1' and
        record['origin']=='INDEPENDENT_SOURCE_INPUT','Observed or malformed data cannot supply context expectations')
    require(record['status']=='COMPLETE' and record['unresolved']==[], 'Unresolved production context inputs prevent preparation')
    require(record['scope'] in ('SOURCE_INPUT','OFFLINE_SYNTHETIC') and
        (record['scope']!='OFFLINE_SYNTHETIC' or purpose=='OFFLINE_FIXTURE'),'Synthetic context cannot qualify native input')
    require(record['source_commit']=='b5bffd3ec4db487e7e3dec59663875b0ef7b72ca' and record['basis_sha256']==basis_sha256,
        'Context source or generated request/profile basis differs')
    for key in ('source_pins','input_pins'):
        require(type(record[key]) is list and 0<len(record[key])<=512,'Context source/input population is unbound')
        for item in record[key]:take(item)
    producers=record['producers']
    require(type(producers) is list and 0<len(producers)<=128,'Complete selected context producer inventory required')
    population=document(record['population_proof'])
    require(type(population) is dict and set(population)=={'schema','origin','source_commit','basis_sha256','source_pins','input_pins','producer_ids','unresolved'} and
        population['schema']=='native-context-population-v1' and population['origin']=='INDEPENDENT_SOURCE_INPUT' and
        population['source_commit']==record['source_commit'] and population['basis_sha256']==basis_sha256 and
        population['source_pins']==record['source_pins'] and population['input_pins']==record['input_pins'] and population['unresolved']==[],
        'Independent complete producer population proof differs')
    require(type(record['phases']) is dict and set(record['phases'])=={'LOAD','USE'},'Exact LOAD and USE context inputs required')
    slots={'developer_aggregate':0,'developer_standalone':1,'mode_standalone':2,'user_aggregate':3,'after_user_standalone':4}
    ids=[];initial_orders=set();delta_orders=set();receipt_paths=set()
    for producer in producers:
        keys={'id','family','source_pin','role','content_item_kind','initial_slot','initial_order','delta_order','standalone','receipts'}
        require(type(producer) is dict and set(producer)==keys,'Context producer declaration is malformed')
        identity=producer['id'];kind=producer['content_item_kind'];slot=producer['initial_slot']
        require(type(identity) is str and re.fullmatch('[A-Za-z0-9_.:-]{1,128}',identity) and identity not in ids,
            'Context producer identity is duplicate or malformed')
        ids.append(identity)
        require(producer['family'] in ('WORLD_STATE','INITIAL_ONLY','TURN_CONTEXT') and producer['source_pin'] in record['source_pins'] and
            producer['role'] in ('user','developer') and type(kind) is str and kind!='user.text' and
            re.fullmatch('[a-z0-9_]+(?:[.][a-z0-9_]+)+',kind) is not None,
            'Unselected producer/source/classification cannot authorize context')
        require(slot in slots and producer['role']==('user' if slot=='user_aggregate' else 'developer') and
            type(producer['standalone']) is bool and
            all(type(producer[key]) is int and 0<=producer[key]<128 for key in ('initial_order','delta_order')),
            'Source context role/grouping/order declaration differs')
        require(producer['initial_order'] not in initial_orders and producer['delta_order'] not in delta_orders,'Duplicate source context order')
        initial_orders.add(producer['initial_order']);delta_orders.add(producer['delta_order'])
        # Initial grouping is owned by build_initial_context's slots. The
        # separate-message flag independently controls later world-state diffs.
        require(producer['family']!='TURN_CONTEXT' or (slot=='developer_aggregate' and not producer['standalone']),
            'Turn-context contributions must use their source developer grouping')
        require(type(producer['receipts']) is dict and set(producer['receipts'])=={'LOAD','USE'},'Both producer phase receipts required')
        for value in producer['receipts'].values():
            require(type(value) is dict and type(value.get('path')) is str and value['path'] not in receipt_paths,'Producer receipt alias or missing pin')
            receipt_paths.add(value['path'])
    require(population['producer_ids']==ids,'Missing, extra or reordered selected producer inventory')
    control_paths={source_input['path'],record['population_proof']['path']}|receipt_paths
    require(len(control_paths)==len(receipt_paths)+2,'Circular context input/control custody')
    phase_states={'LOAD':{},'USE':{}};emitted={'LOAD':[],'USE':[]}
    for producer in producers:
        previous=None
        for phase in ('LOAD','USE'):
            receipt=document(producer['receipts'][phase])
            keys={'schema','origin','producer_id','phase','source_pin','basis_sha256','input_pins','previous_state_sha256','state','branch','fragment'}
            require(type(receipt) is dict and set(receipt)==keys and receipt['schema']=='native-context-producer-v1' and
                receipt['origin']=='INDEPENDENT_SOURCE_INPUT' and receipt['producer_id']==producer['id'] and receipt['phase']==phase and
                receipt['source_pin']==producer['source_pin'] and receipt['basis_sha256']==basis_sha256 and receipt['input_pins']==record['input_pins'],
                'Context rendering receipt is observed, foreign or incompletely bound')
            state=digest(receipt['state']);phase_states[phase][producer['id']]=state
            branch=receipt['branch'];fragment=receipt['fragment']
            if phase=='LOAD':
                require(receipt['previous_state_sha256'] is None and branch in ('PRESENT','ABSENT'),'LOAD requires a proved initial producer branch')
            else:
                require(receipt['previous_state_sha256']==previous,'USE producer state does not follow exact LOAD state')
                if producer['family']=='INITIAL_ONLY':
                    require(state==previous and branch=='INITIAL_ONLY','Changed initial-only producer requires new source binding')
                elif producer['family']=='TURN_CONTEXT':
                    require(branch in ('REEMITTED','ABSENT'),'Turn-context USE rendering branch is unbound')
                elif state==previous:
                    require(branch=='UNCHANGED','USE cannot blindly replay unchanged LOAD world-state context')
                else:
                    require(branch in ('CHANGED','REMOVED','NO_RENDERED_DIFF'),'Changed USE state needs an independently proved rendering decision')
            visible=branch in ('PRESENT','CHANGED','REMOVED','REEMITTED')
            require((fragment is not None)==visible,'Producer emission/omission differs from its source branch')
            if visible:
                require(type(fragment) is dict and fragment.get('path') not in control_paths,'Observed/control receipt cannot be its own context body oracle')
                raw=take(fragment)
                require(len(raw)<=65536,'Private context fragment exceeds existing text bound')
                try:raw.decode('utf-8')
                except UnicodeDecodeError:raise ValueError('Context fragment is not exact UTF-8 text') from None
                emitted[phase].append((producer,branch,{'type':'input_text','bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}))
            previous=state
    def row(entries):
        return {'producers':[entry[0]['id'] for entry in entries], 'branches':[entry[1] for entry in entries],
            'role':entries[0][0]['role'],'content_item_kinds':[entry[0]['content_item_kind'] for entry in entries],
            'content':[entry[2] for entry in entries]}
    load_groups=[]
    for slot in slots:
        selected=sorted([entry for entry in emitted['LOAD'] if entry[0]['initial_slot']==slot],key=lambda entry:entry[0]['initial_order'])
        if slot in ('developer_aggregate','user_aggregate'):
            if selected:load_groups.append(selected)
        else:load_groups.extend([[entry] for entry in selected])
    use_groups=[]
    for entry in sorted([entry for entry in emitted['USE'] if entry[0]['family']=='WORLD_STATE'],key=lambda entry:entry[0]['delta_order']):
        if (use_groups and use_groups[-1][-1][0]['role']==entry[0]['role'] and
                not use_groups[-1][-1][0]['standalone'] and not entry[0]['standalone']):use_groups[-1].append(entry)
        else:use_groups.append([entry])
    turn_contributions=sorted([entry for entry in emitted['USE'] if entry[0]['family']=='TURN_CONTEXT'],key=lambda entry:entry[0]['delta_order'])
    if turn_contributions:use_groups.append(turn_contributions)
    phases={}
    for name,groups in (('LOAD',load_groups),('USE',use_groups)):
        supplied=record['phases'][name]
        require(type(supplied) is dict and set(supplied)=={'wire','empty_prefix_proof'},'Context phase wire/empty proof differs')
        wire=supplied['wire'];clock=wire.get('create_time') if type(wire) is dict else None
        require(type(wire) is dict and set(wire)=={'id','phase','turn_id','create_time'} and
            wire['id'] in ('opaque_nonempty','absent_or_null','absent','null') and wire['phase']=='absent_or_null' and
            wire['turn_id'] in ('required_active','optional_active') and type(clock) is dict and set(clock)=={'required','minimum','maximum'} and
            type(clock['required']) is bool and all(type(clock[key]) in (int,float) and math.isfinite(clock[key]) for key in ('minimum','maximum')) and
            0<=clock['minimum']<=clock['maximum']<=clock['minimum']+60,'Source-supported context wire/time behavior is unbound')
        empty=supplied['empty_prefix_proof']
        if groups:require(empty is None,'Nonempty context cannot carry an empty-prefix substitute')
        else:
            proof=document(empty)
            require(type(proof) is dict and set(proof)=={'schema','origin','phase','basis_sha256','producer_receipts'} and
                proof['schema']=='native-context-empty-v1' and proof['origin']=='INDEPENDENT_SOURCE_INPUT' and proof['phase']==name and
                proof['basis_sha256']==basis_sha256 and proof['producer_receipts']==[producer['receipts'][name] for producer in producers],
                'Empty context lacks a complete independent omission-branch proof')
        phases[name]={'phase':name,'mode':'INITIAL' if name=='LOAD' else 'DIFF',
            'previous_state_sha256':None if name=='LOAD' else digest(phase_states['LOAD']),
            'state_sha256':digest(phase_states[name]),'wire':copy.deepcopy(wire),'empty_prefix_proof':copy.deepcopy(empty),
            'rows':[row(group) for group in groups]}
    return {'schema':'native-context-contract-v1','scope':record['scope'],'source_commit':record['source_commit'],
        'source_input':copy.deepcopy(source_input),'basis_sha256':basis_sha256,'custody':[custody[key] for key in sorted(custody)],'phases':phases}


def checked_pin(value):
    if not isinstance(value, dict) or set(value) != {'path', 'bytes', 'sha256'}:
        raise ValueError('exact file pin required')
    if type(value['bytes']) is not int or value['bytes'] < 0:
        raise ValueError('invalid byte count')
    if pin(value['path']) != value:
        raise ValueError('file pin mismatch')
    return path_literal(value['path'])


def path_literal(value):
    if not isinstance(value, str) or not PureWindowsPath(value).is_absolute():
        raise ValueError('absolute Windows path required')
    if any(c in value for c in ('\n', '\r', '\x00', '*', '?')) or '..' in PureWindowsPath(value).parts:
        raise ValueError('nonliteral path')
    return str(PureWindowsPath(value)).replace('\\', '/')


def toml(value):
    if isinstance(value, bool): return str(value).lower()
    if type(value) is int and value >= 0: return str(value)
    if isinstance(value, str): return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list): return '[' + ','.join(toml(x) for x in value) + ']'
    if isinstance(value, dict):
        return '{' + ','.join(toml(k) + '=' + toml(v) for k, v in value.items()) + '}'
    raise ValueError('unsupported TOML value')


def no_skill_mentions(inputs):
    if not isinstance(inputs, list) or len(inputs) != 1 or set(inputs[0]) != {'type', 'text', 'text_elements'}:
        raise ValueError('one literal text input required')
    row = inputs[0]
    if row['type'] != 'text' or not isinstance(row['text'], str) or row['text_elements'] != []:
        raise ValueError('structured mention/image/skill input forbidden')
    # Conservative bounded restriction on this transport's prompts. Source bytes
    # arrive in the command output; they are not scanned/replaced or re-authored.
    if '$' in row['text'] or 'skill://' in row['text'].lower() or '](' in row['text']:
        raise ValueError('explicit skill/link mention syntax in input')


def local_environment(cwd):
    cwd = str(PureWindowsPath(path_literal(cwd)))
    return [{'environmentId': 'local', 'cwd': cwd, 'runtimeWorkspaceRoots': []}]


def code_mode_spec(binding, command, expected_output, terminal_text):
    """One literal nested call. This is source selection, never native evidence."""
    cwd = str(PureWindowsPath(path_literal(binding['cwd'])))
    shell = str(PureWindowsPath(path_literal(binding['powershell']['path'])))
    if (type(command) is not str or not command or type(expected_output) is not str or
            not expected_output or len(expected_output.encode('utf-8')) > 65536 or
            type(terminal_text) is not str or not terminal_text or '\n' in terminal_text):
        raise ValueError('Exact command/output/terminal selection required')
    arguments = {'cmd': command, 'shell': shell, 'login': False, 'workdir': cwd,
                 'max_output_tokens': 35000, 'yield_time_ms': 10000}
    source = ('// @exec: {"yield_time_ms":30000,"max_output_tokens":40000}\n'
              'text(await tools.exec_command(' + json.dumps(arguments, separators=(',', ':'), ensure_ascii=True) + '));')
    return {'wrapper_source': source, 'arguments': arguments, 'expected_argv': [shell, '-NoProfile', '-Command', command],
            'cwd': cwd, 'expected_output': expected_output, 'terminal_text': terminal_text}


def silent_use_input(binding):
    spec = code_mode_spec(binding, binding['use_command'], binding['use_expected_output'], binding['use_terminal_text'])
    text = ('Silent USE after the verified ACK for this same held worker: execute exactly this one exec wrapper. '
            'No preamble, discovery, extra wrapper or other call. Do not assess or invoke a skill.\n' +
            spec['wrapper_source'] + '\nOnly after complete successful output, emit one final_answer containing only:\n' +
            binding['use_terminal_text'])
    return [{'type': 'text', 'text': text, 'text_elements': []}]


def silent_load_input(binding, ready_text):
    """Source-owned silent LOAD form for the pinned native provider contract."""
    if type(ready_text) is not str or re.fullmatch(r'LOAD_READY_ONLY [0-9a-f]{64}', ready_text) is None:
        raise ValueError('Exact LOAD readiness token required')
    for path in (binding['python']['path'], binding['loader']['path'], binding['powershell']['path'], binding['cwd']):
        path_literal(path)
    quote = lambda s: "'" + s.replace("'", "''") + "'"
    command = '& ' + quote(binding['python']['path']) + ' -I -S -B ' + quote(binding['loader']['path'])
    if binding['load_command'] != command:
        raise ValueError('Exact silent LOAD invocation differs')
    wrapper = code_mode_spec(binding, command, 'PROMPT_ONLY', ready_text)['wrapper_source']
    text = ('Silent LOAD: your first action must be exactly one exec wrapper containing exactly one exec_command invocation below. '
        'No preamble, capability-discovery prose, tool-discovery calls, or other assistant message may precede it. '
        'Do not assess the source or invoke a skill; read the exact documents as data.\n' +
        wrapper + '\n'
        'Only after that command completes successfully and returns the exact pinned output, emit one final_answer containing only the exact readiness token below. '
        'Do not emit commentary or any other message. If the exact tool is unavailable or the command/output fails, do not claim readiness.\n' + ready_text)
    return [{'type': 'text', 'text': text, 'text_elements': []}]


def mcp_cli_key(name):
    """The bounded native CLI path grammar has no quoted-segment decoding."""
    if not isinstance(name, str) or re.fullmatch(r'[A-Za-z0-9_-]+', name) is None:
        raise ValueError('MCP name is not representable in the bounded native CLI key grammar')
    return 'mcp_servers.' + name + '.enabled'


def cli_override_projection(overrides, mcp_names):
    """Validate this generated subset using literal CLI paths and TOML values.

    rust-v0.153.4 keeps the LHS raw and splits literal dots. Only RHS values
    use TOML parsing. This is not a general CLI parser: ambiguous/duplicate
    generated paths and invalid generated values refuse instead of fallback.
    """
    if not isinstance(overrides, list) or not isinstance(mcp_names, list):
        raise ValueError('Generated CLI override selection malformed')
    for name in mcp_names: mcp_cli_key(name)
    if len(set(mcp_names)) != len(mcp_names):
        raise ValueError('Duplicate MCP name in CLI selection')
    result = {}
    for override in overrides:
        if not isinstance(override, str):
            raise ValueError('Generated CLI override must be a string')
        key, separator, rhs = override.partition('=')
        parts = key.split('.')
        if not separator or any(re.fullmatch(r'[A-Za-z0-9_-]+', part) is None for part in parts):
            raise ValueError('Generated CLI key differs from bounded literal path grammar')
        try:
            parsed = tomllib.loads('value=' + rhs)
            if set(parsed) != {'value'}:
                raise ValueError('Generated CLI RHS contains more than one value')
            value = parsed['value']
        except (ValueError, KeyError):
            raise ValueError('Generated CLI value is not a valid TOML value') from None
        table = result
        for part in parts[:-1]:
            table = table.setdefault(part, {})
            if not isinstance(table, dict):
                raise ValueError('Generated CLI path collides with a value')
        if parts[-1] in table:
            raise ValueError('Duplicate generated CLI override path')
        table[parts[-1]] = value
    expected = {name: {'enabled': False} for name in mcp_names}
    selected = result.get('mcp_servers', {})
    if selected != expected or any(row['enabled'] is not False for row in selected.values()):
        raise ValueError('Generated MCP CLI overrides omit or invent a server or false value')
    return result


def validate_mcp_transport_fields(row):
    """Raw transport types/exclusions from native rust-v0.153.4 mcp_types.rs.

    This validates transport fields after the pinned layers and disabling
    override are merged. Shared tool/timeout policy and full native config
    validity remain separate; unrelated metadata is retained unchanged.
    """
    for field in ('command', 'url', 'cwd', 'bearer_token', 'bearer_token_env_var',
                  'http_headers_helper', 'environment_id', 'oauth_resource', 'auth'):
        if field in row and not isinstance(row[field], str):
            raise ValueError('MCP transport field must be a string: ' + field)
    if 'args' in row and not (isinstance(row['args'], list) and
                              all(isinstance(value, str) for value in row['args'])):
        raise ValueError('MCP args must be a string array')
    for field in ('env', 'http_headers', 'env_http_headers'):
        if field in row and not (isinstance(row[field], dict) and
                all(isinstance(key, str) and isinstance(value, str) for key, value in row[field].items())):
            raise ValueError('MCP transport field must be a string map: ' + field)
    if 'env_vars' in row:
        if not isinstance(row['env_vars'], list):
            raise ValueError('MCP env_vars must be an array')
        for value in row['env_vars']:
            if isinstance(value, str):
                continue
            if (not isinstance(value, dict) or not {'name'} <= set(value) <= {'name', 'source'} or
                    not isinstance(value['name'], str) or
                    ('source' in value and value['source'] not in ('local', 'remote'))):
                raise ValueError('MCP env_vars requires a name and optional local/remote source')
    if 'auth' in row and row['auth'] not in ('oauth', 'chatgpt'):
        raise ValueError('Unsupported MCP auth mode')
    if 'oauth' in row:
        oauth = row['oauth']
        if not isinstance(oauth, dict):
            raise ValueError('MCP oauth must be a table')
        for field in ('client_id', 'callback_url'):
            if field in oauth and not isinstance(oauth[field], str):
                raise ValueError('MCP oauth field must be a string: ' + field)
        if 'callback_port' in oauth and not (type(oauth['callback_port']) is int and
                                              0 <= oauth['callback_port'] <= 65535):
            raise ValueError('MCP oauth callback_port must be an unsigned 16-bit integer')
    if 'command' in row:
        prohibited = {'url', 'bearer_token_env_var', 'bearer_token', 'http_headers_helper',
                      'http_headers', 'env_http_headers', 'oauth', 'oauth_resource', 'auth'}
        if set(row) & prohibited:
            raise ValueError('MCP stdio contains an incompatible HTTP field')
    elif 'url' in row:
        if set(row) & {'args', 'env', 'env_vars', 'cwd', 'bearer_token'}:
            raise ValueError('MCP HTTP contains an incompatible transport field')
        if 'http_headers_helper' in row:
            if not row['http_headers_helper'].strip():
                raise ValueError('MCP http_headers_helper must not be empty')
            if row.get('environment_id', 'local') != 'local':
                raise ValueError('MCP http_headers_helper requires the local environment')


def validate_mcp_transports(projection, mcp_names, layers):
    """Check only pinned MCP tables, in supplied precedence; never write config.

    Exact-key table merge preserves inherited entries, including under an
    empty overlay. The returned shape contains no command, URL or credentials.
    Other native configuration layers and full native validity remain separate.
    """
    for name in mcp_names: mcp_cli_key(name)
    expected = {name: {'enabled': False} for name in mcp_names}
    selected = projection.get('mcp_servers', {})
    if (selected != expected or any(row['enabled'] is not False for row in selected.values()) or
            not isinstance(layers, list)):
        raise ValueError('MCP disable projection differs from exact selected names')
    def merge(lower, upper):
        if isinstance(lower, dict) and isinstance(upper, dict):
            result = copy.deepcopy(lower)
            for key, value in upper.items():
                result[key] = merge(result[key], value) if key in result else copy.deepcopy(value)
            return result
        return copy.deepcopy(upper)
    before = {}
    for layer in layers:
        if not isinstance(layer, dict):
            raise ValueError('Pinned MCP configuration table is malformed')
        before = merge(before, layer)
    if set(before) != set(mcp_names):
        raise ValueError('MCP selection differs from the pinned inherited server population')
    after = merge(before, expected)
    if set(after) != set(before):
        raise ValueError('MCP CLI projection introduces a phantom server')
    shapes = []
    for name in mcp_names:
        original, current = before[name], after[name]
        if not isinstance(original, dict) or not isinstance(current, dict):
            raise ValueError('Pinned MCP server configuration is not a table')
        command = current.get('command'); url = current.get('url')
        command_ok = isinstance(command, str) and bool(command.strip())
        url_ok = isinstance(url, str) and bool(url.strip())
        if not (command_ok or url_ok):
            raise ValueError('Disabled MCP entry lacks inherited command or URL transport')
        validate_mcp_transport_fields(current)
        if (current.get('enabled') is not False or
                {key: value for key, value in original.items() if key != 'enabled'} !=
                {key: value for key, value in current.items() if key != 'enabled'}):
            raise ValueError('MCP CLI projection changed a transport or other inherited field')
        shapes.append({'name': name, 'command_nonempty': command_ok, 'url_nonempty': url_ok, 'enabled_after': False})
    return {'names': list(mcp_names), 'no_phantom_keys': True,
            'transport_fields_preserved': True, 'selected_transport_shapes': shapes,
            'native_qualification': False}


def complete_environment(binding, prescribed, config_source_pins=None, *, purpose=None):
    """Derive the explicitly selected complete map without serializing its value.

    The CLI continues to request only its three prescribed assignments. The
    selected existing HOME entry survives native table merge. Each file is
    hashed and parsed from one captured byte string; no later mutable read is
    used to derive the approved value. This policy grants no native authority.
    """
    if 'complete_environment_policy' in binding and (type(purpose) is not str or purpose != 'ISOLATED_QUALIFICATION'):
        raise ValueError('Complete environment policy requires explicit ISOLATED_QUALIFICATION purpose')
    if set(prescribed) != {'PATH', 'PATHEXT', 'SystemRoot'} or not all(isinstance(v, str) for v in prescribed.values()):
        raise ValueError('Prescribed complete environment fields differ')
    if 'complete_environment_policy' not in binding:
        return dict(prescribed)
    policy_pin = binding['complete_environment_policy']
    def captured(row):
        if (not isinstance(row, dict) or set(row) != {'path', 'bytes', 'sha256'} or
                type(row['bytes']) is not int or row['bytes'] < 0):
            raise ValueError('Complete environment requires an exact file pin')
        path_literal(row['path'])
        raw = Path(row['path']).read_bytes()
        if len(raw) != row['bytes'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
            raise ValueError('Complete environment file pin differs')
        return raw
    if not isinstance(policy_pin, dict) or policy_pin.get('sha256') != COMPLETE_ENVIRONMENT_POLICY_SHA256:
        raise ValueError('Complete environment policy selection differs')
    policy = json.loads(captured(policy_pin))
    home_pin = policy['home_config']
    if config_source_pins is not None and home_pin not in config_source_pins:
        raise ValueError('Approved complete environment HOME source is not selected')
    raw = captured(home_pin)
    try:
        home = tomllib.loads(raw.decode('utf8'))
        entries = home['shell_environment_policy']['set']
    except (ValueError, KeyError, TypeError):
        raise ValueError('Complete environment HOME source is malformed') from None
    approved = policy['approved_existing_entry']
    name = approved['name']
    if not isinstance(entries, dict) or set(entries) != {name} or name in prescribed:
        raise ValueError('Complete environment HOME entry population differs')
    value = entries[name]
    if (not isinstance(value, str) or len(value.encode('utf8')) != approved['value_bytes'] or
            hashlib.sha256(value.encode('utf8')).hexdigest() != approved['value_sha256']):
        raise ValueError('Approved complete environment value differs')
    return dict(prescribed, **{name: value})


def _prepare_profile(binding, config_schema, request_schema, *, purpose=None):
    if 'complete_environment_policy' in binding and (type(purpose) is not str or purpose != 'ISOLATED_QUALIFICATION'):
        raise ValueError('Complete environment policy requires explicit ISOLATED_QUALIFICATION purpose')
    try:
        import jsonschema
        from importlib.metadata import version
    except ImportError as exc:
        raise RuntimeError('existing jsonschema unavailable; no acquisition authorized') from exc
    if version('jsonschema') != '4.26.0':
        raise RuntimeError('jsonschema version differs from pinned 4.26.0')
    runtime = pin(jsonschema.__file__)
    if runtime['sha256'] != 'a7e470e134bfd0e3c76482722260d6b1d5a099de823d61cc5cbabb06e4314c67':
        raise RuntimeError('jsonschema module pin differs')
    required = {'native', 'code_mode_host', 'python', 'powershell', 'python_root', 'cwd', 'load_pins', 'loader',
        'use_pins', 'excluded_paths', 'disabled_skill_paths', 'mcp_names', 'model', 'provider',
        'effort', 'load_input', 'use_input', 'load_command', 'use_command', 'use_expected_output', 'use_terminal_text'}
    if set(binding) not in (required, required | {'complete_environment_policy'}, required | {'context_input'},
            required | {'complete_environment_policy','context_input'}): raise ValueError('binding fields differ')
    if set(binding['load_pins']) != ROLES: raise ValueError('LOAD role population differs')
    if not binding['use_pins']: raise ValueError('USE read selection must be explicit')
    native = checked_pin(binding['native'])
    host = checked_pin(binding['code_mode_host'])
    if PureWindowsPath(host) != PureWindowsPath(native).parent / 'codex-code-mode-host.exe':
        raise ValueError('Code-mode host is not the exact selected CLI companion')
    if (Path(native).parent / 'codex-resources' / 'codex-code-mode-host.exe').exists():
        raise ValueError('Unreviewed bundled code-mode host precedence')
    python = checked_pin(binding['python'])
    powershell = checked_pin(binding['powershell'])
    if PureWindowsPath(powershell).name.lower() not in ('powershell.exe', 'pwsh.exe'):
        raise ValueError('explicit supported PowerShell executable required')
    loader = checked_pin(binding['loader'])
    load_paths = [checked_pin(v) for v in binding['load_pins'].values()] + [loader]
    use_paths = [checked_pin(v) for v in binding['use_pins']]
    excludes = [path_literal(p) for p in binding['excluded_paths']]
    if not excludes: raise ValueError('explicit excluded witness paths required')
    runtime_root = path_literal(binding['python_root'])
    cwd = str(PureWindowsPath(path_literal(binding['cwd'])))
    if not PureWindowsPath(python).is_relative_to(PureWindowsPath(runtime_root)):
        raise ValueError('Python outside pinned runtime root')
    grants = [runtime_root, powershell] + load_paths
    for denied in excludes:
        for grant in grants + use_paths:
            if PureWindowsPath(denied).is_relative_to(PureWindowsPath(grant)) or PureWindowsPath(grant).is_relative_to(PureWindowsPath(denied)):
                raise ValueError('read/exclude overlap')
    if set(map(str.lower, load_paths)) & set(map(str.lower, use_paths)):
        raise ValueError('USE hot inputs overlap LOAD')
    for hot in use_paths:
        if any(PureWindowsPath(hot).is_relative_to(PureWindowsPath(g)) for g in grants):
            raise ValueError('hot input reachable in LOAD grant')
    for key in ('model', 'provider', 'effort'):
        if not isinstance(binding[key], str) or not binding[key]: raise ValueError('model binding missing')
    if (binding['model'], binding['provider'], binding['effort']) != ('gpt-6-astra', 'openai', 'low'):
        raise ValueError('bounded worker model/provider/effort binding differs')
    if not isinstance(binding['mcp_names'], list):
        raise ValueError('selection list malformed')
    mcp_paths = [mcp_cli_key(name) for name in binding['mcp_names']]
    for key in ('mcp_names', 'disabled_skill_paths'):
        if not isinstance(binding[key], list) or len(set(binding[key])) != len(binding[key]):
            raise ValueError('selection list malformed')
    for inputs in (binding['load_input'], binding['use_input']): no_skill_mentions(inputs)
    quote = lambda s: "'" + s.replace("'", "''") + "'"
    command = '& ' + quote(binding['python']['path']) + ' -I -S -B ' + quote(binding['loader']['path'])
    if binding['load_command'] != command:
        raise ValueError('exact isolated reader invocation differs')
    ready = re.search(r'(?:^|\n)(LOAD_READY_ONLY [0-9a-f]{64})\Z', binding['load_input'][0]['text'])
    if ready is None or binding['load_input'] != silent_load_input(binding, ready.group(1)):
        raise ValueError('Source-owned silent LOAD input differs')
    if binding['use_input'] != silent_use_input(binding):
        raise ValueError('Source-owned silent USE input differs')
    flat = [('default_permissions', 'worker_load'), ('windows.sandbox', 'elevated'),
        ('notify', []), ('allow_login_shell', False), ('web_search', 'disabled'),
        ('tool_output_token_limit', 40000)]
    flat += [('features.' + k, False) for k in DISABLED_FEATURES]
    shell_dir = str(PureWindowsPath(binding['powershell']['path']).parent)
    prescribed = {'PATH': shell_dir, 'PATHEXT': '.EXE', 'SystemRoot': 'C:\\Windows'}
    complete_environment(binding, prescribed, purpose=purpose)
    flat += [('shell_environment_policy.inherit', 'none'),
        ('shell_environment_policy.set', prescribed)]

    flat += [('orchestrator.mcp.enabled', False), ('orchestrator.skills.enabled', False),
        ('memories.generate_memories', False), ('memories.use_memories', False),
        ('skills.bundled.enabled', False), ('skills.include_instructions', False),
        ('skills.config', [{'path': path_literal(p), 'enabled': False} for p in binding['disabled_skill_paths']])]
    flat += [(path, False) for path in mcp_paths]
    for name, selected in [('worker_load', grants), ('worker_use', grants + use_paths)]:
        fs = {':root': 'deny', ':minimal': 'read'}
        fs.update({p: 'read' for p in selected})
        fs.update({p: 'deny' for p in excludes})
        flat += [('permissions.' + name + '.filesystem', fs), ('permissions.' + name + '.network.enabled', False)]
    overrides = [k + '=' + toml(v) for k, v in flat]
    config = cli_override_projection(overrides, binding['mcp_names'])
    jsonschema.validate(config, config_schema)
    common = {'cwd': cwd, 'approvalPolicy': 'never', 'environments': local_environment(cwd), 'model': binding['model']}
    thread = {'id': 4, 'method': 'thread/start', 'params': dict(common,
        permissions='worker_load', ephemeral=True, experimentalRawEvents=True, modelProvider=binding['provider'],
        allowProviderModelFallback=False)}
    turns = []
    for request_id, profile, inputs in [(5, 'worker_load', binding['load_input']), (6, 'worker_use', binding['use_input'])]:
        turns.append({'id': request_id, 'method': 'turn/start', 'params': dict(common,
            threadId='__FRESH_THREAD_ID__', permissions=profile, effort=binding['effort'], input=inputs)})
    for request in [thread] + turns: jsonschema.validate(request, request_schema)
    return {'status': 'SOURCE_PROPOSAL_ONLY', 'native_qualification': 'NOT_RUN',
        'native_attempt_enabled': False, 'profile_overrides': overrides,
        'server_argv': [native, 'app-server'] + [x for s in overrides for x in ('--config', s)],
        'server_cwd': cwd, 'thread_start': thread, 'turn_start': turns[0], 'use_turn_start': turns[1],
        'load_tool_arguments': code_mode_spec(binding, command, 'PROPOSAL_ONLY', ready.group(1))['arguments'],
        'expected_profiles': ['worker_load', 'worker_use'], 'jsonschema_runtime': runtime,
        'effective_config_projection': config, 'binding_sha256': hashlib.sha256(
            json.dumps(binding,sort_keys=True,separators=(',',':')).encode()).hexdigest()}


def prepare_context_basis(binding, config_schema, request_schema, *, purpose=None):
    """Cold first pass for the independent producer binder, never an invocable plan."""
    proposal=_prepare_profile(binding,config_schema,request_schema,purpose=purpose)
    return {'status':'CONTEXT_INPUT_REQUIRED','native_attempt_enabled':False,
        'basis_sha256':context_basis(binding,proposal),'profile_proposal_without_context':proposal}


def prepare(binding, config_schema, request_schema, *, purpose=None):
    proposal=_prepare_profile(binding,config_schema,request_schema,purpose=purpose)
    proposal['context_contract']=context_contract_from_input(binding,context_basis(binding,proposal),purpose=purpose)
    return proposal


def require_native_acceptance(*args, **kwargs):
    raise RuntimeError('proposal has no native acceptance authority; integrate reviewed same-process readback before any LOAD')
