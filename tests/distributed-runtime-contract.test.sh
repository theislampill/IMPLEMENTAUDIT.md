#!/usr/bin/env bash
# R0030 immutable RED bootstrap. This test is intentionally unregistered until
# R30-J0 composes the P34/P37 owners and registers the GREEN aggregate once.
set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
admission_fixture="$repo_root/fixtures/distributed-runtime/r48-admission-cases.json"
fencing_fixture="$repo_root/fixtures/distributed-runtime/r48-fencing-cases.json"
action_owner="$repo_root/scripts/check-action-selection-contract.sh"
mutation_owner="$repo_root/skills/implementaudit/scripts/apply-observed-mutation.sh"
claim_owner="$repo_root/skills/implementaudit/scripts/claim-run.sh"
tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  printf 'distributed-runtime-contract.test: python is required\n' >&2
  exit 1
fi

fail() {
  printf 'distributed-runtime-contract.test: %s\n' "$*" >&2
  return 1
}

fixture_self_check() {
  "${py_cmd[@]}" - "$admission_fixture" "$fencing_fixture" <<'PY'
import copy
import hashlib
import json
import re
import sys
from pathlib import Path

admission_path, fencing_path = map(Path, sys.argv[1:])
admission = json.loads(admission_path.read_text(encoding="utf-8"))
fencing = json.loads(fencing_path.read_text(encoding="utf-8"))

def require(condition, message):
    if not condition:
        raise SystemExit(f"D48 fixture self-check: {message}")

def decide_admission(case):
    o = case["observations"]
    fields = {
        "distributed_trigger", "cheap_local_operation",
        "semantic_retry_eligible", "effect_state",
        "deadline_remaining_ms", "queue_age_ms", "max_queue_age_ms",
        "requested_units", "downstream_available_units",
        "recovery_available_units",
    }
    require(set(o) == fields, f"{case.get('id')}: admission observation members")
    for name in ("distributed_trigger", "cheap_local_operation", "semantic_retry_eligible"):
        require(type(o[name]) is bool, f"{case['id']}: {name} must be boolean")
    for name in (
        "deadline_remaining_ms", "queue_age_ms", "max_queue_age_ms",
        "requested_units", "downstream_available_units",
        "recovery_available_units",
    ):
        require(type(o[name]) is int and o[name] >= 0,
                f"{case['id']}: {name} must be a non-negative integer")
    require(o["effect_state"] in {
        "NOT_STARTED", "IN_FLIGHT", "UNKNOWN", "COMMITTED_VERIFIED",
        "FAILED_NO_EFFECT", "COMPENSATION_PENDING", "COMPENSATED_VERIFIED",
        "MANUAL_RECONCILIATION",
    }, f"{case['id']}: effect state")
    if not o["distributed_trigger"]:
        return "CHEAP_PATH" if o["cheap_local_operation"] else "REFUSE"
    eligible = (
        not o["cheap_local_operation"]
        and o["semantic_retry_eligible"]
        and o["effect_state"] == "FAILED_NO_EFFECT"
        and o["deadline_remaining_ms"] > 0
        and o["queue_age_ms"] <= o["max_queue_age_ms"]
        and o["requested_units"] > 0
        and o["downstream_available_units"] >= o["requested_units"]
        and o["recovery_available_units"] >= o["requested_units"]
    )
    return "ADMIT" if eligible else "REFUSE"

def decide_fencing(case):
    generation = re.compile(r"^G[0-9A-F]{4}$")
    for name in ("controller_generation", "authority_generation", "protected_generation"):
        require(isinstance(case[name], str) and generation.fullmatch(case[name]),
                f"{case.get('id')}: {name}")
    for name in ("preimage_hex", "candidate_hex", "expected_target_hex"):
        require(isinstance(case[name], str) and len(case[name]) % 2 == 0,
                f"{case.get('id')}: {name}")
        bytes.fromhex(case[name])
    require(re.fullmatch(r"[0-9a-f]{64}", case["protected_target_sha256"]) is not None,
            f"{case.get('id')}: protected target digest")
    actual_digest = hashlib.sha256(bytes.fromhex(case["preimage_hex"])).hexdigest()
    if case["authority_generation"] != case["controller_generation"] or case["authority_generation"] != case["protected_generation"]:
        return "REJECTED_NO_MUTATION", "STALE_AUTHORITY_GENERATION", case["preimage_hex"]
    if case["protected_target_sha256"] != actual_digest:
        return "REJECTED_NO_MUTATION", "PROTECTED_TARGET_IDENTITY_MISMATCH", case["preimage_hex"]
    return "COMMITTED", "NONE", case["candidate_hex"]

require(admission.get("schema") == "implementaudit.distributed-runtime.admission-cases.v1",
        "admission schema")
require(admission.get("cell") == "D48-C04", "admission cell")
admission_ids = [case.get("id") for case in admission.get("cases", [])]
require(admission_ids == [
    "D48-C04-01-eligible-capacity-admitted",
    "D48-C04-02-downstream-exhausted",
    "D48-C04-03-recovery-exhausted",
    "D48-C04-04-unknown-effect-not-retriable",
    "D48-C04-05-expired-deadline",
    "D48-C04-06-local-cheap-path",
], "admission case population/order")
for case in admission["cases"]:
    require(set(case) == {"id", "observations", "expected"},
            f"{case.get('id')}: admission case members")
    require(decide_admission(case) == case["expected"],
            f"{case['id']}: expected admission verdict")

require(fencing.get("schema") == "implementaudit.distributed-runtime.fencing-cases.v1",
        "fencing schema")
require(fencing.get("cell") == "D48-C02", "fencing cell")
fencing_ids = [case.get("id") for case in fencing.get("cases", [])]
require(fencing_ids == [
    "D48-C02-01-current-generation-commits",
    "D48-C02-02-stale-generation-rejected",
    "D48-C02-03-wrong-target-fingerprint-rejected",
], "fencing case population/order")
fencing_members = {
    "id", "controller_generation", "authority_generation",
    "protected_generation", "source_path", "preimage_hex", "candidate_hex",
    "protected_target_sha256", "expected_status", "expected_reason",
    "expected_target_hex",
}
for case in fencing["cases"]:
    require(set(case) == fencing_members, f"{case.get('id')}: fencing case members")
    require(case["source_path"] == "target", f"{case['id']}: bounded source path")
    require(decide_fencing(case) == (
        case["expected_status"], case["expected_reason"], case["expected_target_hex"]),
        f"{case['id']}: expected fencing result")

# Independent mutation controls: both failure families must discriminate their
# unsafe false-green, rather than merely parse their own expected labels.
admission_mutant = copy.deepcopy(admission["cases"][1])
admission_mutant["expected"] = "ADMIT"
require(decide_admission(admission_mutant) != admission_mutant["expected"],
        "downstream-capacity mutant false-greened")
recovery_mutant = copy.deepcopy(admission["cases"][2])
recovery_mutant["expected"] = "ADMIT"
require(decide_admission(recovery_mutant) != recovery_mutant["expected"],
        "recovery-capacity mutant false-greened")
fencing_mutant = copy.deepcopy(fencing["cases"][1])
fencing_mutant["expected_status"] = "COMMITTED"
fencing_mutant["expected_reason"] = "NONE"
fencing_mutant["expected_target_hex"] = fencing_mutant["candidate_hex"]
require(decide_fencing(fencing_mutant) != (
    fencing_mutant["expected_status"], fencing_mutant["expected_reason"],
    fencing_mutant["expected_target_hex"]), "stale-generation mutant false-greened")

print("D48_FIXTURE_SELF_CHECK=PASS admission=6/6 fencing=3/3 mutants=3/3")
PY
}

