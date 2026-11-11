"""Closed public projection for the existing bounded job-log evidence route."""
import hashlib
import json
import re

ALLOWLIST_SHA = 'f3692f04e93cb8bc260579f037e10924037eef390629150860070a132bf76103'
OBSERVER_SHA = '6905748ac568e310bbda01f7f683d6128e916d407f803e850073f40e7151ed8e'
EXECUTOR_SHA = 'b2ca6122d61d3238c853fdbf1d1c6b23e7808b2dbd18e241d41e3b310c44145a'
SOURCE = '64219c67e9f1dc1e54c6be9ed8e56f26ab313606'
TREE = '1dacef701f3999d1f7990311c96c546446e092f7'
MODE_REFUSAL = 'C5 selected image directory mode differs from its fixed profile'
MARKER = b'DG16_SELECTED_DIRECTORY_MODES '
LOG_BOUND = 16384


def need(value, reason):
    if not value:
        raise ValueError(reason)


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('ascii')


def parse(raw, limit):
    need(type(raw) is bytes and 0 < len(raw) <= limit, 'MODE_DIAGNOSTIC_BODY_BOUND')

    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'MODE_DIAGNOSTIC_DUPLICATE_KEY')
            result[key] = value
        return result

    def nonfinite(_):
        raise ValueError('MODE_DIAGNOSTIC_NONFINITE')

    return json.loads(raw, object_pairs_hook=pairs, parse_constant=nonfinite)


def allowed(allowlist_raw):
    need(hashlib.sha256(allowlist_raw).hexdigest() == ALLOWLIST_SHA, 'MODE_DIAGNOSTIC_ALLOWLIST_PIN')
    value = parse(allowlist_raw, LOG_BOUND)
    need(value['source_commit'] == SOURCE, 'MODE_DIAGNOSTIC_ALLOWLIST_SUBJECT')
    return {name: name for name in value['public_directories']}


def mode_ok(value):
    return type(value) is str and re.fullmatch(r'[0-7]{4}', value) is not None and value != '0755'


def project_public(private_raw, allowlist_raw):
    paths = allowed(allowlist_raw)
    private = parse(private_raw, 4 * 1024**2)
    need(set(private) == {'schema', 'authority', 'source', 'executor_sha256',
         'first_topology_only', 'captured_directories', 'layout_mode_gate',
         'original_failure', 'stop', 'private_mismatch_rows'}, 'MODE_DIAGNOSTIC_PRIVATE_SCHEMA')
    need(private['schema'] == 'dg16.c5-private-selected-directory-modes.v1'
         and private['authority'] == 'NONE' and private['source'] == {'source_commit': SOURCE, 'source_tree': TREE}
         and private['executor_sha256'] == EXECUTOR_SHA
         and private['first_topology_only'] is True
         and private['stop'] == 'BEFORE_SECOND_TOPOLOGY_LAUNCHER_OR_IMAGE', 'MODE_DIAGNOSTIC_PRIVATE_BINDING')
    count = private['captured_directories']
    rows = private['private_mismatch_rows']
    need(type(count) is int and 0 < count <= 4096 and type(rows) is list and len(rows) <= count,
         'MODE_DIAGNOSTIC_POPULATION')
    need((private['layout_mode_gate'], private['original_failure']) ==
         (('REFUSED', MODE_REFUSAL) if rows else ('PASSED', None)), 'MODE_DIAGNOSTIC_ORIGINAL_GUARD')
    names = set()
    public = []
    for row in rows:
        need(type(row) is dict and set(row) == {'path', 'mode', 'expected'}
             and type(row['path']) is str and row['path'] not in names
             and mode_ok(row['mode']) and row['expected'] == '0755', 'MODE_DIAGNOSTIC_PRIVATE_ROW')
        name = row['path']
        names.add(name)
        if name in paths:
            # Only reproduce the string from the pinned public table.
            public.append(dict(path=paths[name], observed_mode=row['mode'], expected_mode='0755'))
    withheld = len(rows) - len(public)
    value = dict(schema='dg16.selected-public-directory-modes.v1', authority='NONE',
                 source_commit=SOURCE, source_tree=TREE, executor_sha256=EXECUTOR_SHA,
                 observer_sha256=OBSERVER_SHA, allowlist_sha256=ALLOWLIST_SHA,
                 first_topology_only=True, new_observation_only=True,
                 captured_directories=count, layout_mode_gate=private['layout_mode_gate'],
                 mismatch_count=len(rows), public_rows=sorted(public,key=lambda row:row['path']),
                 unmapped_count=withheld, exact_mismatch_identities_complete=(withheld == 0))
    need(len(encode(value)) <= LOG_BOUND, 'MODE_DIAGNOSTIC_PUBLIC_BOUND')
    return value


