"""Closed observations of captured setup stderr; no emitter or cause authority."""
import ast
import hashlib
import json
import re
import sys
import types

SOURCE_PATH = 'scripts/qualify-work-graph-c5-setup.py'
SOURCE_BYTES = 78790
SOURCE_SHA256 = '5caa2b1771c41b9c13328b44c72b45ff73d65832b6892cc6bc61cfb54bd6cbf1'
CAPTURE_LIMIT = 32768
RECORD_LIMIT = 6144
LINE_SAMPLE = 4
SOURCE_SAMPLE = 8
SCHEMA = 'dg16.launcher-provision-captured-stderr.v1'
SCOPE = 'TEXT_FORMAT_ONLY_NO_EMITTER_OR_CAUSE_AUTHENTICATION'
FUNCTIONS = ('hosted_download', 'hosted_archive_data', 'hosted_tar_launcher',
    'decode_hosted_launcher', 'hosted_parent', 'write_hosted_launcher',
    'provision_hosted_launcher', 'identity', 'emergency_cleanup')
FUNCTION_NAMES = ('<module>', 'decode_hosted_launcher', 'emergency_cleanup',
    'hosted_archive_data', 'hosted_download', 'hosted_download.<locals>.NoRedirect',
    'hosted_download.<locals>.NoRedirect.redirect_request', 'hosted_parent',
    'hosted_tar_launcher', 'identity', 'provision_hosted_launcher',
    'provision_hosted_launcher.<locals>.deadline', 'write_hosted_launcher')
LITERAL_COUNT = 25
LITERAL_SHA256 = '12bb7e665fb17550ef0a2ae59c9bf1dd3cdde46570703d823ba2656c8d5338f5'
KINDS = ('SOURCE_FRAME', 'OTHER_FRAME', 'SOURCE_LITERAL', 'EXCEPTION_FORMAT', 'OTHER')
EXCEPTION_LABELS = (
    ('urllib.error.HTTPError', 'HTTP_ERROR_FORMAT'),
    ('urllib.error.URLError', 'URL_ERROR_FORMAT'),
    ('ssl.SSLCertVerificationError', 'SSL_CERTIFICATE_ERROR_FORMAT'),
    ('ssl.SSLError', 'SSL_ERROR_FORMAT'),
    ('socket.gaierror', 'ADDRESS_ERROR_FORMAT'),
    ('TimeoutError', 'TIMEOUT_ERROR_FORMAT'), ('MemoryError', 'MEMORY_ERROR_FORMAT'),
    ('ImportError', 'IMPORT_ERROR_FORMAT'), ('ModuleNotFoundError', 'MODULE_ERROR_FORMAT'),
    ('OSError', 'OS_ERROR_FORMAT'), ('PermissionError', 'PERMISSION_ERROR_FORMAT'),
    ('FileNotFoundError', 'FILE_NOT_FOUND_FORMAT'), ('FileExistsError', 'FILE_EXISTS_FORMAT'),
    ('ValueError', 'VALUE_ERROR_FORMAT'), ('AssertionError', 'ASSERTION_ERROR_FORMAT'),
    ('RuntimeError', 'RUNTIME_ERROR_FORMAT'), ('TypeError', 'TYPE_ERROR_FORMAT'),
    ('AttributeError', 'ATTRIBUTE_ERROR_FORMAT'), ('NameError', 'NAME_ERROR_FORMAT'),
    ('RecursionError', 'RECURSION_ERROR_FORMAT'), ('OverflowError', 'OVERFLOW_ERROR_FORMAT'),
    ('KeyboardInterrupt', 'KEYBOARD_INTERRUPT_FORMAT'), ('SystemExit', 'SYSTEM_EXIT_FORMAT'))
FRAME = re.compile(rb'  File "([^"\r\n]*)", line ([0-9]{1,9}), in ([^\r\n]{1,256})\Z')


def need(value, code):
    if not value:
        raise ValueError(code)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode('ascii')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def descriptor(raw):
    return dict(bytes=len(raw), sha256=digest(raw))