run_d48_c04() {
  local output status mutant mutant_output mutant_status
  output="$(bash "$action_owner" --repo-root "$repo_root" \
    --distributed-runtime-fixture "$admission_fixture" 2>&1)"
  status=$?
  if [ "$status" -ne 0 ]; then
    printf '%s\n' "$output" >&2
    fail "D48-C04 setup/control: current action-selection owner failed with exit $status"
    return 1
  fi
  if ! grep -Fqx 'D48-C04=PASS cases=6/6' <<<"$output"; then
    printf '%s\n' 'D48-C04 RED: retry admitted without downstream or recovery capacity' >&2
    return 1
  fi
  mutant="$tmp/r48-admission-false-green.json"
  "${py_cmd[@]}" - "$admission_fixture" "$mutant" <<'PY'
import json
import sys
from pathlib import Path
source, target = map(Path, sys.argv[1:])
payload = json.loads(source.read_text(encoding="utf-8"))
case = next(row for row in payload["cases"]
            if row["id"] == "D48-C04-02-downstream-exhausted")
case["expected"] = "ADMIT"
target.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")
PY
  mutant_output="$(bash "$action_owner" --repo-root "$repo_root" \
    --distributed-runtime-fixture "$mutant" 2>&1)"
  mutant_status=$?
  if [ "$mutant_status" -eq 0 ] || \
     ! grep -Fq 'D48-C04-02-downstream-exhausted' <<<"$mutant_output"; then
    printf '%s\n' 'D48-C04 RED: retry admitted without downstream or recovery capacity' >&2
    return 1
  fi
  printf '%s\n' 'D48-C04=PASS cases=6/6'
}

write_bytes() {
  "${py_cmd[@]}" - "$1" "$2" <<'PY'
import sys
from pathlib import Path
path = Path(sys.argv[1])
path.parent.mkdir(parents=True, exist_ok=True)
path.write_bytes(bytes.fromhex(sys.argv[2]))
PY
}

