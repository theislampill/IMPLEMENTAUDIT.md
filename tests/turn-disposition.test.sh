#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

run_root="$tmp/valid-yield"
mkdir -p "$run_root/phases"
for name in STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md; do
  cp "skills/implementaudit/templates/$name" "$run_root/$name"
done
grep -oE '^\| *[0-9]+ *\|' "$run_root/ROADMAP.md" | grep -oE '[0-9]+' | sort -un | while read -r phase; do
  printf 'stub\n' > "$run_root/phases/phase-$phase.md"
done

sed -i \
  -e 's/| Phase |  |/| Phase | 1 |/' \
  -e 's/| Status | open |/| Status | IN_PHASE |/' \
  -e 's/| Route |  |/| Route | governor |/' \
  -e 's/| Route decision projection | PENDING |/| Route decision projection | NOT_REQUIRED |/' \
  -e 's/| Route decision record | none |/| Route decision record | 1111111111111111111111111111111111111111 |/' \
  -e 's/| Owner\/source |  |/| Owner\/source | skills\/implementaudit\/scripts\/evaluate-turn-disposition.py |/' \
  -e 's/| Last check |  |/| Last check | focused baseline passed |/' \
  -e 's/| Next action |  |/| Next action | continue current phase |/' \
  "$run_root/STATE.md"

bash skills/implementaudit/scripts/validate-run-root.sh --nonterminal-yield "$run_root"

expect_yield_pass() {
  local label="$1" root="$2"
  bash skills/implementaudit/scripts/validate-run-root.sh --nonterminal-yield "$root" >/dev/null || {
    printf 'turn-disposition.test: expected valid yield: %s\n' "$label" >&2
    exit 1
  }
}

expect_yield_fail() {
  local label="$1" root="$2"
  if bash skills/implementaudit/scripts/validate-run-root.sh --nonterminal-yield "$root" >/dev/null 2>&1; then
    printf 'turn-disposition.test: expected invalid yield: %s\n' "$label" >&2
    exit 1
  fi
}

for status in open READY_TO_DISPATCH PAUSED; do
  candidate="$tmp/status-$status"
  cp -r "$run_root" "$candidate"
  sed -i "s/| Status | IN_PHASE |/| Status | $status |/" "$candidate/STATE.md"
  expect_yield_pass "$status with durable continuation evidence" "$candidate"
done

for status in BLOCKED INTERRUPTED; do
  candidate="$tmp/status-$status"
  cp -r "$run_root" "$candidate"
  sed -i "s/| Status | IN_PHASE |/| Status | $status |/" "$candidate/STATE.md"
  sed -i '/^|---|---|---|---|---|---|---|---|$/a | 1 | turn-1 | 1 | failed-criterion | waiting on bounded input | retain checkpoint | owner response | open (rerun pending) |' \
    "$candidate/STATE.md"
  expect_yield_pass "$status with an open Andon row" "$candidate"
done

candidate="$tmp/done-is-not-yield"
cp -r "$run_root" "$candidate"
sed -i 's/| Status | IN_PHASE |/| Status | DONE |/' "$candidate/STATE.md"
expect_yield_fail 'DONE is terminal, not a yield' "$candidate"

candidate="$tmp/terminal-marker-is-not-yield"
cp -r "$run_root" "$candidate"
printf '\nAUDIT_COMPLETE\nIMPLEMENTAUDIT_RUN_COMPLETE\n' >> "$candidate/STATE.md"
expect_yield_fail 'yield emits no terminal marker' "$candidate"

candidate="$tmp/handoff-marker-is-not-yield"
cp -r "$run_root" "$candidate"
printf '\nAUDIT_HANDOFF\n' >> "$candidate/STATE.md"
expect_yield_fail 'yield emits no handoff marker' "$candidate"

candidate="$tmp/pending-route"
cp -r "$run_root" "$candidate"
sed -i \
  -e 's/| Route decision projection | NOT_REQUIRED |/| Route decision projection | PENDING |/' \
  -e 's/| Route decision record | 1111111111111111111111111111111111111111 |/| Route decision record | none |/' \
  "$candidate/STATE.md"
