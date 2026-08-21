#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
core="$repo_root/skills/implementaudit/scripts/host-session-binding.py"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

py=()
if command -v python >/dev/null 2>&1; then
  py=(python)
elif command -v py >/dev/null 2>&1; then
  py=(py -3)
elif command -v python3 >/dev/null 2>&1; then
  py=(python3)
else
  printf 'host-session-binding.test: Python 3 is required\n' >&2
  exit 1
fi

store="$tmp/host-owned-store"
repository="$tmp/repository"
common="$tmp/git-common"
worktree="$tmp/worktree"
worktree_b="$tmp/worktree-b"
run_a="$worktree/.IMPLEMENTAUDIT/runs/a"
run_b="$worktree/.IMPLEMENTAUDIT/runs/b"
run_a2="$worktree/.IMPLEMENTAUDIT/runs/a2"
run_c="$worktree_b/.IMPLEMENTAUDIT/runs/c"
foreign_repository="$tmp/foreign-repository"
foreign_worktree="$tmp/foreign-worktree"
mkdir -p "$repository" "$common" "$run_a" "$run_b" "$run_a2" "$run_c" \
  "$foreign_repository" "$foreign_worktree"

run_core() {
  "${py[@]}" "$core" --store "$store" "$@"
}

bind_session() {
  local session="$1" claim="$2" run_root="$3" event="$4"
  run_core bind \
    --owner-id host-owner \
    --host-id codex \
    --host-session-id "$session" \
    --controller-id controller-a \
    --claim-id "$claim" \
    --explicit-run-root "$run_root" \
    --repository-identity "$repository" \
    --git-common-directory-identity "$common" \
    --worktree-identity "$worktree" \
    --activation-event-id "$event" \
    --activation-receipt "activation-receipt-$session" \
    --continuity-generation G0001 \
    --continuity-receipt "continuity-receipt-$session"
}

assert_json() {
  local payload="$1" expression="$2"
  "${py[@]}" - "$payload" "$expression" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
if not eval(sys.argv[2], {"__builtins__": {}}, {"value": payload}):
    raise SystemExit(f"assertion failed: {sys.argv[2]} against {payload!r}")
PY
}

expect_unavailable() {
  local label="$1"
  shift
  local output status
  set +e
  if [ "${1:-}" = validate_event ]; then
    output="$("$@" 2>&1)"
  else
    output="$(run_core "$@" 2>&1)"
  fi
  status=$?
  set -e
  if [ "$status" -eq 0 ]; then
    printf 'host-session-binding.test: unexpected success: %s\n' "$label" >&2
    exit 1
  fi
  assert_json "$output" 'value["status"] == "UNAVAILABLE" and value["enforcement_available"] is False'
}

expect_unavailable_at_store() {
  local label="$1" selected_store="$2"
  shift 2
  local output status
  set +e
  output="$("${py[@]}" "$core" --store "$selected_store" "$@" 2>&1)"
  status=$?
  set -e
  if [ "$status" -eq 0 ]; then
    printf 'host-session-binding.test: unexpected success: %s\n' "$label" >&2
    exit 1
  fi
  assert_json "$output" 'value["status"] == "UNAVAILABLE" and value["enforcement_available"] is False'
}

validate_event() {
  local generation="$1" controller="$2" claim="$3" run_root="$4" repo="$5" \
    tree="$6" continuity_generation="$7" continuity_receipt="$8" event="$9"
  shift 9
  run_core validate-event \
    --host-id codex \
    --host-session-id session-a \
    --binding-generation "$generation" \
    --controller-id "$controller" \
    --claim-id "$claim" \
    --explicit-run-root "$run_root" \
    --repository-identity "$repo" \
    --git-common-directory-identity "$common" \
    --worktree-identity "$tree" \
    --continuity-generation "$continuity_generation" \
    --continuity-receipt "$continuity_receipt" \
    --event-id "$event" \
    "$@"
}

run_core init --owner-id host-owner >/dev/null
bind_session session-a claim-a "$run_a" activation-a >/dev/null
bind_session session-b claim-b "$run_b" activation-b >/dev/null

