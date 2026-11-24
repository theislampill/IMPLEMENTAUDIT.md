"""Explicit source-bound canonical stdout field relations; all other bytes survive."""
import copy
import json
import math
import re


class Refusal(ValueError):
    pass


def demand(value, code):
    if not value:
        raise Refusal(code)


def encoded(value, *, indent=None, sort_keys=True):
    return json.dumps(value, indent=indent, sort_keys=sort_keys, allow_nan=False).encode()


def duration(value):
    demand(type(value) in (int, float) and math.isfinite(value) and value >= 0, 'DIAGNOSTIC_DURATION_DOMAIN')


def cost(value, profile):
    demand(set(value) == {'scope', 'source_sha256', 'tests', 'failures', 'errors', 'metrics'}, 'REPOSITORY_COST_FIELDS')
    demand(value['source_sha256'] == profile['source_files']['scripts/operational-evidence.py']['sha256'] and
           value['tests'] == 17 and value['failures'] == value['errors'] == 0, 'REPOSITORY_COST_SOURCE_OR_RESULT')
    demand(set(value['metrics']) == set(profile['repository_cost_metrics']), 'REPOSITORY_COST_POPULATION')
    result = copy.deepcopy(value)
    raw_durations = {}
    for name, metric in value['metrics'].items():
        demand(set(metric) == {'python_parses', 'secure_reads', 'stability_fences', 'git_reads', 'seconds'},
               'REPOSITORY_COST_METRIC_FIELDS')
        demand(all(type(metric[k]) is int and metric[k] >= 0 for k in metric if k != 'seconds'), 'REPOSITORY_COST_COUNTER_DOMAIN')
        duration(metric['seconds']); raw_durations[name] = metric['seconds']
        result['metrics'][name]['seconds'] = '<DECLARED_REPOSITORY_DIAGNOSTIC_SECONDS>'
    # Keep the original source assertions as explicit independent readback.
    for name, key, expected in [('release', 'python_parses', 1), ('secure_reader_counter', 'secure_reads', 2),
                                ('constructed_publication', 'python_parses', 1), ('repository', 'stability_fences', 3),
                                ('next_transaction', 'python_parses', 1)]:
        demand(value['metrics'][name][key] == expected, 'REPOSITORY_COST_ASSERTION')
    return result, raw_durations


def composition(value, profile):
    demand(set(value) == {'scope', 'current_source_gate', 'native_admission', 'sources', 'transport_sha256',
                          'source_controls', 'commands'}, 'COMPOSITION_FIELDS')
    demand(value['current_source_gate'] == 'EXACT_CURRENT_CORE_POSIX_SOURCE_SELECTED' and
           value['native_admission'] == 'NOT_ESTABLISHED' and
           value['sources'] == profile['historical_composition_sources'] and
           value['transport_sha256'] == profile['source_files']['scripts/work-graph-continuity-transport.py']['sha256'] and
           value['source_controls'] == ['omitted-member', 'extra-member', 'reordered-members', 'changed-buffer',
                                       'mutable-population', 'foreign-path'], 'COMPOSITION_SOURCE_OR_AUTHORITY')
    result = copy.deepcopy(value)
    commands = ['--current-controller', '--require-current-continuity', '--verify-resume-receipt']
    demand(type(value['commands']) is list and len(value['commands']) == 3, 'COMPOSITION_POPULATION')
    repository = source_root = None
    for original, changed, command in zip(value['commands'], result['commands'], commands):
        demand(set(original) == {'command', 'status', 'closure'} and original['command'] == command and
               original['status'] == 'PASS', 'COMPOSITION_COMMAND')
        closure = original['closure']
        demand(set(closure) == {'schema', 'repository', 'members', 'startup'} and
               closure['schema'] == 'implementaudit.continuity-source-closure.v2', 'COMPOSITION_CLOSURE')
        demand(type(closure['repository']) is str and re.fullmatch(r'/tmp/work-graph-composition-[a-z0-9_]{8}/repository', closure['repository']),
               'COMPOSITION_REPOSITORY_ROLE')
        repository = repository or closure['repository']
        demand(repository == closure['repository'] and closure['startup'] == {
            'profile': 'ISOLATED_CPYTHON_V1', 'isolated': True, 'no_site': True, 'dont_write_bytecode': True},
            'COMPOSITION_STARTUP_OR_COUPLING')
        demand(len(closure['members']) == 6, 'COMPOSITION_MEMBER_POPULATION')
        changed['closure']['repository'] = '<COMPOSITION_REPOSITORY>'
        for row, normalized, pin in zip(closure['members'], changed['closure']['members'], profile['historical_composition_sources']):
            demand(set(row) == {'name', 'path', 'bytes', 'sha256', 'mode', 'links', 'readonly', 'seals'}, 'COMPOSITION_MEMBER_FIELDS')
            name, size, digest, mode = pin
            demand([row['name'], row['bytes'], row['sha256'], row['mode']] == pin and
                   row['links'] == 1 and row['readonly'] is True and row['seals'] == 15, 'COMPOSITION_MEMBER_BINDING')
            suffix = '/skills/implementaudit/scripts/' + name
            demand(type(row['path']) is str and row['path'].endswith(suffix), 'COMPOSITION_SOURCE_ROLE')
            prefix = row['path'][:-len(suffix)]
            demand(re.fullmatch(r'/tmp/historical-continuity-engine-[a-z0-9_]{8}', prefix), 'COMPOSITION_SOURCE_ROLE')
            source_root = source_root or prefix
            demand(source_root == prefix, 'COMPOSITION_SOURCE_COUPLING')
            normalized['path'] = '<COMPOSITION_HISTORICAL_SOURCE>' + suffix
    return result


