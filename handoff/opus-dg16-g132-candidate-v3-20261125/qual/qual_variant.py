"""Negative-control inner: report what the self-check sees and that the sender refuses to proceed.

Used (a) unsandboxed, as the original sender UID with no sandbox at all, and (b) inside deliberately weakened
variants of the whole-sender bwrap argv. It never reaches a private read: enter_sender_sandbox refuses first,
and root_payload / Commands(root) are then called to show they refuse without the verified sandbox.
"""
import json
import sys
import time
from pathlib import Path
import importlib.util

HERE = Path(__file__).absolute().parent
PACKET = HERE.parent
spec = importlib.util.spec_from_file_location('carrier_loader', str(PACKET / 'carrier' / 'carrier_loader.py'))
loader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(loader)
pub = loader.load()
SC, K, F = pub.sender_capture, pub.carrier, pub.files
facts, failures = SC.sandbox_facts(sys.argv[2])
reads = []
real_acquire = F.acquire


def observed_acquire(*a, **k):
    reads.append(str(a[0]))
    return real_acquire(*a, **k)


F.acquire = observed_acquire


def refusal(fn):
    try:
        fn()
        return 'NO_REFUSAL'
    except BaseException as exc:  # noqa: BLE001 - closed code only
        return f'{type(exc).__name__}:{exc}'


out = dict(variant=sys.argv[3] if len(sys.argv) > 3 else None, failures=failures,
           observed={k: facts.get(k) for k in ('status', 'uid_map', 'interfaces', 'top', 'environment', 'descriptors',
                                               'max_user_namespaces')},
           enter_sender_sandbox=refusal(lambda: SC.enter_sender_sandbox(sys.argv[2])))
out['root_payload_without_verified_sandbox'] = K.root_payload('424242', '0' * 40, 1, b'x')['result']['code']
out['commands_root_without_verified_sandbox'] = refusal(
    lambda: K.Commands(dict(_sender_selection={}, sender_tools={}, limits={}), 'root', Path('/nonexistent'), None,
                       time.monotonic() + 5, None))
out['private_reads'] = reads
print(json.dumps(out, sort_keys=True), flush=True)