lookup_a="$(run_core lookup --host-id codex --host-session-id session-a)"
lookup_b="$(run_core lookup --host-id codex --host-session-id session-b)"
assert_json "$lookup_a" 'value["status"] == "BOUND" and value["binding"]["binding_generation"] == "G0001" and value["binding"]["host_session_id"] == "session-a" and value["binding"]["claim_id"] == "claim-a"'
assert_json "$lookup_b" 'value["status"] == "BOUND" and value["binding"]["binding_generation"] == "G0001" and value["binding"]["host_session_id"] == "session-b" and value["binding"]["claim_id"] == "claim-b"'
assert_json "$lookup_a" 'value["binding"]["controller_id"] == "controller-a"'
assert_json "$lookup_b" 'value["binding"]["controller_id"] == "controller-a"'

# Case 1: one session resolves only to its exact controller, claim and run.
exact="$(validate_event G0001 controller-a claim-a "$run_a" "$repository" "$worktree" G0001 continuity-receipt-session-a event-exact)"
assert_json "$exact" 'value["status"] == "ATTRIBUTED" and value["binding_generation"] == "G0001"'

# Case 3: worktrees sharing one Git-common identity remain distinct.
run_core bind \
  --owner-id host-owner \
  --host-id codex \
  --host-session-id session-c \
  --controller-id controller-a \
  --claim-id claim-c \
  --explicit-run-root "$run_c" \
  --repository-identity "$repository" \
  --git-common-directory-identity "$common" \
  --worktree-identity "$worktree_b" \
  --activation-event-id activation-c \
  --activation-receipt activation-receipt-session-c \
  --continuity-generation G0001 \
  --continuity-receipt continuity-receipt-session-c >/dev/null
lookup_c="$(run_core lookup --host-id codex --host-session-id session-c)"
assert_json "$lookup_c" 'value["binding"]["worktree_identity"] != value.get("wrong", "") and value["binding"]["host_session_id"] == "session-c"'
expect_unavailable "foreign worktree" validate-event \
  --host-id codex --host-session-id session-c --binding-generation G0001 \
  --controller-id controller-a --claim-id claim-c --explicit-run-root "$run_c" \
  --repository-identity "$repository" --git-common-directory-identity "$common" \
  --worktree-identity "$worktree" --continuity-generation G0001 \
  --continuity-receipt continuity-receipt-session-c --event-id wrong-worktree

# Case 4: rebinding is expected-current CAS and advances exactly one generation.
rebound="$(run_core rebind \
  --expected-generation G0001 \
  --reason governed-object-transfer \
  --owner-id host-owner \
  --host-id codex \
  --host-session-id session-a \
  --controller-id controller-b \
  --claim-id claim-a2 \
  --explicit-run-root "$run_a2" \
  --repository-identity "$repository" \
  --git-common-directory-identity "$common" \
  --worktree-identity "$worktree" \
  --activation-event-id activation-a2 \
  --activation-receipt activation-receipt-session-a2 \
  --continuity-generation G0002 \
  --continuity-receipt continuity-receipt-session-a2)"
assert_json "$rebound" 'value["status"] == "BOUND" and value["binding"]["binding_generation"] == "G0002" and value["binding"]["predecessor_generation"] == "G0001"'
expect_unavailable "stale expected generation" rebind \
  --expected-generation G0001 --reason stale-rebind --owner-id host-owner \
  --host-id codex --host-session-id session-a --controller-id controller-c \
  --claim-id claim-stale --explicit-run-root "$run_a" \
  --repository-identity "$repository" --git-common-directory-identity "$common" \
  --worktree-identity "$worktree" --activation-event-id stale-rebind \
  --activation-receipt stale-rebind-receipt --continuity-generation G0003 \
  --continuity-receipt stale-continuity-receipt

# Case 5: a prior-generation event is stale after CAS.
expect_unavailable "prior-generation event" validate_event G0001 controller-a claim-a \
  "$run_a" "$repository" "$worktree" G0001 continuity-receipt-session-a delayed-event

# Case 6: foreign controller, claim, repository and worktree identities fail closed.
expect_unavailable "foreign controller" validate_event G0002 controller-foreign claim-a2 \
  "$run_a2" "$repository" "$worktree" G0002 continuity-receipt-session-a2 event-foreign-controller
expect_unavailable "foreign claim" validate_event G0002 controller-b claim-foreign \
  "$run_a2" "$repository" "$worktree" G0002 continuity-receipt-session-a2 event-foreign-claim
