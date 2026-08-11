#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
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
import hashlib
import json
import os
import pathlib
import sys

identity = "sha256:" + hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest()
exit_code = int(os.environ.get("IMPLEMENTAUDIT_TEST_STUB_EXIT", "0"))
pathlib.Path(os.environ["IMPLEMENTAUDIT_REHEARSAL_STUB_EVENT"]).write_text(
    json.dumps({
        "stub_identity": identity,
        "nonce": os.environ["IMPLEMENTAUDIT_REHEARSAL_STUB_NONCE"],
        "exit_code": exit_code,
    }) + "\n",
    encoding="utf-8",
)
raise SystemExit(exit_code)
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
sed 's/exit_code = int(os.environ.get("IMPLEMENTAUDIT_TEST_STUB_EXIT", "0"))/exit_code = 23/' \
  "$tmp/producer-stub.py" > "$tmp/producer-stub-23.py"
chmod +x "$tmp/production-wrapper.py" "$tmp/producer-stub.py" "$tmp/producer-stub-23.py" "$tmp/ignoring-wrapper.py"

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

must_pass() {
  local label="$1"; shift
  "$@" >/dev/null 2>&1 || fail "$label must pass"
}
must_fail() {
  local label="$1"; shift
  if "$@" >/dev/null 2>&1; then fail "$label must fail"; fi
}
rehearse() {
  bash "$checker" --phase "$1" --rehearsal "$2" --launch "$3"
}
run_production_rehearsal() {
  API_TOKEN=fixture-token MODEL=fixture-model HELDOUT_CREDENTIAL_SENTINEL=withhold-me \
  IMPLEMENTAUDIT_REHEARSAL_PRODUCER_STUB="${IMPLEMENTAUDIT_TEST_PRODUCER_STUB:-$tmp/producer-stub.py}" \
  "$@"
}

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

# F7: a repaired receipt may pass on a manual re-run. The policy itself must
# keep that repair manual and forbid automatic retries.
unset IMPLEMENTAUDIT_TEST_SCOPE_GAP
must_pass F7 run_production_rehearsal rehearse "$tmp/phase-budget.md" "$tmp/receipt-good.json" "$tmp/launch-good.json"
[ -f "$tmp/rehearsal-terminal.json" ] || fail "F7 checker did not bind the observed terminal"
! grep -q 'IMPLEMENTAUDIT_REHEARSAL_TERMINAL\|IMPLEMENTAUDIT_REHEARSAL_STUB_PROOF' \
  "$tmp/production-wrapper.py" || fail "F7 wrapper must not author proof or terminal"

# F10/R30: the native phase validator consumes the same audit object and
# executes the declared checker route; this is not a direct-test/prose proxy.
must_pass F10-native-phase-consumer run_production_rehearsal \
  bash skills/implementaudit/scripts/validate-phase.sh "$tmp/phase-consumer.md"
[ -f "$tmp/consumer-terminal.json" ] || fail "F10 native phase route did not bind terminal"

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