expect_yield_fail 'PENDING route projection blocks yield' "$candidate"

candidate="$tmp/missing-next-action"
cp -r "$run_root" "$candidate"
sed -i 's/| Next action | continue current phase |/| Next action |  |/' "$candidate/STATE.md"
expect_yield_fail 'bare abandonment has no next action' "$candidate"

candidate="$tmp/blocked-without-andon"
cp -r "$run_root" "$candidate"
sed -i 's/| Status | IN_PHASE |/| Status | BLOCKED |/' "$candidate/STATE.md"
expect_yield_fail 'BLOCKED requires an open Andon row' "$candidate"

candidate="$tmp/empty-andon-shell"
cp -r "$run_root" "$candidate"
sed -i 's/| Status | IN_PHASE |/| Status | BLOCKED |/' "$candidate/STATE.md"
sed -i '/^|---|---|---|---|---|---|---|---|$/a | 1 | forged-occ | | | | | | |' \
  "$candidate/STATE.md"
expect_yield_fail 'exact review empty Andon shell row' "$candidate"

missing_rows=(
  'row-id::| forged | turn-1 | 1 | failed-criterion | waiting on bounded input | retain checkpoint | owner response | open (rerun pending) |'
  'occ::| 1 | | 1 | failed-criterion | waiting on bounded input | retain checkpoint | owner response | open (rerun pending) |'
  'phase::| 1 | turn-1 | | failed-criterion | waiting on bounded input | retain checkpoint | owner response | open (rerun pending) |'
  'class::| 1 | turn-1 | 1 | | waiting on bounded input | retain checkpoint | owner response | open (rerun pending) |'
  'abnormality::| 1 | turn-1 | 1 | failed-criterion | | retain checkpoint | owner response | open (rerun pending) |'
  'countermeasure::| 1 | turn-1 | 1 | failed-criterion | waiting on bounded input | | owner response | open (rerun pending) |'
  'rerun-evidence::| 1 | turn-1 | 1 | failed-criterion | waiting on bounded input | retain checkpoint | | open (rerun pending) |'
  'outcome::| 1 | turn-1 | 1 | failed-criterion | waiting on bounded input | retain checkpoint | owner response | |'
  'resolved-outcome::| 1 | turn-1 | 1 | failed-criterion | waiting on bounded input | retain checkpoint | owner response | resolved |'
  'recognized-class::| 1 | turn-1 | 1 | invented-class | waiting on bounded input | retain checkpoint | owner response | open (rerun pending) |'
)
for status in BLOCKED INTERRUPTED; do
  for row_case in "${missing_rows[@]}"; do
    label="${row_case%%::*}"
    row="${row_case#*::}"
    candidate="$tmp/partial-andon-$status-$label"
    cp -r "$run_root" "$candidate"
    sed -i "s/| Status | IN_PHASE |/| Status | $status |/" "$candidate/STATE.md"
    sed -i "/^|---|---|---|---|---|---|---|---|$/a $row" "$candidate/STATE.md"
    expect_yield_fail "$status requires substantive Andon $label" "$candidate"
  done
done

wrapped_placeholder_rows=(
  'backtick::| 1 | `none` | `none` | failed-criterion | `none` | `pending` | `none` | `pending` |'
  'emphasis::| 1 | **none** | _none_ | failed-criterion | **none** | _pending_ | **none** | _pending_ |'
  "quoted::| 1 | \"none\" | 'none' | failed-criterion | \"none\" | 'pending' | \"none\" | 'pending' |"
  'whitespace::| 1 |   none   |   none   | failed-criterion |   none   |   pending   |   none   |   pending   |'
)
for status in BLOCKED INTERRUPTED; do
  for row_case in "${wrapped_placeholder_rows[@]}"; do
    label="${row_case%%::*}"
    row="${row_case#*::}"
    candidate="$tmp/wrapped-placeholder-$status-$label"
    cp -r "$run_root" "$candidate"
    sed -i "s/| Status | IN_PHASE |/| Status | $status |/" "$candidate/STATE.md"
    sed -i "/^|---|---|---|---|---|---|---|---|$/a $row" "$candidate/STATE.md"
    expect_yield_fail "$status rejects $label-wrapped Andon placeholders" "$candidate"
  done