def bind_source(raw):
    """Compile exact public source as data under this runtime; never execute it."""
    need(type(raw) is bytes and len(raw) == SOURCE_BYTES and digest(raw) == SOURCE_SHA256,
         'LAUNCHER_OBSERVATION_SOURCE_PIN')
    need(sys.implementation.name == 'cpython' and sys.version_info[:2] == (3, 12),
         'LAUNCHER_OBSERVATION_RUNTIME')
    code = compile(raw, SOURCE_PATH, 'exec', dont_inherit=True, optimize=0)
    functions = []
    def visit(item):
        root = item.co_qualname.split('.')[0]
        if item.co_name == '<module>' or root in FUNCTIONS:
            lines = sorted({line for _, _, line in item.co_lines() if line is not None and line > 0})
            functions.append(dict(function=item.co_qualname, name=item.co_name,
                                  first_line=item.co_firstlineno, lines=lines))
        for child in item.co_consts:
            if type(child) is types.CodeType:
                visit(child)
    visit(code)
    functions.sort(key=lambda row: (row['function'], row['first_line']))
    literals = []
    tree = ast.parse(raw)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name in FUNCTIONS:
            for item in ast.walk(node):
                if (isinstance(item, ast.Raise) and isinstance(item.exc, ast.Call)
                    and isinstance(item.exc.func, ast.Name) and item.exc.args
                    and isinstance(item.exc.args[0], ast.Constant)
                    and type(item.exc.args[0].value) is str):
                    literals.append(dict(function=node.name, line=item.lineno,
                        exception=item.exc.func.id, text=item.exc.args[0].value))
    literals.sort(key=lambda row: (row['line'], row['function'], row['exception'], row['text']))
    for ordinal, row in enumerate(literals):
        row['id'] = 'SETUP_LITERAL_%03d' % ordinal
    need(tuple(row['function'] for row in functions) == FUNCTION_NAMES
         and len(literals) == LITERAL_COUNT and digest(canonical(literals)) == LITERAL_SHA256,
         'LAUNCHER_OBSERVATION_CATALOG_CLOSURE')
    public = dict(source=dict(path=SOURCE_PATH, bytes=SOURCE_BYTES, sha256=SOURCE_SHA256),
        runtime=dict(implementation=sys.implementation.name, version=list(sys.version_info[:3])),
        catalog=dict(function_count=len(functions), site_count=sum(len(row['lines']) for row in functions),
            sha256=digest(canonical(functions)), literal_count=len(literals),
            literal_sha256=digest(canonical(literals))))
    return dict(public=public, functions=functions, literals=literals)


def _exception(line, catalog):
    for label, category in EXCEPTION_LABELS:
        prefix = label.encode('ascii')
        if line == prefix or line.startswith(prefix + b': '):
            literal_ids = [row['id'] for row in catalog['literals']
                if line == (row['exception'] + ': ' + row['text']).encode('utf-8')]
            status = None
            if category == 'HTTP_ERROR_FORMAT':
                match = re.fullmatch(rb'urllib\.error\.HTTPError: HTTP Error ([1-5][0-9]{2}): [^\r\n]*', line)
                if match:
                    status = int(match.group(1))
            number = None
            match = re.match(re.escape(prefix) + rb': \[Errno ([0-9]{1,4})\](?: |$)', line)
            if match and int(match.group(1)) <= 4095:
                number = int(match.group(1))
            return dict(class_id=category, source_literal_ids=literal_ids,
                        http_status_format=status, errno_format=number)
    return dict(class_id='UNKNOWN', source_literal_ids=[], http_status_format=None, errno_format=None)


