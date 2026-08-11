#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
probe_only=0
if [ "${1:-}" = "--r30-probe" ]; then
  probe_only=1
  shift
  [ "${1:-}" = "--repo-root" ] && [ "$#" -eq 2 ] || {
    printf 'usage: scarce-resource-rehearsal-contract.test.sh --r30-probe --repo-root <dir>\n' >&2
    exit 2
  }
  repo_root="$(cd "$2" && pwd)"
  shift 2
elif [ "$#" -ne 0 ]; then
  printf 'usage: scarce-resource-rehearsal-contract.test.sh [--r30-probe --repo-root <dir>]\n' >&2
  exit 2
fi
cd "$repo_root"

checker="skills/implementaudit/scripts/check-authorization-binding.sh"
policy="skills/implementaudit/references/phase-design.md"
template="skills/implementaudit/templates/phase-goal.txt"
fixture="fixtures/scarce-resource-rehearsal/cases.json"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
fail() { printf 'scarce-resource-rehearsal-contract: %s\n' "$*" >&2; exit 1; }

# The declared wrapper is the production-side launch boundary.  It receives no
# terminal or receipt controls: it propagates the bounded producer result, and
# the producer alone emits its execution event.  The checker is the terminal
# author after observing that event.
cat > "$tmp/production-wrapper.py" <<'PY'
#!/usr/bin/env python3
import os
import subprocess
import sys

stub = os.environ["IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB"]
if os.environ.get("HELDOUT_CREDENTIAL_SENTINEL"):
    raise SystemExit("caller credential sentinel leaked into wrapper")
if os.environ.get("API_TOKEN") != "" or os.environ.get("MODEL") != "":
    raise SystemExit("declared environment keys must be empty rehearsal placeholders")
raise SystemExit(subprocess.run([sys.executable, stub], check=False).returncode)
PY
cat > "$tmp/producer-stub.py" <<'PY'
#!/usr/bin/env python3
raise SystemExit(0)
PY
cat > "$tmp/ignoring-wrapper.py" <<'PY'
#!/usr/bin/env python3
import os
import subprocess
import sys

# Deliberately wrong: a wrapper that ignores the producer exit must not pass
# merely because it returns zero itself.
subprocess.run([sys.executable, os.environ["IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB"]], check=False)
PY
printf '%s\n' '#!/usr/bin/env python3' 'raise SystemExit(23)' > "$tmp/producer-stub-23.py"
printf '%s\n' '#!/usr/bin/env python3' 'import time' 'time.sleep(60)' > "$tmp/producer-stub-hang.py"
cat > "$tmp/producer-stub-child-hang.py" <<'PY'
#!/usr/bin/env python3
import subprocess
import sys
import time
from pathlib import Path

child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"])
Path(__file__).with_suffix(".pid").write_text(str(child.pid), encoding="utf-8")
time.sleep(60)
PY
printf '%s\n' '#!/usr/bin/env python3' 'import time' 'time.sleep(60)' > "$tmp/wrapper-hang.py"
chmod +x "$tmp/production-wrapper.py" "$tmp/producer-stub.py" "$tmp/producer-stub-23.py" \
  "$tmp/producer-stub-hang.py" "$tmp/producer-stub-child-hang.py" "$tmp/wrapper-hang.py" "$tmp/ignoring-wrapper.py"

cat > "$tmp/phase-budget.md" <<'EOF'
Scarce resource budget: 2 model-calls
Residual risk: none
EOF
cat > "$tmp/phase-none.md" <<'EOF'
Scarce resource budget: none
Residual risk: none
EOF
cat > "$tmp/phase-gap.md" <<'EOF'
Scarce resource budget: 2 model-calls
Residual risk: terminal-writer is interposed during rehearsal
EOF
cat > "$tmp/phase-gap-missing.md" <<'EOF'
Scarce resource budget: 2 model-calls
Residual risk: none
EOF

python - "$fixture" "$tmp" "$tmp/production-wrapper.py" "$tmp/rehearsal-terminal.json" "$tmp/producer-stub.py" <<'PY'
import copy
import hashlib
import json
import pathlib
import sys

