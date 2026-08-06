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

python - "$fixture" "$tmp" <<'PY'
import copy
import hashlib
import json
import pathlib
import sys

fixture = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"))
out = pathlib.Path(sys.argv[2])

def canonical_hash(argv, env_keys):
    preimage = json.dumps(
        {"argv": argv, "env_keys_present": sorted(env_keys)},
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(preimage).hexdigest()

launch = {
    "argv": fixture["argv"],
    "env_keys_present": fixture["env_keys_present"],
    "terminal_artifact_path": fixture["terminal_artifact_path"],
    "launch_records": 1,
    "metered_calls": 0,
}
receipt = {
    "rehearsed_command_hash": canonical_hash(launch["argv"], launch["env_keys_present"]),
    "stub_identity": fixture["stub_identity"],
    "stubbed_components": ["producer"],
    "env_keys_present": fixture["env_keys_present"],
    "terminal_artifact_path": fixture["terminal_artifact_path"],
    "exit_code": 0,
    "disposition": "PASS",
    "timestamp": "2026-08-06T12:00:00Z",
}

def write(name, value):
    (out / name).write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

write("launch-good.json", launch)
write("receipt-good.json", receipt)

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
must_fail F5-missing-residual rehearse "$tmp/phase-gap-missing.md" "$tmp/receipt-gap.json" "$tmp/launch-good.json"
must_pass F5-matched-residual rehearse "$tmp/phase-gap.md" "$tmp/receipt-gap.json" "$tmp/launch-good.json"

# F7: a repaired receipt may pass on a manual re-run. The policy itself must
# keep that repair manual and forbid automatic retries.
must_pass F7 rehearse "$tmp/phase-budget.md" "$tmp/receipt-good.json" "$tmp/launch-good.json"

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
printf '%s' "$p411_text" | grep -qi 'second apparatus.*cold review' || fail "F6 second-apparatus judgment must remain cold review"
printf '%s' "$p411_text" | grep -qi 'manual repair.*re-run' || fail "F7 manual repair/re-run rule missing"
printf '%s' "$p411_text" | grep -qi 'no automatic retr\|must not automatically retr' || fail "F7 automatic retry prohibition missing"
grep -q '^Scarce resource budget: {{N <resource> | none}}$' "$template" || fail "phase budget field missing"

printf 'scarce-resource-rehearsal-contract: ok (F1-F8; zero metered calls)\n'