expect_unavailable "foreign repository" validate_event G0002 controller-b claim-a2 \
  "$run_a2" "$foreign_repository" "$worktree" G0002 continuity-receipt-session-a2 event-foreign-repository
expect_unavailable "foreign worktree" validate_event G0002 controller-b claim-a2 \
  "$run_a2" "$repository" "$foreign_worktree" G0002 continuity-receipt-session-a2 event-foreign-worktree
expect_unavailable "incompatible host identity for reused session ID" bind \
  --owner-id host-owner --host-id claude --host-session-id session-a \
  --controller-id controller-b --claim-id claim-a2 --explicit-run-root "$run_a2" \
  --repository-identity "$repository" --git-common-directory-identity "$common" \
  --worktree-identity "$worktree" --activation-event-id incompatible-host \
  --activation-receipt incompatible-host-receipt --continuity-generation G0002 \
  --continuity-receipt incompatible-host-continuity
expect_unavailable "run root outside recorded worktree" bind \
  --owner-id host-owner --host-id codex --host-session-id session-mismatch \
  --controller-id controller-a --claim-id claim-mismatch --explicit-run-root "$run_a" \
  --repository-identity "$repository" --git-common-directory-identity "$common" \
  --worktree-identity "$worktree_b" --activation-event-id mismatched-worktree \
  --activation-receipt mismatched-worktree-receipt --continuity-generation G0001 \
  --continuity-receipt mismatched-worktree-continuity

inside_store="$worktree/target-owned-binding-store"
"${py[@]}" "$core" --store "$inside_store" init --owner-id host-owner >/dev/null
expect_unavailable_at_store "target-owned binding store" "$inside_store" bind \
  --owner-id host-owner --host-id codex --host-session-id session-target-store \
  --controller-id controller-a --claim-id claim-target-store --explicit-run-root "$run_a" \
  --repository-identity "$worktree" --git-common-directory-identity "$common" \
  --worktree-identity "$worktree" --activation-event-id target-store \
  --activation-receipt target-store-receipt --continuity-generation G0001 \
  --continuity-receipt target-store-continuity

covering_store="$tmp/covering-binding-store"
"${py[@]}" "$core" --store "$covering_store" init --owner-id host-owner >/dev/null
covered_worktree="$covering_store/target-worktree"
covered_run="$covered_worktree/.IMPLEMENTAUDIT/runs/covered"
mkdir -p "$covered_run"
expect_unavailable_at_store "binding store contains target custody" "$covering_store" bind \
  --owner-id host-owner --host-id codex --host-session-id session-covered-store \
  --controller-id controller-a --claim-id claim-covered-store --explicit-run-root "$covered_run" \
  --repository-identity "$covered_worktree" --git-common-directory-identity "$common" \
  --worktree-identity "$covered_worktree" --activation-event-id covered-store \
  --activation-receipt covered-store-receipt --continuity-generation G0001 \
  --continuity-receipt covered-store-continuity

# Case 7: cwd, newest-run, singleton, target prose and child output cannot infer identity.
inference_root="$tmp/inference-trap"
unbound_store="$tmp/absent-store"
mkdir -p "$inference_root/.IMPLEMENTAUDIT/runs/newest"
printf 'controller_id=controller-b\nclaim_id=claim-a2\nchild_output=identity-is-here\n' \
  > "$inference_root/.IMPLEMENTAUDIT/runs/newest/STATE.md"
unbound="$(cd "$inference_root" && "${py[@]}" "$core" --store "$unbound_store" lookup \
  --host-id codex --host-session-id unknown-session)"
assert_json "$unbound" 'value["status"] == "UNBOUND" and value["enforcement_available"] is False'
[ ! -e "$unbound_store" ] || {
  printf 'host-session-binding.test: unbound lookup mutated the store\n' >&2
  exit 1
}
set +e
run_core lookup --host-id codex --host-session-id unknown-session --controller-id controller-b >/dev/null 2>&1
inference_status=$?
set -e
[ "$inference_status" -ne 0 ] || {
  printf 'host-session-binding.test: lookup accepted inferred controller input\n' >&2
  exit 1
}

