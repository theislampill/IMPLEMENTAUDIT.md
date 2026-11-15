#!/usr/bin/env python3
"""FABLE scratch tool: propagate one episode's identities through the public operator static source.

Pure text/pin propagation of an EXISTING reviewed static-source set to a successor episode. It writes
only into a fresh output directory, installs nothing, and issues no admission. Every digest is
recomputed from the bytes it names; nothing is accepted by old-or-new alternation.

Identity inputs that only Root/Sol can supply are explicit parameters:
  --workflow-commit   the ACTUAL integration commit of the successor (a Root act; may be a
                      fail-closed placeholder, which the operator's own 40-hex guards refuse)
  --install-root      the operator installation directory selected for the successor

argv: <previous-static-dir> <successor-candidate-dir> <out-dir> --old-branch --new-branch
      --old-commit --workflow-commit --old-install-root --install-root [--old-composition-name --composition-name]
"""
import argparse, hashlib, json, re
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('previous', type=Path); p.add_argument('candidate', type=Path); p.add_argument('out', type=Path)
for name in ('old-branch', 'new-branch', 'old-commit', 'workflow-commit', 'old-install-root', 'install-root'):
    p.add_argument('--' + name, required=True)
p.add_argument('--old-composition-name', default='composition'); p.add_argument('--composition-name', default='composition')
a = p.parse_args()
sha = lambda b: hashlib.sha256(b).hexdigest()
files = {q.relative_to(a.previous).as_posix(): q.read_bytes() for q in sorted(a.previous.rglob('*')) if q.is_file()}
report = dict(changed={}, unchanged=[])


def once(raw, old, new, label, count=1):
    old, new = old.encode(), new.encode()
    if raw.count(old) != count: raise ValueError(f'{label}: expected {count} occurrence(s) of previous identity, found {raw.count(old)}')
    return raw.replace(old, new)


def assign(raw, name, value, label):
    pattern = re.compile(rb'(?m)^' + name.encode() + rb" = '[0-9a-f]{64}'$")
    if len(pattern.findall(raw)) != 1: raise ValueError(label + ': assignment ' + name)
    return pattern.sub(name.encode() + b" = '" + value.encode() + b"'", raw)


# 1. frozen core members come from the successor candidate's receiver, byte for byte
for name in ('root_common.py', 'root_acquire.py', 'public_receiver.py', 'prepare_live_control.py'):
    files['core/' + name] = (a.candidate / 'receiver' / name).read_bytes()
common = files['core/root_common.py']
if re.search(rb"(?m)^BRANCH = '" + re.escape(a.new_branch.encode()) + rb"'$", common) is None: raise ValueError('core/root_common.py BRANCH is not the successor branch')
if re.search(rb"(?m)^COMMON_SHA = '" + sha(common).encode() + rb"'$", files['core/root_acquire.py']) is None: raise ValueError('core/root_acquire.py COMMON_SHA does not pin core/root_common.py')
# 2. installation selection
files['codex_callbacks.js'] = once(files['codex_callbacks.js'], a.old_install_root, a.install_root, 'codex_callbacks.js installationRoot')
# 3. workflow body pin
workflow = (a.candidate / 'candidate/public/.github/workflows/dg16-r5-full-g2.yml').read_bytes()
files['concrete_root_bridge.py'] = assign(files['concrete_root_bridge.py'], 'WORKFLOW_SHA', sha(workflow), 'concrete_root_bridge.py')
# 4. event context
for name in ('event_driver.js', 'operator_setup.py'):
    files[name] = once(once(files[name], a.old_branch, a.new_branch, name + ' branch'), a.old_commit, a.workflow_commit, name + ' workflow_commit')
# 5. operator core pins and composition directory
core = files['public_operator_v2.py']
match = re.search(rb'(?m)^PINS = (\{.*\})$', core)
pins = json.loads(match.group(1).decode().replace("'", '"'))
for name in pins:
    pins[name] = sha(files['core/' + name])
core = core[:match.start(1)] + repr(pins).encode() + core[match.end(1):]
if a.old_composition_name != a.composition_name:
    core = once(core, "str(root/'" + a.old_composition_name + "')", "str(root/'" + a.composition_name + "')", 'composition path join')
    core = once(core, "ROOT/\\'" + a.old_composition_name + "\\'", "ROOT/\\'" + a.composition_name + "\\'", 'composition assignment')
files['public_operator_v2.py'] = core
# 6. digest chain: core -> operator -> setup
files['root_operator.py'] = assign(files['root_operator.py'], 'CORE_SHA', sha(files['public_operator_v2.py']), 'root_operator.py')
setup = files['operator_setup.py']
setup = assign(setup, 'CORE', sha(files['public_operator_v2.py']), 'operator_setup.py')
setup = assign(setup, 'BRIDGE', sha(files['concrete_root_bridge.py']), 'operator_setup.py')
setup = assign(setup, 'OPERATOR', sha(files['root_operator.py']), 'operator_setup.py')
files['operator_setup.py'] = setup
a.out.mkdir(parents=True, exist_ok=False)
for name, raw in files.items():
    target = a.out / name; target.parent.mkdir(parents=True, exist_ok=True); target.write_bytes(raw)
    previous = (a.previous / name).read_bytes()
    if previous == raw: report['unchanged'].append(name)
    else: report['changed'][name] = dict(before=sha(previous), after=sha(raw), bytes=len(raw))
print(json.dumps(report, indent=2, sort_keys=True))