prepare_fencing_case() {
  local case_id="$1" controller_generation="$2" authority_generation="$3"
  local protected_generation="$4" source_path="$5" preimage_hex="$6"
  local candidate_hex="$7" protected_sha="$8"
  local case_repo="$tmp/$case_id" run_rel run_root receipt phase_file
  mkdir -p "$case_repo/artifacts"
  git -C "$case_repo" init -q
  git -C "$case_repo" config user.email d48-fixture@example.invalid
  git -C "$case_repo" config user.name d48-fixture
  printf 'D48-C02 cooperating protected-sink fixture\n' >"$case_repo/fixture-seed"
  git -C "$case_repo" add fixture-seed
  git -C "$case_repo" commit -q -m fixture

  run_rel="$(cd "$case_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs \
    bash "$claim_owner" --controller d48-c02 "${case_id,,}")" || return 1
  run_root="$case_repo/$run_rel"
  local promised
  for promised in STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md; do
    cp "$repo_root/skills/implementaudit/templates/$promised" "$run_root/$promised"
  done
  sed -i '/^| 1 |  |  | - |  |  |  | open |$/d' "$run_root/ROADMAP.md"

  write_bytes "$case_repo/$source_path" "$preimage_hex"
  write_bytes "$case_repo/artifacts/candidate.bin" "$candidate_hex"
  phase_file="$run_root/phases/phase-1.md"
  mkdir -p "$run_root/phases" "$run_root/mutation-fences"
  "${py_cmd[@]}" - \
    "$repo_root/fixtures/phase-validation/valid-full-spec.md" "$phase_file" \
    "$run_rel" "$source_path" "$run_root/ROADMAP.md" "$run_root/STATE.md" \
    "$controller_generation" "$(git -C "$case_repo" rev-parse HEAD)" \
    "$(git -C "$case_repo" rev-parse 'HEAD^{tree}')" <<'PY'
import json
import re
import sys
from pathlib import Path

source_file, output_file, run_rel, source, roadmap_file, state_file, epoch, head, tree = sys.argv[1:]
text = Path(source_file).read_text(encoding="utf-8")
text = text.replace("Phase: 1 of 3", "Phase: 1 of 1")
text = text.replace("Run root: .IMPLEMENTAUDIT/runs/add-settings-Xy9Zq1", f"Run root: {run_rel}")
text = text.replace("Baseline ref: abc123def456", "Baseline ref: HEAD")
text = text.replace("Owner/source: src/routes/settings.ts", "Owner/source: issue:#200 D48-C02")
needle = "- Step 1: Create the settings route — target: src/routes/settings.ts (registerSettingsRoutes); change: add GET /api/settings handler behind requireAuth from src/middleware/auth.ts; verify: npm run build; expected: exit 0 with no errors"
authority = json.dumps({"operation": "replace", "source": source, "destination": None}, separators=(",", ":"))
text = text.replace(needle, needle + "\n  mutation-authority: " + authority)
scope = json.dumps({"in": [source], "out": ["README.md"]}, separators=(",", ":"))
text = text.replace("In scope: src/routes/settings.ts, tests/settings.test.ts, src/app.ts", "In scope: D48-C02 protected mutation fixture\nMutation scope: " + scope)
Path(output_file).write_text(text, encoding="utf-8", newline="\n")

with Path(roadmap_file).open("a", encoding="utf-8", newline="\n") as handle:
    handle.write("| 1 | D48-C02 cooperating protected mutation |\n")

state_path = Path(state_file)
state = state_path.read_text(encoding="utf-8")
state = state.replace("| Run root |  |", f"| Run root | `{run_rel}` |")
state = state.replace("| Next action |  |", "| Next action | exercise protected mutation fence |")
state = re.sub(r"^Current epoch: .+$", f"Current epoch: {epoch}", state, flags=re.M)
anchor = "| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|"
row = f"| {epoch} | new-session | 2026-08-20T00:00:00Z | repo at `{head}` / `{tree}` | yes | D48-C02 fixture reconciliation complete |"
state_path.write_text(state.replace(anchor, anchor + "\n" + row), encoding="utf-8", newline="\n")
PY

  receipt="$(cd "$case_repo" && bash "$claim_owner" \
    --resume-controller d48-c02 --boundary new-session --epoch "$controller_generation")" \
    || return 1
  (cd "$case_repo" && bash "$claim_owner" --verify-resume-receipt "$receipt") >/dev/null \
    || return 1
  "${py_cmd[@]}" - "$run_root/mutation-fences/phase-1-step-1.json" \
    "$source_path" "$protected_sha" "$controller_generation" \
    "$authority_generation" "$protected_generation" "$receipt" <<'PY'
import json
import sys
from pathlib import Path