done

evaluator="skills/implementaudit/scripts/evaluate-turn-disposition.py"

make_request() {
  local output="$1" claim="$2" root="$3" route_mode="$4" binding_mode="$5"
  python - "$output" "$claim" "$root" "$route_mode" "$binding_mode" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

output, claim, root, route_mode, binding_mode = sys.argv[1:]
proof_layers = {
    "source_core": "PRESENT",
    "package": "UNVERIFIED",
    "install": "UNVERIFIED",
    "host_activation": "UNVERIFIED",
}
if claim == "NO_ACTIVE_AUDIT_OBJECT":
    request = {
        "schema": "implementaudit.turn-disposition-request.v1",
        "claim": claim,
        "run_root": None,
        "binding": None,
        "route": None,
    }
else:
    obligation = "obligation-1" if route_mode == "open-required" else None
    transaction = "transaction-1" if obligation else None
    correlation_root = root
    if binding_mode == "foreign":
        correlation_root = str(Path(root).parent / "foreign-object")
    correlation = {
        "host_id": "host-1",
        "host_session_id": "session-1",
        "binding_generation": "G0001",
        "controller_id": "v0333-release",
        "claim_id": "claim-1",
        "explicit_run_root": correlation_root,
        "repository_identity": str(Path(root).parent),
        "git_common_directory_identity": str(Path(root).parent / "git-common"),
        "worktree_identity": str(Path(root).parent),
        "applicable_continuity_generation": "G00FD",
        "applicable_continuity_receipt": "refs/implementaudit/continuity-receipts/v0333-release/G00FD@" + "a" * 40,
        "event_id": "event-1",
        "turn_id": "turn-1",
        "tool_use_id": None,
        "agent_id": None,
        "obligation_id": obligation,
        "route_transaction_id": transaction,
    }
    correlation_id = "sha256:" + hashlib.sha256(
        json.dumps(correlation, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    binding_result = {
        "schema": "implementaudit.host-session-binding-result.v1",
        "status": "ATTRIBUTED" if binding_mode != "ambiguous" else "UNAVAILABLE",
        "binding_generation": "G0002" if binding_mode == "stale" else "G0001",
        "correlation_id": correlation_id,
        "host_activation_proven": False,
        "proof_layers": proof_layers,
    }
    if obligation:
        binding_result["obligation_id"] = obligation
        binding_result["route_transaction_id"] = transaction
    decision = "REQUIRED" if route_mode == "open-required" else "NOT_REQUIRED"
    route = {
        "schema": "implementaudit.route-transaction-result.v1",
        "status": "CURRENT",
        "decision": decision,
        "classification": "JUDGEMENT_REQUIRED" if decision == "REQUIRED" else "MECHANICALLY_NOT_REQUIRED",
        "advance_allowed": False,
        "admission_required": decision == "NOT_REQUIRED",
        "enforcement_available": True,
        "record_oid": "1" * 40,
        "record_identity": "sha256:" + "2" * 64,
        "obligation_id": obligation,
        "route_state": "UNSATISFIED" if obligation else None,
        "governor_decision_count": 0,
        "history_query": None,
        "history_read_performed": False,
        "mirror_claim": "ABSENT",
        "mirror_status": "IGNORED_ABSENT",
        "projection_status": "CURRENT",
        "proof_layers": proof_layers,
        "host_activation_proven": False,
    }
    request = {
        "schema": "implementaudit.turn-disposition-request.v1",
        "claim": claim,
        "run_root": root,
        "binding": {"correlation": correlation, "result": binding_result},
        "route": route,
    }
Path(output).write_text(json.dumps(request, sort_keys=True) + "\n", encoding="utf-8")
PY
}

expect_disposition() {
  local label="$1" expected_rc="$2" expected_disposition="$3" request="$4"
  local output rc=0
  output="$(python "$evaluator" --request "$request")" || rc=$?
  if [ "$rc" -ne "$expected_rc" ]; then
    printf 'turn-disposition.test: %s returned %s, expected %s: %s\n' "$label" "$rc" "$expected_rc" "$output" >&2
    exit 1
  fi
  python - "$output" "$expected_disposition" <<'PY'
import json
import sys
payload = json.loads(sys.argv[1])
expected = sys.argv[2]
assert payload["schema"] == "implementaudit.turn-disposition-result.v1"
assert payload["disposition"] == expected
assert payload["stop_allowed"] is (expected != "BLOCK")
assert payload["host_activation_proven"] is False
PY
}

request="$tmp/ty-1.json"
make_request "$request" NO_ACTIVE_AUDIT_OBJECT unused none none
expect_disposition TY-1 0 NO_ACTIVE_AUDIT_OBJECT "$request"

terminal_root="$tmp/terminal-closure"
cp -r "$run_root" "$terminal_root"
sed -i \
  -e 's/| Status | IN_PHASE |/| Status | DONE |/' \
  -e 's/| Audit object state | open |/| Audit object state | terminal verified closure |/' \
  "$terminal_root/STATE.md"
printf '\nAUDIT_COMPLETE\nIMPLEMENTAUDIT_RUN_COMPLETE\n' >> "$terminal_root/STATE.md"
request="$tmp/ty-2.json"
make_request "$request" TERMINAL_CLOSURE "$terminal_root" not-required valid
expect_disposition TY-2 0 TERMINAL_CLOSURE "$request"

handoff_root="$tmp/audited-handoff"
cp -r "$run_root" "$handoff_root"
sed -i \
  -e 's/| Status | IN_PHASE |/| Status | BLOCKED |/' \
  -e 's/Handoff state, if any:/Handoff state, if any: audited blocker recorded/' \
  "$handoff_root/STATE.md"
sed -i '/^|---|---|---|---|---|---|---|---|$/a | 1 | handoff-occ-1 | 1 | owner-unclear | waiting on bounded owner input | retain checkpoint | owner response | open (rerun pending) |' \
  "$handoff_root/STATE.md"
printf '\nAUDIT_HANDOFF\n' >> "$handoff_root/STATE.md"
request="$tmp/ty-3.json"
make_request "$request" AUDITED_HANDOFF "$handoff_root" not-required valid
expect_disposition TY-3 0 AUDITED_HANDOFF "$request"

for handoff_placeholder in none pending 'n/a' 'not applicable' - TBD TODO unknown '   '; do
  placeholder_root="$tmp/handoff-placeholder-${handoff_placeholder//[^A-Za-z0-9]/_}"
  cp -r "$handoff_root" "$placeholder_root"
  sed -i "s|^Handoff state, if any:.*|Handoff state, if any: $handoff_placeholder|" \
    "$placeholder_root/STATE.md"
  request="$tmp/handoff-placeholder-${handoff_placeholder//[^A-Za-z0-9]/_}.json"
  make_request "$request" AUDITED_HANDOFF "$placeholder_root" not-required valid
  expect_disposition "handoff-placeholder-$handoff_placeholder" 3 BLOCK "$request"
done

arbitrary_handoff_root="$tmp/arbitrary-handoff"
cp -r "$handoff_root" "$arbitrary_handoff_root"
sed -i 's/^Handoff state, if any:.*/Handoff state, if any: prose recorded/' \
  "$arbitrary_handoff_root/STATE.md"
sed -i '/^| 1 | handoff-occ-1 |/d' "$arbitrary_handoff_root/STATE.md"
request="$tmp/arbitrary-handoff.json"
make_request "$request" AUDITED_HANDOFF "$arbitrary_handoff_root" not-required valid
expect_disposition arbitrary-handoff-prose-without-typed-state 3 BLOCK "$request"

actionless_handoff_root="$tmp/actionless-handoff"
cp -r "$handoff_root" "$actionless_handoff_root"
sed -i 's/| Next action | continue current phase |/| Next action | none |/' \
  "$actionless_handoff_root/STATE.md"
request="$tmp/actionless-handoff.json"
make_request "$request" AUDITED_HANDOFF "$actionless_handoff_root" not-required valid
expect_disposition actionless-handoff 3 BLOCK "$request"

set_handoff_andon_state() {
  local root="$1" state="$2" state_file="$1/STATE.md"
  case "$state" in
    unresolved) ;;
    resolved)
      sed -i 's/| open (rerun pending) |/| resolved |/' "$state_file"
      ;;
    absent)
      sed -i '/^| 1 | handoff-occ-1 |/d' "$state_file"
      ;;
    malformed)
      sed -i 's/| 1 | handoff-occ-1 | 1 | owner-unclear |/| 1 | handoff-occ-1 | | owner-unclear |/' "$state_file"
      ;;
    empty)
      sed -i 's/^| 1 | handoff-occ-1 |.*$/| 1 | handoff-occ-1 | | | | | | |/' "$state_file"
      ;;
    placeholder)
      sed -i 's/^| 1 | handoff-occ-1 |.*$/| 1 | `none` | `none` | owner-unclear | `none` | `pending` | `none` | `pending` |/' "$state_file"
      ;;
    stale)
      sed -i 's/| handoff-occ-1 | 1 | owner-unclear |/| handoff-occ-1 | 0 | owner-unclear |/' "$state_file"
      ;;
    historical-resolved)
      sed -i '/^| 1 | handoff-occ-1 |/a | 2 | historical-occ-1 | 0 | failed-criterion | prior phase issue | retained prior evidence | prior rerun | resolved |' "$state_file"
      ;;
    duplicate)
      sed -i '/^| 1 | handoff-occ-1 |/p' "$state_file"
      ;;
    contradictory)
      sed -i '/^| 1 | handoff-occ-1 |/a | 2 | handoff-occ-1 | 1 | owner-unclear | waiting on bounded owner input | retain checkpoint | owner response | resolved |' "$state_file"
      ;;
    *)
      printf 'turn-disposition.test: unknown typed handoff state: %s\n' "$state" >&2
      exit 1
      ;;
  esac
}