def observe(stderr, source_raw, setup_filename, complete):
    need(type(stderr) is bytes and len(stderr) <= CAPTURE_LIMIT, 'LAUNCHER_OBSERVATION_CAPTURE_BOUND')
    need(type(complete) is bool, 'LAUNCHER_OBSERVATION_COMPLETE_TYPE')
    need(type(setup_filename) is str and setup_filename.startswith('/')
         and setup_filename.endswith('/' + SOURCE_PATH) and len(setup_filename) <= 4096
         and not any(x in setup_filename for x in ('"', '\r', '\n', '\x00')),
         'LAUNCHER_OBSERVATION_FILENAME')
    catalog = bind_source(source_raw)
    filename = setup_filename.encode('utf-8')
    index = {}
    for row in catalog['functions']:
        for line in row['lines']:
            index.setdefault((row['name'].encode('utf-8'), line), []).append([row['function'], line])
    pieces = stderr.split(b'\n')
    lines = [part + b'\n' for part in pieces[:-1]]
    if pieces[-1]:
        lines.append(pieces[-1])
    line_rows = []
    frame_rows = []
    source_rows = []
    partition = {kind: dict(lines=0, bytes=0) for kind in KINDS}
    for ordinal, raw in enumerate(lines):
        text = raw[:-1] if raw.endswith(b'\n') else raw
        match = FRAME.fullmatch(text)
        kind = 'OTHER'
        if match:
            sites = index.get((match.group(3), int(match.group(2))), []) if match.group(1) == filename else []
            kind = 'SOURCE_FRAME' if sites else 'OTHER_FRAME'
            frame = dict(frame_ordinal=len(frame_rows), line_ordinal=ordinal,
                         **descriptor(raw), sites=sites)
            frame_rows.append(frame)
            if sites:
                source_rows.append(dict(source_ordinal=len(source_rows), **frame))
        else:
            category = _exception(text, catalog)
            if category['source_literal_ids']:
                kind = 'SOURCE_LITERAL'
            elif category['class_id'] != 'UNKNOWN':
                kind = 'EXCEPTION_FORMAT'
        partition[kind]['lines'] += 1
        partition[kind]['bytes'] += len(raw)
        line_rows.append(dict(ordinal=ordinal, kind=kind, **descriptor(raw)))
    terminated = bool(stderr.endswith(b'\n'))
    eligible = bool(complete and lines and terminated)
    terminal = dict(eligible=eligible, line=(dict(ordinal=len(lines)-1, **descriptor(lines[-1])) if lines else None),
        class_id='INCOMPLETE_CAPTURE' if not complete else ('EMPTY_COMPLETE_CAPTURE' if not lines else 'UNKNOWN'),
        source_literal_ids=[], http_status_format=None, errno_format=None)
    if eligible:
        terminal.update(_exception(lines[-1][:-1], catalog))
    record = dict(schema=SCHEMA, scope=SCOPE, **catalog['public'],
        capture=dict(complete=complete, **descriptor(stderr)), ends_with_lf=terminated,
        captured_bytes_fully_described=True,
        lines=dict(count=len(lines), bytes=sum(len(raw) for raw in lines),
            table_sha256=digest(canonical(line_rows)), sample=line_rows[:LINE_SAMPLE],
            omitted=max(0, len(line_rows)-LINE_SAMPLE)),
        partition=[dict(kind=kind, **partition[kind]) for kind in KINDS],
        frames=dict(count=len(frame_rows), source_matched=len(source_rows),
            other=len(frame_rows)-len(source_rows), table_sha256=digest(canonical(frame_rows))),
        source_frames=dict(count=len(source_rows), sample=source_rows[:SOURCE_SAMPLE],
            omitted=max(0, len(source_rows)-SOURCE_SAMPLE), table_sha256=digest(canonical(source_rows))),
        terminal=terminal)
    validate_public(record)
    return record


def _closed(value, fields):
    need(type(value) is dict and set(value) == set(fields.split()), 'LAUNCHER_OBSERVATION_FIELDS')


def _uint(value, bound=CAPTURE_LIMIT):
    need(type(value) is int and 0 <= value <= bound, 'LAUNCHER_OBSERVATION_INTEGER')


def _hash(value):
    need(type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None,
         'LAUNCHER_OBSERVATION_HASH')


def _desc(value):
    _uint(value['bytes']); _hash(value['sha256'])
    if value['bytes'] == 0:
        need(value['sha256'] == digest(b''), 'LAUNCHER_OBSERVATION_EMPTY_DIGEST')


