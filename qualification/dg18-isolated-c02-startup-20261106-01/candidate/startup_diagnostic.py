#!/usr/bin/env python3
"""Bounded startup observer. No launcher, admission grant, controller, or turn API."""
from pathlib import Path
import ast
import hashlib
import json
import queue
import re
import threading
import tomllib
from urllib.parse import urlsplit

SCHEMA = 'dg18.c02.startup-diagnostic.v1'
MAX_FRAME = 65536
MAX_STDOUT = 262144
MAX_STDERR = 65536
MAX_RECORDS = 32
MAX_DEPTH = 16
MAX_CONFIG = 65536
PIN_DIGESTS = {
    'guard_definitions.py': 'e76c4aae445b439007964d8c5f642130fd56aa00d83568e5fc4c692dcd2e7a3e',
    'ServerNotification.json': 'cc06d031345c7f1f08f0ac8ccb42d889b3246fadada1aabdf4688027975efad7',
    'app_server_lib.rs': 'a44b0266619d6adda0c1e7135d5be18e6581cff44307e78097efecc5195f8b6c',
    'core_config_mod.rs': 'e027e9fb2e4cd101abdb3984768eef07d1d0ac7c8aa631989011cd17bda0c6df',
    'LICENSE': 'd17f227e4df5da1600391338865ce0f3055211760a36688f816941d58232d8dc',
}
# Exact text in the retained official source. Matches are consistency, not origin proof.
EXACT_SUMMARIES = {
    'Invalid configuration; using defaults.': 'CONFIG_LOAD_DEFAULT_FALLBACK',
    'Error parsing rules; custom rules not applied.': 'EXEC_POLICY_PARSE_WARNING',
    'Codex rebuilt its local database': 'DATABASE_RECOVERY_NOTICE',
    '`--dangerously-bypass-hook-trust` is enabled. Enabled hooks may run without review for this invocation.': 'HOOK_TRUST_BYPASS_NOTICE',
    '`[features.guardianv2].async_classifier_mode` is deprecated and ignored. Async classification always uses conversations; remove this setting from config.toml or profile configuration files.': 'GUARDIAN_DEPRECATED_SETTING',
}
PROJECT_PREFIX = ('Project-local config, hooks, and exec policies are disabled in the following folders '
                  'until the project is trusted, but skills still load.\n')
KINDS = set(EXACT_SUMMARIES.values()) | {'PROJECT_CONFIG_DISABLED_SHAPE', 'OTHER_SCHEMA_VALID', 'UNCLASSIFIED'}
SCHEMA_RESULTS = {'VALID', 'INVALID', 'NOT_EVALUATED'}
PROFILE_RESULTS = {'CLOSED_STARTUP_WARNING', 'EXTRA_FIELDS_REFUSED', 'THREAD_SCOPE_REFUSED',
                   'ENVELOPE_REFUSED', 'STRING_LIMIT_REFUSED', 'INTEGER_TOKEN_REFUSED', 'NOT_EVALUATED'}
ORDER_RESULTS = {'AFTER_INITIALIZE_REPLY', 'BEFORE_INITIALIZE_REPLY', 'BEFORE_INITIALIZE_REQUEST'}
PATH_RELATIONS = {'ABSENT', 'AUTHORED_CONFIG', 'OWNED_HOME_OTHER', 'OWNED_SUBJECT_OTHER', 'OTHER_OR_RELATIVE', 'INVALID'}
FIELD_CATEGORIES = {'MODEL', 'MODEL_PROVIDER', 'MODEL_CONTEXT_WINDOW', 'PROJECT_TRUST', 'FEATURES',
                    'PROVIDER', 'MCP', 'OTHER', 'MULTIPLE', 'ABSENT', 'UNKNOWN', 'INVALID_RANGE'}
GUARD_RESULTS = {'NOT_CALLED', 'ACCEPTED', 'FOREIGN_OR_UNKNOWN_NATIVE_SCOPE',
                 'UNKNOWN_NATIVE_RECORD', 'UNKNOWN_NATIVE_RESPONSE_ENVELOPE',
                 'UNKNOWN_DUPLICATE_OR_FAILED_RESPONSE', 'NATIVE_RESPONSE_ID_TYPE',
                 'RESPONSE_SHAPE', 'FRESH_CANARY_UNKNOWN_WIRE_SHAPE',
                 'FRESH_CANARY_UNSOLICITED_EARLY_MCP', 'UNKNOWN_NATIVE_NOTIFICATION',
                 'GUARD_REFUSED_OTHER', 'GUARD_UNEXPECTED_EXCEPTION'}