expect_handoff_evidence() {
  local label="$1" handoff_state="$2" next_action="$3" expected_rc="$4" expected_disposition="$5"
  local andon_state="${6:-unresolved}"
  local root="$tmp/handoff-evidence-$label" request="$tmp/handoff-evidence-$label.json"
  cp -r "$handoff_root" "$root"
  set_handoff_andon_state "$root" "$andon_state"
  sed -i \
    -e "s|^Handoff state, if any:.*|Handoff state, if any: $handoff_state|" \
    -e "s#| Next action | continue current phase |#| Next action | $next_action |#" \
    "$root/STATE.md"
  make_request "$request" AUDITED_HANDOFF "$root" not-required valid
  expect_disposition "$label" "$expected_rc" "$expected_disposition" "$request"
}

expect_typed_state_pair() {
  local label="$1" andon_state="$2" handoff_state="$3" expected_rc="$4" expected_disposition="$5"
  local root="$tmp/typed-state-$label" request="$tmp/typed-state-$label.json" yield_root="$tmp/typed-state-$label-yield"
  cp -r "$handoff_root" "$root"
  set_handoff_andon_state "$root" "$andon_state"
  sed -i "s|^Handoff state, if any:.*|Handoff state, if any: $handoff_state|" "$root/STATE.md"
  make_request "$request" AUDITED_HANDOFF "$root" not-required valid
  expect_disposition "$label-handoff" "$expected_rc" "$expected_disposition" "$request"
  cp -r "$root" "$yield_root"
  sed -i '/^AUDIT_HANDOFF$/d' "$yield_root/STATE.md"
  if [ "$expected_rc" -eq 0 ]; then
    expect_yield_pass "$label shares typed acceptance" "$yield_root"
  else
    expect_yield_fail "$label shares typed refusal" "$yield_root"
  fi
}