def turn_disposition(value, profile):
    expected = profile['turn_disposition_cases']
    demand(set(value) == {'passed', 'total', 'results'} and value['passed'] == value['total'] == len(expected) and
           len(value['results']) == len(expected), 'TURN_REPORT_POPULATION')
    result = copy.deepcopy(value)
    root = None
    for row, changed, slot in zip(value['results'], result['results'], expected):
        demand(set(row) == {'case', 'expected_accept', 'exit', 'pass', 'output'} and
               row['case'] == slot['case'] and row['expected_accept'] is slot['expected_accept'] and row['pass'] is True and
               type(row['exit']) is int and ((row['exit'] == 0) is row['expected_accept']) and type(row['output']) is str,
               'TURN_REPORT_CASE')
        matches = list(re.finditer(r'/tmp/turn-disposition-[a-z0-9_]{8}(?=/)', row['output']))
        for match in matches:
            root = root or match.group(0)
            demand(root == match.group(0), 'TURN_ALLOCATION_COUPLING')
            tail = row['output'][match.end()+1:]
            demand(any(tail.startswith(name + '/') or tail == name for name in (slot['case'], slot['case'] + '-skill')),
                   'TURN_CASE_PATH_ROLE')
        for match in reversed(matches):
            changed['output'] = changed['output'][:match.start()] + '<TURN_FIXTURE_ROOT>' + changed['output'][match.end():]
    return result


def d48(raw):
    prefix = b'D48_RESULT_PREFIX_CAPTURE='
    lines = [line for line in raw.splitlines(keepends=True) if line.startswith(prefix)]
    demand(len(lines) == 1, 'D48_DECLARED_SLOT_POPULATION')
    line = lines[0]
    value = json.loads(line[len(prefix):])
    demand(type(value) is list and len(value) == 2 and line == prefix + encoded(value) + b'\n', 'D48_CAPTURE_ENCODING')
    result = copy.deepcopy(value); allocation = None
    for row, changed, suffix in zip(value, result, ('result.json', 'result.tmp')):
        demand(set(row) == {'path', 'completed_count', 'serialized_count'} and
               type(row['completed_count']) is int and row['completed_count'] > 0 and
               row['completed_count'] == row['serialized_count'], 'D48_CAPTURE_FIELDS')
        match = re.fullmatch(r'(\.IMPLEMENTAUDIT/runs/d48-fence-[A-Za-z0-9]{6}/mutation-transactions/[0-9a-f]{32}-p1-s1)/' + re.escape(suffix), row['path'])
        demand(match is not None, 'D48_TRANSACTION_ROLE')
        allocation = allocation or match.group(1)
        demand(allocation == match.group(1), 'D48_TRANSACTION_COUPLING')
        changed['path'] = '<D48_TRANSACTION>/' + suffix
    return raw.replace(line, prefix + encoded(result) + b'\n', 1)