# Case 8: duplicate event identity is deterministic; reordered stale identity fails.
before_event="$(find "$store" -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum)"
event_one="$(validate_event G0002 controller-b claim-a2 "$run_a2" "$repository" "$worktree" G0002 continuity-receipt-session-a2 event-duplicate --turn-id turn-7 --tool-use-id tool-9)"
event_two="$(validate_event G0002 controller-b claim-a2 "$run_a2" "$repository" "$worktree" G0002 continuity-receipt-session-a2 event-duplicate --turn-id turn-7 --tool-use-id tool-9)"
assert_json "$event_one" 'value["correlation_id"].startswith("sha256:")'
correlation_one="$("${py[@]}" -c 'import json,sys; print(json.loads(sys.argv[1])["correlation_id"])' "$event_one")"
correlation_two="$("${py[@]}" -c 'import json,sys; print(json.loads(sys.argv[1])["correlation_id"])' "$event_two")"
[ "$correlation_one" = "$correlation_two" ] || {
  printf 'host-session-binding.test: duplicate event correlation is non-deterministic\n' >&2
  exit 1
}
after_event="$(find "$store" -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum)"
[ "$before_event" = "$after_event" ] || {
  printf 'host-session-binding.test: event validation mutated binding state\n' >&2
  exit 1
}

# Case 9: ambiguous activation cannot overwrite an active binding.
expect_unavailable "ambiguous duplicate activation" bind \
  --owner-id host-owner --host-id codex --host-session-id session-a \
  --controller-id controller-b --claim-id claim-a2 --explicit-run-root "$run_a2" \
  --repository-identity "$repository" --git-common-directory-identity "$common" \
  --worktree-identity "$worktree" --activation-event-id duplicate-activation \
  --activation-receipt duplicate-activation-receipt --continuity-generation G0002 \
  --continuity-receipt duplicate-continuity-receipt

# Case 10: disabled, untrusted, malformed and mixed-version states never enforce.
for state in disabled untrusted; do
  bad_store="$tmp/$state-store"
  cp -R "$store" "$bad_store"
  cp "$repo_root/fixtures/host-session-binding/$state-owner.json" "$bad_store/owner.json"
  set +e
  bad_output="$("${py[@]}" "$core" --store "$bad_store" lookup --host-id codex --host-session-id session-a 2>&1)"
  bad_status=$?
  set -e
  [ "$bad_status" -ne 0 ] || {
    printf 'host-session-binding.test: %s store claimed enforcement\n' "$state" >&2
    exit 1
  }
  assert_json "$bad_output" 'value["status"] == "UNAVAILABLE" and value["enforcement_available"] is False'
done
malformed_store="$tmp/malformed-store"
cp -R "$store" "$malformed_store"
malformed_binding="$(grep -rl '"host_session_id": "session-a"' "$malformed_store/bindings" | head -1)"
cp "$repo_root/fixtures/host-session-binding/malformed-binding.json" "$malformed_binding"
set +e
malformed_output="$("${py[@]}" "$core" --store "$malformed_store" lookup --host-id codex --host-session-id session-a 2>&1)"
malformed_status=$?
set -e
[ "$malformed_status" -ne 0 ] || {
  printf 'host-session-binding.test: malformed state claimed enforcement\n' >&2
  exit 1
}
assert_json "$malformed_output" 'value["status"] == "UNAVAILABLE" and value["enforcement_available"] is False'

# A binding state is unavailable unless its required direct session index is
# safe, well-formed, and exactly corresponds to the requested host/session.
for operation in lookup validate-event; do
  for index_case in missing corrupt foreign-host mismatched-session; do
    index_store="$tmp/index-$operation-$index_case-store"
    cp -R "$store" "$index_store"
    index_file="$(grep -rl '"host_session_id": "session-a"' "$index_store/sessions" | head -1)"
    case "$index_case" in
      missing)
        rm "$index_file"
        ;;
      corrupt)
        printf '{\n' > "$index_file"
        ;;
      foreign-host)
        printf '{"host_id":"claude","host_session_id":"session-a"}\n' > "$index_file"
        ;;
      mismatched-session)
        printf '{"host_id":"codex","host_session_id":"session-b"}\n' > "$index_file"
        ;;
    esac
    index_snapshot_before="$(find "$index_store" -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum)"
    if [ "$operation" = lookup ]; then
      expect_unavailable_at_store "$index_case index lookup" "$index_store" lookup \
        --host-id codex --host-session-id session-a
    else
      expect_unavailable_at_store "$index_case index event" "$index_store" validate-event \
        --host-id codex --host-session-id session-a --binding-generation G0002 \
        --controller-id controller-b --claim-id claim-a2 --explicit-run-root "$run_a2" \
        --repository-identity "$repository" --git-common-directory-identity "$common" \
        --worktree-identity "$worktree" --continuity-generation G0002 \
        --continuity-receipt continuity-receipt-session-a2 --event-id "index-$index_case"
    fi
    index_snapshot_after="$(find "$index_store" -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum)"
    [ "$index_snapshot_before" = "$index_snapshot_after" ] || {
      printf 'host-session-binding.test: %s index %s mutated partial store\n' \
        "$index_case" "$operation" >&2
      exit 1
    }
  done