expect_handoff_evidence \
  negated-blocker-nominal-action \
  'no blocker remains; work is complete' \
  wait \
  3 BLOCK resolved

negated_handoffs=(
  'not-blocked::not blocked; work may proceed'
  'none-remain::none of the blockers remain'
  'without-blocker::without any blocker; work is complete'
  'resolved-blocker::the blocker is resolved'
  'complete-blocker::blocked work is complete'
)
for handoff_case in "${negated_handoffs[@]}"; do
  label="${handoff_case%%::*}"
  handoff_state="${handoff_case#*::}"
  expect_handoff_evidence "$label" "$handoff_state" 'request owner authorization for phase 1' 3 BLOCK resolved
done

for nominal_action in wait resume continue fix review reconcile rerun handoff; do
  expect_handoff_evidence \
    "nominal-action-$nominal_action" \
    'blocked by missing owner authorization' \
    "$nominal_action" \
    3 BLOCK
done

expect_handoff_evidence \
  substantive-owner-handoff \
  'blocked by missing owner authorization' \
  'request owner authorization for phase 1' \
  0 AUDITED_HANDOFF

expect_handoff_evidence \
  resolved-owner-decision \
  'owner decision is resolved' \
  'request owner authorization for phase 1' \
  3 BLOCK resolved

