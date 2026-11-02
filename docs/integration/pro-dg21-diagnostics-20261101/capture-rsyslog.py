"""Disposable exact rsyslogd export capture; no policy mutation or admission."""
import base64
import hashlib
import json
from pathlib import Path
import runpy


def main():
    owner = runpy.run_path('scripts/qualify-work-graph-c5-setup.py')
    owner['_bwrap_root']()
    need = owner['_bwrap_need']
    before = owner['hosted_bwrap_policy_inventory']()
    name = 'rsyslogd'
    row = before.get(name)
    need(row == dict(attach='<unknown>', mode='enforce',
        sha256='5b27abe427665c8fcd79e611a1d2f542f642af313a9151fa601e58e3776d5a9f'),
        'observed rsyslogd record changed; diagnostic is inapplicable')
    root = Path('/sys/kernel/security/apparmor/policy')
    entries = list((root / 'profiles').iterdir())
    need(len(entries) <= 4096, 'selected profile lookup exceeds bound')
    selected = [entry for entry in entries
                if owner['_bwrap_read'](entry / 'name').decode('utf-8').strip() == name]
    need(len(selected) == 1, 'selected profile lookup is missing or ambiguous')
    exported = owner['_bwrap_selected_export'](selected[0], root)
    raw = base64.b64decode(exported['base64'], validate=True)
    need(0 < len(raw) <= 65536 and len(raw) == exported['bytes']
         and hashlib.sha256(raw).hexdigest() == exported['sha256'], 'export integrity differs')
    try:
        owner['_bwrap_prove_nonmatch'](raw, name, row)
    except ValueError as error:
        need(owner['hosted_bwrap_policy_inventory']() == before, 'diagnostic inventory changed')
        encoded = exported['base64']
        parts = (len(encoded) + 4095) // 4096
        need(1 <= parts <= 22, 'diagnostic output exceeds bound')
        metadata = {key: value for key, value in exported.items() if key != 'base64'}
        print(json.dumps(dict(schema='implementaudit.rejected-opaque-policy-diagnostic.v1',
            authority='NONE', policy_operations=0, name=name, record=row,
            exported=metadata, parts=parts, refusal=str(error)[:256],
            inventory_bookends_equal=True,
            inventory_sha256=hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest())), flush=True)
        for part in range(parts):
            print(json.dumps(dict(schema='implementaudit.rejected-opaque-policy-chunk.v1',
                raw_sha256=exported['sha256'], part=part, parts=parts,
                base64_fragment=encoded[part * 4096:(part + 1) * 4096])), flush=True)
        raise
    else:
        need(owner['hosted_bwrap_policy_inventory']() == before, 'diagnostic inventory changed')
        print(json.dumps(dict(scope='READ_ONLY_SELECTED_PROFILE_PROOF', name=name,
            policy_operations=0, authority='NONE', result='NO_REFUSAL_REPRODUCED',
            inventory_bookends_equal=True)), flush=True)


if __name__ == '__main__':
    main()
