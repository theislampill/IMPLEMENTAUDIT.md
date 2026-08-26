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
expect_yield_pass 'PENDING route diagnostic cannot veto yield' "$candidate"

candidate="$tmp/absent-route-projection"
cp -r "$run_root" "$candidate"
sed -i \
  -e '/^| Route decision projection |/d' \
  -e '/^| Route decision record |/d' \
  "$candidate/STATE.md"
expect_yield_pass 'absent route diagnostics cannot veto yield' "$candidate"

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
host_stop_adapter="$repo_root/skills/implementaudit/scripts/host-stop-interlock.py"
host_binding_core="$repo_root/skills/implementaudit/scripts/host-session-binding.py"
route_core="$repo_root/skills/implementaudit/scripts/route-transaction.py"
claim_helper="$repo_root/skills/implementaudit/scripts/claim-run.sh"

make_request() {
  local output="$1" claim="$2" root="$3" route_mode="$4" binding_mode="$5"
  local projection_status="${6:-CURRENT}"
  python - "$output" "$claim" "$root" "$route_mode" "$binding_mode" "$projection_status" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

output, claim, root, route_mode, binding_mode, projection_status = sys.argv[1:]
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
    obligation = "sha256:" + "3" * 64 if route_mode == "open-required" else None
    transaction = "sha256:" + "4" * 64 if obligation else None
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
        "route_transaction_id": transaction,
        "route_state": "UNSATISFIED" if obligation else None,
        "governor_decision_count": 0,
        "history_query": None,
        "history_read_performed": False,
        "mirror_claim": "ABSENT",
        "mirror_status": "IGNORED_ABSENT",
        "projection_status": projection_status,
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
    closed)
      sed -i 's/| open (rerun pending) |/| closed |/' "$state_file"
      ;;
    done)
      sed -i 's/| open (rerun pending) |/| done |/' "$state_file"
      ;;
    outcome-gibberish)
      sed -i 's/| open (rerun pending) |/| gibberish |/' "$state_file"
      ;;
    outcome-terminal)
      sed -i 's/| open (rerun pending) |/| terminal |/' "$state_file"
      ;;
    outcome-resolved-colon)
      sed -i 's/| open (rerun pending) |/| resolved: owner replied |/' "$state_file"
      ;;
    escalated)
      sed -i 's/| open (rerun pending) |/| escalated (cites #7) |/' "$state_file"
      ;;
    blocked)
      sed -i 's/| open (rerun pending) |/| blocked (handoff condition) |/' "$state_file"
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
    malformed-nonnumeric)
      sed -i '/^| 1 | handoff-occ-1 |/a | forged | forged-occ-1 | 1 | owner-unclear | malformed row | retain checkpoint | owner response | open (rerun pending) |' "$state_file"
      ;;
    structural-extra-cell)
      sed -i '/^| 1 | handoff-occ-1 |/a | 2 | extra-occ-1 | 1 | failed-criterion | extra cell row | retain checkpoint | owner response | open (rerun pending) | injected |' "$state_file"
      ;;
    structural-leading-space)
      sed -i '/^| 1 | handoff-occ-1 |/a\ | forged | forged-occ-1 | 1 | failed-criterion | indented row | retain checkpoint | owner response | open (rerun pending) |' "$state_file"
      ;;
    structural-missing-trailing)
      sed -i '/^| 1 | handoff-occ-1 |/a | 2 | missing-trailing-occ-1 | 1 | failed-criterion | missing trailing delimiter | retain checkpoint | owner response | open (rerun pending)' "$state_file"
      ;;
    structural-empty-extra)
      sed -i '/^| 1 | handoff-occ-1 |/a | 2 | empty-extra-occ-1 | 1 | failed-criterion | empty extra cell | retain checkpoint | owner response | open (rerun pending) | |' "$state_file"
      ;;
    v05-wrapped)
      sed -i 's#^| 1 | handoff-occ-1 |.*$#| 1 | `handoff-occ-1` | `1` | owner-unclear | *waiting on bounded owner input* | _retain checkpoint_ | "owner response" | `open (rerun pending)` |#' "$state_file"
      ;;
    a03-current-terminal-active)
      sed -i '/^| 1 | handoff-occ-1 |/a | 2 | terminal-occ-1 | 1 | failed-criterion | completed sibling | retained evidence | final rerun | resolved |' "$state_file"
      ;;
    b01-preamble-prose)
      sed -i '/^Open reruns, escalations,/a Narrative-only Andon preamble.' "$state_file"
      ;;
    b02-post-table-prose)
      sed -i '/^## Occurrence resolution and residuals$/i Post-table narrative after the body terminator.\
' "$state_file"
      ;;
    b03-outside-section-table)
      sed -i '/^AUDIT_HANDOFF$/i ## Unrelated table\
\
| value | note |\
|---|---|\
| outside | ignored |\
' "$state_file"
      ;;
    n01-missing-section)
      sed -i '/^## Andon log$/,/^## Occurrence resolution and residuals$/{ /^## Occurrence resolution and residuals$/!d; }' "$state_file"
      ;;
    n01-duplicate-section)
      sed -i '/^## Occurrence resolution and residuals$/i ## Andon log\
\
| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |\
|---|---|---|---|---|---|---|---|\
| 2 | duplicate-section-occ | 1 | failed-criterion | duplicate section | retain checkpoint | owner response | open (rerun pending) |\
' "$state_file"
      ;;
    d01-n18-sole-case-alias)
      sed -i 's/^## Andon log$/## andon log/' "$state_file"
      ;;
    d01-n19-case-alias-duplicate)
      append_andon_alias "$state_file" '## andon log'
      ;;
    d01-n20-trailing-space-alias-duplicate)
      append_andon_alias "$state_file" '## Andon log '
      ;;
    d01-n21-indented-alias-duplicate)
      append_andon_alias "$state_file" ' ## Andon log'
      ;;
    d01-n22-internal-space-alias-duplicate)
      append_andon_alias "$state_file" '##  Andon   log'
      ;;
    d01-n23-closing-hash-alias-duplicate)
      append_andon_alias "$state_file" '## Andon log ##'
      ;;
    d01-n24-tab-alias-duplicate)
      append_andon_alias "$state_file" $'##\tAndon\tlog\t'
      ;;
    n02-missing-header)
      sed -i '/^| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |$/d' "$state_file"
      ;;
    n02-duplicate-header)
      sed -i '/^| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |$/p' "$state_file"
      ;;
    n02-missing-separator)
      sed -i '/^|---|---|---|---|---|---|---|---|$/d' "$state_file"
      ;;
    n02-duplicate-separator)
      sed -i '/^|---|---|---|---|---|---|---|---|$/p' "$state_file"
      ;;
    n02-reordered-header-separator)
      sed -i \
        -e 's/^| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |$/__ANDON_HEADER__/' \
        -e 's/^|---|---|---|---|---|---|---|---|$/| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |/' \
        -e 's/^__ANDON_HEADER__$/|---|---|---|---|---|---|---|---|/' \
        "$state_file"
      ;;
    n02-separated-header)
      sed -i '/^| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |$/G' "$state_file"
      ;;
    n02-altered-separator)
      sed -i 's/^|---|---|---|---|---|---|---|---|$/|---|---|---|---|---|---|---|--|/' "$state_file"
      ;;
    n04-missing-leading)
      sed -i '/^| 1 | handoff-occ-1 |/a 2 | missing-leading-occ | 1 | failed-criterion | missing leading delimiter | retain checkpoint | owner response | open (rerun pending) |' "$state_file"
      ;;
    n04-trailing-content)
      sed -i '/^| 1 | handoff-occ-1 |/a | 2 | trailing-content-occ | 1 | failed-criterion | trailing content | retain checkpoint | owner response | open (rerun pending) | trailing' "$state_file"
      ;;
    n05-missing-cell)
      sed -i '/^| 1 | handoff-occ-1 |/a | 2 | missing-cell-occ | 1 | failed-criterion | missing cell | retain checkpoint | open (rerun pending) |' "$state_file"
      ;;
    n08-embedded-pipe)
      sed -i '/^| 1 | handoff-occ-1 |/a | 2 | embedded-pipe-occ | 1 | failed-criterion | embedded | pipe | retain checkpoint | owner response | open (rerun pending) |' "$state_file"
      ;;
    n09-empty-id)
      sed -i '/^| 1 | handoff-occ-1 |/a | | empty-id-occ | 1 | failed-criterion | empty row id | retain checkpoint | owner response | open (rerun pending) |' "$state_file"
      ;;
    n09-wrapper-id)
      sed -i '/^| 1 | handoff-occ-1 |/a | `2` | wrapper-id-occ | 1 | failed-criterion | wrapped row id | retain checkpoint | owner response | open (rerun pending) |' "$state_file"
      ;;
    n10-unknown-class)
      sed -i '/^| 1 | handoff-occ-1 |/a | 2 | unknown-class-occ | 1 | invented-class | invalid class | retain checkpoint | owner response | open (rerun pending) |' "$state_file"
      ;;
    n10-plural-class)
      sed -i '/^| 1 | handoff-occ-1 |/a | 2 | plural-class-occ | 1 | failed-criterion regression | plural class | retain checkpoint | owner response | open (rerun pending) |' "$state_file"
      ;;
    n16-misplaced-preheader-row)
      sed -i '/^Open reruns, escalations,/a | 2 | misplaced-preheader-occ | 1 | failed-criterion | misplaced row | retain checkpoint | owner response | open (rerun pending) |' "$state_file"
      ;;
    n16-misplaced-second-header)
      sed -i '/^## Occurrence resolution and residuals$/i | # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |\
' "$state_file"
      ;;
    n17-legacy-stop-table)
      sed -i \
        -e 's/^| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |$/| # | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |/' \
        -e 's/^|---|---|---|---|---|---|---|---|$/|---|---|---|---|---|---|---|/' \
        -e 's/^| 1 | handoff-occ-1 | 1 | owner-unclear |/| 1 | 1 | owner-unclear |/' \
        "$state_file"
      ;;
    a04-active-after-terminator)
      sed -i '/^| 1 | handoff-occ-1 |/s/^/\n/' "$state_file"
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

