#!/usr/bin/env python3
"""Operator-side hold-before-spend gate. Reads only PRO_SENDER_OPERATION.json (public metadata).
Changes no pinned source. Exit 0 = budget covers the chain; exit 3 = HOLD, do not start the sender."""
import argparse, json, sys, time
def decide(operation, min_remaining_ms, now_ms):
    issued, expires = operation['issued_unix_ms'], operation['expires_unix_ms']
    if not (type(issued) is int and type(expires) is int and type(min_remaining_ms) is int and min_remaining_ms > 0):
        return dict(status='HOLD', code='MALFORMED_OPERATION_OR_FLOOR', remaining_ms=None)
    remaining = expires - now_ms
    if not issued <= now_ms < expires:
        return dict(status='HOLD', code='OPERATION_NOT_CURRENT', remaining_ms=remaining)
    if remaining < min_remaining_ms:
        return dict(status='HOLD', code='REMAINING_BUDGET_BELOW_CHAIN_FLOOR', remaining_ms=remaining)
    return dict(status='PROCEED', code='BUDGET_COVERS_CHAIN', remaining_ms=remaining)
def main():
    p = argparse.ArgumentParser(); p.add_argument('--operation', required=True)
    p.add_argument('--min-remaining-ms', type=int, required=True); a = p.parse_args()
    r = decide(json.load(open(a.operation, 'rb')), a.min_remaining_ms, time.time_ns() // 1000000)
    r.update(authority='NONE', min_remaining_ms=a.min_remaining_ms, sender_started=False)
    print(json.dumps(r, sort_keys=True)); sys.exit(0 if r['status'] == 'PROCEED' else 3)
if __name__ == '__main__': main()
