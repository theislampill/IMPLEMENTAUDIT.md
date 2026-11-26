"""Observe a failed full stdout relation without supplying comparator bytes.

Source roles are validated output intervals, never authenticated emitters.
Only the separately bounded private result contains byte windows or arbitrary
JSON keys. The public result has a closed vocabulary and descriptor-only data.
"""
import base64
import copy
import hashlib
import json
import re


LIMIT = 128 * 1024**2
MODES = ('legacy', 'dag')
SOURCE_ROLES = {
    'repository_cost': 'fixtures/operational-evidence/repository-fence-cost-controls.py',
    'composition': 'tests/work-graph-composition-cases.py',
    'turn_disposition': 'tests/turn-disposition-cases.py',
    'pending_durability': 'tests/cognition-pending-durability.py',
    'pending_loader': 'tests/cognition-pending-loader.py',
    'd48': 'tests/distributed_generation_fence.py',
    'repro_progress': 'scripts/build-release-asset.sh',
    'build_release_asset': 'tests/release-asset.test.sh',
    'build_codex_install': 'tests/release-asset-install.test.sh',
    'build_claude_install': 'tests/release-asset-install-claude.test.sh',
    'build_plugin_install': 'tests/plugin-install.test.sh',
    'build_release_check': 'scripts/build-release-asset.sh',
    'source_pack': 'scripts/build-source-evidence-pack.sh',
}
FIELD_TOKENS = frozenset('scope source_sha256 tests failures errors metrics python_parses secure_reads '
    'stability_fences git_reads seconds release secure_reader_counter constructed_publication repository '
    'next_transaction current_source_gate native_admission sources transport_sha256 source_controls '
    'commands command status closure schema members startup profile isolated no_site dont_write_bytecode '
    'name path bytes sha256 mode links readonly seals passed total results case expected_accept exit pass '
    'output completed_count serialized_count evidence_dir'.split())
BINDING_KEYS = {'source_commit', 'source_tree', 'role_profile_sha256', 'receiver_inputs_sha256',
                'source_manifest_sha256', 'pair_plan_sha256', 'runtime_observation_sha256'}


class Refusal(ValueError):
    pass