append_andon_alias() {
  local state_file="$1" heading="$2"
  python - "$state_file" "$heading" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
heading = sys.argv[2]
marker = "## Occurrence resolution and residuals"
alias = "\n".join((
    heading,
    "",
    "| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |",
    "|---|---|---|---|---|---|---|---|",
    "| forged | alias-occ | 1 | failed-criterion | malformed alias state | retain checkpoint | owner response | open (rerun pending) |",
    "",
))
payload = path.read_text(encoding="utf-8")
if payload.count(marker) != 1:
    raise SystemExit("turn-disposition.test: expected one occurrence-resolution marker")
path.write_text(payload.replace(marker, alias + marker, 1), encoding="utf-8")
PY
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

typed_state_refusal_failures=()
record_typed_state_refusal_pair() {
  local label="$1" andon_state="$2"
  local root="$tmp/typed-refusal-$label" request="$tmp/typed-refusal-$label.json" yield_root="$tmp/typed-refusal-$label-yield"
  local handoff_rc yield_rc
  cp -r "$handoff_root" "$root"
  set_handoff_andon_state "$root" "$andon_state"
  make_request "$request" AUDITED_HANDOFF "$root" not-required valid
  set +e
  python "$evaluator" --request "$request" >/dev/null 2>&1
  handoff_rc=$?
  set -e
  cp -r "$root" "$yield_root"
  sed -i '/^AUDIT_HANDOFF$/d' "$yield_root/STATE.md"
  set +e
  bash skills/implementaudit/scripts/validate-run-root.sh --nonterminal-yield "$yield_root" >/dev/null 2>&1
  yield_rc=$?
  set -e
  if [ "$handoff_rc" -ne 3 ]; then
    typed_state_refusal_failures+=("$label-handoff=$handoff_rc")
  fi
  if [ "$yield_rc" -eq 0 ]; then
    typed_state_refusal_failures+=("$label-yield=$yield_rc")
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

convergence_refusals=(
  'N01-missing-section::n01-missing-section'
  'N01-duplicate-section::n01-duplicate-section'
  'D01-N18-sole-case-alias::d01-n18-sole-case-alias'
  'D01-N19-case-alias-duplicate::d01-n19-case-alias-duplicate'
  'D01-N20-trailing-space-alias-duplicate::d01-n20-trailing-space-alias-duplicate'
  'D01-N21-indented-alias-duplicate::d01-n21-indented-alias-duplicate'
  'D01-N22-internal-space-alias-duplicate::d01-n22-internal-space-alias-duplicate'
  'D01-N23-closing-hash-alias-duplicate::d01-n23-closing-hash-alias-duplicate'
  'D01-N24-tab-alias-duplicate::d01-n24-tab-alias-duplicate'
  'D01-N25-exact-duplicate::n01-duplicate-section'
  'N02-missing-header::n02-missing-header'
  'N02-duplicate-header::n02-duplicate-header'
  'N02-missing-separator::n02-missing-separator'
  'N02-duplicate-separator::n02-duplicate-separator'
  'N02-reordered-header-separator::n02-reordered-header-separator'
  'N02-separated-header::n02-separated-header'
  'N02-altered-separator::n02-altered-separator'
  'N03-indentation+N13-valid-malformed::structural-leading-space'
  'N04-missing-leading+N13-valid-malformed::n04-missing-leading'
  'N04-missing-trailing+N13-valid-malformed::structural-missing-trailing'
  'N04-trailing-content+N13-valid-malformed::n04-trailing-content'
  'N05-missing-cell+N13-valid-malformed::n05-missing-cell'
  'N06-empty-required::empty'
  'N06-placeholder-required::placeholder'
  'N07-extra-cell+N13-valid-malformed::structural-extra-cell'
  'N07-empty-extra-cell+N13-valid-malformed::structural-empty-extra'
  'N08-embedded-pipe+N13-valid-malformed::n08-embedded-pipe'
  'N09-nonnumeric-id+N13-valid-malformed::malformed-nonnumeric'
  'N09-empty-id+N13-valid-malformed::n09-empty-id'
  'N09-wrapper-id+N13-valid-malformed::n09-wrapper-id'
  'N09-duplicate-occurrence-class::duplicate'
  'N10-unknown-class+N13-valid-malformed::n10-unknown-class'
  'N10-plural-class+N13-valid-malformed::n10-plural-class'
  'N11-unknown-outcome::outcome-gibberish'
  'N11-terminal-looking-unknown::outcome-terminal'
  'N11-malformed-terminal::outcome-resolved-colon'
  'N12-malformed-phase::malformed'
  'N12-stale-only::stale'
  'N14-terminal-only-resolved::resolved'
  'N14-terminal-only-closed::closed'
  'N14-terminal-only-done::done'
  'N15-contradictory-current::contradictory'
  'N16-misplaced-preheader-row::n16-misplaced-preheader-row'
  'N16-misplaced-second-header::n16-misplaced-second-header'
  'N17-legacy-stop-table::n17-legacy-stop-table'
  'B04-zero-rows::absent'
  'A02-valid-malformed-sibling::malformed-nonnumeric'
  'A04-active-after-terminator::a04-active-after-terminator'
)
for refusal_case in "${convergence_refusals[@]}"; do
  label="${refusal_case%%::*}"
  andon_state="${refusal_case#*::}"
  record_typed_state_refusal_pair "$label" "$andon_state"
done
if [ "${#typed_state_refusal_failures[@]}" -ne 0 ]; then
  printf 'turn-disposition.test: typed Andon refusal mismatch: %s\n' \
    "${typed_state_refusal_failures[*]}" >&2
  exit 1
fi

convergence_admissions=(
  'V01+B05-current-open::unresolved'
  'V02-current-escalated::escalated'
  'V03-current-blocked::blocked'
  'V04+A01-history-current::historical-resolved'
  'V05-balanced-wrappers::v05-wrapped'
  'A03-current-terminal-plus-active::a03-current-terminal-active'
  'B01-preamble-prose::b01-preamble-prose'
  'B02-post-table-prose::b02-post-table-prose'
  'B03-outside-section-table::b03-outside-section-table'
)
for admission_case in "${convergence_admissions[@]}"; do
  label="${admission_case%%::*}"
  andon_state="${admission_case#*::}"
  expect_typed_state_pair "$label" "$andon_state" 'plain affirmative handoff evidence' 0 AUDITED_HANDOFF
done

for terminal_state in closed done; do
  expect_typed_state_pair \
    "$terminal_state-typed-awaiting" \
    "$terminal_state" \
    'awaiting owner decision' \
    3 BLOCK
done

for active_state in escalated blocked; do
  expect_typed_state_pair \
    "$active_state-typed" \
    "$active_state" \
    'plain affirmative handoff evidence' \
    0 AUDITED_HANDOFF
done

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

projection_diagnostics=(
  'current-matched|CURRENT|MATCHED|matching diagnostic prose'
  'invalid-stale|INVALID|INVALID|prior-record'
  'legacy-absent|LEGACY_ABSENT|ABSENT|none'
  'unavailable-contradictory|UNAVAILABLE|contradictory|not-a-route-oid'
)
for projection_case in "${projection_diagnostics[@]}"; do
  IFS='|' read -r label projection_status state_projection state_record <<<"$projection_case"
  projection_root="$tmp/projection-$label"
  cp -r "$run_root" "$projection_root"
  sed -i \
    -e "s/| Route decision projection | NOT_REQUIRED |/| Route decision projection | $state_projection |/" \
    -e "s/| Route decision record | 1111111111111111111111111111111111111111 |/| Route decision record | $state_record |/" \
    "$projection_root/STATE.md"
  request="$tmp/projection-$label.json"
  make_request "$request" NONTERMINAL_YIELD "$projection_root" not-required valid "$projection_status"
  expect_disposition "projection-diagnostic-$label" 0 NONTERMINAL_YIELD "$request"
done

request="$tmp/projection-rows-absent.json"
make_request "$request" NONTERMINAL_YIELD "$tmp/absent-route-projection" not-required valid LEGACY_ABSENT
expect_disposition projection-rows-absent 0 NONTERMINAL_YIELD "$request"

request="$tmp/malformed-projection-status.json"
make_request "$request" NONTERMINAL_YIELD "$run_root" not-required valid MATCHED
expect_disposition malformed-projection-status 2 BLOCK "$request"

request="$tmp/nontype-projection-status.json"
make_request "$request" NONTERMINAL_YIELD "$run_root" not-required valid CURRENT
python - "$request" <<'PY'
import json
import sys
from pathlib import Path
path = Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
payload["route"]["projection_status"] = ["CURRENT"]
path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
PY
expect_disposition nontype-projection-status 2 BLOCK "$request"

open_route_root="$tmp/open-route"
cp -r "$run_root" "$open_route_root"
request="$tmp/open-route.json"
make_request "$request" NONTERMINAL_YIELD "$open_route_root" open-required valid INVALID
expect_disposition permissive-projection-cannot-rescue-open-R0033 3 BLOCK "$request"

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
expect_disposition satisfied-R0033-invalid-projection 0 NONTERMINAL_YIELD "$request"

required_join_request="$tmp/required-transaction-join.json"
cp "$request" "$required_join_request"

mutate_required_transaction() {
  local output="$1" expression="$2"
  python - "$required_join_request" "$output" "$expression" <<'PY'
import hashlib
import json
import sys
from pathlib import Path

source, output, expression = sys.argv[1:]
payload = json.loads(Path(source).read_text(encoding="utf-8"))
exec(expression, {"__builtins__": {}, "hashlib": hashlib}, {"value": payload})
Path(output).write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
PY
}

transaction_mutations=(
  'swapped|value["route"]["route_transaction_id"]=value["route"]["obligation_id"]|3'
  'foreign|value["route"]["route_transaction_id"]="sha256:"+"5"*64|3'
  'missing|value["route"].pop("route_transaction_id")|2'
  'null-half|value["route"]["route_transaction_id"]=None|3'
  'malformed|value["route"]["route_transaction_id"]="not-a-transaction"|2'
  'caller-computed|value["route"]["route_transaction_id"]="sha256:"+hashlib.sha256(b"caller-computed").hexdigest()|3'
  'oid-substituted|value["route"]["route_transaction_id"]=value["route"]["record_oid"]|2'
  'locally-appended|value["route"].pop("route_transaction_id");value["route"]["route_transaction_id"]="sha256:"+hashlib.sha256(b"local-adapter").hexdigest()|3'
)
for transaction_case in "${transaction_mutations[@]}"; do
  IFS='|' read -r label expression expected_rc <<<"$transaction_case"
  candidate="$tmp/required-transaction-$label.json"
  mutate_required_transaction "$candidate" "$expression"
  expect_disposition "required-transaction-$label" "$expected_rc" BLOCK "$candidate"
done

stale_transaction_request="$tmp/required-transaction-stale.json"
mutate_required_transaction "$stale_transaction_request" 'value["route"]["status"]="STALE"'
expect_disposition required-transaction-stale 3 BLOCK "$stale_transaction_request"

request="$tmp/pending-route-result.json"
make_request "$request" NONTERMINAL_YIELD "$run_root" not-required valid INVALID
python - "$request" <<'PY'
import json
import sys
from pathlib import Path
path = Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
payload["route"]["decision"] = "PENDING"
path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
PY
expect_disposition permissive-projection-cannot-rescue-pending-route 3 BLOCK "$request"

request="$tmp/stale-route-result.json"
make_request "$request" NONTERMINAL_YIELD "$run_root" not-required valid INVALID
python - "$request" <<'PY'
import json
import sys
from pathlib import Path
path = Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
payload["route"]["status"] = "STALE"
path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
PY
expect_disposition stale-route-remains-blocked 3 BLOCK "$request"

request="$tmp/malformed-route-record.json"
make_request "$request" NONTERMINAL_YIELD "$run_root" not-required valid INVALID
python - "$request" <<'PY'
import json
import sys
from pathlib import Path
path = Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
payload["route"]["record_oid"] = "not-a-route-oid"
path.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
PY
expect_disposition malformed-route-record-remains-unavailable 2 BLOCK "$request"

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

[ -f "$host_stop_adapter" ] || {
  printf 'turn-disposition.test: HC-H7B RED: Stop interlock adapter is absent\n' >&2
  exit 1
}

stop_repo="$tmp/stop-repo"
stop_run_rel=".IMPLEMENTAUDIT/runs/stop-ABC123"
stop_run_shell="$stop_repo/$stop_run_rel"
stop_store="$tmp/stop-plugin-data/host-session-binding-v1"
stop_session="stop-session"
stop_controller="stop-controller"
stop_claim="99999999999999999999999999999999"
mkdir -p "$stop_repo" "$stop_run_shell"
git -C "$stop_repo" init -q
git -C "$stop_repo" config user.email hc-h7b@example.invalid
git -C "$stop_repo" config user.name 'HC-H7B fixture'
printf 'stop fixture\n' > "$stop_repo/baseline.txt"
git -C "$stop_repo" add baseline.txt
git -C "$stop_repo" commit -qm 'HC-H7B fixture'

stop_repo_custody="$(python - "$stop_repo" <<'PY'
import os,sys
print(os.path.abspath(sys.argv[1]).replace("\\", "/"))
PY
)"
stop_common_custody="$stop_repo_custody/.git"
stop_run_root="$stop_repo_custody/$stop_run_rel"
cp -R "$run_root/." "$stop_run_shell/"
stop_head="$(git -C "$stop_repo" rev-parse HEAD)"
stop_tree="$(git -C "$stop_repo" rev-parse 'HEAD^{tree}')"
python - "$stop_run_shell/STATE.md" "$stop_head" "$stop_tree" <<'PY'
import sys
from pathlib import Path

path=Path(sys.argv[1]); head,tree=sys.argv[2:]
text=path.read_text(encoding="utf-8")
text=text.replace("| Next action | continue current phase |", "| Next action | continue exact route-bound action |")
anchor=(
 "| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n"
 "|---|---|---|---|---|---|"
)
row=f"| G0001 | new-session | 2026-08-23T00:00:00Z | {head} {tree} | yes | exact Stop boundary |"
if text.count(anchor) != 1:
 raise SystemExit("turn-disposition.test: Stop fixture lost continuity table")
path.write_text(text.replace(anchor, anchor+"\n"+row), encoding="utf-8", newline="\n")
PY

cat > "$stop_run_shell/.claimed" <<EOF
schema=implementaudit.run-claim.v2
claim_id=$stop_claim
claimed_at_utc=2026-08-23T00:00:00Z
mode=full
templates=STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md
repo_root=$stop_repo_custody
git_common_dir=$stop_common_custody
run_base=.IMPLEMENTAUDIT/runs
run_root=$stop_run_rel
run_name=stop-ABC123
EOF
printf 'controller_id=%s\n' "$stop_controller" > "$stop_run_shell/.controller"

stop_controller_record="$(printf 'implementaudit.controller-current.v1\t%s\t%s\t%s\n' \
  "$stop_controller" "$stop_claim" "$stop_run_root" | git -C "$stop_repo" hash-object -w --stdin)"
git -C "$stop_repo" update-ref "refs/implementaudit/controllers/$stop_controller" "$stop_controller_record"
stop_invalidation_oid="$(printf 'implementaudit.continuity-invalidation.v1\t%s\t%s\t%s\tnew-session\tstop-boundary-event\n' \
  "$stop_controller" "$stop_controller_record" "$stop_claim" | git -C "$stop_repo" hash-object -w --stdin)"
git -C "$stop_repo" update-ref "refs/implementaudit/continuity-invalidations/$stop_controller" "$stop_invalidation_oid"
stop_state_sha="$(sha256sum "$stop_run_shell/STATE.md" | cut -d' ' -f1)"
stop_road_sha="$(sha256sum "$stop_run_shell/ROADMAP.md" | cut -d' ' -f1)"
stop_receipt_oid="$(printf 'implementaudit.continuity-receipt.v2\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\tnew-session\tG0001\tcontinue exact route-bound action\n' \
  "$stop_controller" "$stop_controller_record" "$stop_claim" "$stop_head" "$stop_tree" \
  "$stop_state_sha" "$stop_road_sha" "$stop_invalidation_oid" | git -C "$stop_repo" hash-object -w --stdin)"
stop_receipt="refs/implementaudit/continuity-receipts/$stop_controller/G0001@$stop_receipt_oid"
git -C "$stop_repo" update-ref "refs/implementaudit/continuity-receipts/$stop_controller/G0001" "$stop_receipt_oid"
[ "$(cd "$stop_repo" && bash "$claim_helper" --require-current-continuity "$stop_controller")" = "$stop_receipt" ] || {
  printf 'turn-disposition.test: Stop fixture continuity is not current\n' >&2
  exit 1
}

python "$host_binding_core" --store "$stop_store" init --owner-id stop-owner >/dev/null
python "$host_binding_core" --store "$stop_store" bind \
  --owner-id stop-owner --host-id codex --host-session-id "$stop_session" \
  --controller-id "$stop_controller" --claim-id "$stop_claim" \
  --explicit-run-root "$stop_run_root" --repository-identity "$stop_repo_custody" \
  --git-common-directory-identity "$stop_common_custody" --worktree-identity "$stop_repo_custody" \
  --activation-event-id stop-activation --activation-receipt stop-activation-receipt \
  --continuity-generation G0001 --continuity-receipt "$stop_receipt" >/dev/null

write_stop_route_request() {
  local output="$1" required_reason="${2:-}"
  python - "$output" "$required_reason" "$stop_repo/baseline.txt" <<'PY'
import hashlib,json,sys

def digest(value):
 return "sha256:"+hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
def file_digest(path):
 return "sha256:"+hashlib.sha256(open(path,"rb").read()).hexdigest()

target,reason,baseline=sys.argv[1:]
argv=["route-read-snapshot"] if not reason else ["route-trigger",reason]
identity="action:pure_bounded_read_or_validation"
action={"identity":identity,"class":"PURE_BOUNDED_READ_OR_VALIDATION","argv":argv}
action["digest"]=digest(action)
value={
 "schema":"implementaudit.route-decision-request.v1",
 "predicate_version":"R0033.route-predicate.v1",
 "boundary":{"kind":"new-session","event_id":"stop-boundary-event",
             "digest":digest({"kind":"new-session","event_id":"stop-boundary-event"})},
 "scope":{"identity":"continue exact route-bound action",
          "digest":digest({"identity":"continue exact route-bound action"})},
 "action":action,
 "inputs":[{"identity":"input:repository","path":"baseline.txt","digest":file_digest(baseline)}],
}
with open(target,"w",encoding="utf-8",newline="\n") as handle:
 json.dump(value,handle,sort_keys=True,separators=(",",":")); handle.write("\n")
PY
}

run_stop_route() {
  (
    cd "$stop_repo"
    python "$route_core" "$@" --controller "$stop_controller" --store "$stop_store" \
      --host-id codex --host-session-id "$stop_session" --binding-generation G0001
  )
}

stop_event() {
  local turn="$1" reentry="$2" message="$3"
  python - "$stop_session" "$turn" "$reentry" "$message" <<'PY'
import json,sys
session,turn,reentry,message=sys.argv[1:]
print(json.dumps({
 "session_id":session,"turn_id":turn,"hook_event_name":"Stop",
 "stop_hook_active":reentry=="true","last_assistant_message":message,
 "cwd":"untrusted-cwd","transcript_path":"untrusted-transcript",
},sort_keys=True,separators=(",",":")))
PY
}

run_stop_hook() {
  local plugin_data="$1" payload="$2" output status
  set +e
  output="$(cd "$tmp" && PLUGIN_ROOT="$repo_root" PLUGIN_DATA="$plugin_data" \
    python "$host_stop_adapter" <<<"$payload" 2>"$tmp/stop-hook.err")"
  status=$?
  set -e
  [ "$status" -eq 0 ] || {
    printf 'turn-disposition.test: Stop hook exited %s: %s\n' "$status" "$(cat "$tmp/stop-hook.err")" >&2
    exit 1
  }
  [ ! -s "$tmp/stop-hook.err" ] || {
    printf 'turn-disposition.test: Stop hook leaked stderr: %s\n' "$(cat "$tmp/stop-hook.err")" >&2
    exit 1
  }
  printf '%s\n' "$output"
}

assert_stop_result() {
  local payload="$1" expression="$2" label="$3"
  python - "$payload" "$expression" <<'PY' || {
import json,sys
value=json.loads(sys.argv[1])
assert value.get("schema") == "implementaudit.host-stop-interlock-result.v1"
assert value.get("host_activation_proven") is False
assert "continue" not in value and "stopReason" not in value
assert eval(sys.argv[2],{"__builtins__":{}},{"value":value})
PY
    printf 'turn-disposition.test: Stop result mismatch: %s\n%s\n' "$label" "$payload" >&2
    exit 1
  }
}

write_stop_action_context() {
  local seed="$1"
  python - "$stop_run_shell/R0035_ACTION_CONTEXT.json" "$stop_receipt" "$seed" <<'PY'
import json,sys
path,receipt,seed=sys.argv[1:]
value={
 "schema":"implementaudit.proximal-action-selection-context.v1",
 "currentness":{"receipt":receipt,"current":True},
 "action_population":{
  "target_action_sha256":seed*64,
  "actions":[{"action_sha256":seed*64,"effect_class":"BOUNDED_CORRECTION"}],
 },
 "qualification":None,
}
with open(path,"w",encoding="utf-8",newline="\n") as handle:
 json.dump(value,handle,sort_keys=True,separators=(",",":")); handle.write("\n")
PY
}

stop_snapshot() {
  python - "$stop_repo" "$stop_store" "$stop_run_shell" <<'PY'
import hashlib,os,subprocess,sys
from pathlib import Path
repo,store,run=map(Path,sys.argv[1:])
h=hashlib.sha256()
def add(label,data):
 h.update(label.encode()+b"\0"+len(data).to_bytes(8,"big")+data)
add("refs",subprocess.check_output(["git","for-each-ref","--format=%(refname) %(objectname)"],cwd=repo))
add("status",subprocess.check_output(["git","status","--porcelain=v1","-uall"],cwd=repo))
for label,root in (("store",store),("run",run)):
 if not root.exists(): continue
 for path in sorted(root.rglob("*"),key=lambda item:item.as_posix()):
  rel=path.relative_to(root).as_posix()
  if path.is_symlink(): add(label+":"+rel,b"SYMLINK")
  elif path.is_file(): add(label+":"+rel,path.read_bytes())
print(h.hexdigest())
PY
}

cheap_route_request="$tmp/stop-route-cheap.json"
write_stop_route_request "$cheap_route_request"
cheap_decision="$(run_stop_route decide --request "$cheap_route_request" --expected-record none)"
cheap_oid="$(python -c 'import json,sys; print(json.loads(sys.argv[1])["record_oid"])' "$cheap_decision")"
python - "$cheap_decision" <<'PY'
import json,sys
value=json.loads(sys.argv[1])
assert value["decision"] == "NOT_REQUIRED" and value["advance_allowed"] is False
PY

# R0035 action selection is now a mandatory executable continuation input.  An
# active governed turn with no exact action population must block rather than
# silently taking a caller-asserted NOT_REQUIRED path.
missing_action_event="$(stop_event turn-missing-action false 'Attempted ordinary continuation without R0035 action selection.')"
missing_action_result="$(run_stop_hook "$tmp/stop-plugin-data" "$missing_action_event")"
assert_stop_result "$missing_action_result" \
  'value["status"] == "BLOCK" and value["decision"] == "block" and "proximal action selection" in value["reason"]' \
  'missing R0035 action population reached ordinary continuation'

write_stop_action_context 1
# The R0033 pure-read package binds the non-ignored worktree read set.  Make the
# newly materialized fixed R0035 transport co-current before exercising Stop.
cheap_decision="$(run_stop_route decide --request "$cheap_route_request" --expected-record "$cheap_oid")"
cheap_oid="$(python -c 'import json,sys; print(json.loads(sys.argv[1])["record_oid"])' "$cheap_decision")"
false_terminal_event="$(stop_event turn-false-terminal false $'Status update.\nAUDIT_COMPLETE\nIMPLEMENTAUDIT_RUN_COMPLETE')"
false_terminal_result="$(run_stop_hook "$tmp/stop-plugin-data" "$false_terminal_event")"
assert_stop_result "$false_terminal_result" \
  'value["status"] == "BLOCK" and value["decision"] == "block" and value["disposition"] == "BLOCK" and "terminal closure" in value["reason"]' \
  'false terminal claim reached host Stop'

write_stop_action_context 2
cheap_decision="$(run_stop_route decide --request "$cheap_route_request" --expected-record "$cheap_oid")"
cheap_oid="$(python -c 'import json,sys; print(json.loads(sys.argv[1])["record_oid"])' "$cheap_decision")"
progress_event="$(stop_event turn-progress false 'Progress is durable; continuing the exact route-bound action.')"
progress_result="$(run_stop_hook "$tmp/stop-plugin-data" "$progress_event")"
assert_stop_result "$progress_result" \
  'value["status"] == "ALLOW" and "decision" not in value and value["disposition"] == "NONTERMINAL_YIELD" and value["active_audit_object"] is True and value["proximal_action_decision"] == "NOT_REQUIRED" and value["proximal_action_reason"] == "FEWER_THAN_TWO_BOUNDED_ACTIONS"' \
  'valid nonterminal progress was imprisoned'

snapshot_before="$(stop_snapshot)"
duplicate_one="$(run_stop_hook "$tmp/stop-plugin-data" "$progress_event")"
duplicate_two="$(run_stop_hook "$tmp/stop-plugin-data" "$progress_event")"
snapshot_after="$(stop_snapshot)"
[ "$duplicate_one" = "$duplicate_two" ] || {
  printf 'turn-disposition.test: duplicate Stop delivery was not deterministic\n' >&2
  exit 1
}
[ "$snapshot_before" = "$snapshot_after" ] || {
  printf 'turn-disposition.test: duplicate Stop delivery changed refs/store/run state\n' >&2
  exit 1
}
copied_selection_result="$(run_stop_hook "$tmp/stop-plugin-data" \
  "$(stop_event turn-progress-copy false 'Tried to reuse copied R0035 selection bytes.')")"
assert_stop_result "$copied_selection_result" \
  'value["status"] == "BLOCK" and value["decision"] == "block" and "consumed" in value["reason"]' \
  'copied R0035 selection bytes authorized another turn'

write_stop_action_context 3
required_route_request="$tmp/stop-route-required.json"
write_stop_route_request "$required_route_request" MAINTAINER_QUALIFICATION
required_decision="$(run_stop_route decide --request "$required_route_request" --expected-record "$cheap_oid")"
required_oid="$(python -c 'import json,sys; print(json.loads(sys.argv[1])["record_oid"])' "$required_decision")"
required_obligation="$(python -c 'import json,sys; print(json.loads(sys.argv[1])["obligation_id"])' "$required_decision")"
required_transaction="$(python -c 'import json,sys; print(json.loads(sys.argv[1])["route_transaction_id"])' "$required_decision")"

unsatisfied_result="$(run_stop_hook "$tmp/stop-plugin-data" "$(stop_event turn-unsatisfied false 'Waiting without a satisfied governed route.')")"
assert_stop_result "$unsatisfied_result" \
  'value["status"] == "BLOCK" and value["decision"] == "block" and value["disposition"] == "BLOCK"' \
  'unsatisfied REQUIRED route advanced'

required_attribution="$(python "$host_binding_core" --store "$stop_store" validate-event \
  --host-id codex --host-session-id "$stop_session" --binding-generation G0001 \
  --controller-id "$stop_controller" --claim-id "$stop_claim" --explicit-run-root "$stop_run_root" \
  --repository-identity "$stop_repo_custody" --git-common-directory-identity "$stop_common_custody" \
  --worktree-identity "$stop_repo_custody" --continuity-generation G0001 --continuity-receipt "$stop_receipt" \
  --event-id host:HC-H7B-required --obligation-id "$required_obligation" \
  --route-transaction-id "$required_transaction")"
required_correlation="$(python -c 'import json,sys; print(json.loads(sys.argv[1])["correlation_id"])' "$required_attribution")"
route_packet="$tmp/stop-route-packet.json"
child_return="$tmp/stop-child-return.json"
governor_decision="$tmp/stop-governor-decision.json"
python - "$route_packet" "$child_return" "$governor_decision" "$required_obligation" \
  "$required_transaction" "$required_correlation" <<'PY'
import hashlib,json,sys
packet_path,return_path,decision_path,obligation,transaction,correlation=sys.argv[1:]
def write(path,value):
 raw=(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()
 open(path,"wb").write(raw)
 return "sha256:"+hashlib.sha256(raw).hexdigest()
packet={
 "schema":"implementaudit.route-packet.v1","obligation_id":obligation,
 "route_transaction_id":transaction,"target_identity":"audit-implement",
 "source_event":{"schema":"implementaudit.source-event.v1","source_identity":"host:HC-H7B-required",
  "provenance":{"schema":"implementaudit.source-event-provenance.v1",
   "event_id":"host:HC-H7B-required","host_correlation_id":correlation},
  "body":"qualify the exact maintainer candidate once","kind":"one-shot-action",
  "reactivation":{"reopen":False,"target_changed":False,"invalidating_evidence":False}},
}
packet_digest=write(packet_path,packet)
returned={"schema":"implementaudit.child-return.v1","obligation_id":obligation,
 "route_transaction_id":transaction,"packet_digest":packet_digest,"status":"RETURNED",
 "payload":{"result":"bounded child analysis","requested_next_child":"audit-state"}}
return_digest=write(return_path,returned)
decision={"schema":"implementaudit.governor-route-decision.v1","obligation_id":obligation,
 "route_transaction_id":transaction,"return_digest":return_digest,"outcome":"SATISFIED",
 "reason":"governor reconciled the exact mapped child return"}
write(decision_path,decision)
PY

opened="$(run_stop_route open --request "$required_route_request" --expected-record "$required_oid" \
  --packet "$route_packet" 2>"$tmp/stop-open.visible")"
open_oid="$(python -c 'import json,sys; print(json.loads(sys.argv[1])["record_oid"])' "$opened")"
returned="$(run_stop_route return --request "$required_route_request" --expected-record "$open_oid" \
  --return "$child_return")"
return_oid="$(python -c 'import json,sys; print(json.loads(sys.argv[1])["record_oid"])' "$returned")"
completed="$(run_stop_route complete --request "$required_route_request" --expected-record "$return_oid" \
  --packet "$route_packet" --return "$child_return" --decision "$governor_decision")"
python - "$completed" <<'PY'
import json,sys
value=json.loads(sys.argv[1])
assert value["route_state"] == "SATISFIED" and value["governor_decision_count"] == 1
PY

required_progress_result="$(run_stop_hook "$tmp/stop-plugin-data" \
  "$(stop_event turn-required-satisfied false 'Continuing after the exact governed route returned.')")"
assert_stop_result "$required_progress_result" \
  'value["status"] == "ALLOW" and value["disposition"] == "NONTERMINAL_YIELD" and "decision" not in value and value["proximal_action_decision"] == "NOT_REQUIRED"' \
  'satisfied REQUIRED route did not reach H7A'

unbound_data="$tmp/unbound-stop-plugin-data"
unbound_result="$(run_stop_hook "$unbound_data" "$(stop_event unbound-turn false 'Ordinary unbound turn.')")"
assert_stop_result "$unbound_result" \
  'value["status"] == "UNBOUND" and value["disposition"] == "NO_ACTIVE_AUDIT_OBJECT" and "decision" not in value' \
  'ordinary unbound session did not take zero-scan allow path'
[ ! -e "$unbound_data" ] || {
  printf 'turn-disposition.test: unbound Stop created PLUGIN_DATA state\n' >&2
  exit 1
}

reentry_data="$tmp/reentry-stop-plugin-data"
reentry_result="$(run_stop_hook "$reentry_data" "$(stop_event reentry-turn true 'Host forced-exit re-entry.')")"
assert_stop_result "$reentry_result" \
  'value["status"] == "REENTRY" and value["forced_exit_evidence"] is False and "decision" not in value' \
  'Stop re-entry created an agent prison'
[ ! -e "$reentry_data" ] || {
  printf 'turn-disposition.test: Stop re-entry inspected or created PLUGIN_DATA state\n' >&2
  exit 1
}

for hostile_stop in \
  '{' \
  '{"session_id":"stop-session","session_id":"stop-session","turn_id":"dup","hook_event_name":"Stop","stop_hook_active":false,"last_assistant_message":"duplicate"}' \
  '{"session_id":"bad\\u000asession","turn_id":"bad","hook_event_name":"Stop","stop_hook_active":false,"last_assistant_message":"control"}' \
  '{"session_id":"stop-session","turn_id":"wrong","hook_event_name":"SessionStart","stop_hook_active":false,"last_assistant_message":"foreign"}'; do
  hostile_result="$(run_stop_hook "$tmp/stop-plugin-data" "$hostile_stop")"
  assert_stop_result "$hostile_result" \
    'value["status"] == "BLOCK" and value["decision"] == "block" and value["disposition"] == "BLOCK"' \
    'malformed or foreign Stop input did not fail closed'
done
oversized_stop="$(python - <<'PY'
import json
print(json.dumps({"session_id":"stop-session","turn_id":"oversized","hook_event_name":"Stop",
 "stop_hook_active":False,"last_assistant_message":"x"*70000}))
PY
)"
oversized_result="$(run_stop_hook "$tmp/stop-plugin-data" "$oversized_stop")"
assert_stop_result "$oversized_result" \
  'value["status"] == "BLOCK" and value["decision"] == "block"' \
  'oversized Stop input did not fail closed'

python "$host_binding_core" --store "$stop_store" tombstone \
  --owner-id stop-owner --host-id codex --host-session-id "$stop_session" \
  --expected-generation G0001 --reason fixture-session-ended >/dev/null
tombstoned_result="$(run_stop_hook "$tmp/stop-plugin-data" \
  "$(stop_event tombstoned-turn false 'A tombstoned binding cannot stop an active object.')")"
assert_stop_result "$tombstoned_result" \
  'value["status"] == "BLOCK" and value["decision"] == "block" and value["disposition"] == "BLOCK"' \
  'tombstoned binding did not fail closed'

printf 'turn-disposition.test: ok (TY-1..TY-6 + binding + R0033 + strict decoding + HC-H7B Stop integration)\n'