TERMINALS = {'OPEN', 'WARNING_GUARD_REFUSED', 'WARNING_UNEXPECTEDLY_ACCEPTED', 'MALFORMED_JSON',
             'FRAME_LIMIT', 'TOTAL_STDOUT_LIMIT', 'STDERR_LIMIT', 'RECORD_LIMIT', 'JSON_DEPTH_LIMIT',
             'UNSOLICITED_BEFORE_SEND', 'UNEXPECTED_NATIVE_RECORD', 'GUARD_REFUSED',
             'MATCHED_REPLY_THEN_QUIET', 'INITIALIZE_TIMEOUT', 'EOF', 'TRUNCATED_FRAME',
             'READ_FAILURE', 'WRITE_FAILURE', 'RETENTION_FAILURE', 'PREFLIGHT_REFUSED', 'PROCESS_BINDING_REFUSED',
             'PROCESS_EXIT', 'INTERNAL_FAILURE', 'INTERRUPTED'}

class Refusal(ValueError):
    def __init__(self, code):
        super().__init__(code)
        self.code = code

def need(ok, code):
    if not ok:
        raise Refusal(code)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + '\n').encode()

def strict_json(raw):
    need(len(raw) <= MAX_FRAME, 'FRAME_LIMIT')
    def unique(pairs):
        result = {}
        for key, value in pairs:
            need(key not in result, 'MALFORMED_JSON')
            result[key] = value
        return result
    def bad_constant(_):
        raise Refusal('MALFORMED_JSON')
    try:
        value = json.loads(raw.decode('utf-8'), object_pairs_hook=unique, parse_constant=bad_constant)
    except (ValueError, UnicodeError, RecursionError) as exc:
        if isinstance(exc, Refusal):
            raise
        raise Refusal('MALFORMED_JSON') from None
    stack = [(value, 0)]
    while stack:
        item, depth = stack.pop()
        need(depth <= MAX_DEPTH, 'JSON_DEPTH_LIMIT')
        if type(item) is dict:
            stack.extend((v, depth + 1) for v in item.values())
            stack.extend((k, depth + 1) for k in item)
        elif type(item) is list:
            stack.extend((v, depth + 1) for v in item)
        elif type(item) is str:
            need(not any(0xD800 <= ord(c) <= 0xDFFF for c in item), 'MALFORMED_JSON')
        elif type(item) is float:
            need(item not in (float('inf'), float('-inf')), 'MALFORMED_JSON')
    return value

def load_pinned():
    deps = Path(__file__).resolve().parent / 'deps'
    raw = {}
    for name, digest in PIN_DIGESTS.items():
        path = deps / name
        need(not path.is_symlink() and path.is_file(), 'PIN_MEMBER_TYPE')
        raw[name] = path.read_bytes()
        need(sha(raw[name]) == digest, 'PIN_MEMBER_CHANGED')
    schema = json.loads(raw['ServerNotification.json'])
    variant = [v for v in schema['oneOf'] if v.get('properties', {}).get('method', {}).get('enum') == ['configWarning']]
    need(len(variant) == 1, 'PIN_VARIANT')
    # The fixture is already independently received as the exact source AST. Compile only its definitions.
    tree = ast.parse(raw['guard_definitions.py'])
    need(all(isinstance(n, ast.ClassDef) for n in tree.body), 'PIN_AST_SHAPE')
    ns = {'queue': queue, 'threading': threading, 're': re}
    exec(compile(tree, '<pinned-c02-guard-definitions>', 'exec'), ns)
    return schema, variant[0], ns['FreshCanaryQuiescenceV1'], ns['QuiescenceRefusal']

