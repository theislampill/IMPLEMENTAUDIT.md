import sys, types, subprocess, json, shutil
from pathlib import Path
stage_b, adapted, original, work = map(Path, sys.argv[1:5])
if work.exists(): shutil.rmtree(work)
work.mkdir()
m = types.ModuleType('sb'); m.__file__ = str(stage_b); exec(compile(stage_b.read_bytes(), str(stage_b), 'exec'), m.__dict__)
def run(core, store, *a):
    r = subprocess.run([sys.executable, '-I', '-B', str(core), '--store', str(store), *a], capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()[:160]
for label, core in (('original packaged', original), ('adapted packaged', adapted)):
    store = work / ('store-' + label.split()[0])
    gate = m.private_store_directory(store, create=True)
    print(label, 'gate:', 'PASS' if gate else gate)
    print(label, 'init:', run(core, store, 'init', '--owner-id', 'opus-check'))
    print(label, 'lookup:', run(core, store, 'lookup', '--host-id', 'h', '--host-session-id', 's'))
