"""Closed private-input plaintext; this codec supplies no transfer authority.

Expected descriptors must come from the independently reviewed fixed input
composition. Neither a public recipient key nor this codec authenticates root.
The 16 MiB transport ceiling is a separate prospective containment bound, not
an original operation timing, memory or input-size award.
"""
import base64
import binascii
import hashlib
import json
import re

MAX_ENTRIES = 256
MAX_FILE_BYTES = 4 * 1024**2
MAX_TOTAL_BYTES = 16 * 1024**2
MAX_PLAINTEXT_BYTES = 24 * 1024**2
SCHEMA = 'dg16.private-fixed-input-bundle.v1'


def need(value, code):
    if not value:
        raise ValueError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def check_index(index):
    need(type(index) is dict and 1 <= len(index) <= MAX_ENTRIES, 'INPUT_INDEX_POPULATION')
    total = 0
    names = set(index)
    for name, row in index.items():
        need(type(name) is str and len(name) <= 512, 'INPUT_NAME_BOUND')
        parts = name.split('/')
        need(1 <= len(parts) <= 6 and all(re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,127}', part)
             and part not in ('.', '..') for part in parts), 'INPUT_NAME_SCOPE')
        need(not any('/'.join(parts[:i]) in names for i in range(1, len(parts))), 'INPUT_FILE_DIRECTORY_ALIAS')
        need(type(row) is dict and set(row) == {'bytes', 'sha256'}, 'INPUT_DESCRIPTOR_FIELDS')
        need(type(row['bytes']) is int and 0 <= row['bytes'] <= MAX_FILE_BYTES
             and type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256']), 'INPUT_DESCRIPTOR_VALUE')
        total += row['bytes']
    need(total <= MAX_TOTAL_BYTES, 'INPUT_TOTAL_BOUND')
    return sha(encode(index))


def check_request(value):
    need(type(value) is str and re.fullmatch('[0-9a-f]{64}', value), 'ACTUAL_REQUEST_DIGEST_REQUIRED')


def pack(index, bodies, request_sha256):
    pin = check_index(index)
    check_request(request_sha256)
    need(type(bodies) is dict and set(bodies) == set(index), 'ACTUAL_INPUT_POPULATION')
    encoded = {}
    for name, row in index.items():
        raw = bodies[name]
        need(type(raw) is bytes and len(raw) == row['bytes'] and sha(raw) == row['sha256'], 'ACTUAL_INPUT_BODY_CHANGED')
        encoded[name] = base64.b64encode(raw).decode('ascii')
    raw = encode(dict(schema=SCHEMA, request_sha256=request_sha256, input_index_sha256=pin, bodies=encoded))
    need(len(raw) <= MAX_PLAINTEXT_BYTES, 'INPUT_PLAINTEXT_BOUND')
    return raw


def unpack(raw, index, request_sha256):
    pin = check_index(index)
    check_request(request_sha256)
    need(type(raw) is bytes and 0 < len(raw) <= MAX_PLAINTEXT_BYTES, 'INPUT_PLAINTEXT_BOUND')
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'INPUT_DUPLICATE_JSON_KEY')
            result[key] = value
        return result
    def constant(_):
        raise ValueError('INPUT_NONFINITE_JSON')
    try:
        value = json.loads(raw, object_pairs_hook=pairs, parse_constant=constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError('INPUT_JSON_REFUSED') from exc
    need(type(value) is dict and set(value) == {'schema', 'request_sha256', 'input_index_sha256', 'bodies'},
         'INPUT_BUNDLE_FIELDS')
    need(value['schema'] == SCHEMA and value['request_sha256'] == request_sha256
         and value['input_index_sha256'] == pin, 'INPUT_BUNDLE_CONTEXT')
    need(encode(value) == raw, 'INPUT_NONCANONICAL_JSON')
    data = value['bodies']
    need(type(data) is dict and set(data) == set(index), 'ACTUAL_INPUT_POPULATION')
    result = {}
    for name, row in index.items():
        text = data[name]
        need(type(text) is str and len(text) == 4 * ((row['bytes'] + 2) // 3), 'INPUT_ENCODED_BODY_BOUND')
        try:
            body = base64.b64decode(text, validate=True)
        except (ValueError, binascii.Error) as exc:
            raise ValueError('INPUT_BASE64_REFUSED') from exc
        need(base64.b64encode(body).decode('ascii') == text and len(body) == row['bytes']
             and sha(body) == row['sha256'], 'ACTUAL_INPUT_BODY_CHANGED')
        result[name] = body
    return result