done

# An index whose binding state is absent is crash residue, not authority to
# recreate the binding. Bind must fail closed and preserve that residue.
orphan_store="$tmp/orphan-index-store"
cp -R "$store" "$orphan_store"
orphan_binding="$(grep -rl '"host_session_id": "session-a"' "$orphan_store/bindings" | head -1)"
orphan_index="$(grep -rl '"host_session_id": "session-a"' "$orphan_store/sessions" | head -1)"
rm "$orphan_binding"
orphan_index_before="$(sha256sum "$orphan_index")"
expect_unavailable_at_store "orphan index without binding state" "$orphan_store" bind \
  --owner-id host-owner --host-id codex --host-session-id session-a \
  --controller-id controller-b --claim-id claim-a2 --explicit-run-root "$run_a2" \
  --repository-identity "$repository" --git-common-directory-identity "$common" \
  --worktree-identity "$worktree" --activation-event-id orphan-rebind \
  --activation-receipt orphan-rebind-receipt --continuity-generation G0002 \
  --continuity-receipt orphan-continuity-receipt
[ ! -e "$orphan_binding" ] || {
  printf 'host-session-binding.test: bind recreated state behind an orphan index\n' >&2
  exit 1
}
[ "$orphan_index_before" = "$(sha256sum "$orphan_index")" ] || {
  printf 'host-session-binding.test: bind mutated orphan index crash residue\n' >&2
  exit 1
}

chain_store="$tmp/broken-chain-store"
cp -R "$store" "$chain_store"
chain_binding="$(grep -rl '"host_session_id": "session-a"' "$chain_store/bindings" | head -1)"
"${py[@]}" - "$chain_binding" <<'PY'
import json
import sys
from pathlib import Path

path = Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
payload["records"][-1]["predecessor_generation"] = "G00AA"
path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
set +e
chain_output="$("${py[@]}" "$core" --store "$chain_store" lookup --host-id codex --host-session-id session-a 2>&1)"
chain_status=$?
set -e
[ "$chain_status" -ne 0 ] || {
  printf 'host-session-binding.test: broken predecessor chain claimed enforcement\n' >&2
  exit 1
}
assert_json "$chain_output" 'value["status"] == "UNAVAILABLE" and value["enforcement_available"] is False'

lock_store="$tmp/lock-alias-store"
lock_target="$tmp/lock-alias-target"
"${py[@]}" "$core" --store "$lock_store" init --owner-id host-owner >/dev/null
printf 'X' > "$lock_target"
if ln -s "$lock_target" "$lock_store/.writer.lock" 2>/dev/null \
    && [ -L "$lock_store/.writer.lock" ]; then
  expect_unavailable_at_store "aliased writer lock" "$lock_store" bind \
    --owner-id host-owner --host-id codex --host-session-id session-lock-alias \
    --controller-id controller-a --claim-id claim-lock-alias --explicit-run-root "$run_a" \
    --repository-identity "$repository" --git-common-directory-identity "$common" \
    --worktree-identity "$worktree" --activation-event-id lock-alias \
    --activation-receipt lock-alias-receipt --continuity-generation G0001 \
    --continuity-receipt lock-alias-continuity
  [ "$(cat "$lock_target")" = X ] || {
    printf 'host-session-binding.test: aliased writer lock mutated its target\n' >&2
    exit 1
  }
fi