def build_paths(raw, profile):
    lines = raw.splitlines(keepends=True)
    package = [i for i, line in enumerate(lines) if line.startswith(b'package-contract: wrote /tmp/')]
    checksums = [i for i, line in enumerate(lines) if line.startswith(b'write-release-checksums: wrote /tmp/')]
    groups = profile['build_groups']
    demand(len(package) == 2 * len(groups) and len(checksums) == sum(len(g['checksums']) for g in groups),
           'BUILD_DECLARED_SLOT_POPULATION')
    roots, expected_checksums = [], []
    for ordinal, group in enumerate(groups):
        suffix = '/' + group['subdir'] if group['subdir'] else ''
        first, second = package[ordinal*2:ordinal*2+2]
        match = re.fullmatch(rb'package-contract: wrote (/tmp/tmp\.[A-Za-z0-9]{10})' + re.escape((suffix + '/IMPLEMENTAUDIT.plugin.zip\n').encode()), lines[first])
        demand(match is not None, 'BUILD_ROOT_ROLE')
        root = match.group(1)
        demand(lines[second] == b'package-contract: wrote ' + root + (suffix + '/IMPLEMENTAUDIT.skill\n').encode(), 'BUILD_MEMBER_ORDER')
        demand(root not in roots, 'BUILD_DISTINCT_ALLOCATION_ROLES'); roots.append(root)
        token = ('<BUILD_' + group['role'].upper() + '>').encode()
        lines[first] = lines[first].replace(root, token, 1)
        lines[second] = lines[second].replace(root, token, 1)
        expected_checksums.extend((b'write-release-checksums: wrote ' + root + b'/' + name.encode() + b'\n',
                                   b'write-release-checksums: wrote ' + token + b'/' + name.encode() + b'\n')
                                  for name in group['checksums'])
    for index, (expected, replacement) in zip(checksums, expected_checksums):
        demand(lines[index] == expected, 'BUILD_CHECKSUM_ROLE_ORDER'); lines[index] = replacement
    for label, group_index, suffix in [
        (b'install-codex-from-release: installed IMPLEMENTAUDIT.skill into ', 1, b'/codex home with spaces/skills/implementaudit\n'),
        (b'install-claude-from-release: copied IMPLEMENTAUDIT.skill files into ', 2, b'/claude host root with spaces/skills/implementaudit\n')]:
        found = [i for i, line in enumerate(lines) if line.startswith(label)]
        demand(len(found) == 1 and lines[found[0]] == label + roots[group_index] + suffix, 'INSTALL_DECLARED_ROLE')
        lines[found[0]] = label + ('<BUILD_' + groups[group_index]['role'].upper() + '>').encode() + suffix
    pack_lines = [i for i, line in enumerate(lines) if line.startswith(b'build-source-evidence-pack: wrote ')]
    demand(len(pack_lines) == profile['source_pack_slots'], 'SOURCE_PACK_SLOT_POPULATION')
    packs = set()
    for ordinal, index in enumerate(pack_lines):
        match = re.fullmatch(rb'build-source-evidence-pack: wrote (/tmp/tmp\.[A-Za-z0-9]{10})/IMPLEMENTAUDIT-SOURCE-EVIDENCE.zip\n', lines[index])
        demand(match is not None and match.group(1) not in packs, 'SOURCE_PACK_ALLOCATION_ROLE')
        packs.add(match.group(1))
        lines[index] = b'build-source-evidence-pack: wrote <SOURCE_PACK_' + str(ordinal).encode() + b'>/IMPLEMENTAUDIT-SOURCE-EVIDENCE.zip\n'
    return b''.join(lines)


def normalize(raw, profile, evidence, pending):
    demand(type(raw) is bytes and len(raw) <= 128 * 1024**2 and
           profile.get('schema') == 'dg16.full-output-role-profile.proposed.v1', 'STDOUT_INPUT_PROFILE')
    seen, edits, observations = {}, [], {}
    for start, end, value in evidence.documents(raw):
        role = None
        if value.get('scope') == 'CONSTRUCTED_REPOSITORY_CONTROLS_NOT_NATIVE_ACCEPTANCE_OR_BUDGET': role = 'repository_cost'
        elif value.get('scope') == 'CURRENT_ENGINE_HISTORICAL_SIX_SOURCE_INPUTS': role = 'composition'
        elif set(value) == {'passed', 'total', 'results'} and value.get('results') and value['results'][0].get('case') == profile['turn_disposition_cases'][0]['case']: role = 'turn_disposition'
        else:
            for name in evidence.ROLES:
                if value == pending[name]['report']: role = name
        if role is None: continue
        demand(role not in seen, 'DUPLICATE_CANONICAL_ROLE'); seen[role] = True
        indent, sort_keys = (2, False) if role == 'turn_disposition' else (None, True)
        demand(raw[start:end] == encoded(value, indent=indent, sort_keys=sort_keys), 'CANONICAL_ROLE_ENCODING')
        if role == 'repository_cost': changed, observations[role] = cost(value, profile)
        elif role == 'composition': changed = composition(value, profile)
        elif role == 'turn_disposition': changed = turn_disposition(value, profile)
        else:
            changed = copy.deepcopy(value); changed['evidence_dir'] = '<' + role.upper() + '_ARTIFACT_ROOT>'
        edits.append((start, end, encoded(changed, indent=indent, sort_keys=sort_keys)))
    demand(set(seen) == {'repository_cost', 'composition', 'turn_disposition', *evidence.ROLES}, 'CANONICAL_ROLE_POPULATION')
    normalized = raw
    for start, end, replacement in reversed(edits): normalized = normalized[:start] + replacement + normalized[end:]
    normalized = d48(normalized)
    normalized = build_paths(normalized, profile)
    return normalized, observations