def validate_public(record):
    """Closed public grammar; exact private recomputation is separately required."""
    need(type(record) is dict and len(canonical(record)) <= RECORD_LIMIT, 'LAUNCHER_OBSERVATION_RECORD_BOUND')
    _closed(record, 'schema scope source runtime catalog capture ends_with_lf captured_bytes_fully_described lines partition frames source_frames terminal')
    need(record['schema'] == SCHEMA and record['scope'] == SCOPE
         and record['source'] == dict(path=SOURCE_PATH, bytes=SOURCE_BYTES, sha256=SOURCE_SHA256),
         'LAUNCHER_OBSERVATION_SOURCE_RELATION')
    need(type(record['source']['bytes']) is int, 'LAUNCHER_OBSERVATION_SOURCE_TYPE')
    _closed(record['runtime'], 'implementation version')
    version = record['runtime']['version']
    need(record['runtime']['implementation'] == 'cpython' and type(version) is list and len(version) == 3,
         'LAUNCHER_OBSERVATION_RUNTIME_FIELDS')
    for part in version: _uint(part, 10000)
    need(version[:2] == [3, 12], 'LAUNCHER_OBSERVATION_RUNTIME_VERSION')
    catalog = record['catalog']; _closed(catalog, 'function_count site_count sha256 literal_count literal_sha256')
    for key in ('function_count', 'site_count', 'literal_count'): _uint(catalog[key], 4096)
    need(catalog['function_count'] == len(FUNCTION_NAMES) and catalog['site_count'] >= len(FUNCTION_NAMES)
         and catalog['literal_count'] == LITERAL_COUNT and catalog['literal_sha256'] == LITERAL_SHA256,
         'LAUNCHER_OBSERVATION_CATALOG_CLOSURE')
    _hash(catalog['sha256']); _hash(catalog['literal_sha256'])
    capture = record['capture']; _closed(capture, 'complete bytes sha256'); _desc(capture)
    need(type(capture['complete']) is bool and type(record['ends_with_lf']) is bool
         and record['captured_bytes_fully_described'] is True, 'LAUNCHER_OBSERVATION_FLAGS')
    lines = record['lines']; _closed(lines, 'count bytes table_sha256 sample omitted')
    for key in ('count','bytes','omitted'): _uint(lines[key])
    _hash(lines['table_sha256'])
    need(lines['bytes'] == capture['bytes'] and lines['count'] <= capture['bytes']
         and (lines['count'] == 0) == (capture['bytes'] == 0), 'LAUNCHER_OBSERVATION_LINE_CONSERVATION')
    need(type(lines['sample']) is list and len(lines['sample']) == min(LINE_SAMPLE, lines['count'])
         and lines['omitted'] == lines['count']-len(lines['sample']), 'LAUNCHER_OBSERVATION_LINE_SAMPLE')
    sampled = {}; sampled_kinds = {}
    for ordinal, row in enumerate(lines['sample']):
        _closed(row, 'ordinal kind bytes sha256'); _desc(row); _uint(row['ordinal'])
        need(row['ordinal'] == ordinal and row['bytes'] > 0 and row['kind'] in KINDS,
             'LAUNCHER_OBSERVATION_LINE_ORDER')
        sampled[ordinal] = descriptor_tuple(row)
        sampled_kinds[ordinal] = row['kind']
    partition = record['partition']
    need(type(partition) is list and len(partition) == len(KINDS), 'LAUNCHER_OBSERVATION_PARTITION')
    for kind, row in zip(KINDS, partition):
        _closed(row, 'kind lines bytes'); _uint(row['lines']); _uint(row['bytes'])
        need(row['kind'] == kind and row['lines'] <= row['bytes']
             and (row['lines'] == 0) == (row['bytes'] == 0), 'LAUNCHER_OBSERVATION_PARTITION_ROW')
    need(sum(row['lines'] for row in partition) == lines['count']
         and sum(row['bytes'] for row in partition) == capture['bytes'], 'LAUNCHER_OBSERVATION_PARTITION_SUM')
    frames = record['frames']; _closed(frames, 'count source_matched other table_sha256')
    for key in ('count','source_matched','other'): _uint(frames[key])
    _hash(frames['table_sha256'])
    need(frames['count'] == frames['source_matched']+frames['other'] <= lines['count']
         and frames['source_matched'] == partition[0]['lines'] and frames['other'] == partition[1]['lines'],
         'LAUNCHER_OBSERVATION_FRAME_CONSERVATION')
    source = record['source_frames']; _closed(source, 'count sample omitted table_sha256')
    _uint(source['count']); _uint(source['omitted']); _hash(source['table_sha256'])
    need(source['count'] == frames['source_matched'] and type(source['sample']) is list
         and len(source['sample']) == min(SOURCE_SAMPLE, source['count'])
         and source['omitted'] == source['count']-len(source['sample']), 'LAUNCHER_OBSERVATION_SOURCE_SAMPLE')
    previous_frame = previous_line = -1
    for ordinal, row in enumerate(source['sample']):
        _closed(row, 'source_ordinal frame_ordinal line_ordinal bytes sha256 sites'); _desc(row)
        for key in ('source_ordinal','frame_ordinal','line_ordinal'): _uint(row[key])
        need(row['source_ordinal'] == ordinal and previous_frame < row['frame_ordinal'] < frames['count']
             and previous_line < row['line_ordinal'] < lines['count'] and row['bytes'] > 0,
             'LAUNCHER_OBSERVATION_SOURCE_ORDER')
        previous_frame, previous_line = row['frame_ordinal'], row['line_ordinal']
        need(type(row['sites']) is list and 0 < len(row['sites']) <= 8, 'LAUNCHER_OBSERVATION_SITE_COUNT')
        for site in row['sites']:
            need(type(site) is list and len(site) == 2 and type(site[0]) is str
                 and site[0] in FUNCTION_NAMES, 'LAUNCHER_OBSERVATION_SITE_ROLE')
            _uint(site[1], 1439); need(site[1] > 0, 'LAUNCHER_OBSERVATION_SITE_LINE')
        need(row['sites'] == sorted(row['sites']) and len({tuple(x) for x in row['sites']}) == len(row['sites']),
             'LAUNCHER_OBSERVATION_SITE_DUPLICATE')
        need(row['line_ordinal'] not in sampled or sampled[row['line_ordinal']] == descriptor_tuple(row),
             'LAUNCHER_OBSERVATION_SAMPLE_JOIN')
        need(row['line_ordinal'] not in sampled_kinds or sampled_kinds[row['line_ordinal']] == 'SOURCE_FRAME',
             'LAUNCHER_OBSERVATION_SAMPLE_KIND')
        sampled[row['line_ordinal']] = descriptor_tuple(row)
        sampled_kinds[row['line_ordinal']] = 'SOURCE_FRAME'
    if source['sample']:
        need(source['omitted'] <= frames['count']-previous_frame-1
             and source['omitted'] <= lines['count']-previous_line-1, 'LAUNCHER_OBSERVATION_OMISSION_CAPACITY')
    known_bytes = sum(value[0] for value in sampled.values())
    unknown_lines = lines['count']-len(sampled)
    need(known_bytes+unknown_lines <= capture['bytes'] <= known_bytes+unknown_lines*CAPTURE_LIMIT,
         'LAUNCHER_OBSERVATION_SAMPLE_BYTE_CONSERVATION')
    terminal = record['terminal']; _closed(terminal, 'eligible line class_id source_literal_ids http_status_format errno_format')
    need(type(terminal['eligible']) is bool and terminal['eligible'] == bool(capture['complete'] and lines['count'] and record['ends_with_lf']),
         'LAUNCHER_OBSERVATION_TERMINAL_ELIGIBILITY')
    allowed = {value for _, value in EXCEPTION_LABELS} | {'UNKNOWN','EMPTY_COMPLETE_CAPTURE','INCOMPLETE_CAPTURE'}
    need(terminal['class_id'] in allowed and type(terminal['source_literal_ids']) is list
         and len(terminal['source_literal_ids']) <= catalog['literal_count'], 'LAUNCHER_OBSERVATION_TERMINAL_CLASS')
    need(len(set(terminal['source_literal_ids'])) == len(terminal['source_literal_ids'])
         and all(type(x) is str and x in {'SETUP_LITERAL_%03d' % i for i in range(LITERAL_COUNT)}
                 for x in terminal['source_literal_ids']),
         'LAUNCHER_OBSERVATION_TERMINAL_LITERALS')
    if lines['count']:
        _closed(terminal['line'], 'ordinal bytes sha256'); _desc(terminal['line']); _uint(terminal['line']['ordinal'])
        need(terminal['line']['ordinal'] == lines['count']-1 and terminal['line']['bytes'] > 0,
             'LAUNCHER_OBSERVATION_TERMINAL_LINE')
        last = terminal['line']['ordinal']
        need(last not in sampled or sampled[last] == descriptor_tuple(terminal['line']),
             'LAUNCHER_OBSERVATION_TERMINAL_SAMPLE_JOIN')
        sampled[last] = descriptor_tuple(terminal['line'])
        if terminal['eligible'] and terminal['class_id'] not in ('UNKNOWN','EMPTY_COMPLETE_CAPTURE','INCOMPLETE_CAPTURE'):
            kind = 'SOURCE_LITERAL' if terminal['source_literal_ids'] else 'EXCEPTION_FORMAT'
            need(last not in sampled_kinds or sampled_kinds[last] == kind, 'LAUNCHER_OBSERVATION_TERMINAL_KIND')
            sampled_kinds[last] = kind
    else:
        need(terminal['line'] is None and terminal['class_id'] == ('EMPTY_COMPLETE_CAPTURE' if capture['complete'] else 'INCOMPLETE_CAPTURE')
             and not record['ends_with_lf'], 'LAUNCHER_OBSERVATION_EMPTY_TERMINAL')
    if terminal['eligible']:
        need(terminal['class_id'] not in ('EMPTY_COMPLETE_CAPTURE','INCOMPLETE_CAPTURE'),
             'LAUNCHER_OBSERVATION_ELIGIBLE_TERMINAL_CLASS')
    if terminal['class_id'] == 'UNKNOWN':
        need(not terminal['source_literal_ids'] and terminal['http_status_format'] is None
             and terminal['errno_format'] is None, 'LAUNCHER_OBSERVATION_UNKNOWN_TERMINAL')
    if not terminal['eligible']:
        need(not terminal['source_literal_ids'] and terminal['http_status_format'] is None
             and terminal['errno_format'] is None
             and terminal['class_id'] == ('INCOMPLETE_CAPTURE' if not capture['complete'] else
                 'EMPTY_COMPLETE_CAPTURE' if not lines['count'] else 'UNKNOWN'), 'LAUNCHER_OBSERVATION_INCOMPLETE_TERMINAL')
    if terminal['http_status_format'] is not None:
        _uint(terminal['http_status_format'],599)
        need(terminal['class_id'] == 'HTTP_ERROR_FORMAT' and terminal['http_status_format'] >= 100,
             'LAUNCHER_OBSERVATION_HTTP_FORMAT')
    if terminal['errno_format'] is not None: _uint(terminal['errno_format'],4095)
    known_bytes = sum(value[0] for value in sampled.values())
    unknown_lines = lines['count']-len(sampled)
    need(known_bytes+unknown_lines <= capture['bytes'] <= known_bytes+unknown_lines*CAPTURE_LIMIT,
         'LAUNCHER_OBSERVATION_TERMINAL_BYTE_CONSERVATION')
    for row in partition:
        known = [sampled[i][0] for i, kind in sampled_kinds.items() if kind == row['kind']]
        need(len(known) <= row['lines'] and sum(known) <= row['bytes'], 'LAUNCHER_OBSERVATION_PARTITION_SAMPLE_JOIN')
    empty = digest(canonical([]))
    for count, value in [(lines['count'],lines['table_sha256']), (frames['count'],frames['table_sha256']),
                         (source['count'],source['table_sha256'])]:
        if count == 0: need(value == empty, 'LAUNCHER_OBSERVATION_EMPTY_TABLE')
    return record


def descriptor_tuple(row):
    return row['bytes'], row['sha256']


def validate_against(record, stderr, source_raw, setup_filename, complete):
    validate_public(record)
    expected = observe(stderr, source_raw, setup_filename, complete)
    need(canonical(record) == canonical(expected), 'LAUNCHER_OBSERVATION_PRIVATE_RECOMPUTATION')
    return record
