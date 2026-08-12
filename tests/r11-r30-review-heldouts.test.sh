#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
outer_timeout_only=0
windows_custody_only=0
candidate_probe_only=0
case "${1:-}" in
  --outer-timeout-heldout) outer_timeout_only=1; shift;;
  --windows-custody-reproducer) windows_custody_only=1; shift;;
  --candidate-probe-heldout) candidate_probe_only=1; shift;;
esac
[ "$#" -eq 0 ] || { printf 'usage: r11-r30-review-heldouts.test.sh [--outer-timeout-heldout|--candidate-probe-heldout]\n' >&2; exit 2; }
cd "$repo_root"

checker="skills/implementaudit/scripts/check-authorization-binding.sh"
reachability="scripts/check-helper-reachability.sh"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
failures=()

if [ "$windows_custody_only" -eq 1 ]; then
  candidate="$tmp/windows-custody-candidate"
  mkdir -p "$candidate/tests"
  cp tests/scarce-resource-rehearsal-contract.test.sh "$candidate/tests/"
  sed -i '/^checker=/i sleep 60 \&\nprintf "%s\\n" "$!" > "$PWD/.windows-custody-child.pid"\nwait' \
    "$candidate/tests/scarce-resource-rehearsal-contract.test.sh"
  python - "$BASH" "$candidate" <<'PY'
import os, subprocess, sys, time
from pathlib import Path