fixture = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
out = pathlib.Path(sys.argv[2])
wrapper = sys.argv[3]
terminal = sys.argv[4]
stub = pathlib.Path(sys.argv[5])

def canonical_hash(argv, env_keys):
    preimage = json.dumps(
        {"argv": argv, "env_keys_present": sorted(env_keys)},
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(preimage).hexdigest()

launch = {
    "argv": [sys.executable, wrapper, "--input", "fixture.txt"],
    "env_keys_present": fixture["env_keys_present"],
    "terminal_artifact_path": terminal,
    "launch_records": 1,
    "metered_calls": 0,
}
receipt = {
    "rehearsed_command_hash": canonical_hash(launch["argv"], launch["env_keys_present"]),
    "stub_identity": "sha256:" + hashlib.sha256(stub.read_bytes()).hexdigest(),
    "stubbed_components": ["producer"],
    "env_keys_present": fixture["env_keys_present"],
    "terminal_artifact_path": terminal,
    "exit_code": 0,
    "disposition": "PASS",
    "timestamp": "2026-08-06T12:00:00Z",
}

def write(name, value):
    (out / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

write("launch-good.json", launch)
write("receipt-good.json", receipt)

gap_launch = copy.deepcopy(launch)
gap_launch["terminal_artifact_path"] = str(out / "rehearsal-gap-terminal.json")
write("launch-gap.json", gap_launch)

f1_launch = copy.deepcopy(launch)
f1_launch.update(argv=[], launch_records=0, metered_calls=0)
f1_receipt = copy.deepcopy(receipt)
f1_receipt.update(exit_code=2, disposition="FAIL")
write("launch-f1-zero.json", f1_launch)
write("receipt-f1-fail.json", f1_receipt)

path_mismatch = copy.deepcopy(receipt)
path_mismatch["terminal_artifact_path"] = "evidence/other-terminal.json"
write("receipt-path-mismatch.json", path_mismatch)

drift_launch = copy.deepcopy(launch)
drift_launch["env_keys_present"] = ["API_TOKEN", "MODEL", "REGION"]
write("launch-drift.json", drift_launch)

gap = copy.deepcopy(receipt)
gap["stubbed_components"] = ["producer", "terminal-writer"]
gap["disposition"] = "PASS_WITH_SCOPE_GAP"
gap["terminal_artifact_path"] = gap_launch["terminal_artifact_path"]
write("receipt-gap.json", gap)

extra = copy.deepcopy(receipt)
extra["unexpected"] = "not allowed"
write("receipt-extra.json", extra)
env_values = copy.deepcopy(receipt)
env_values["env_values"] = {"API_TOKEN": "redacted-but-still-forbidden"}
write("receipt-env-values.json", env_values)
key_value = copy.deepcopy(receipt)
key_value["env_keys_present"] = ["API_TOKEN=secret", "MODEL"]
write("receipt-key-value.json", key_value)
unsorted_keys = copy.deepcopy(receipt)
unsorted_keys["env_keys_present"] = ["MODEL", "API_TOKEN"]
write("receipt-unsorted.json", unsorted_keys)
duplicate_keys = copy.deepcopy(receipt)
duplicate_keys["env_keys_present"] = ["API_TOKEN", "API_TOKEN", "MODEL"]
write("receipt-duplicate.json", duplicate_keys)
bad_type = copy.deepcopy(receipt)
bad_type["exit_code"] = True
write("receipt-type-invalid.json", bad_type)

# Raw JSON is intentional: ordinary dict serialization cannot preserve
# duplicate object members. A strict untrusted-data parser must reject both
# contradictions instead of silently retaining the final value.
receipt_text = json.dumps(receipt, indent=2) + "\n"
(out / "receipt-duplicate-member.json").write_text(
    receipt_text.replace('"exit_code": 0', '"exit_code": 2,\n  "exit_code": 0', 1),
    encoding="utf-8",
)
launch_text = json.dumps(launch, indent=2) + "\n"
(out / "launch-duplicate-member.json").write_text(
    launch_text.replace('"argv": [', '"argv": [],\n  "argv": [', 1),
    encoding="utf-8",
)

def phase(name, receipt_path, launch_path, receipt, stub_path=stub):
    (out / name).write_text(
        "Scarce resource budget: 2 model-calls\n"
        "Residual risk: terminal-writer is interposed during rehearsal\n"
        f"Rehearsal receipt: {receipt_path}\n"
        f"Rehearsal launch: {launch_path}\n"
        f"Rehearsal producer stub: {stub_path}\n"
        f"Rehearsal command hash: {receipt['rehearsed_command_hash']}\n"
        f"Rehearsal terminal artifact: {receipt['terminal_artifact_path']}\n"
        f"Rehearsal environment keys: {','.join(receipt['env_keys_present'])}\n",
        encoding="utf-8",
    )

phase("phase-budget.md", out / "receipt-good.json", out / "launch-good.json", receipt)
phase("phase-gap.md", out / "receipt-gap.json", out / "launch-gap.json", gap)
phase("phase-gap-missing.md", out / "receipt-gap.json", out / "launch-gap.json", gap)

consumer_launch = copy.deepcopy(launch)
consumer_launch["terminal_artifact_path"] = str(out / "consumer-terminal.json")
consumer_receipt = copy.deepcopy(receipt)
consumer_receipt["terminal_artifact_path"] = consumer_launch["terminal_artifact_path"]
write("launch-consumer.json", consumer_launch)
write("receipt-consumer.json", consumer_receipt)
consumer_phase = pathlib.Path("fixtures/run-root-example/phases/phase-1.md").read_text(encoding="utf-8")
consumer_fields = (
    "Scarce resource budget: 2 model-calls\n"
    f"Rehearsal receipt: {out / 'receipt-consumer.json'}\n"
    f"Rehearsal launch: {out / 'launch-consumer.json'}\n"
    f"Rehearsal producer stub: {stub}\n"
    f"Rehearsal command hash: {consumer_receipt['rehearsed_command_hash']}\n"
    f"Rehearsal terminal artifact: {consumer_receipt['terminal_artifact_path']}\n"
    f"Rehearsal environment keys: {','.join(consumer_receipt['env_keys_present'])}\n"
)
(out / "phase-consumer.md").write_text(
    consumer_phase.replace("Depends on phases: none\n", "Depends on phases: none\n" + consumer_fields),
    encoding="utf-8",
)

ignored_launch = copy.deepcopy(launch)
ignored_launch["argv"] = [sys.executable, str(out / "ignoring-wrapper.py"), "--input", "fixture.txt"]
ignored_launch["terminal_artifact_path"] = str(out / "ignored-terminal.json")
ignored_receipt = copy.deepcopy(receipt)
ignored_receipt["rehearsed_command_hash"] = canonical_hash(
    ignored_launch["argv"], ignored_launch["env_keys_present"]
)
ignored_receipt["terminal_artifact_path"] = ignored_launch["terminal_artifact_path"]
ignored_stub = out / "producer-stub-23.py"
ignored_receipt["stub_identity"] = "sha256:" + hashlib.sha256(ignored_stub.read_bytes()).hexdigest()
write("launch-ignored.json", ignored_launch)
write("receipt-ignored.json", ignored_receipt)
phase("phase-ignored.md", out / "receipt-ignored.json", out / "launch-ignored.json", ignored_receipt, ignored_stub)
PY

python - "$tmp" <<'PY'
import hashlib, json, re, sys
from pathlib import Path

out = Path(sys.argv[1])
base_launch = json.loads((out / "launch-good.json").read_text(encoding="utf-8"))
base_receipt = json.loads((out / "receipt-good.json").read_text(encoding="utf-8"))
base_phase = (out / "phase-budget.md").read_text(encoding="utf-8")

def command_hash(launch):
    return hashlib.sha256(json.dumps({"argv": launch["argv"], "env_keys_present": sorted(launch["env_keys_present"])}, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()

def write_case(name, wrapper, stub):
    launch = dict(base_launch)
    launch["argv"] = [sys.executable, str(wrapper), "--input", "fixture.txt"]
    launch["terminal_artifact_path"] = str(out / f"terminal-{name}.json")
    receipt = dict(base_receipt)
    receipt["rehearsed_command_hash"] = command_hash(launch)
    receipt["stub_identity"] = "sha256:" + hashlib.sha256(stub.read_bytes()).hexdigest()
    receipt["terminal_artifact_path"] = launch["terminal_artifact_path"]
    (out / f"launch-{name}.json").write_text(json.dumps(launch), encoding="utf-8")
    (out / f"receipt-{name}.json").write_text(json.dumps(receipt), encoding="utf-8")
    replacements = {
        "Rehearsal receipt": out / f"receipt-{name}.json", "Rehearsal launch": out / f"launch-{name}.json",
        "Rehearsal producer stub": stub, "Rehearsal command hash": receipt["rehearsed_command_hash"],
        "Rehearsal terminal artifact": receipt["terminal_artifact_path"],
    }
    phase = base_phase
    for field, value in replacements.items():
        phase = re.sub(rf"(?m)^{re.escape(field)}:.*$", lambda _: f"{field}: {value}", phase)
    (out / f"phase-{name}.md").write_text(phase, encoding="utf-8")

write_case("producer-hang", out / "production-wrapper.py", out / "producer-stub-hang.py")
write_case("producer-child-hang", out / "production-wrapper.py", out / "producer-stub-child-hang.py")
write_case("wrapper-hang", out / "wrapper-hang.py", out / "producer-stub.py")
PY

must_pass() {
  local label="$1"; shift
  "$@" >/dev/null 2>&1 || fail "$label must pass"
}
must_fail() {
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then fail "$label must fail"; fi
}
must_timeout_diagnostic() {
  local label="$1" expected="$2"; shift 2
  local log="$tmp/$label.log"
  command -v timeout >/dev/null 2>&1 || fail "$label needs timeout"
  if timeout 12 "$@" >"$log" 2>&1; then fail "$label must fail"; fi
  grep -Fq "$expected" "$log" || { cat "$log" >&2; fail "$label must report $expected"; }
}
must_not_leave_pid() {
  local label="$1" pid_file="$2"
  python - "$pid_file" <<'PY' || fail "$label left a child process"
import os, subprocess, sys
from pathlib import Path

pid = int(Path(sys.argv[1]).read_text(encoding="utf-8"))
if os.name == "nt":
    result = subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    raise SystemExit(1 if result.returncode == 0 else 0)
try:
    os.kill(pid, 0)
except OSError:
    raise SystemExit(0)
os.kill(pid, 9)
raise SystemExit(1)
PY
}
rehearse() {
  bash "$checker" --phase "$1" --rehearsal "$2" --launch "$3"
}
run_production_rehearsal() {
  API_TOKEN=fixture-token MODEL=fixture-model HELDOUT_CREDENTIAL_SENTINEL=withhold-me \
  IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB="${IMPLEMENTAUDIT_TEST_PRODUCER_STUB:-$tmp/producer-stub.py}" \
  "$@"
}

run_phase_with_timeout() {
  local log_path="$1" seconds="$2"; shift 2
  python - "$log_path" "$seconds" "$@" <<'PY'
import os, signal, subprocess, sys
from pathlib import Path

log_path, seconds, *command = sys.argv[1:]
creationflags = subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    start_new_session=os.name != "nt", creationflags=creationflags)
timed_out = False
try:
    stdout, stderr = process.communicate(timeout=float(seconds))
except subprocess.TimeoutExpired:
    timed_out = True
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    else:
        os.killpg(process.pid, signal.SIGKILL)
    stdout, stderr = process.communicate()
Path(log_path).write_bytes(stdout + stderr)
if timed_out:
    sys.stderr.write(f"r30 probe: candidate validate-phase timed out after {seconds}s\n")
    raise SystemExit(124)
raise SystemExit(process.returncode)
PY
}

r30_probe() {
  local probe_skills="$tmp/r30-probe-skills" real_helper="$tmp/r30-real-check-authorization-binding.sh"
  local sentinel marker nonce log_path
  marker="${IMPLEMENTAUDIT_TEST_R30_SENTINEL_MARKER:-$tmp/r30-sentinel-marker.json}"
  log_path="$tmp/r30-probe-validator.log"
  cp -R "$repo_root/skills" "$probe_skills"
  sentinel="$probe_skills/implementaudit/scripts/check-authorization-binding.sh"
  mv "$sentinel" "$real_helper"
  cmp -s "$real_helper" "$repo_root/skills/implementaudit/scripts/check-authorization-binding.sh" \
    || fail "R30 probe relocated helper differs from candidate source"
  nonce="$(python - <<'PY'
import secrets
print(secrets.token_hex(32))
PY
)"
  cat > "$sentinel" <<EOF
#!/usr/bin/env bash
set -euo pipefail
python - "$marker" "$nonce" "\$@" <<'PY'
import json, os, stat, sys
from pathlib import Path

marker, nonce, *argv = sys.argv[1:]
fd = os.open(marker, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
with os.fdopen(fd, "w", encoding="utf-8") as stream:
    json.dump({"nonce": nonce, "argv": argv}, stream, separators=(",", ":"))
    stream.write("\\n")
entry = Path(marker).lstat()
if not stat.S_ISREG(entry.st_mode) or entry.st_nlink != 1:
    raise SystemExit("invalid verifier sentinel marker")
PY
exec "$real_helper" "\$@"
EOF
  chmod 700 "$sentinel" "$real_helper"
  if ! run_production_rehearsal run_phase_with_timeout "$log_path" 10 \
    "$BASH" -c 'cd "$1" && exec bash validate-phase.sh "$2"' r30-probe \
    "$probe_skills/implementaudit/scripts" "$tmp/phase-consumer.md"; then
    cat "$log_path" >&2 || true
    fail "R30 native phase consumer failed"
  fi
  python - "$marker" "$nonce" "$tmp/phase-consumer.md" "$tmp/receipt-consumer.json" "$tmp/launch-consumer.json" <<'PY' \
    || fail "R30 native phase route did not invoke the declared helper"
import json, os, stat, sys
from pathlib import Path

marker, nonce, phase, receipt, launch = map(Path, sys.argv[1:])
entry = marker.lstat()
if not stat.S_ISREG(entry.st_mode) or entry.st_nlink != 1:
    raise SystemExit(1)
observed = json.loads(marker.read_text(encoding="utf-8"))
argv = observed.get("argv") if type(observed) is dict else None
expected_paths = (phase, receipt, launch)
identity = type(argv) is list and len(argv) == 6 and argv[::2] == ["--phase", "--rehearsal", "--launch"]
if identity:
    identity = all(Path(actual).resolve() == expected for actual, expected in zip(argv[1::2], expected_paths))
if observed.get("nonce") != str(nonce) or not identity:
    sys.stderr.write("r30 probe: verifier sentinel marker identity mismatch\n")
    raise SystemExit(1)
PY
  [ -f "$tmp/consumer-terminal.json" ] || fail "R30 native phase route did not bind terminal"
  python - "$tmp/launch-consumer.json" "$tmp/consumer-terminal.json" <<'PY' \
    || fail "R30 probe did not retain the zero-meter terminal receipt"
import json, pathlib, sys
launch = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
terminal = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
raise SystemExit(0 if launch["metered_calls"] == 0 and terminal["exit_code"] == 0 else 1)
PY
}

if [ "$probe_only" -eq 1 ]; then
  r30_probe
  printf 'scarce-resource-rehearsal-contract: r30-probe ok (F10; zero metered calls)\n'
  exit 0
fi

# F1: a failed malformed-argv rehearsal cannot authorize launch; the fixture
# independently proves that neither a launch record nor a metered call occurred.
must_fail F1 rehearse "$tmp/phase-budget.md" "$tmp/receipt-f1-fail.json" "$tmp/launch-f1-zero.json"
python - "$tmp/launch-f1-zero.json" <<'PY' || fail "F1 counters must remain zero"
import json, pathlib, sys
d = json.loads(pathlib.Path(sys.argv[1]).read_text())
raise SystemExit(0 if d["launch_records"] == 0 and d["metered_calls"] == 0 else 1)
PY

# F2/F3: transport/path incompatibility and post-rehearsal identity drift are
# rejected before a real launch can occur.
must_fail F2 rehearse "$tmp/phase-budget.md" "$tmp/receipt-path-mismatch.json" "$tmp/launch-good.json"
must_fail F3 rehearse "$tmp/phase-budget.md" "$tmp/receipt-good.json" "$tmp/launch-drift.json"

# F4: an explicit `none` budget has no receipt obligation.
must_pass F4 bash "$checker" --phase "$tmp/phase-none.md"

# F5: interposed stubbing is a scope gap and every extra component must be
# named by the phase's residual-risk statement.
must_fail F5-missing-residual rehearse "$tmp/phase-gap-missing.md" "$tmp/receipt-gap.json" "$tmp/launch-gap.json"

# F9: a self-consistent receipt and launch declaration cannot establish a
# rehearsal while the declared production wrapper and bounded producer stub
# have not executed. This was intentionally RED against the former inert
# checker and remains the detached-record false-positive control.
must_fail F9-static-record-false-positive rehearse "$tmp/phase-budget.md" "$tmp/receipt-good.json" "$tmp/launch-good.json"
[ ! -e "$tmp/wrapper-proof" ] || fail "F9 must not claim wrapper execution from a static record"
[ ! -e "$tmp/stub-proof" ] || fail "F9 must not claim stub execution from a static record"

IMPLEMENTAUDIT_TEST_SCOPE_GAP=1 \
must_pass F5-matched-residual run_production_rehearsal rehearse "$tmp/phase-gap.md" "$tmp/receipt-gap.json" "$tmp/launch-gap.json"

# A malicious wrapper can mask the transport exit, but it cannot mask the
# separate stub event: a zero wrapper exit plus producer exit 23 still blocks.
IMPLEMENTAUDIT_TEST_PRODUCER_STUB="$tmp/producer-stub-23.py" \
must_fail F6-stub-exit-propagation run_production_rehearsal rehearse \
  "$tmp/phase-ignored.md" "$tmp/receipt-ignored.json" "$tmp/launch-ignored.json"
[ ! -e "$tmp/ignored-terminal.json" ] || fail "F6 nonzero stub must not receive a terminal"

# The bounded transport cannot leave a hung producer or wrapper behind, and
# must preserve its own timeout diagnostic rather than letting the outer test
# watchdog become the only verdict.
API_TOKEN=fixture-token MODEL=fixture-model HELDOUT_CREDENTIAL_SENTINEL=withhold-me \
IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB="$tmp/producer-stub-hang.py" \
must_timeout_diagnostic F6-producer-timeout 'producer timed out' \
  bash "$checker" --phase "$tmp/phase-producer-hang.md" --rehearsal "$tmp/receipt-producer-hang.json" --launch "$tmp/launch-producer-hang.json"
[ ! -e "$tmp/terminal-producer-hang.json" ] || fail "F6 producer timeout must not receive a terminal"
IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB="$tmp/producer-stub-child-hang.py" \
must_timeout_diagnostic F6-producer-child-timeout 'producer timed out' \
  bash "$checker" --phase "$tmp/phase-producer-child-hang.md" --rehearsal "$tmp/receipt-producer-child-hang.json" --launch "$tmp/launch-producer-child-hang.json"
must_not_leave_pid F6-producer-child-timeout "$tmp/producer-stub-child-hang.pid"
API_TOKEN=fixture-token MODEL=fixture-model HELDOUT_CREDENTIAL_SENTINEL=withhold-me \
IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB="$tmp/producer-stub.py" \
must_timeout_diagnostic F6-wrapper-timeout 'wrapper timed out' \
  bash "$checker" --phase "$tmp/phase-wrapper-hang.md" --rehearsal "$tmp/receipt-wrapper-hang.json" --launch "$tmp/launch-wrapper-hang.json"
[ ! -e "$tmp/terminal-wrapper-hang.json" ] || fail "F6 wrapper timeout must not receive a terminal"

# F7: a repaired receipt may pass on a manual re-run. The policy itself must
# keep that repair manual and forbid automatic retries.
unset IMPLEMENTAUDIT_TEST_SCOPE_GAP
must_pass F7 run_production_rehearsal rehearse "$tmp/phase-budget.md" "$tmp/receipt-good.json" "$tmp/launch-good.json"
[ -f "$tmp/rehearsal-terminal.json" ] || fail "F7 checker did not bind the observed terminal"
! grep -q 'IMPLEMENTAUDIT_REHEARSAL_TERMINAL\|IMPLEMENTAUDIT_REHEARSAL_STUB_PROOF' \
  "$tmp/production-wrapper.py" || fail "F7 wrapper must not author proof or terminal"

# F10/R30: the native phase validator consumes the same audit object and
# executes the declared checker route; this is not a direct-test/prose proxy.
r30_probe

# The verifier-owned sentinel accepts only an absent path it can create.  A
# pre-existing hardlink or symlink must not become an alias for its marker.
sentinel_victim="$tmp/r30-sentinel-victim"
printf 'sentinel-victim\n' > "$sentinel_victim"
for sentinel_alias in "$tmp/r30-sentinel-hardlink" "$tmp/r30-sentinel-symlink"; do
  rm -f "$sentinel_alias"
  if [ "$sentinel_alias" = "$tmp/r30-sentinel-hardlink" ]; then
    ln "$sentinel_victim" "$sentinel_alias"
  elif ! ln -s "$sentinel_victim" "$sentinel_alias" 2>/dev/null; then
    continue
  fi
  if IMPLEMENTAUDIT_TEST_R30_SENTINEL_MARKER="$sentinel_alias" \
    bash "$0" --r30-probe --repo-root "$repo_root" >/dev/null 2>&1; then
    fail "F10 pre-existing sentinel alias must fail"
  fi
done

# F8: strict schemas reject extras, value-bearing fields/key-value strings,
# ordering/uniqueness violations, and booleans masquerading as integers.
for case in extra env-values key-value unsorted duplicate type-invalid; do
  must_fail "F8-$case" rehearse "$tmp/phase-budget.md" "$tmp/receipt-$case.json" "$tmp/launch-good.json"
done
must_fail F8-duplicate-receipt-member rehearse "$tmp/phase-budget.md" "$tmp/receipt-duplicate-member.json" "$tmp/launch-good.json"
must_fail F8-duplicate-launch-member rehearse "$tmp/phase-budget.md" "$tmp/receipt-good.json" "$tmp/launch-duplicate-member.json"

# Policy/template owners: P4-11 occupies its ordered slot, requires exact
# apparatus rehearsal and independent cold review of a second apparatus, and
# exposes the budget field beside mandatory commands.
p410="$(grep -n '^\*\*Rule P4-10 ' "$policy" | cut -d: -f1)"
p411="$(grep -n '^\*\*Rule P4-11 ' "$policy" | cut -d: -f1)"
p412="$(grep -n '^\*\*Rule P4-12 ' "$policy" | cut -d: -f1)"
[ "$p410" -lt "$p411" ] && [ "$p411" -lt "$p412" ] || fail "P4-11 must sit between P4-10 and P4-12"
p411_text="$(sed -n "${p411},$((p412 - 1))p" "$policy" | tr '\n' ' ')"
printf '%s' "$p411_text" | grep -qi 'exact.*wrapper.*argv.*environment-key.*terminal' || fail "P4-11 missing exact apparatus identity"
printf '%s' "$p411_text" | grep -Fq 'IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB' || fail "P4-11 missing bounded producer substitution control"
printf '%s' "$p411_text" | grep -qi 'second apparatus.*cold review' || fail "F6 second-apparatus judgment must remain cold review"
printf '%s' "$p411_text" | grep -qi 'manual repair.*re-run' || fail "F7 manual repair/re-run rule missing"
printf '%s' "$p411_text" | grep -qi 'no automatic retr\|must not automatically retr' || fail "F7 automatic retry prohibition missing"
grep -q '^Scarce resource budget: {{N <resource> | none}}$' "$template" || fail "phase budget field missing"
grep -q '^Rehearsal terminal artifact: {{PATH | none}}$' "$template" || fail "phase terminal binding field missing"

printf 'scarce-resource-rehearsal-contract: ok (F1-F10; zero metered calls)\n'
