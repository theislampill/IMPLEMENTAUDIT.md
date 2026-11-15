#!/usr/bin/env python3
"""Control: does carrier.root_payload refuse BEFORE reserving SEND_RESERVED.json when the
remaining original window cannot cover the chain? Executes the actual source lines of the
span [binding=P.load() .. reserve(...'SEND_RESERVED.json'...)] against stubs. No crypto, no I/O."""
import os, sys, textwrap, time, types, importlib.util
class Refused(Exception): pass
class Spent(Exception): pass
def span(path):
    lines = open(path, encoding='utf-8').read().split('\n')
    a = next(i for i, l in enumerate(lines) if l.strip().startswith("binding=P.load();deadline="))
    b = next(i for i, l in enumerate(lines) if "'SEND_RESERVED.json'" in l and i > a)
    return textwrap.dedent('\n'.join(lines[a:b + 1])), lines
def run(path, remaining_ms):
    code, lines = span(path)
    def need(c, m):
        if not c: raise Refused(m)
    P = types.SimpleNamespace(load=lambda: {'limits': {'acquisition_seconds': 600}, 'branch': 'b', 'workflow_path': 'w', 'job_name': 'qualify'},
                              need=need, context=lambda c: None, REPOSITORY='r', sha=lambda b: 'h', encode=lambda v: b'{}')
    expires = int(time.time() * 1000) + remaining_ms
    SP = types.SimpleNamespace(load=lambda *a: {'operation': {'expires_unix_ms': expires}})
    V = types.SimpleNamespace(artifact_files=lambda a: {'REQUEST.json': b'x'})
    F = types.SimpleNamespace(private_directory=lambda d: (os.open(os.devnull, os.O_RDONLY), None))
    def reserve(*a): raise Spent('SEND_RESERVED')
    ns = dict(P=P, SP=SP, V=V, F=F, time=time, os=os, reserve=reserve, new_budget=lambda d: None,
              session_path=lambda *a, **k: 'd', workflow_commit='c', run_id='1', artifact_id=1, archive=b'', token=None)
    for l in lines:  # module-level constants from the file under test
        if l.startswith('MIN_SENDER_CHAIN_SECONDS='): exec(l, ns)
    try: exec(code, ns)
    except Refused as e: return 'REFUSED_BEFORE_SPEND:' + str(e)
    except Spent: return 'SENDER_SPENT'
    return 'NO_SPEND_POINT'
def gate_cases():
    spec = importlib.util.spec_from_file_location('g', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pre_sender_budget_gate.py'))
    g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
    op = dict(issued_unix_ms=1000, expires_unix_ms=601000)
    return [g.decide(op, 300000, 601000 - 7839)['status'], g.decide(op, 300000, 601000 - 300000)['status'],
            g.decide(op, 300000, 601000 - 299999)['status'], g.decide(op, 300000, 601001)['status'], g.decide(op, 300000, 999)['status'],
            g.decide(dict(issued_unix_ms=1000, expires_unix_ms='x'), 300000, 2000)['status']]
if __name__ == '__main__':
    path = sys.argv[1]
    got = {'g131_7839ms': run(path, 7839), 'short_120s': run(path, 120000), 'floor_minus_2s': run(path, 298000),
           'adverse_ample_400s': run(path, 400000), 'adverse_expired': run(path, -5)}
    want = {'g131_7839ms': 'REFUSED', 'short_120s': 'REFUSED', 'floor_minus_2s': 'REFUSED', 'adverse_ample_400s': 'SENDER_SPENT', 'adverse_expired': 'REFUSED'}
    ok = all(got[k].startswith(want[k]) for k in want)
    for k in got: print(('ok  ' if got[k].startswith(want[k]) else 'FAIL'), k, got[k])
    gc = gate_cases(); gok = gc == ['HOLD', 'PROCEED', 'HOLD', 'HOLD', 'HOLD', 'HOLD']; print('ok  ' if gok else 'FAIL', 'standalone_gate', gc)
    print('RESULT', 'PASS' if ok and gok else 'FAIL'); sys.exit(0 if ok and gok else 1)