path, source, digest, controller, authority, protected, receipt = sys.argv[1:]
payload = {
    "schema": "implementaudit.protected-mutation-fence.v1",
    "phase": 1,
    "step": 1,
    "source_path": source,
    "protected_target": {"sha256": digest, "byte_length": 9},
    "controller_generation": controller,
    "authority_generation": authority,
    "protected_generation": protected,
    "verified_resume_receipt": receipt,
}
Path(path).write_text(json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
PY
  printf '%s\t%s\t%s\n' "$case_repo" "$run_root" "$phase_file"
}

run_one_fencing_case() {
  local row="$1" case_id controller_generation authority_generation
  local protected_generation source_path preimage_hex candidate_hex protected_sha
  local expected_status expected_reason expected_target_hex prepared case_repo run_root
  IFS=$'\t' read -r case_id controller_generation authority_generation \
    protected_generation source_path preimage_hex candidate_hex protected_sha \
    expected_status expected_reason expected_target_hex <<<"$row"
  prepared="$(prepare_fencing_case "$case_id" "$controller_generation" \
    "$authority_generation" "$protected_generation" "$source_path" \
    "$preimage_hex" "$candidate_hex" "$protected_sha")" || {
      fail "D48-C02 setup/control: could not prepare $case_id"
      return 2
    }
  IFS=$'\t' read -r case_repo run_root _ <<<"$prepared"
  local output exit_code actual_status actual_reason actual_target
  output="$(bash "$mutation_owner" --repo-root "$case_repo" --run-root "$run_root" \
    --phase 1 --step 1 --preimage "$case_repo/$source_path" \
    --candidate "$case_repo/artifacts/candidate.bin" 2>"$case_repo/helper.err")"
  exit_code=$?
  actual_status="$("${py_cmd[@]}" -c 'import json,sys; print(json.loads(sys.stdin.read())["status"])' <<<"$output" 2>/dev/null)" || actual_status=INVALID
  actual_reason="$("${py_cmd[@]}" -c 'import json,sys; print(json.loads(sys.stdin.read())["reason_code"])' <<<"$output" 2>/dev/null)" || actual_reason=INVALID
  actual_target="$("${py_cmd[@]}" - "$case_repo/$source_path" <<'PY'
import sys
from pathlib import Path
path = Path(sys.argv[1])
print(path.read_bytes().hex() if path.is_file() else "ABSENT")
PY
)" || actual_target=INVALID

  if [ "$actual_status" != "$expected_status" ] || \
     [ "$actual_reason" != "$expected_reason" ] || \
     [ "$actual_target" != "$expected_target_hex" ]; then
    if [ "$case_id" = "D48-C02-01-current-generation-commits" ]; then
      printf '%s\n' "helper-exit=$exit_code status=$actual_status reason=$actual_reason target=$actual_target" >&2
      fail "D48-C02 setup/control: current generation did not reach the cooperating sink"
      return 2
    fi
    printf '%s\n' 'D48-C02 RED: stale generation reached protected mutation' >&2
    return 1
  fi
  return 0
}

run_d48_c02() {
  local rows row status=0
  rows="$("${py_cmd[@]}" - "$fencing_fixture" <<'PY'
import json
import sys
for case in json.load(open(sys.argv[1], encoding="utf-8"))["cases"]:
    print("\t".join(str(case[name]) for name in (
        "id", "controller_generation", "authority_generation",
        "protected_generation", "source_path", "preimage_hex", "candidate_hex",
        "protected_target_sha256", "expected_status", "expected_reason",
        "expected_target_hex")))
PY
)" || return 2
  while IFS= read -r row; do
    [ -n "$row" ] || continue
    run_one_fencing_case "$row"
    case $? in
      0) ;;
      1) status=1; break ;;
      *) return 2 ;;
    esac
  done <<<"$rows"
  if [ "$status" -eq 0 ]; then
    printf '%s\n' 'D48-C02=PASS cases=3/3'
  fi
  return "$status"
}

usage() {
  printf '%s\n' 'usage: distributed-runtime-contract.test.sh [--self-check | --cell D48-C02|D48-C04]' >&2
  exit 2
}

fixture_self_check || exit 1
case "${1:-}" in
  --self-check)
    [ "$#" -eq 1 ] || usage
    exit 0
    ;;
  --cell)
    [ "$#" -eq 2 ] || usage
    case "$2" in
      D48-C02) run_d48_c02; exit $? ;;
      D48-C04) run_d48_c04; exit $? ;;
      *) usage ;;
    esac
    ;;
  "")
    [ "$#" -eq 0 ] || usage
    failures=0
    run_d48_c02 || failures=$((failures + 1))
    run_d48_c04 || failures=$((failures + 1))
    [ "$failures" -eq 0 ] || exit 1
    ;;
  *) usage ;;
esac

printf '%s\n' 'distributed-runtime-contract.test: ok'
