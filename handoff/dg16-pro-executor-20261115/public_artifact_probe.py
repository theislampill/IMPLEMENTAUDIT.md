#!/usr/bin/env python3
"""Source qualification of the unchanged public artifact interfaces.

Reads one actual GitHub download result through the original no-echo frame.
Only the selected historical public terminal artifact may be materialized.
No private/cipher request, authority grant, Codex event or acceptance is issued.
"""
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import stat
import sys
import types
import urllib.parse
import zipfile

REPO = Path(__file__).resolve().parents[2]
CUSTODY = REPO / 'handoff/dg16-g221-root-execution-inputs/g220-custody/operator-static-source'
ARTIFACT_ID = 14136761564
ARCHIVE_NAME = 'dg16-full-registry-43640583300-1.zip'
EXPECTED = {'bytes': 15700, 'sha256': '4a18656e3431b579e7a459cb9f811bd85e1e226787c28933239946e4637ede98'}
STAGE = 'entry'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    global STAGE
    if len(sys.argv) != 2 or not sys.flags.isolated or not sys.dont_write_bytecode:
        raise ValueError('ISOLATED_FIXED_ENTRY_REQUIRED')
    parse_only = sys.argv[1] == '--parse-only'
    target = Path(sys.argv[1])
    if target.exists() or not target.parent.is_dir():
        raise ValueError('FRESH_OUTPUT_REQUIRED')
    core = load('probe_exact_public_core', CUSTODY / 'public_operator_v2.py')
    bridge = load('probe_exact_original_bridge', CUSTODY / 'concrete_root_bridge.py')
    resolver = bridge.resolver_helpers((CUSTODY / 'resolve_artifact.py').read_bytes())
    owner = types.SimpleNamespace(integer=core.integer, parse=core.parse, desc=core.desc,
                                  AUTH='SOURCE_QUALIFICATION_ONLY_NO_ACCEPTANCE')
    acquire_raw = (CUSTODY / 'core/root_acquire.py').read_bytes()
    acquire = core.selected(acquire_raw, {'download_reference'},
                            {'K': owner, 'need': core.need, 'parse': core.parse,
                             'desc': core.desc, 're': re, 'urllib': urllib})
    STAGE = 'ephemeral-frame'
    raw = resolver.read_ephemeral_frame(4 * 1024**2)
    STAGE = 'download-shape'
    note, url = acquire.download_reference(raw, ARTIFACT_ID, ARCHIVE_NAME)
    raw = None
    if parse_only:
        url = None
        print(json.dumps({'status': 'PUBLIC_DOWNLOAD_SHAPE_RECEIVED', 'network_calls': 0,
                          'scope': 'SOURCE_QUALIFICATION_ONLY', 'safe_note': note}), flush=True)
        return
    STAGE = 'body-get'
    try:
        body = resolver.fetch_once(url, EXPECTED['bytes'], 45)
    finally:
        url = None
    STAGE = 'body-digest'
    core.need(core.desc(body) == EXPECTED, 'ACTUAL_ARCHIVE_DIGEST')
    receiver_raw = (CUSTODY / 'core/public_receiver.py').read_bytes()
    receiver = core.selected(receiver_raw,
        {'need', 'sha', 'encode', 'strict', 'expected_names', 'decode_zip', 'public_codec'},
        {'hashlib': hashlib, 'json': json, 'io': io, 'zipfile': zipfile, 'stat': stat},
        constants={'NAMES'})
    STAGE = 'public-decoder'
    members = receiver.decode_zip(body, 'terminal')
    fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    try:
        view = memoryview(body)
        while view:
            count = os.write(fd, view)
            core.need(count > 0, 'SHORT_PUBLIC_WRITE')
            view = view[count:]
        os.fsync(fd)
    finally:
        os.close(fd)
    core.need(core.desc(target.read_bytes()) == EXPECTED, 'PUBLIC_ARCHIVE_READBACK')
    print(json.dumps({'scope': 'ACTUAL_HISTORICAL_PUBLIC_DOWNLOAD_INTERFACE_QUALIFICATION',
        'original_acceptance': False, 'host_run': '43640583300', 'historical_conclusion': 'failure',
        'artifact_id': ARTIFACT_ID, 'archive': EXPECTED, 'member_count': len(members),
        'members': sorted(members), 'body_get_attempts': 1,
        'download_result': note['actual_tool_result'], 'signed_url_retained': False,
        'source_sha256': {name: hashlib.sha256((CUSTODY / name).read_bytes()).hexdigest()
                         for name in ['public_operator_v2.py', 'concrete_root_bridge.py',
                                      'resolve_artifact.py', 'core/root_acquire.py',
                                      'core/public_receiver.py']}}, sort_keys=True), flush=True)


if __name__ == '__main__':
    try:
        main()
    except BaseException as error:
        code = str(error) if re.fullmatch('[A-Z0-9_]{1,96}', str(error)) else type(error).__name__
        print(json.dumps({'scope': 'SOURCE_QUALIFICATION_ONLY', 'status': 'REFUSED_OR_UNCERTAIN',
                          'automatic_retry': False, 'signed_url_retained': False,
                          'stage': STAGE, 'fixed_reason_or_type': code}), flush=True)
        raise SystemExit(1)