def schema_valid(value, schema, definitions):
    """Evaluator for exactly the warning wrapper and its three pinned definitions.

    Unknown schema keywords fail closed. Formats/descriptions are annotations here;
    in particular the pinned position minimum is zero although its prose says 1-based.
    """
    supported = {'$ref', 'type', 'properties', 'required', 'enum', 'anyOf', 'description', 'format', 'minimum', 'title'}
    need(set(schema) <= supported, 'UNSUPPORTED_PINNED_SCHEMA_KEYWORD')
    if '$ref' in schema:
        ref = schema['$ref']
        need(ref.startswith('#/definitions/'), 'PIN_REF')
        return schema_valid(value, definitions[ref.removeprefix('#/definitions/')], definitions)
    if 'anyOf' in schema and not any(schema_valid(value, s, definitions) for s in schema['anyOf']):
        return False
    typ = schema.get('type')
    matches = {'object': type(value) is dict, 'string': type(value) is str,
               'null': value is None, 'integer': type(value) is int or
               (type(value) is float and value.is_integer())}
    if typ and not any(matches.get(t, False) for t in (typ if type(typ) is list else [typ])):
        return False
    if 'enum' in schema and value not in schema['enum']:
        return False
    if 'minimum' in schema and (type(value) not in (int, float) or value < schema['minimum']):
        return False
    if type(value) is dict:
        if not set(schema.get('required', [])) <= set(value):
            return False
        if not all(schema_valid(value[k], s, definitions) for k, s in schema.get('properties', {}).items() if k in value):
            return False
    return True

class ConfigSnapshot:
    def __init__(self, raw, expected_sha256, home, subject):
        need(type(raw) is bytes and len(raw) <= MAX_CONFIG, 'CONFIG_SIZE')
        self.raw, self.home, self.subject = raw, Path(home), Path(subject)
        self.path = self.home / 'config.toml'
        self.profile = {'preimage_matches': sha(raw) == expected_sha256, 'syntax': 'INVALID',
                        'model_matches': False, 'features_match': False, 'project_trust_matches': False,
                        'provider_loopback': False, 'retries_zero': False, 'mcp_shape_matches': False,
                        'scope': 'AUTHORED_FILE_ONLY', 'effective_merged_config': 'UNKNOWN'}
        self.lines = []
        try:
            text = raw.decode('utf-8')
            doc = tomllib.loads(text)
        except (UnicodeError, tomllib.TOMLDecodeError, RecursionError):
            return
        self.lines = text.splitlines()
        self.profile['syntax'] = 'VALID'
        self.profile['model_matches'] = (doc.get('model') == 'dg18-emulated-model' and
            doc.get('model_provider') == 'dg18_canary' and type(doc.get('model_context_window')) is int and
            doc['model_context_window'] == 258400)
        features = doc.get('features')
        self.profile['features_match'] = bool(type(features) is dict and set(features) == {'hooks', 'apps'} and
            features['hooks'] is True and features['apps'] is False)
        self.profile['project_trust_matches'] = doc.get('projects') == {str(self.subject): {'trust_level': 'trusted'}}
        providers = doc.get('model_providers')
        provider = providers.get('dg18_canary') if type(providers) is dict else None
        if type(provider) is dict:
            try:
                raw_url = provider.get('base_url', '')
                url = urlsplit(raw_url) if type(raw_url) is str else None
                loopback = (url is not None and raw_url == url.geturl() and
                    url.scheme == 'http' and url.hostname == '127.0.0.1' and
                    url.port is not None and 1 <= url.port <= 65535 and url.username is None and
                    url.password is None and '?' not in raw_url and '#' not in raw_url and
                    not url.query and not url.fragment and url.path in ('', '/', '/v1'))
            except (TypeError, ValueError):
                loopback = False
            self.profile['provider_loopback'] = bool(loopback)
            self.profile['retries_zero'] = all(type(provider.get(k)) is int and provider[k] == 0
                for k in ('request_max_retries', 'stream_max_retries'))
        servers = doc.get('mcp_servers')
        mcp = servers.get('cua_repl') if type(servers) is dict else None
        if type(mcp) is dict:
            args = mcp.get('args')
            self.profile['mcp_shape_matches'] = bool(mcp.get('command') == '/usr/bin/python3' and
                type(args) is list and len(args) == 3 and all(type(v) is str for v in args) and
                args[1] == '--log' and Path(args[0]).is_absolute() and Path(args[2]).is_absolute())

    def path_relation(self, value):
        if value is None:
            return 'ABSENT'
        if type(value) is not str:
            return 'INVALID'
        p = Path(value)
        if not p.is_absolute() or '..' in p.parts:
            return 'OTHER_OR_RELATIVE'
        if p == self.path:
            return 'AUTHORED_CONFIG'
        if p.is_relative_to(self.home):
            return 'OWNED_HOME_OTHER'
        if p.is_relative_to(self.subject):
            return 'OWNED_SUBJECT_OTHER'
        return 'OTHER_OR_RELATIVE'

    def field_at_range(self, loc, relation):
        if loc is None:
            return 'ABSENT'
        if relation != 'AUTHORED_CONFIG' or not self.lines:
            return 'UNKNOWN'
        # Multiline TOML strings can contain table-looking lines. Do not infer
        # field provenance from this conservative line classifier in that case.
        if b'\"\"\"' in self.raw or bytes([39, 39, 39]) in self.raw:
            return 'UNKNOWN'
        try:
            start, end = loc['start'], loc['end']
            a, b = start['line'], end['line']
            if any(type(v) is not int for v in (a, b, start['column'], end['column'])):
                return 'INVALID_RANGE'
            if not (1 <= a <= b <= len(self.lines) and start['column'] >= 1 and end['column'] >= 1):
                return 'INVALID_RANGE'
            # The pinned description defines columns in Unicode scalar values.
            # Strict JSON excludes surrogate code points; Python len matches this unit.
            if start['column'] > len(self.lines[a-1]) + 1 or end['column'] > len(self.lines[b-1]) + 1:
                return 'INVALID_RANGE'
            if a == b and start['column'] > end['column']:
                return 'INVALID_RANGE'
            table, seen = '', set()
            for index, line in enumerate(self.lines, 1):
                line = line.strip()
                if line.startswith('[') and line.endswith(']'):
                    table = line
                category = 'OTHER'
                if line.startswith('#') or not line:
                    category = 'OTHER'
                elif table.startswith('[projects.'):
                    category = 'PROJECT_TRUST'
                elif table == '[features]':
                    category = 'FEATURES'
                elif table.startswith('[model_providers.'):
                    category = 'PROVIDER'
                elif table.startswith('[mcp_servers.'):
                    category = 'MCP'
                elif not table:
                    for key, label in (('model', 'MODEL'), ('model_provider', 'MODEL_PROVIDER'),
                                       ('model_context_window', 'MODEL_CONTEXT_WINDOW')):
                        if re.match(r'^' + key + r'\s*=', line):
                            category = label
                if a <= index <= b:
                    seen.add(category)
            return next(iter(seen)) if len(seen) == 1 else 'MULTIPLE'
        except (KeyError, TypeError, ValueError):
            return 'INVALID_RANGE'