def checked_context(context):
    need(type(context) is dict and set(context) == {'run_id', 'run_attempt', 'head_sha',
         'image_os', 'image_version'}, 'MODE_DIAGNOSTIC_LOG_CONTEXT')
    need(type(context['run_id']) is int and 0 < context['run_id'] < 10**20
         and type(context['run_attempt']) is int and context['run_attempt'] == 1
         and type(context['head_sha']) is str and re.fullmatch('[0-9a-f]{40}',context['head_sha']) is not None
         and context['image_os'] == 'ubuntu24'
         and type(context['image_version']) is str and re.fullmatch(r'[0-9.]{1,40}',context['image_version']) is not None,
         'MODE_DIAGNOSTIC_LOG_CONTEXT')
    return context


def make_log_marker(private_raw, allowlist_raw, actual_context):
    value = project_public(private_raw, allowlist_raw)
    marker = MARKER + encode(dict(context=checked_context(actual_context), observation=value)) + b'\n'
    need(len(marker) <= LOG_BOUND, 'MODE_DIAGNOSTIC_LOG_BOUND')
    return marker


def receive_log_marker(marker, allowlist_raw, actual_context):
    """Validate one exact line extracted from the authenticated job log."""
    paths = allowed(allowlist_raw)
    need(type(marker) is bytes and len(marker) <= LOG_BOUND and marker.startswith(MARKER)
         and marker.endswith(b'\n') and marker.count(b'\n') == 1, 'MODE_DIAGNOSTIC_LOG_MARKER')
    value = parse(marker[len(MARKER):], LOG_BOUND)
    need(type(value) is dict and set(value) == {'context','observation'}
         and checked_context(value['context']) == checked_context(actual_context)
         and MARKER + encode(value) + b'\n' == marker, 'MODE_DIAGNOSTIC_LOG_BINDING')
    obs = value['observation']
    fixed = dict(schema='dg16.selected-public-directory-modes.v1', authority='NONE',
                 source_commit=SOURCE, source_tree=TREE, executor_sha256=EXECUTOR_SHA,
                 observer_sha256=OBSERVER_SHA, allowlist_sha256=ALLOWLIST_SHA,
                 first_topology_only=True, new_observation_only=True)
    variable = {'captured_directories','layout_mode_gate','mismatch_count','public_rows',
                'unmapped_count','exact_mismatch_identities_complete'}
    need(type(obs) is dict and set(obs) == set(fixed)|variable and all(
         type(obs[k]) is type(v) and obs[k] == v for k,v in fixed.items()), 'MODE_DIAGNOSTIC_PUBLIC_BINDING')
    count, total, withheld = (obs[k] for k in ('captured_directories','mismatch_count','unmapped_count'))
    public = obs['public_rows']
    need(type(count) is type(total) is type(withheld) is int and 0 < count <= 4096
         and type(public) is list and 0 <= withheld <= total <= count
         and len(public) + withheld == total, 'MODE_DIAGNOSTIC_PUBLIC_COUNT')
    seen=[]
    for row in public:
        need(type(row) is dict and set(row)=={'path','observed_mode','expected_mode'}
             and type(row['path']) is str and row['path'] in paths
             and mode_ok(row['observed_mode']) and row['expected_mode']=='0755', 'MODE_DIAGNOSTIC_PUBLIC_ROW')
        seen.append(row['path'])
    need(seen == sorted(set(seen)) and obs['layout_mode_gate'] == ('REFUSED' if total else 'PASSED')
         and obs['exact_mismatch_identities_complete'] is (withheld == 0), 'MODE_DIAGNOSTIC_PUBLIC_DISPOSITION')
    return obs