bash, candidate = sys.argv[1:]
process = subprocess.Popen([bash, "tests/scarce-resource-rehearsal-contract.test.sh", "--r30-probe", "--repo-root", "."],
    cwd=candidate, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
pid_file = Path(candidate) / ".windows-custody-child.pid"
deadline = time.monotonic() + 3
while not pid_file.exists() and time.monotonic() < deadline:
    time.sleep(.02)
if not pid_file.exists():
    process.kill(); process.communicate(); raise SystemExit("windows-custody: child PID was not recorded")
child = int(pid_file.read_text(encoding="utf-8"))
try:
    process.communicate(timeout=1)
except subprocess.TimeoutExpired:
    subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    try: process.kill()
    except ProcessLookupError: pass
    try: process.communicate(timeout=1)
    except subprocess.TimeoutExpired:
        if process.stdout: process.stdout.close()
        if process.stderr: process.stderr.close()
        try: process.wait(timeout=1)
        except subprocess.TimeoutExpired: pass
listed = subprocess.run(["tasklist", "/FI", f"PID eq {child}", "/FO", "CSV", "/NH"], capture_output=True, text=True, check=False)
alive = str(child) in listed.stdout
if alive:
    subprocess.run(["taskkill", "/PID", str(child), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
raise SystemExit("windows-custody: launcher=%s child=%s survived=%s" % (process.pid, child, alive) if alive else 0)
PY
  printf 'r11-r30-review-heldouts: windows-custody reproducer unexpectedly cleaned child\n' >&2
  exit 1
fi

python - "$tmp" <<'PY'
import hashlib
import json
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
stub = root / "producer-stub.py"
stub.write_text("#!/usr/bin/env python3\nraise SystemExit(23)\n", encoding="utf-8")
stub.chmod(0o755)
success_stub = root / "producer-success.py"
success_stub.write_text("#!/usr/bin/env python3\nraise SystemExit(0)\n", encoding="utf-8")
success_stub.chmod(0o755)

def wrapper(name, body):
    path = root / name
    path.write_text("#!/usr/bin/env python3\n" + body, encoding="utf-8")
    path.chmod(0o755)
    return path

forging = wrapper("forging-wrapper.py", '''import hashlib, json, os, pathlib
stub = pathlib.Path(os.environ["IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB"])
pathlib.Path(os.environ["IMPLEMENTAUDIT_REHEARSAL_STUB_EVENT"]).write_text(json.dumps({
  "stub_identity": "sha256:" + hashlib.sha256(stub.read_bytes()).hexdigest(),
  "nonce": os.environ["IMPLEMENTAUDIT_REHEARSAL_STUB_NONCE"], "exit_code": 0}), encoding="utf-8")
''')
ignoring = wrapper("ignoring-wrapper.py", '''import hashlib, json, os, pathlib, subprocess, sys
stub = pathlib.Path(os.environ["IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB"])
subprocess.run([sys.executable, stub], check=False)
pathlib.Path(os.environ["IMPLEMENTAUDIT_REHEARSAL_STUB_EVENT"]).write_text(json.dumps({
  "stub_identity": "sha256:" + hashlib.sha256(stub.read_bytes()).hexdigest(),
  "nonce": os.environ["IMPLEMENTAUDIT_REHEARSAL_STUB_NONCE"], "exit_code": 0}), encoding="utf-8")
''')
leaking = wrapper("leaking-wrapper.py", '''import hashlib, json, os, pathlib
stub = pathlib.Path(os.environ["IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB"])
if os.environ.get("HELDOUT_CREDENTIAL_SENTINEL"):
  pathlib.Path(os.environ["IMPLEMENTAUDIT_TEST_INHERITED_MARKER"]).write_text("visible\\n", encoding="utf-8")
pathlib.Path(os.environ["IMPLEMENTAUDIT_REHEARSAL_STUB_EVENT"]).write_text(json.dumps({
  "stub_identity": "sha256:" + hashlib.sha256(stub.read_bytes()).hexdigest(),
  "nonce": os.environ["IMPLEMENTAUDIT_REHEARSAL_STUB_NONCE"], "exit_code": 0}), encoding="utf-8")
''')
victim = root / "hardlink-victim.txt"
victim.write_text("do-not-overwrite\n", encoding="utf-8")
hardlinking = wrapper("hardlinking-wrapper.py", f'''import os, pathlib, subprocess, sys
target = pathlib.Path(sys.argv[sys.argv.index("--terminal") + 1])
subprocess.run([sys.executable, os.environ["IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB"]], check=True)
os.link({str(victim)!r}, target)
''')

def canonical_hash(argv, env_keys):
    return hashlib.sha256(json.dumps({"argv": argv, "env_keys_present": sorted(env_keys)},
        separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def payload(suffix, wrapper_path, argv_suffix="fixture.txt", env_keys=["API_TOKEN", "MODEL"], stub_path=stub, extra_argv=[]):
    terminal = root / f"terminal-{suffix}.json"
    argv = [sys.executable, str(wrapper_path), "--input", argv_suffix] + extra_argv
    receipt = {"rehearsed_command_hash": canonical_hash(argv, env_keys),
      "stub_identity": "sha256:" + hashlib.sha256(stub_path.read_bytes()).hexdigest(),
      "stubbed_components": ["producer"], "env_keys_present": env_keys,
      "terminal_artifact_path": str(terminal), "exit_code": 0, "disposition": "PASS",
      "timestamp": "2026-08-11T12:00:00Z"}
    launch = {"argv": argv, "env_keys_present": env_keys, "terminal_artifact_path": str(terminal),
              "launch_records": 1, "metered_calls": 0}
    receipt_path, launch_path = root / f"receipt-{suffix}.json", root / f"launch-{suffix}.json"
    receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
    launch_path.write_text(json.dumps(launch), encoding="utf-8")
    return receipt, receipt_path, launch_path

def complete_phase(name, receipt, receipt_path, launch_path, stub_path=stub):
    base = pathlib.Path("fixtures/run-root-example/phases/phase-1.md").read_text(encoding="utf-8")
    fields = ("Scarce resource budget: 1 model-call\n"
      f"Rehearsal receipt: {receipt_path}\nRehearsal launch: {launch_path}\n"
      f"Rehearsal producer stub: {stub_path}\nRehearsal command hash: {receipt['rehearsed_command_hash']}\n"
      f"Rehearsal terminal artifact: {receipt['terminal_artifact_path']}\n"
      f"Rehearsal environment keys: {','.join(receipt['env_keys_present'])}\n")
    path = root / name
    path.write_text(base.replace("Depends on phases: none\n", "Depends on phases: none\n" + fields), encoding="utf-8")
    return path

forged, forged_receipt, forged_launch = payload("forged", forging)
ignored, ignored_receipt, ignored_launch = payload("ignored", ignoring)
inherited, inherited_receipt, inherited_launch = payload("inherited", leaking)
changed, changed_receipt, changed_launch = payload("changed", forging, "changed-fixture.txt", ["ALT_TOKEN"])
hardlinked, hardlinked_receipt, hardlinked_launch = payload("hardlinked", hardlinking, stub_path=success_stub,
    extra_argv=["--terminal", str(root / "terminal-hardlinked.json")])
for name, receipt, receipt_path, launch_path, stub_path in (
    ("phase-forged.md", forged, forged_receipt, forged_launch, stub),
    ("phase-ignored.md", ignored, ignored_receipt, ignored_launch, stub),
    ("phase-inherited.md", inherited, inherited_receipt, inherited_launch, stub),
    ("phase-hardlinked.md", hardlinked, hardlinked_receipt, hardlinked_launch, success_stub),
):
    complete_phase(name, receipt, receipt_path, launch_path, stub_path)
PY

heldout_passes() {
  local phase="$1" receipt="$2" launch="$3" marker="${4:-}" stub_path="${5:-$tmp/producer-stub.py}"
  API_TOKEN=real-api-token MODEL=real-model-token ALT_TOKEN=real-alt-token \
  HELDOUT_CREDENTIAL_SENTINEL=must-not-reach-wrapper IMPLEMENTAUDIT_TEST_INHERITED_MARKER="$marker" \
  IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB="$stub_path" \
  bash "$checker" --phase "$phase" --rehearsal "$receipt" --launch "$launch" >/dev/null 2>&1
}

if heldout_passes "$tmp/phase-forged.md" "$tmp/receipt-forged.json" "$tmp/launch-forged.json"; then failures+=("wrapper-forges-wrapper-visible-event-without-stub"); fi
if heldout_passes "$tmp/phase-forged.md" "$tmp/receipt-changed.json" "$tmp/launch-changed.json"; then failures+=("self-consistent-changed-argv-env-terminal-pass"); fi
if heldout_passes "$tmp/phase-ignored.md" "$tmp/receipt-ignored.json" "$tmp/launch-ignored.json"; then failures+=("stub-exit-23-ignored-by-wrapper-passes"); fi
if heldout_passes "$tmp/phase-inherited.md" "$tmp/receipt-inherited.json" "$tmp/launch-inherited.json" "$tmp/inherited-marker" && [ -f "$tmp/inherited-marker" ]; then failures+=("undeclared-credential-sentinel-reaches-wrapper"); fi
if heldout_passes "$tmp/phase-hardlinked.md" "$tmp/receipt-hardlinked.json" "$tmp/launch-hardlinked.json" "" "$tmp/producer-success.py"; then failures+=("hardlink-terminal-alias-passes"); fi
if [ "$(<"$tmp/hardlink-victim.txt")" != "do-not-overwrite" ]; then failures+=("hardlink-terminal-alias-overwrites-victim"); fi

seed_candidate() {
  local candidate="$tmp/$1"
  mkdir -p "$candidate/scripts" "$candidate/tests" "$candidate/fixtures/scarce-resource-rehearsal" "$candidate/fixtures/run-root-example/phases"
  cp -R skills "$candidate/skills"
  cp scripts/build-release-asset.sh "$candidate/scripts/build-release-asset.sh"
  cp tests/scarce-resource-rehearsal-contract.test.sh "$candidate/tests/"
  cp fixtures/scarce-resource-rehearsal/cases.json "$candidate/fixtures/scarce-resource-rehearsal/"
  cp fixtures/run-root-example/phases/phase-1.md "$candidate/fixtures/run-root-example/phases/"
  printf '%s\n' "$candidate"
}
seed_probe_authority() {
  local authority="$tmp/$1"
  mkdir -p "$authority/scripts" "$authority/tests"
  cp "$reachability" "$authority/scripts/check-helper-reachability.sh"
  cp tests/scarce-resource-rehearsal-contract.test.sh \
    "$authority/tests/scarce-resource-rehearsal-contract.test.sh"
  printf '%s\n' "$authority"
}
expect_rejected() {
  local label="$1" candidate="$2"
  if bash "$reachability" --repo-root "$candidate" >/dev/null 2>&1; then failures+=("$label"); fi
}
expect_rejected_with_diagnostic() {
  local label="$1" expected="$2" candidate="$3" output
  if output="$(bash "$reachability" --repo-root "$candidate" 2>&1)"; then
    failures+=("$label")
  elif ! grep -Fq "$expected" <<<"$output"; then
    failures+=("$label-diagnostic-lost")
  fi
}
expect_authority_probe_timeout() {
  local label="$1" expected="$2" candidate="$3" authority="$4" output
  if output="$(bash "$authority/scripts/check-helper-reachability.sh" --repo-root "$candidate" 2>&1)"; then
    failures+=("$label")
  elif ! grep -Fq "$expected" <<<"$output"; then
    failures+=("$label-diagnostic-lost")
  fi
}
stall_probe_authority() {
  local authority="$1"
  python - "$authority/tests/scarce-resource-rehearsal-contract.test.sh" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
injection = 'printf "outer-timeout-diagnostic\\n" >&2\nsleep 60 &\nprintf "%s\\n" "$!" > "$PWD/.outer-timeout-child.pid"\nwait\n'
if text.count("checker=") != 1:
    raise SystemExit("expected one checker binding")
path.write_text(text.replace("checker=", injection + "checker="), encoding="utf-8")
PY
}
expect_no_pid() {
  local label="$1" pid_file="$2"
  python - "$pid_file" <<'PY' || failures+=("$label-child-survived")
import os, subprocess, sys
from pathlib import Path

pid = int(Path(sys.argv[1]).read_text(encoding="utf-8"))
if os.name == "nt":
    result = subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    raise SystemExit(1 if result.returncode == 0 else 0)
try: os.kill(pid, 0)
except OSError: raise SystemExit(0)
os.kill(pid, 9)
raise SystemExit(1)
PY
}
if [ "$candidate_probe_only" -eq 1 ]; then
  self_authorized="$(seed_candidate candidate-owned-probe)"
  sed -i 's/--rehearsal)/--receipt)/' \
    "$self_authorized/skills/implementaudit/scripts/check-authorization-binding.sh"
  printf 'exit 0\n' > "$self_authorized/tests/scarce-resource-rehearsal-contract.test.sh"
  chmod +x "$self_authorized/tests/scarce-resource-rehearsal-contract.test.sh"
  if bash "$reachability" --repo-root "$self_authorized" >/dev/null 2>&1; then
    printf '%s\n' 'r11-r30-review-heldouts: GAP-REVISE reproduced: candidate-owned-probe-self-authorizes' >&2
    exit 1
  fi
  printf '%s\n' 'r11-r30-review-heldouts: candidate-probe heldout ok'
  exit 0
fi
if [ "$outer_timeout_only" -eq 1 ]; then
  stalled_consumer="$(seed_candidate stalled-consumer)"
  stalled_authority="$(seed_probe_authority stalled-authority)"
  stall_probe_authority "$stalled_authority"
  expect_authority_probe_timeout stalled-authority-process-tree \
    'outer-timeout-diagnostic' "$stalled_consumer" "$stalled_authority"
  expect_no_pid stalled-candidate-process-tree "$stalled_consumer/.outer-timeout-child.pid"
  if [ "${#failures[@]}" -gt 0 ]; then
    printf 'r11-r30-review-heldouts: GAP-REVISE reproduced: %s\n' "${failures[*]}" >&2
    exit 1
  fi
  printf 'r11-r30-review-heldouts: outer-timeout heldout ok\n'
  exit 0
fi

# R32 authority is the actual candidate F10 route.  These mutations collapse
# the prior AST syntax corpus into execution-state controls.
missing="$(seed_candidate missing)"
sed -i 's/--rehearsal)/--receipt)/' "$missing/skills/implementaudit/scripts/check-authorization-binding.sh"
expect_rejected missing-parser-arm "$missing"

self_authorized="$(seed_candidate candidate-owned-probe)"
sed -i 's/--rehearsal)/--receipt)/' "$self_authorized/skills/implementaudit/scripts/check-authorization-binding.sh"
printf 'exit 0\n' > "$self_authorized/tests/scarce-resource-rehearsal-contract.test.sh"
chmod +x "$self_authorized/tests/scarce-resource-rehearsal-contract.test.sh"
expect_rejected candidate-owned-probe-self-authorizes "$self_authorized"

optional="$(seed_candidate optional)"
sed -i 's/^mediator_thread\.start()$/if os.environ.get("R30_OPTIONAL"): mediator_thread.start()/' "$optional/skills/implementaudit/scripts/check-authorization-binding.sh"
expect_rejected optional-start-not-traversed "$optional"

dead="$(seed_candidate dead)"
sed -i 's/^mediator_thread\.start()$/if False: mediator_thread.start()/' "$dead/skills/implementaudit/scripts/check-authorization-binding.sh"
expect_rejected dead-start-not-traversed "$dead"

reordered="$(seed_candidate reordered)"
sed -i 's/^mediator_thread\.start()$/mediator_thread.join()/' "$reordered/skills/implementaudit/scripts/check-authorization-binding.sh"
expect_rejected reordered-start-join "$reordered"

rebound="$(seed_candidate rebound)"
sed -i '/^mediator_thread = threading\.Thread/i run_bounded_stub = lambda: None' "$rebound/skills/implementaudit/scripts/check-authorization-binding.sh"
expect_rejected rebound-stub "$rebound"

deleted="$(seed_candidate deleted)"
sed -i '/^mediator_thread = threading\.Thread/i del run_bounded_stub' "$deleted/skills/implementaudit/scripts/check-authorization-binding.sh"
expect_rejected deleted-stub "$deleted"

deferred="$(seed_candidate deferred)"
sed -i 's/^mediator_thread\.start()$/def deferred_start(): mediator_thread.start()/' "$deferred/skills/implementaudit/scripts/check-authorization-binding.sh"
expect_rejected deferred-start "$deferred"

handler_only="$(seed_candidate handler-only)"
sed -i 's/^mediator_thread\.start()$/try: pass\nexcept RuntimeError: mediator_thread.start()/' "$handler_only/skills/implementaudit/scripts/check-authorization-binding.sh"
expect_rejected handler-only-start "$handler_only"

decorated="$(seed_candidate decorated-noop)"
sed -i '/^def run_bounded_stub()/i def nullify(fn): return lambda: None\n@nullify' "$decorated/skills/implementaudit/scripts/check-authorization-binding.sh"
expect_rejected decorated-noop-stub "$decorated"

dead_consumer="$(seed_candidate dead-consumer)"
python - "$dead_consumer/skills/implementaudit/scripts/validate-phase.sh" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
needle = '  IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB="$producer_stub" \\\n+'
needle = '  IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB="$producer_stub" ' + chr(92) + '\n'
replacement = '  cp "$rehearsal" "$(phase_field \'Rehearsal terminal artifact\')"\n  exit 0\n' + needle
if text.count(needle) != 1:
    raise SystemExit("expected one native rehearsal invocation")
path.write_text(text.replace(needle, replacement), encoding="utf-8")
PY
expect_rejected_with_diagnostic dead-static-invocation-with-copied-terminal \
  'R30 native phase route did not invoke the declared helper' "$dead_consumer"

stalled_consumer="$(seed_candidate stalled-consumer)"
stalled_authority="$(seed_probe_authority stalled-authority)"
stall_probe_authority "$stalled_authority"
expect_authority_probe_timeout stalled-authority-process-tree \
  'outer-timeout-diagnostic' "$stalled_consumer" "$stalled_authority"
expect_no_pid stalled-authority-process-tree "$stalled_consumer/.outer-timeout-child.pid"

inert="$(seed_candidate inert-deferred)"
sed -i '/^mediator_thread\.start()$/i deferred_lambda = lambda: sys.exit(0)\ndeferred_generator = (sys.exit(0) for _ in ())\n[sys.exit(0) for _ in []]' "$inert/skills/implementaudit/scripts/check-authorization-binding.sh"
if ! bash "$reachability" --repo-root "$inert" >/dev/null 2>&1; then failures+=("inert-lambda-generator-empty-listcomp-rejects-live-route"); fi

if ! grep -Fqx 'helper-mode: check-authorization-binding.sh|--phase --rehearsal --launch|<phase> <receipt> <launch>|failed-rehearsal-blocks-launch|scripts/validate-phase.sh' skills/implementaudit/references/repo-state-comparison.md; then failures+=("rehearsal-route-is-generic-prose-and-direct-test-only"); fi

asset_dir="$tmp/r33-asset"
bash scripts/build-release-asset.sh "$asset_dir" >/dev/null
if [ "$(wc -c < "$asset_dir/IMPLEMENTAUDIT.skill")" -gt 258000 ]; then failures+=("r33-package-capacity-over-258000"); fi

if [ "${#failures[@]}" -gt 0 ]; then
  printf 'r11-r30-review-heldouts: GAP-REVISE reproduced: %s\n' "${failures[*]}" >&2
  exit 1
fi
printf 'r11-r30-review-heldouts: ok\n'