class Observer:
    def __init__(self, config, request_digest, *, pinned=None, process=None):
        self.schema, self.variant, guard_class, self.guard_error = pinned or load_pinned()
        self.config = config
        need(re.fullmatch('[0-9a-f]{64}', request_digest) is not None, 'REQUEST_DIGEST')
        self.request_digest = request_digest
        self.ledger = guard_class(queue.Queue(maxsize=MAX_RECORDS), native_process=process)
        self.requested = False
        self.reply = False
        self.records = 0
        self.guard_result = 'NOT_CALLED'
        self.terminal = 'OPEN'
        self.warning = None

    def request(self):
        need(not self.requested and self.terminal == 'OPEN', 'INITIALIZE_ALREADY_REQUESTED')
        message = {'id': 1, 'method': 'initialize', 'params': {'clientInfo': {
            'name': 'r5_c02_native_tail_actual_controlled_canary', 'version': 'r5'},
            'capabilities': {'experimentalApi': True}}}
        self.ledger.before_send(message)
        self.requested = True
        return (json.dumps(message, separators=(',', ':')) + '\n').encode()

    def finish(self, terminal):
        need(terminal in TERMINALS and terminal != 'OPEN', 'UNKNOWN_TERMINAL')
        if self.terminal == 'OPEN':
            self.terminal = terminal

    def _guard(self, message):
        try:
            self.ledger.ingest(message)
            self.ledger.queue.get_nowait()
            self.guard_result = 'ACCEPTED'
            return True
        except self.guard_error as exc:
            reason = str(exc)
            self.guard_result = reason if reason in GUARD_RESULTS else 'GUARD_REFUSED_OTHER'
        except Exception:
            self.guard_result = 'GUARD_UNEXPECTED_EXCEPTION'
        return False

    def _warning(self, message):
        out = {'schema': 'NOT_EVALUATED', 'profile': 'NOT_EVALUATED', 'category': 'UNCLASSIFIED',
               'ordering': 'AFTER_INITIALIZE_REPLY' if self.reply else
                   ('BEFORE_INITIALIZE_REPLY' if self.requested else 'BEFORE_INITIALIZE_REQUEST'),
               'details_present': False, 'path_relation': 'INVALID', 'range_field': 'UNKNOWN',
               'origin': 'UNKNOWN', 'cause_evidence': 'NO_MATCH'}
        params = message.get('params')
        valid = schema_valid(message, self.variant, self.schema['definitions'])
        out['schema'] = 'VALID' if valid else 'INVALID'
        if not valid:
            return out
        out['details_present'] = params.get('details') is not None
        relation = self.config.path_relation(params.get('path'))
        out['path_relation'] = relation
        out['range_field'] = self.config.field_at_range(params.get('range'), relation)
        if 'threadId' in message or 'threadId' in params:
            out['profile'] = 'THREAD_SCOPE_REFUSED'
            return out
        if set(message) not in ({'method', 'params'}, {'method', 'params', 'emittedAtMs'}) or (
            'emittedAtMs' in message and not (type(message['emittedAtMs']) is int and 0 <= message['emittedAtMs'] < 2**63)):
            out['profile'] = 'ENVELOPE_REFUSED'
            return out
        allowed = {'summary', 'details', 'path', 'range'}
        loc = params.get('range')
        extra = bool(set(params) - allowed)
        if loc is not None:
            extra |= set(loc) != {'start', 'end'} or any(set(loc[k]) != {'line', 'column'} for k in ('start', 'end'))
        if extra:
            out['profile'] = 'EXTRA_FIELDS_REFUSED'
            return out
        if loc is not None and any(type(loc[k][field]) is not int
                                   for k in ('start','end') for field in ('line','column')):
            out['profile'] = 'INTEGER_TOKEN_REFUSED'
            return out
        if any(type(params.get(k)) is str and len(params[k].encode('utf-8')) > limit
               for k, limit in (('summary', 8192), ('details', 16384), ('path', 4096))):
            out['profile'] = 'STRING_LIMIT_REFUSED'
            return out
        out['profile'] = 'CLOSED_STARTUP_WARNING'
        summary = params['summary']
        if summary in EXACT_SUMMARIES:
            out['category'] = EXACT_SUMMARIES[summary]
            out['cause_evidence'] = 'EXACT_SUMMARY_SOURCE_CONSISTENCY'
        elif summary.startswith(PROJECT_PREFIX) and re.fullmatch(
                re.escape(PROJECT_PREFIX) + r'(?:    [1-9][0-9]*\. [^\n]+\n       [^\n]+\n)+', summary):
            out['category'] = 'PROJECT_CONFIG_DISABLED_SHAPE'
            out['cause_evidence'] = 'SOURCE_TEMPLATE_CONSISTENCY'
        else:
            out['category'] = 'OTHER_SCHEMA_VALID'
            out['cause_evidence'] = 'UNRESOLVED_SOURCE_BRANCH'
        return out

    def frame(self, raw):
        need(self.terminal == 'OPEN', 'OBSERVER_ALREADY_TERMINAL')
        self.records += 1
        if self.records > MAX_RECORDS:
            self.finish('RECORD_LIMIT')
            return
        try:
            message = strict_json(raw)
        except Refusal as exc:
            self.finish(exc.code)
            return
        if type(message) is dict and message.get('method') == 'configWarning':
            self.warning = self._warning(message)
            accepted = self._guard(message) if self.requested else False
            self.finish('UNSOLICITED_BEFORE_SEND' if not self.requested else
                        ('WARNING_UNEXPECTEDLY_ACCEPTED' if accepted else 'WARNING_GUARD_REFUSED'))
            return
        if not self.requested:
            self.finish('UNSOLICITED_BEFORE_SEND')
            return
        # Only the matching initialize result and two already-guarded startup notices
        # may prolong observation. Thread/MCP/turn/server-request records stop immediately.
        response = type(message) is dict and set(message) == {'id', 'result'} and type(message['id']) is int and message['id'] == 1
        notice = type(message) is dict and message.get('method') in {'remoteControl/status/changed', 'account/rateLimits/updated'} and 'id' not in message
        accepted = self._guard(message)
        if not accepted:
            self.finish('GUARD_REFUSED')
        elif response and not self.reply:
            self.reply = True
        elif not notice:
            self.finish('UNEXPECTED_NATIVE_RECORD')

    def report(self):
        return {'schema': SCHEMA, 'authority': 'NONE', 'request_digest': self.request_digest,
                'native_version_scope': '0.166.0', 'guard_source_scope': '35bf9823856eb4efe254b882954120480632230e',
                'terminal': self.terminal, 'records': min(self.records, MAX_RECORDS + 1),
                'initialize_requested': self.requested, 'initialize_reply_observed': self.reply,
                'initialize_reply_validation': 'GUARD_DICT_RESULT_ONLY', 'guard_result': self.guard_result,
                'ordering_evidence': 'OBSERVER_READ_ORDER_ONLY',
                'range_interpretation': 'CONSERVATIVE_AUTHORED_LINE_CLASS',
                'warning': self.warning, 'authored_config': self.config.profile.copy(),
                'initialized_sent': False, 'thread_request_sent': False, 'model_turn_requested': False,
                'protected_transaction_executed': False, 'admission_established_by_candidate': False,
                'runtime_origin_proved': False, 'old_v3_warning_cause_resolved': False}

