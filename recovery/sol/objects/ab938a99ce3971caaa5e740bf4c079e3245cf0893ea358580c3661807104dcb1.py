"""Pure decoding of an actual supported immutable GitHub file result.

No acquisition, synthesized API object, issuer authentication or persistence.
Consumers retain the original raw wrapper descriptor and actual Root provenance.
"""
import base64
import binascii
import hashlib
import json
import re

TOOL = 'mcp__codex_apps__github_fetch_file'
REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
WRAPPER_MAXIMUM = 4 * 1024**2
# Root's already-held BASE64_ROUTE_METADATA.json confirms this immutable form.
DISPLAY_URL_PREFIX = 'https://github.com/theislampill/IMPLEMENTAUDIT.md/blob/'


def need(ok, code):
    if not ok:
        raise ValueError(code)


def _parse(raw):
    def pairs(rows):
        value = {}
        for name, item in rows:
            need(name not in value, 'FILE_RESULT_DUPLICATE_KEY')
            value[name] = item
        return value
    try:
        return json.loads(raw, object_pairs_hook=pairs,
                          parse_constant=lambda _: need(False, 'FILE_RESULT_NONFINITE'))
    except (UnicodeError, json.JSONDecodeError, RecursionError):
        raise ValueError('FILE_RESULT_JSON_REFUSED') from None


def decode_file_result(raw_actual_wrapper, call, expected, maximum):
    """Return verified file bytes, preserving no transformed tool wrapper.

    call: {tool: TOOL, arguments: {repository_full_name, path, ref, encoding}}
    expected: {bytes, sha256, git_blob_sha}; maximum is the consumer's bound.
    All call/expected data must come from the consumer's independent selection.
    """
    need(type(raw_actual_wrapper) is bytes and 0 < len(raw_actual_wrapper) <= WRAPPER_MAXIMUM,
         'FILE_RESULT_WRAPPER_BOUND')
    need(type(maximum) is int and maximum > 0, 'FILE_RESULT_CONSUMER_MAXIMUM')
    need(type(expected) is dict and set(expected) == {'bytes', 'sha256', 'git_blob_sha'}
         and type(expected['bytes']) is int and 0 <= expected['bytes'] <= maximum
         and type(expected['sha256']) is str and re.fullmatch('[0-9a-f]{64}', expected['sha256'])
         and type(expected['git_blob_sha']) is str and re.fullmatch('[0-9a-f]{40}', expected['git_blob_sha']),
         'FILE_RESULT_EXPECTED_DESCRIPTOR')
    need(type(call) is dict and set(call) == {'tool', 'arguments'} and call['tool'] == TOOL,
         'FILE_RESULT_SUPPORTED_TOOL_REQUIRED')
    args = call['arguments']
    need(type(args) is dict and set(args) == {'repository_full_name', 'path', 'ref', 'encoding'}
         and args['repository_full_name'] == REPOSITORY and args['encoding'] == 'base64'
         and type(args['ref']) is str and re.fullmatch('[0-9a-f]{40}', args['ref'])
         and type(args['path']) is str and 0 < len(args['path']) <= 4096
         and all(part not in ('', '.', '..') for part in args['path'].split('/'))
         and not any(ch in args['path'] for ch in ('\\', ':', '\0', '\r', '\n', '?', '#')),
         'FILE_RESULT_EXACT_IMMUTABLE_CALL')
    need(type(DISPLAY_URL_PREFIX) is str, 'ROOT_ACTUAL_DISPLAY_URL_RULE_REQUIRED')
    value = _parse(raw_actual_wrapper)
    need(type(value) is dict and set(value) <= {'content', 'structuredContent', 'isError', '_meta'}
         and value.get('isError') is False and type(value.get('content')) is list
         and type(value.get('structuredContent')) is dict and type(value.get('_meta', {})) is dict,
         'FILE_RESULT_FULL_COMPLETE_WRAPPER')
    meta = value.get('_meta', {})
    need(not any(meta.get(k) for k in ('truncated', 'isTruncated', 'partial', 'hasMore',
                                      'has_more', 'nextCursor', 'next_cursor')),
         'FILE_RESULT_PARTIAL_REFUSED')
    body = value['structuredContent']
    need(set(body) == {'content', 'encoding', 'sha', 'display_url', 'display_title'}
         and body['encoding'] == 'base64' and body['sha'] == expected['git_blob_sha']
         and type(body['content']) is str and body['display_title'] == args['path'].rsplit('/', 1)[-1]
         and body['display_url'] == DISPLAY_URL_PREFIX + args['ref'] + '/' + args['path'],
         'FILE_RESULT_IMMUTABLE_SUBJECT')
    # Only explicit CR and LF are transport line separators. Spaces, tabs,
    # non-ASCII characters, excess padding and nonzero padding bits refuse.
    text = body['content'].replace('\r', '').replace('\n', '')
    need(len(text) == 4 * ((expected['bytes'] + 2) // 3), 'FILE_RESULT_BASE64_LENGTH')
    try:
        decoded = base64.b64decode(text.encode('ascii'), validate=True)
    except (UnicodeError, ValueError, binascii.Error):
        raise ValueError('FILE_RESULT_BASE64_REFUSED') from None
    need(base64.b64encode(decoded).decode('ascii') == text, 'FILE_RESULT_BASE64_NONCANONICAL')
    need(len(decoded) == expected['bytes'] and len(decoded) <= maximum
         and hashlib.sha256(decoded).hexdigest() == expected['sha256'], 'FILE_RESULT_BODY_CHANGED')
    git = hashlib.sha1(b'blob ' + str(len(decoded)).encode('ascii') + b'\0' + decoded).hexdigest()
    need(git == expected['git_blob_sha'], 'FILE_RESULT_GIT_BLOB_CHANGED')
    return decoded