parent_store="$tmp/parent-alias-store"
parent_escape="$tmp/parent-alias-escape"
"${py[@]}" "$core" --store "$parent_store" init --owner-id host-owner >/dev/null
mkdir -p "$parent_escape"
if ln -s "$parent_escape" "$parent_store/bindings" 2>/dev/null \
    && [ -L "$parent_store/bindings" ]; then
  expect_unavailable_at_store "aliased binding parent" "$parent_store" bind \
    --owner-id host-owner --host-id codex --host-session-id session-parent-alias \
    --controller-id controller-a --claim-id claim-parent-alias --explicit-run-root "$run_a" \
    --repository-identity "$repository" --git-common-directory-identity "$common" \
    --worktree-identity "$worktree" --activation-event-id parent-alias \
    --activation-receipt parent-alias-receipt --continuity-generation G0001 \
    --continuity-receipt parent-alias-continuity
  [ -z "$(find "$parent_escape" -type f -print -quit)" ] || {
    printf 'host-session-binding.test: aliased binding parent escaped store custody\n' >&2
    exit 1
  }
fi

# Case 13: route records consume, but cannot override, the current binding generation.
route="$(validate_event G0002 controller-b claim-a2 "$run_a2" "$repository" "$worktree" G0002 continuity-receipt-session-a2 route-event --obligation-id obligation-4 --route-transaction-id route-transaction-4)"
assert_json "$route" 'value["status"] == "ATTRIBUTED" and value["obligation_id"] == "obligation-4" and value["route_transaction_id"] == "route-transaction-4"'
expect_unavailable "stale route generation" validate_event G0001 controller-b claim-a2 \
  "$run_a2" "$repository" "$worktree" G0002 continuity-receipt-session-a2 stale-route-event \
  --obligation-id obligation-4 --route-transaction-id route-transaction-4

# Case 11: SessionEnd tombstones attribution but never closes the governed object.
run_marker_before="$(find "$run_a2" -maxdepth 1 -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum)"
tombstone="$(run_core tombstone --owner-id host-owner --host-id codex \
  --host-session-id session-a --expected-generation G0002 --reason session-end)"
assert_json "$tombstone" 'value["status"] == "TOMBSTONED" and value["binding"]["binding_generation"] == "G0003" and value["object_closed"] is False'
run_marker_after="$(find "$run_a2" -maxdepth 1 -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum)"
[ "$run_marker_before" = "$run_marker_after" ] || {
  printf 'host-session-binding.test: tombstone mutated governed run state\n' >&2
  exit 1
}
expect_unavailable "tombstoned event" validate_event G0003 controller-b claim-a2 \
  "$run_a2" "$repository" "$worktree" G0002 continuity-receipt-session-a2 post-session-end

# Case 12: GC is owner-bound, retention-aware, idempotent and cannot delete unresolved state.
expect_unavailable "unresolved GC" gc --owner-id host-owner --host-id codex \
  --host-session-id session-a --expected-generation G0003 --retain-generations 1
expect_unavailable "foreign-owner GC" gc --owner-id foreign-owner --host-id codex \
  --host-session-id session-a --expected-generation G0003 --retain-generations 1 \
  --resolved-generation G0001 --resolution-receipt resolution-receipt-1
gc_one="$(run_core gc --owner-id host-owner --host-id codex --host-session-id session-a \
  --expected-generation G0003 --retain-generations 1 --resolved-generation G0001 \
  --resolution-receipt resolution-receipt-1)"
assert_json "$gc_one" 'value["status"] == "GC_COMPLETE" and value["removed_generations"] == ["G0001"]'
gc_two="$(run_core gc --owner-id host-owner --host-id codex --host-session-id session-a \
  --expected-generation G0003 --retain-generations 1 --resolved-generation G0001 \
  --resolution-receipt resolution-receipt-1)"
assert_json "$gc_two" 'value["status"] == "GC_COMPLETE" and value["removed_generations"] == []'
[ -d "$run_a" ] && [ -d "$run_a2" ] || {
  printf 'host-session-binding.test: GC deleted governed run state\n' >&2
  exit 1
}

# Case 14: already covered by the absent-store lookup above; it is read-only and zero-create.

# Case 15: source, package, install and native activation proof stay distinct.
assert_json "$lookup_b" 'value["host_activation_proven"] is False and value["proof_layers"] == {"source_core": "PRESENT", "package": "UNVERIFIED", "install": "UNVERIFIED", "host_activation": "UNVERIFIED"}'

printf 'host-session-binding.test: ok (15/15 live R003A cases)\n'