def validate_public(value):
    """A whitelist, not a redactor. Raw source strings have no output slot."""
    empty = Observer.__new__(Observer)
    empty.request_digest = '0'*64; empty.terminal = 'OPEN'; empty.records = 0
    empty.requested = False; empty.reply = False; empty.guard_result = 'NOT_CALLED'; empty.warning = None
    empty.config = ConfigSnapshot(b'', sha(b''), '/fixture/home', '/fixture/subject')
    template = Observer.report(empty)
    need(type(value) is dict and set(value) == set(template), 'PUBLIC_KEYS')
    variable = {'request_digest', 'terminal', 'records', 'initialize_requested', 'initialize_reply_observed',
                'guard_result', 'warning', 'authored_config'}
    for key in set(template) - variable:
        need(type(value[key]) is type(template[key]) and value[key] == template[key], 'PUBLIC_CONSTANT')
    need(type(value['request_digest']) is str and re.fullmatch('[0-9a-f]{64}', value['request_digest']), 'PUBLIC_BINDING')
    need(type(value['terminal']) is str and value['terminal'] in TERMINALS and
         type(value['guard_result']) is str and value['guard_result'] in GUARD_RESULTS, 'PUBLIC_ENUM')
    need(type(value['records']) is int and 0 <= value['records'] <= MAX_RECORDS + 1, 'PUBLIC_COUNT')
    need(all(type(value[k]) is bool for k in ('initialize_requested','initialize_reply_observed')), 'PUBLIC_BOOL')
    cfg = value['authored_config']; cfg_template = empty.config.profile
    need(type(cfg) is dict and set(cfg) == set(cfg_template), 'PUBLIC_CONFIG_KEYS')
    for k, v in cfg_template.items():
        if type(v) is bool:
            need(type(cfg[k]) is bool, 'PUBLIC_CONFIG_BOOL')
        elif k == 'syntax':
            need(type(cfg[k]) is str and cfg[k] in {'VALID','INVALID'}, 'PUBLIC_CONFIG_SYNTAX')
        else:
            need(cfg[k] == v, 'PUBLIC_CONFIG_SCOPE')
    warning = value['warning']
    if warning is not None:
        enums = {'schema': SCHEMA_RESULTS, 'profile': PROFILE_RESULTS, 'category': KINDS,
                 'ordering': ORDER_RESULTS, 'path_relation': PATH_RELATIONS, 'range_field': FIELD_CATEGORIES,
                 'origin': {'UNKNOWN'}, 'cause_evidence': {'NO_MATCH','EXACT_SUMMARY_SOURCE_CONSISTENCY',
                     'SOURCE_TEMPLATE_CONSISTENCY','UNRESOLVED_SOURCE_BRANCH'}}
        need(type(warning) is dict and set(warning) == set(enums) | {'details_present'}, 'PUBLIC_WARNING_KEYS')
        need(all(type(warning[k]) is str and warning[k] in vals for k, vals in enums.items()), 'PUBLIC_WARNING_ENUM')
        need(type(warning['details_present']) is bool, 'PUBLIC_WARNING_BOOL')
    return encoded(value)