def demand(value, code):
    if not value:
        raise Refusal('STDOUT_LOCATION_' + code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def desc(raw):
    return {'bytes': len(raw), 'sha256': sha(raw)}


def encode(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()


def digest(value, length=64):
    return type(value) is str and re.fullmatch('[0-9a-f]{' + str(length) + '}', value) is not None


def number(value, maximum):
    return type(value) is int and 0 <= value <= maximum


def descriptor(value, maximum=LIMIT):
    return type(value) is dict and set(value) == {'bytes', 'sha256'} and \
        number(value['bytes'], maximum) and digest(value['sha256'])


def context(normalizer, pending):
    """Copy only actual received operands; never rerun or increment the normalizer."""
    replacements = []
    for lane in 'ab':
        for label, member in [('package-contract: wrote ', normalizer.e.MEMBERS[0]),
                              ('package-contract: wrote ', normalizer.e.MEMBERS[1]),
                              ('write-release-checksums: wrote ', normalizer.e.MEMBERS[2])]:
            operand = str(normalizer.rroot / ('out-' + lane) / member)
            replacements.append(((label + operand + '\n').encode(),
                                 (label + normalizer.repro_aliases[operand] + '\n').encode()))
    return {'repro_replacements': replacements,
            'pending': {role: {'report': copy.deepcopy(pending[role]['report'])}
                        for role in ('pending_durability', 'pending_loader')}}


def stage(before, edits):
    """Apply an ordered, nonoverlapping edit census and retain its byte map."""
    cursor = total = 0
    chunks, mapped = [], []
    for start, end, replacement, role, json_prefix in sorted(edits, key=lambda row: row[0]):
        demand(type(replacement) is bytes and cursor <= start < end <= len(before), 'EDIT_RANGE')
        unchanged = before[cursor:start]
        chunks.extend((unchanged, replacement)); total += len(unchanged)
        mapped.append(dict(start=start, end=end, after_start=total,
            after_end=total + len(replacement), replacement=replacement, role=role,
            json_prefix=json_prefix))
        total += len(replacement); cursor = end
    chunks.append(before[cursor:])
    return dict(before=before, after=b''.join(chunks), edits=mapped)


def line_stage(before, after, role):
    left, right = before.splitlines(keepends=True), after.splitlines(keepends=True)
    demand(len(left) == len(right), 'LINE_POPULATION')
    edits, cursor = [], 0
    for a, b in zip(left, right):
        if a != b:
            name, prefix = role(b)
            edits.append((cursor, cursor + len(a), b, name, prefix))
        cursor += len(a)
    result = stage(before, edits)
    demand(result['after'] == after, 'LINE_RECONSTRUCTION')
    return result


def trace(raw, ctx, stdout, profile, evidence):
    """Independently reconstruct precisely the already-adopted transformations."""
    edits, replacements = [], ctx['repro_replacements']
    demand(type(replacements) is list and len(replacements) == 6, 'REPRO_POPULATION')
    lines = raw.splitlines(keepends=True)
    offsets, cursor = [], 0
    for line in lines:
        offsets.append(cursor); cursor += len(line)
    for old, new in replacements:
        demand(type(old) is bytes and type(new) is bytes and lines.count(old) == 1, 'REPRO_OPERAND')
        index = lines.index(old)
        edits.append((offsets[index], offsets[index] + len(old), new, 'repro_progress', None))
    stages = [stage(raw, edits)]
    before = stages[-1]['after']; seen, edits = set(), []
    for start, end, value in evidence.documents(before):
        role = None
        if value.get('scope') == 'CONSTRUCTED_REPOSITORY_CONTROLS_NOT_NATIVE_ACCEPTANCE_OR_BUDGET':
            role = 'repository_cost'
        elif value.get('scope') == 'CURRENT_ENGINE_HISTORICAL_SIX_SOURCE_INPUTS':
            role = 'composition'
        elif set(value) == {'passed', 'total', 'results'} and value.get('results') and \
                value['results'][0].get('case') == profile['turn_disposition_cases'][0]['case']:
            role = 'turn_disposition'
        else:
            for name in evidence.ROLES:
                if value == ctx['pending'][name]['report']:
                    role = name
        if role is None:
            continue
        demand(role not in seen, 'DUPLICATE_ROLE'); seen.add(role)
        indent, sort_keys = (2, False) if role == 'turn_disposition' else (None, True)
        demand(before[start:end] == stdout.encoded(value, indent=indent, sort_keys=sort_keys), 'ROLE_ENCODING')
        if role == 'repository_cost':
            changed = stdout.cost(value, profile)[0]
        elif role == 'composition':
            changed = stdout.composition(value, profile)
        elif role == 'turn_disposition':
            changed = stdout.turn_disposition(value, profile)
        else:
            changed = copy.deepcopy(value)
            changed['evidence_dir'] = '<' + role.upper() + '_ARTIFACT_ROOT>'
        edits.append((start, end, stdout.encoded(changed, indent=indent, sort_keys=sort_keys), role, 0))
    demand(seen == {'repository_cost', 'composition', 'turn_disposition', *evidence.ROLES}, 'ROLE_POPULATION')
    stages.append(stage(before, edits))
    before = stages[-1]['after']
    stages.append(line_stage(before, stdout.d48(before), lambda _: ('d48', len(b'D48_RESULT_PREFIX_CAPTURE='))))
    before = stages[-1]['after']
    def build_role(line):
        for group in profile['build_groups']:
            if ('<BUILD_' + group['role'].upper() + '>').encode() in line:
                return 'build_' + group['role'], None
        demand(b'<SOURCE_PACK_' in line, 'BUILD_ROLE')
        return 'source_pack', None
    stages.append(line_stage(before, stdout.build_paths(before, profile), build_role))
    return stages


def json_spans(raw):
    """Index canonical JSON value tokens in byte coordinates, without evaluation."""
    # Existing role guards require json.dumps(ensure_ascii=True) encoding.
    demand(raw.isascii(), 'JSON_ENCODING')
    spans, position, visited = {}, 0, 0
    def whitespace():
        nonlocal position
        while position < len(raw) and raw[position] in b' \r\n\t':
            position += 1
    def string():
        nonlocal position
        start = position; demand(raw[position:position+1] == b'"', 'JSON_STRING')
        position += 1
        while position < len(raw):
            char = raw[position]; position += 1
            if char == 92:
                position += 1
            elif char == 34:
                return start, position
        raise Refusal('STDOUT_LOCATION_JSON_STRING_END')
    def value(path, depth):
        nonlocal position, visited
        visited += 1; demand(depth <= 64 and visited <= 1000000, 'JSON_INDEX_BOUND')
        whitespace(); start = position
        char = raw[position:position+1]
        if char == b'{':
            position += 1; whitespace()
            if raw[position:position+1] != b'}':
                while True:
                    whitespace(); a, b = string(); key = json.loads(raw[a:b])
                    whitespace(); demand(raw[position:position+1] == b':', 'JSON_COLON'); position += 1
                    value(path + (key,), depth + 1); whitespace()
                    if raw[position:position+1] != b',': break
                    position += 1
            demand(raw[position:position+1] == b'}', 'JSON_OBJECT_END'); position += 1
        elif char == b'[':
            position += 1; whitespace(); index = 0
            if raw[position:position+1] != b']':
                while True:
                    value(path + (index,), depth + 1); index += 1; whitespace()
                    if raw[position:position+1] != b',': break
                    position += 1
            demand(raw[position:position+1] == b']', 'JSON_ARRAY_END'); position += 1
        elif char == b'"':
            string()
        else:
            while position < len(raw) and raw[position] not in b',]} \r\n\t':
                position += 1
            demand(position > start, 'JSON_VALUE')
        spans[path] = (start, position)
    value((), 0); whitespace(); demand(position == len(raw), 'JSON_TRAILER')
    return spans


def reverse_location(stages, offset):
    start, end, kind = offset, offset + 1, 'BYTE'
    if offset == len(stages[-1]['after']):
        start = end = len(stages[-1]['before']); kind = 'EOF'
        # EOF is invariant under every complete reconstruction.
        return dict(kind='EOF', start=len(stages[0]['before']), end=len(stages[0]['before'])), 'UNATTRIBUTED', None
    role, field = 'UNATTRIBUTED', None
    for item in reversed(stages):
        overlaps = [e for e in item['edits'] if start < e['after_end'] and end > e['after_start']]
        if not overlaps:
            shift = sum((e['after_end'] - e['after_start']) - (e['end'] - e['start'])
                        for e in item['edits'] if e['after_end'] <= start)
            start -= shift; end -= shift
            continue
        demand(len(overlaps) == 1, 'AMBIGUOUS_REVERSE_INTERVAL')
        edit = overlaps[0]; demand(edit['after_start'] <= start <= end <= edit['after_end'], 'REVERSE_INTERVAL_CROSSING')
        role = edit['role']
        if edit['json_prefix'] is not None and kind == 'BYTE':
            prefix = edit['json_prefix']
            original = item['before'][edit['start'] + prefix:edit['end']].rstrip(b'\n')
            replacement = edit['replacement'][prefix:].rstrip(b'\n')
            point = start - edit['after_start'] - prefix
            after_spans = json_spans(replacement)
            choices = [(path, bounds) for path, bounds in after_spans.items() if bounds[0] <= point < bounds[1]]
            if choices:
                path, (a, b) = max(choices, key=lambda row: len(row[0]))
                before_spans = json_spans(original); demand(path in before_spans, 'JSON_FIELD_JOIN')
                c, d = before_spans[path]; field = list(path) if path else None
                if original[c:d] == replacement[a:b]:
                    start = edit['start'] + prefix + c + point - a; end = start + 1
                    continue
                if role == 'turn_disposition' and path and path[-1] == 'output':
                    # The existing role guard permits exactly this allocation
                    # operand inside the JSON string; all other encoded bytes
                    # survive. Reconstruct it before claiming a precise point.
                    token = original[c:d]
                    inner = stage(token, [(m.start(), m.end(), b'<TURN_FIXTURE_ROOT>', role, None)
                        for m in re.finditer(rb'/tmp/turn-disposition-[a-z0-9_]{8}(?=/)', token)])
                    demand(inner['after'] == replacement[a:b], 'TURN_FIELD_RECONSTRUCTION')
                    located, _, _ = reverse_location([inner], point - a)
                    start = edit['start'] + prefix + c + located['start']
                    end = edit['start'] + prefix + c + located['end']
                    kind = located['kind']
                    continue
                start, end, kind = edit['start'] + prefix + c, edit['start'] + prefix + d, 'FIELD_REPLACEMENT'
                continue
        start, end, kind = edit['start'], edit['end'], 'REPLACEMENT_INTERVAL'
    return dict(kind=kind, start=start, end=end), role, field


def window(raw, point):
    start = max(0, point - 64); end = min(len(raw), start + 128)
    return dict(start=start, end=end, **desc(raw[start:end]),
                base64=base64.b64encode(raw[start:end]).decode('ascii'))


def safe_field(field):
    return type(field) is list and 0 < len(field) <= 32 and all(
        (type(v) is str and v in FIELD_TOKENS) or number(v, 1000000) for v in field)


def observe(raw, normalized, contexts, binding, captures, *, stdout, profile, evidence):
    demand(all(type(v) is dict and set(v) == set(MODES) for v in (raw, normalized, contexts, captures)), 'ROUTE_POPULATION')
    demand(type(binding) is dict and set(binding) == BINDING_KEYS and
           all(digest(binding[k], 40 if k in ('source_commit','source_tree') else 64) for k in binding), 'BINDING')
    demand(binding['source_commit'] == profile['source_commit'] and binding['source_tree'] == profile['source_tree'] and
           binding['role_profile_sha256'] == sha(encode(profile)), 'PROFILE_BINDING')
    for mode in MODES:
        demand(type(raw[mode]) is bytes and type(normalized[mode]) is bytes and
               len(raw[mode]) <= LIMIT and len(normalized[mode]) <= LIMIT, 'STREAM_BOUND')
        row = captures[mode]
        demand(type(row) is dict and set(row) == {'result_sha256','census_sha256','raw_stdout'} and
               digest(row['result_sha256']) and digest(row['census_sha256']) and row['raw_stdout'] == desc(raw[mode]), 'CAPTURE_BINDING')
    if normalized['legacy'] == normalized['dag']:
        return None, {}
    offset = next((i for i,(a,b) in enumerate(zip(normalized['legacy'],normalized['dag'])) if a != b),
                  min(len(normalized['legacy']),len(normalized['dag'])))
    routes, private = {}, {}
    for mode in MODES:
        stages = trace(raw[mode], contexts[mode], stdout, profile, evidence)
        demand(stages[-1]['after'] == normalized[mode], 'NORMALIZATION_READBACK')
        location, role, field = reverse_location(stages, offset)
        source = None if role == 'UNATTRIBUTED' else {k: profile['source_files'][SOURCE_ROLES[role]][k] for k in ('bytes','sha256')}
        raw_span, normalized_span = window(raw[mode], location['start']), window(normalized[mode], offset)
        routes[mode] = dict(raw=desc(raw[mode]), normalized=desc(normalized[mode]),
            capture_result_sha256=captures[mode]['result_sha256'], capture_census_sha256=captures[mode]['census_sha256'],
            raw_location=location, role=role, source=source, field=field if safe_field(field) else None,
            field_path_sha256=sha(encode(field)) if field is not None else None,
            raw_span={k:v for k,v in raw_span.items() if k != 'base64'},
            normalized_span={k:v for k,v in normalized_span.items() if k != 'base64'})
        private[mode] = dict(raw_span=raw_span, normalized_span=normalized_span,
            field=field if field is not None and len(encode(field)) <= 4096 else None,
            trace=[dict(before=desc(s['before']), after=desc(s['after']), edit_count=len(s['edits'])) for s in stages])
    public = dict(schema='dg16.stdout-first-difference-location.v1',
        source_binding='VALIDATED_OUTPUT_INTERVAL_NOT_EMITTER', binding=dict(binding),
        first_different_normalized_offset=offset, routes=routes)
    demand(len(encode(public)) <= 8192 and len(encode(private)) <= 16384, 'DIAGNOSTIC_BOUND')
    return public, private


def validate(value, relation, *, source_commit, source_tree, role_profile_sha, inputs_sha, profile):
    """Closed export validation. No arbitrary key, byte, value, path or filename."""
    if relation['equal']:
        demand(value is None, 'ON_EQUAL_STREAM'); return
    demand(type(value) is dict and set(value) == {'schema','source_binding','binding','first_different_normalized_offset','routes'} and
           value['schema'] == 'dg16.stdout-first-difference-location.v1' and
           value['source_binding'] == 'VALIDATED_OUTPUT_INTERVAL_NOT_EMITTER', 'PUBLIC_SCHEMA')
    binding = value['binding']
    demand(type(binding) is dict and set(binding) == BINDING_KEYS and
           all(digest(binding[k], 40 if k in ('source_commit','source_tree') else 64) for k in binding) and
           binding['source_commit'] == source_commit and binding['source_tree'] == source_tree and
           binding['role_profile_sha256'] == role_profile_sha and binding['receiver_inputs_sha256'] == inputs_sha, 'PUBLIC_BINDING')
    demand(sha(encode(profile)) == role_profile_sha and profile['source_commit'] == source_commit and
           profile['source_tree'] == source_tree, 'PUBLIC_PROFILE')
    witness = relation['witnesses'][0]; offset = value['first_different_normalized_offset']
    demand(number(offset, LIMIT) and offset == witness['first_different_offset'] and
           type(value['routes']) is dict and set(value['routes']) == set(MODES), 'PUBLIC_OFFSET')
    for mode, side in (('legacy','left'),('dag','right')):
        row = value['routes'][mode]
        demand(type(row) is dict and set(row) == {'raw','normalized','capture_result_sha256','capture_census_sha256',
            'raw_location','role','source','field','field_path_sha256','raw_span','normalized_span'} and
            descriptor(row['raw']) and descriptor(row['normalized']) and row['normalized'] == witness[side] and
            digest(row['capture_result_sha256']) and digest(row['capture_census_sha256']), 'PUBLIC_ROUTE')
        location = row['raw_location']; size = row['raw']['bytes']
        demand(type(location) is dict and set(location) == {'kind','start','end'} and
            location['kind'] in ('BYTE','EOF','FIELD_REPLACEMENT','REPLACEMENT_INTERVAL') and
            number(location['start'],size) and number(location['end'],size) and
            (location['start'] == location['end'] == size if location['kind'] == 'EOF' else location['start'] < location['end']) and
            (location['end'] == location['start'] + 1 if location['kind'] == 'BYTE' else True), 'PUBLIC_RAW_RANGE')
        demand(row['role'] in ('UNATTRIBUTED', *SOURCE_ROLES) and
               (row['source'] is None if row['role'] == 'UNATTRIBUTED' else descriptor(row['source'],16*1024**2)), 'PUBLIC_SOURCE')
        if row['role'] != 'UNATTRIBUTED':
            demand(row['source'] == {k:profile['source_files'][SOURCE_ROLES[row['role']]][k]
                                    for k in ('bytes','sha256')}, 'PUBLIC_SOURCE_PIN')
        demand((row['field'] is None or safe_field(row['field'])) and
               (row['field_path_sha256'] is None or digest(row['field_path_sha256'])), 'PUBLIC_FIELD')
        if row['field'] is not None:
            demand(row['field_path_sha256'] == sha(encode(row['field'])), 'PUBLIC_FIELD_HASH')
        for name, length, point in [('raw_span',size,location['start']),('normalized_span',row['normalized']['bytes'],offset)]:
            span = row[name]
            demand(type(span) is dict and set(span) == {'start','end','bytes','sha256'} and
                number(span['start'],length) and number(span['end'],length) and span['start'] <= point <= span['end'] and
                number(span['bytes'],128) and span['end'] - span['start'] == span['bytes'] and digest(span['sha256']), 'PUBLIC_SPAN')
    demand(len(encode(value)) <= 8192, 'PUBLIC_BOUND')
