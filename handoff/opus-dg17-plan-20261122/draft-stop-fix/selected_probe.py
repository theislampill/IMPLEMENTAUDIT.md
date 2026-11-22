"""Source-only execution of the real selected Stop path. Not host-native evidence."""
import hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
SK = Path(sys.argv[1]); base = Path(tempfile.mkdtemp(prefix='stopprobe-', dir=sys.argv[2])).resolve()
ev, run, store = base/'evidence', base/'run', base/'store'
for p in (ev, run, store): p.mkdir()
owner = SK/'scripts'/'host-session-binding.py'
policy = dict(schema='implementaudit.codex-stop-policy.v1', session_id='sel-1', evidence_directory=str(ev), cwd=str(base),
              binding_store=str(store), binding_owner=str(owner.resolve()), binding_owner_sha256=hashlib.sha256(owner.read_bytes()).hexdigest(),
              binding=dict(explicit_run_root=str(run)), validator=str((SK/'scripts'/'validate-run-root.sh').resolve()), bash=r'C:\Program Files\Git\bin\bash.exe')
raw = json.dumps(policy).encode(); pol = base/'policy.json'; pol.write_bytes(raw); digest = hashlib.sha256(raw).hexdigest()
ev0 = dict(session_id='sel-1', turn_id='t1', hook_event_name='Stop', stop_hook_active=False, last_assistant_message='Which option should I take?', cwd=str(base))
cases = {'ordinary unbound session': dict(ev0, session_id='other-session'),
         'ordinary session + new host field': dict(ev0, session_id='other-session', agent_id='a1'),
         'selected session, no binding in store': ev0,
         'selected session, no binding, stop_hook_active=true': dict(ev0, stop_hook_active=True),
         'selected session + new host field': dict(ev0, agent_id='a1'),
         'malformed JSON (any session)': None}
for name, event in cases.items():
    data = b'{not json' if event is None else json.dumps(event).encode()
    r = subprocess.run([sys.executable, '-I', '-S', '-B', str(SK/'scripts'/'host-stop-interlock.py'), '--codex-stop-policy', str(pol), digest],
                       input=data, capture_output=True, timeout=60)
    out = r.stdout.decode(errors='replace').strip()
    try: d = json.loads(out); verdict = 'BLOCK' if d.get('decision') == 'block' else 'ALLOW'
    except Exception: d, verdict = out, '?'
    print(f'{name:52} exit={r.returncode} {verdict} {json.dumps(d)[:230]}')
print('receipts written:', sorted(p.name[:14] for p in ev.iterdir()))