expect_handoff_evidence \
  negated-awaiting-owner-decision \
  'not awaiting owner decision' \
  'request owner authorization for phase 1' \
  3 BLOCK resolved

expect_handoff_evidence \
  active-owner-decision \
  'awaiting owner decision' \
  'request owner authorization for phase 1' \
  0 AUDITED_HANDOFF

expect_typed_state_pair \
  resolved-typed-awaiting \
  resolved \
  'awaiting owner decision' \
  3 BLOCK

for typed_state in absent malformed empty placeholder stale duplicate contradictory; do
  expect_typed_state_pair \
    "$typed_state-typed-awaiting" \
    "$typed_state" \
    'awaiting owner decision' \
    3 BLOCK
done

expect_typed_state_pair \
  historical-resolved-plus-current-unresolved \
  historical-resolved \
  'plain affirmative handoff evidence' \
  0 AUDITED_HANDOFF

for narrative_case in \
  'owner decision is not resolved' \
  'owner decision remains unresolved' \
  'owner decision is resolved' \
  'owner decision is no longer pending' \
  'owner request is no longer required' \
  'plain affirmative handoff evidence'; do
  label="${narrative_case//[^A-Za-z0-9]/-}"
  expect_typed_state_pair \
    "unresolved-$label" \
    unresolved \
    "$narrative_case" \
    0 AUDITED_HANDOFF
done

surface_handoff_root="$tmp/surface-handoff"
cp -r "$handoff_root" "$surface_handoff_root"
sed -i 's/AUDIT_HANDOFF/ANDON_HANDOFF/' "$surface_handoff_root/STATE.md"
sed -i '/^ANDON_HANDOFF$/i ANDON_PROBE\nANDON_ESCALATE' "$surface_handoff_root/STATE.md"
request="$tmp/surface-handoff.json"
make_request "$request" AUDITED_HANDOFF "$surface_handoff_root" not-required valid
expect_disposition surface-handoff-is-not-audit-handoff 3 BLOCK "$request"

combined_handoff_root="$tmp/combined-handoff"
cp -r "$surface_handoff_root" "$combined_handoff_root"
printf 'AUDIT_HANDOFF\n' >> "$combined_handoff_root/STATE.md"
request="$tmp/combined-handoff.json"
make_request "$request" AUDITED_HANDOFF "$combined_handoff_root" not-required valid
expect_disposition combined-surface-and-audit-handoff 0 AUDITED_HANDOFF "$request"

duplicate_handoff_root="$tmp/duplicate-handoff"
cp -r "$combined_handoff_root" "$duplicate_handoff_root"
printf 'AUDIT_HANDOFF\n' >> "$duplicate_handoff_root/STATE.md"
request="$tmp/duplicate-handoff.json"
make_request "$request" AUDITED_HANDOFF "$duplicate_handoff_root" not-required valid
expect_disposition duplicate-final-audit-handoff 3 BLOCK "$request"

out_of_order_handoff_root="$tmp/out-of-order-handoff"
cp -r "$handoff_root" "$out_of_order_handoff_root"
sed -i '/^AUDIT_HANDOFF$/i ANDON_ESCALATE\nANDON_PROBE\nANDON_HANDOFF' \
  "$out_of_order_handoff_root/STATE.md"
request="$tmp/out-of-order-handoff.json"
make_request "$request" AUDITED_HANDOFF "$out_of_order_handoff_root" not-required valid
expect_disposition out-of-order-surface-handoff 3 BLOCK "$request"

request="$tmp/ty-4.json"
make_request "$request" NONTERMINAL_YIELD "$run_root" not-required valid
expect_disposition TY-4 0 NONTERMINAL_YIELD "$request"

request="$tmp/ty-5.json"
make_request "$request" TERMINAL_CLOSURE "$run_root" not-required valid
expect_disposition TY-5 3 BLOCK "$request"

request="$tmp/ty-6.json"
make_request "$request" NONTERMINAL_YIELD "$tmp/missing-next-action" not-required valid
expect_disposition TY-6 3 BLOCK "$request"

for binding_case in stale foreign ambiguous; do
  request="$tmp/binding-$binding_case.json"
  make_request "$request" NONTERMINAL_YIELD "$run_root" not-required "$binding_case"
  expect_disposition "binding-$binding_case" 3 BLOCK "$request"
done

open_route_root="$tmp/open-route"
cp -r "$run_root" "$open_route_root"
sed -i 's/| Route decision projection | NOT_REQUIRED |/| Route decision projection | REQUIRED |/' \
  "$open_route_root/STATE.md"
request="$tmp/open-route.json"
make_request "$request" NONTERMINAL_YIELD "$open_route_root" open-required valid
expect_disposition open-R0033 3 BLOCK "$request"

python - "$request" <<'PY'
import json
import sys
from pathlib import Path
path = Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
payload["route"]["advance_allowed"] = True
payload["route"]["route_state"] = "SATISFIED"
payload["route"]["governor_decision_count"] = 1
path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
PY
expect_disposition satisfied-R0033 0 NONTERMINAL_YIELD "$request"

mixed_closure="$tmp/mixed-closure"
cp -r "$terminal_root" "$mixed_closure"
printf 'AUDIT_HANDOFF\n' >> "$mixed_closure/STATE.md"
request="$tmp/mixed-closure.json"
make_request "$request" TERMINAL_CLOSURE "$mixed_closure" not-required valid
expect_disposition closure-handoff-exclusivity 3 BLOCK "$request"

mixed_handoff="$tmp/mixed-handoff"
cp -r "$handoff_root" "$mixed_handoff"
printf 'IMPLEMENTAUDIT_RUN_COMPLETE\n' >> "$mixed_handoff/STATE.md"
request="$tmp/mixed-handoff.json"
make_request "$request" AUDITED_HANDOFF "$mixed_handoff" not-required valid
expect_disposition handoff-completion-exclusivity 3 BLOCK "$request"

request="$tmp/no-object-with-input.json"
make_request "$request" NO_ACTIVE_AUDIT_OBJECT unused none none
python - "$request" "$run_root" <<'PY'
import json
import sys
from pathlib import Path
path = Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
payload["run_root"] = sys.argv[2]
path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
PY
expect_disposition no-object-input 3 BLOCK "$request"

request="$tmp/duplicate-member.json"
printf '{"schema":"implementaudit.turn-disposition-request.v1","schema":"implementaudit.turn-disposition-request.v1","claim":"NO_ACTIVE_AUDIT_OBJECT","run_root":null,"binding":null,"route":null}\n' > "$request"
expect_disposition duplicate-member 2 BLOCK "$request"

request="$tmp/extra-member.json"
make_request "$request" NO_ACTIVE_AUDIT_OBJECT unused none none
python - "$request" <<'PY'
import json
import sys
from pathlib import Path
path = Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
payload["invented"] = True
path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
PY
expect_disposition extra-member 2 BLOCK "$request"

request="$tmp/zero-object-cheap.json"
make_request "$request" NO_ACTIVE_AUDIT_OBJECT unused none none
python_executable="$(command -v python)"
zero_output="$(PATH=/definitely-unavailable "$python_executable" "$evaluator" --request "$request")"
python - "$zero_output" <<'PY'
import json
import sys
payload = json.loads(sys.argv[1])
assert payload["disposition"] == "NO_ACTIVE_AUDIT_OBJECT"
assert payload["stop_allowed"] is True
PY

printf 'turn-disposition.test: ok (TY-1..TY-6 + binding + R0033 + strict decoding)\n'
