#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
core="$repo_root/skills/implementaudit/scripts/route-transaction.py"
claim="$repo_root/skills/implementaudit/scripts/claim-run.sh"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

if command -v python >/dev/null 2>&1; then
  py=(python)
elif command -v python3 >/dev/null 2>&1; then
  py=(python3)
elif command -v py >/dev/null 2>&1; then
  py=(py -3)
else
  printf 'route-obligation-contract.test: Python 3 is required\n' >&2
  exit 1
fi

fail() {
  printf 'route-obligation-contract.test: %s\n' "$*" >&2
  exit 1
}

case "${R0033_CASE_FILTER:-}" in
  '') ;;
  G01|G02|G03|G04|G05|G06|G07|G08)
    [ "${R0033_FILTER_MODE:-}" = NON_QUALIFYING ] ||
      fail "R0033_CASE_FILTER requires explicit R0033_FILTER_MODE=NON_QUALIFYING" ;;
  *) fail "R0033_CASE_FILTER is not one exact governed case" ;;
esac

emit_route_summary() {
  if [ -n "${R0033_CASE_FILTER:-}" ]; then
    printf 'route-obligation-contract.test: FILTERED_NON_QUALIFYING case=%s selected-case-only\n' \
      "$R0033_CASE_FILTER"
  else
    printf 'route-obligation-contract.test: request-free current-result matrix GREEN\n'
    printf 'route-obligation-contract.test: G01-G40 common governed-child matrix GREEN\n'
    printf 'route-obligation-contract.test: ok (61/61 live H2A cases + HC-H2B route/return/completion/replay + active-boundary OPEN/RETURNED recovery + all-four child-route matrix; first RED preserved)\n'
  fi
}

if [ "${R0033_SUMMARY_CONTRACT_PROBE:-}" = filtered ]; then
  [ -n "${R0033_CASE_FILTER:-}" ] || fail "filtered summary probe requires one exact case filter"
  probe_summary="$(emit_route_summary)"
  case "$probe_summary" in
    *GREEN*|*61/61*|*all-four*)
      fail "filtered summary probe emitted a full qualification receipt: $probe_summary" ;;
  esac
  printf '%s\n' "$probe_summary"
  exit 0
fi

# Preserve the pre-H2A semantic control: current continuity plus equivalent
# governor reasoning still advances when no canonical route decision exists.
# Feature-file absence is not treated as the RED; the old continuity-only
# advancement path is exercised explicitly.
mkdir -p "$tmp/repo/.IMPLEMENTAUDIT/runs/current-ABC123"
git -C "$tmp/repo" init -q
git -C "$tmp/repo" config user.email test@example.invalid
git -C "$tmp/repo" config user.name test
printf 'baseline\n' > "$tmp/repo/baseline.txt"
git -C "$tmp/repo" add baseline.txt
git -C "$tmp/repo" commit -qm baseline

# Bind custody in the path grammar seen by the selected Python runtime. Git for
# Windows converts MSYS /tmp arguments before launching Python, while WSL keeps
# them POSIX; the strict claim validator intentionally rejects a mixed spelling.
repo_custody="$("${py[@]}" - "$tmp/repo" <<'PY'
import os,sys
print(os.path.abspath(sys.argv[1]).replace("\\", "/"))
PY
)"
common_custody="$repo_custody/.git"

run_root="$repo_custody/.IMPLEMENTAUDIT/runs/current-ABC123"
claim_id=0123456789abcdef0123456789abcdef
cat > "$run_root/.claimed" <<EOF
schema=implementaudit.run-claim.v2
claim_id=$claim_id
claimed_at_utc=2026-08-20T00:00:00Z
mode=full
templates=STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md
repo_root=$repo_custody
git_common_dir=$common_custody
run_base=.IMPLEMENTAUDIT/runs
run_root=.IMPLEMENTAUDIT/runs/current-ABC123
run_name=current-ABC123
EOF
printf 'controller_id=controller-route\n' > "$run_root/.controller"
for template in STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md; do
  cp "$repo_root/skills/implementaudit/templates/$template" "$run_root/$template"
done
"${py[@]}" - "$run_root/STATE.md" "$(git -C "$tmp/repo" rev-parse HEAD)" "$(git -C "$tmp/repo" rev-parse 'HEAD^{tree}')" <<'PY'
from pathlib import Path
import sys
p = Path(sys.argv[1])
s = p.read_text(encoding="utf-8")
s = s.replace("| Next action |  |", "| Next action | execute exact route-bound action |")
s = s.replace(
    "| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|",
    "| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|\n"
    f"| G0001 | new-session | 2026-08-20T00:00:00Z | {sys.argv[2]} {sys.argv[3]} | yes | exact test boundary |",
)
p.write_text(s, encoding="utf-8")
PY

controller_record="$(printf 'implementaudit.controller-current.v1\tcontroller-route\t%s\t%s\n' "$claim_id" "$run_root" | git -C "$tmp/repo" hash-object -w --stdin)"
git -C "$tmp/repo" update-ref refs/implementaudit/controllers/controller-route "$controller_record"
mint_initial_receipt() {
  local controller="$1" controller_oid="$2" claim_local="$3" root="$4" event_id="$5"
  local head tree state_sha road_sha invalidation_oid invalidation_ref receipt_oid receipt_ref
  head="$(git -C "$tmp/repo" rev-parse HEAD)"
  tree="$(git -C "$tmp/repo" rev-parse 'HEAD^{tree}')"
  state_sha="$(sha256sum "$root/STATE.md" | cut -d' ' -f1)"
  road_sha="$(sha256sum "$root/ROADMAP.md" | cut -d' ' -f1)"
  invalidation_ref="refs/implementaudit/continuity-invalidations/$controller"
  invalidation_oid="$(printf 'implementaudit.continuity-invalidation.v1\t%s\t%s\t%s\tnew-session\t%s\n' \
    "$controller" "$controller_oid" "$claim_local" "$event_id" \
    | git -C "$tmp/repo" hash-object -w --stdin)"
  git -C "$tmp/repo" update-ref "$invalidation_ref" "$invalidation_oid" 0000000000000000000000000000000000000000
  receipt_ref="refs/implementaudit/continuity-receipts/$controller/G0001"
  receipt_oid="$(printf 'implementaudit.continuity-receipt.v2\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\tnew-session\tG0001\texecute exact route-bound action\n' \
    "$controller" "$controller_oid" "$claim_local" "$head" "$tree" "$state_sha" "$road_sha" "$invalidation_oid" \
    | git -C "$tmp/repo" hash-object -w --stdin)"
  git -C "$tmp/repo" update-ref "$receipt_ref" "$receipt_oid" 0000000000000000000000000000000000000000
  printf '%s@%s\n' "$receipt_ref" "$receipt_oid"
}
continuity_receipt="$(mint_initial_receipt controller-route "$controller_record" "$claim_id" "$run_root" exact-boundary-event)"
[ "$(cd "$tmp/repo" && bash "$claim" --require-current-continuity controller-route)" = "$continuity_receipt" ] ||
  fail "initial route fixture did not establish exact raw continuity"

set +e
if [ -f "$core" ]; then
  red_output="$(
    cd "$tmp/repo"
    "${py[@]}" "$core" check --controller controller-route \
      --store "$tmp/absent-host-store" --host-id codex \
      --host-session-id route-red --binding-generation G0001 \
      --request "$tmp/absent-request.json" 2>&1
  )"
  red_status=$?
else
  red_output="$(
    cd "$tmp/repo"
    bash "$claim" --require-current-continuity controller-route
  )"
  red_status=$?
fi
set -e

if [ "$red_status" -eq 0 ]; then
  fail "RED: governor-only equivalent reasoning advanced without canonical PENDING|NOT_REQUIRED|REQUIRED authority (continuity=$continuity_receipt; observed=$red_output)"
fi

assert_json() {
  local payload="$1" expression="$2"
  "${py[@]}" - "$payload" "$expression" <<'PY'
import json, sys
value = json.loads(sys.argv[1])
if not eval(sys.argv[2], {"__builtins__": {}}, {"value": value}):
    raise SystemExit(f"assertion failed: {sys.argv[2]} against {value!r}")
PY
}

expect_blocked() {
  local label="$1"
  shift
  local output status
  set +e
  output="$("$@" 2>&1)"
  status=$?
  set -e
  [ "$status" -ne 0 ] || fail "unexpected advancement: $label"
  assert_json "$output" 'value["decision"] in ("PENDING", "NOT_REQUIRED", "REQUIRED") and value["advance_allowed"] is False'
  printf '%s\n' "$output"
}

route() {
  local controller="$1" session="$2" generation="$3"
  local active_core="${ROUTE_CORE:-$core}"
  shift 3
  (
    unset BASH_XTRACEFD
    cd "$tmp/repo"
    if [ -n "${IMPLEMENTAUDIT_R0033_TEST_BARRIER:-}" ]; then
      export IMPLEMENTAUDIT_R0033_TEST_BARRIER
    fi
    "${py[@]}" "$active_core" "$@" --controller "$controller" --store "$tmp/host-store" \
      --host-id codex --host-session-id "$session" --binding-generation "$generation"
  )
}

observe() {
  local controller="$1" session="$2" generation="$3"
  (
    unset BASH_XTRACEFD
    cd "$tmp/repo"
    "${py[@]}" "$core" observe-current --controller "$controller" \
      --store "$tmp/host-store" --host-id codex --host-session-id "$session" \
      --binding-generation "$generation"
  )
}

expect_observe_blocked() {
  local label="$1" controller="$2" session="$3" generation="$4"
  local output status
  set +e
  output="$(observe "$controller" "$session" "$generation" 2>&1)"
  status=$?
  set -e
  [ "$status" -ne 0 ] || fail "request-free observation unexpectedly advanced: $label"
  assert_json "$output" 'value["decision"] in ("PENDING", "NOT_REQUIRED", "REQUIRED") and value["advance_allowed"] is False'
  printf '%s\n' "$output"
}

expect_observe_flag_rejected() {
  local label="$1"
  shift
  local output status
  set +e
  output="$({
    cd "$tmp/repo"
    "${py[@]}" "$core" observe-current --controller controller-cheap \
      --store "$tmp/host-store" --host-id codex --host-session-id session-cheap \
      --binding-generation G0001 "$@"
  } 2>&1)"
  status=$?
  set -e
  [ "$status" -ne 0 ] || fail "request-free observer accepted caller authority: $label"
  [[ "$output" == *"unrecognized arguments"* ]] || fail "request-free observer rejected $label for the wrong reason: $output"
}

read_only_snapshot() {
  "${py[@]}" - "$tmp/repo" "$tmp/host-store" "$repo_root" <<'PY'
import hashlib,os,subprocess,sys
from pathlib import Path
repo,store,source=map(Path,sys.argv[1:])
digest=hashlib.sha256()
def add(label,data):
 digest.update(label.encode()+b"\0"+len(data).to_bytes(8,"big")+data)
def command(label,*argv,cwd):
 add(label,subprocess.check_output(argv,cwd=cwd))
command("refs","git","for-each-ref","--format=%(refname) %(objectname)",cwd=repo)
command("objects","git","count-objects","-v",cwd=repo)
command("repo-status","git","status","--porcelain=v1","-uall",cwd=repo)
command("source-status","git","status","--porcelain=v1","-uall",cwd=source)
for label,root in (
 ("store",store),
 ("runs",repo/".IMPLEMENTAUDIT"/"runs"),
 ("route-lock",repo/".git"/"implementaudit-locks"),
):
 if not root.exists():
  add(label,b"MISSING")
  continue
 for path in sorted(root.rglob("*"),key=lambda value:value.as_posix()):
  relative=path.relative_to(root).as_posix().encode()
  if path.is_symlink(): payload=b"SYMLINK\0"+os.readlink(path).encode()
  elif path.is_file(): payload=b"FILE\0"+path.read_bytes()
  elif path.is_dir(): payload=b"DIR"
  else: payload=b"OTHER"
  add(label+":"+relative.decode(),payload)
print(digest.hexdigest())
PY
}

make_run() {
  local controller="$1" run_name="$2" claim_id_local="$3" event_id="$4"
  local target="$repo_custody/.IMPLEMENTAUDIT/runs/$run_name"
  mkdir -p "$target"
  cat > "$target/.claimed" <<EOF
schema=implementaudit.run-claim.v2
claim_id=$claim_id_local
claimed_at_utc=2026-08-20T00:00:00Z
mode=full
templates=STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md
repo_root=$repo_custody
git_common_dir=$common_custody
run_base=.IMPLEMENTAUDIT/runs
run_root=.IMPLEMENTAUDIT/runs/$run_name
run_name=$run_name
EOF
  printf 'controller_id=%s\n' "$controller" > "$target/.controller"
  for template in STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md; do
    cp "$repo_root/skills/implementaudit/templates/$template" "$target/$template"
  done
  "${py[@]}" - "$target/STATE.md" "$(git -C "$tmp/repo" rev-parse HEAD)" "$(git -C "$tmp/repo" rev-parse 'HEAD^{tree}')" <<'PY'
from pathlib import Path
import sys
p=Path(sys.argv[1]); s=p.read_text(encoding="utf-8")
s=s.replace("| Next action |  |", "| Next action | execute exact route-bound action |")
s=s.replace("| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|",
f"| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|\n| G0001 | new-session | 2026-08-20T00:00:00Z | {sys.argv[2]} {sys.argv[3]} | yes | exact H2A boundary |")
p.write_text(s, encoding="utf-8")
PY
  local record receipt
  record="$(printf 'implementaudit.controller-current.v1\t%s\t%s\t%s\n' "$controller" "$claim_id_local" "$target" | git -C "$tmp/repo" hash-object -w --stdin)"
  git -C "$tmp/repo" update-ref "refs/implementaudit/controllers/$controller" "$record"
  receipt="$(mint_initial_receipt "$controller" "$record" "$claim_id_local" "$target" "$event_id")"
  [ "$(cd "$tmp/repo" && bash "$claim" --require-current-continuity "$controller")" = "$receipt" ] ||
    fail "$controller fixture did not establish exact raw continuity"
  printf '%s\n' "$receipt"
}

host_core="$repo_root/skills/implementaudit/scripts/host-session-binding.py"
host() { "${py[@]}" "$host_core" --store "$tmp/host-store" "$@"; }
host init --owner-id host-owner >/dev/null

bind_host() {
  local session="$1" controller="$2" claim_local="$3" root="$4" receipt="$5" event="$6" generation="${7:-G0001}"
  host bind --owner-id host-owner --host-id codex --host-session-id "$session" \
    --controller-id "$controller" --claim-id "$claim_local" --explicit-run-root "$root" \
    --repository-identity "$tmp/repo" --git-common-directory-identity "$tmp/repo/.git" \
    --worktree-identity "$tmp/repo" --activation-event-id "$event" \
    --activation-receipt "activation-$event" --continuity-generation "$generation" \
    --continuity-receipt "$receipt" >/dev/null
}

promote_to_v3() {
  local controller="$1" claim_local="$2" root="$3" run_name="$4" event="$5"
  local boundary_kind="${6:-manual-resume}"
  local invalidation invalidation_oid head tree state_sha road_sha graph_sha
  local manifest_raw manifest_oid manifest_sha pointer_ref marker_ref pointer_oid receipt receipt_oid marker_oid
  invalidation="$(cd "$tmp/repo" && bash "$claim" --invalidate-continuity "$controller" --boundary "$boundary_kind" --event "$event")"
  invalidation_oid="${invalidation##*@}"
  head="$(git -C "$tmp/repo" rev-parse HEAD)"; tree="$(git -C "$tmp/repo" rev-parse 'HEAD^{tree}')"
  "${py[@]}" - "$root/STATE.md" "$head" "$tree" "$boundary_kind" "$event" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]); head,tree,boundary,event=sys.argv[2:]
s=p.read_text(encoding="utf-8").replace("Current epoch: G0001","Current epoch: G0002")
anchor_prefix=f"| G0001 | new-session | 2026-08-20T00:00:00Z | {head} {tree} | yes | "
anchors=[line for line in s.splitlines() if line.startswith(anchor_prefix)]
row=f"| G0002 | {boundary} | 2026-08-20T00:05:00Z | {head} {tree} | yes | exact successor route boundary {event} |"
if len(anchors)!=1: raise SystemExit("v3 fixture lost its unique G0001 anchor")
anchor=anchors[0]
p.write_text(s.replace(anchor,anchor+"\n"+row),encoding="utf-8")
PY
  printf '\nExact v3 route recovery reconciled.\n' >> "$root/ROADMAP.md"
  printf '%s' '{"schema":"implementaudit.work-graph.fixture.v1"}' > "$root/WORK_GRAPH.json"
  state_sha="$(sha256sum "$root/STATE.md" | cut -d' ' -f1)"
  road_sha="$(sha256sum "$root/ROADMAP.md" | cut -d' ' -f1)"
  graph_sha="$(sha256sum "$root/WORK_GRAPH.json" | cut -d' ' -f1)"
  manifest_raw='{"schema_version":"implementaudit.generation-manifest.fixture.v1"}'
  manifest_oid="$(printf '%s' "$manifest_raw" | git -C "$tmp/repo" hash-object -w --stdin)"
  manifest_sha="$(printf '%s' "$manifest_raw" | sha256sum | cut -d' ' -f1)"
  pointer_ref="refs/implementaudit/current-generations/$controller"
  marker_ref="refs/implementaudit/current-generation-migrations/$controller"
  pointer_oid="$("${py[@]}" - "$controller" "$claim_local" "$run_name" \
    "$manifest_oid" "$manifest_sha" "$state_sha" "$road_sha" "$graph_sha" <<'PY' \
    | git -C "$tmp/repo" hash-object -w --stdin
import hashlib,json,sys
controller,claim,run,manifest_oid,manifest_digest,state,road,graph=sys.argv[1:]
body={
 "schema_version":"implementaudit.state-generation-pointer.v1","controller_id":controller,
 "claim_id":claim,"run_id":run,"generation_id":"G0002","source_epoch":"G0002",
 "predecessor_pointer_oid":None,"predecessor_pointer_digest":None,
 "generation_manifest_oid":manifest_oid,"generation_manifest_digest":manifest_digest,
 "cold_high_water":"00000000000000000001","hot_state_digest":state,"hot_roadmap_digest":road,
 "work_graph_path":"WORK_GRAPH.json","work_graph_digest":graph,
 "query_contract_version":"implementaudit.history-query.v1","degraded_state":"NONE",
}
canonical=lambda value: json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)
body["pointer_digest"]=hashlib.sha256(canonical(body).encode()).hexdigest()
print(canonical(body),end="")
PY
  )"
  git -C "$tmp/repo" update-ref "$pointer_ref" "$pointer_oid" 0000000000000000000000000000000000000000
  receipt="$(cd "$tmp/repo" && bash "$claim" --resume-controller "$controller" --boundary "$boundary_kind" --epoch G0002)"
  receipt_oid="${receipt##*@}"
  marker_oid="$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s' \
    implementaudit.current-generation-migration.v1 "$controller" "$claim_local" "$run_name" G0002 \
    "$pointer_ref" implementaudit.state-generation-pointer.v1 \
    "refs/implementaudit/continuity-receipts/$controller/G0002" "$receipt_oid" true \
    | git -C "$tmp/repo" hash-object -w --stdin)"
  git -C "$tmp/repo" update-ref "$marker_ref" "$marker_oid" 0000000000000000000000000000000000000000
  [ "$(cd "$tmp/repo" && bash "$claim" --require-current-continuity "$controller")" = "$receipt" ] || fail "v3 fixture did not become current"
  printf '%s\n' "$receipt"
}

promote_v3_next() {
  local controller="$1" claim_local="$2" root="$3" run_name="$4" event="$5"
  local boundary_kind="${6:-manual-resume}" current_epoch="${7:-G0002}" next_epoch="${8:-G0003}"
  local invalidation invalidation_oid head tree state_sha road_sha graph_sha
  local manifest_raw manifest_oid manifest_sha pointer_ref old_pointer_oid old_pointer_digest pointer_oid
  local receipt marker_ref
  invalidation="$(cd "$tmp/repo" && bash "$claim" --invalidate-continuity "$controller" --boundary "$boundary_kind" --event "$event")"
  invalidation_oid="${invalidation##*@}"
  head="$(git -C "$tmp/repo" rev-parse HEAD)"; tree="$(git -C "$tmp/repo" rev-parse 'HEAD^{tree}')"
  "${py[@]}" - "$root/STATE.md" "$head" "$tree" "$boundary_kind" "$event" "$current_epoch" "$next_epoch" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]); head,tree,boundary,event,current_epoch,next_epoch=sys.argv[2:]
s=p.read_text(encoding="utf-8").replace(f"Current epoch: {current_epoch}",f"Current epoch: {next_epoch}")
anchor_prefix=f"| {current_epoch} | "
anchors=[line for line in s.splitlines() if line.startswith(anchor_prefix)]
row=f"| {next_epoch} | {boundary} | 2026-08-20T00:10:00Z | {head} {tree} | yes | exact later successor route boundary {event} |"
if len(anchors)!=1: raise SystemExit("v3 successor fixture lost its unique predecessor anchor")
anchor=anchors[0]
p.write_text(s.replace(anchor,anchor+"\n"+row),encoding="utf-8")
PY
  printf '\nExact later v3 route recovery reconciled.\n' >> "$root/ROADMAP.md"
  state_sha="$(sha256sum "$root/STATE.md" | cut -d' ' -f1)"
  road_sha="$(sha256sum "$root/ROADMAP.md" | cut -d' ' -f1)"
  graph_sha="$(sha256sum "$root/WORK_GRAPH.json" | cut -d' ' -f1)"
  manifest_raw='{"schema_version":"implementaudit.generation-manifest.fixture.v1","generation":"later"}'
  manifest_oid="$(printf '%s' "$manifest_raw" | git -C "$tmp/repo" hash-object -w --stdin)"
  manifest_sha="$(printf '%s' "$manifest_raw" | sha256sum | cut -d' ' -f1)"
  pointer_ref="refs/implementaudit/current-generations/$controller"
  marker_ref="refs/implementaudit/current-generation-migrations/$controller"
  old_pointer_oid="$(git -C "$tmp/repo" rev-parse --verify "$pointer_ref")"
  old_pointer_digest="$(git -C "$tmp/repo" cat-file blob "$old_pointer_oid" | "${py[@]}" -c 'import json,sys; print(json.load(sys.stdin)["pointer_digest"])')"
  pointer_oid="$("${py[@]}" - "$controller" "$claim_local" "$run_name" "$next_epoch" \
    "$old_pointer_oid" "$old_pointer_digest" "$manifest_oid" "$manifest_sha" \
    "$state_sha" "$road_sha" "$graph_sha" <<'PY' \
    | git -C "$tmp/repo" hash-object -w --stdin
import hashlib,json,sys
controller,claim,run,generation,previous_oid,previous_digest,manifest_oid,manifest_digest,state,road,graph=sys.argv[1:]
body={
 "schema_version":"implementaudit.state-generation-pointer.v1","controller_id":controller,
 "claim_id":claim,"run_id":run,"generation_id":generation,"source_epoch":generation,
 "predecessor_pointer_oid":previous_oid,"predecessor_pointer_digest":previous_digest,
 "generation_manifest_oid":manifest_oid,"generation_manifest_digest":manifest_digest,
 "cold_high_water":"00000000000000000002","hot_state_digest":state,"hot_roadmap_digest":road,
 "work_graph_path":"WORK_GRAPH.json","work_graph_digest":graph,
 "query_contract_version":"implementaudit.history-query.v1","degraded_state":"NONE",
}
canonical=lambda value: json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)
body["pointer_digest"]=hashlib.sha256(canonical(body).encode()).hexdigest()
print(canonical(body),end="")
PY
  )"
  git -C "$tmp/repo" update-ref "$pointer_ref" "$pointer_oid" "$old_pointer_oid"
  [ "$(git -C "$tmp/repo" rev-parse --verify "$marker_ref")" ] || fail "v3 successor fixture lost its permanent genesis marker"
  receipt="$(cd "$tmp/repo" && bash "$claim" --resume-controller "$controller" --boundary "$boundary_kind" --epoch "$next_epoch")"
  [ "$(cd "$tmp/repo" && bash "$claim" --require-current-continuity "$controller")" = "$receipt" ] || fail "later v3 fixture did not become current"
  printf '%s\n' "$receipt"
}

bind_host route-red controller-route "$claim_id" "$run_root" "$continuity_receipt" activation-required
cheap_claim=11111111111111111111111111111111
pending_claim=22222222222222222222222222222222
history_claim=33333333333333333333333333333333
v3_claim=44444444444444444444444444444444
cheap_receipt="$(make_run controller-cheap cheap-ABC123 "$cheap_claim" exact-boundary-event)"
pending_receipt="$(make_run controller-pending pending-ABC123 "$pending_claim" exact-boundary-event)"
history_receipt="$(make_run controller-history history-ABC123 "$history_claim" exact-boundary-event)"
v3_predecessor_receipt="$(make_run controller-v3 v3-ABC123 "$v3_claim" exact-boundary-event)"
cheap_root="$repo_custody/.IMPLEMENTAUDIT/runs/cheap-ABC123"
pending_root="$repo_custody/.IMPLEMENTAUDIT/runs/pending-ABC123"
history_root="$repo_custody/.IMPLEMENTAUDIT/runs/history-ABC123"
v3_root="$repo_custody/.IMPLEMENTAUDIT/runs/v3-ABC123"
bind_host session-cheap controller-cheap "$cheap_claim" "$cheap_root" "$cheap_receipt" activation-cheap
bind_host session-pending controller-pending "$pending_claim" "$pending_root" "$pending_receipt" activation-pending
bind_host session-history controller-history "$history_claim" "$history_root" "$history_receipt" activation-history

write_request() {
  local target="$1" action_class="$2" required_reason="${3:-}"
  "${py[@]}" - "$target" "$action_class" "$required_reason" "$tmp/repo/baseline.txt" \
    "$claim" "$repo_root/skills/implementaudit/scripts/check-closure-surface.sh" <<'PY'
import hashlib, json, sys
def h(value): return "sha256:"+hashlib.sha256(json.dumps(value,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
def file_hash(path): return "sha256:"+hashlib.sha256(open(path,"rb").read()).hexdigest()
argv={
 "MECHANICAL_CURRENTNESS_ACTION":[sys.argv[5],"--require-current-continuity","controller-cheap"],
 "PURE_BOUNDED_READ_OR_VALIDATION":["route-read-snapshot"],
 "EXACT_PACKAGE_OR_TOPOLOGY_VERIFICATION":["bash","-n",sys.argv[6]],
 "SAFE_STATUS_OR_CONTAINMENT":["route-safe-status"],
 "EXACT_ALREADY_BOUND_DETERMINISTIC_ACTION":["sha256sum","baseline.txt"],
}.get(sys.argv[2],["unknown-action"])
if sys.argv[3]: argv=["route-trigger",sys.argv[3]]
action_identity="action:"+sys.argv[2].lower()
inputs=[{"identity":"input:repository","path":"baseline.txt","digest":file_hash(sys.argv[4])}]
inputs=sorted(inputs,key=lambda item:item["identity"])
value={
 "schema":"implementaudit.route-decision-request.v1",
 "predicate_version":"R0033.route-predicate.v1",
 "boundary":{"kind":"new-session","event_id":"exact-boundary-event","digest":h({"kind":"new-session","event_id":"exact-boundary-event"})},
 "scope":{"identity":"execute exact route-bound action","digest":h({"identity":"execute exact route-bound action"})},
 "action":{"identity":action_identity,"digest":h({"identity":action_identity,"class":sys.argv[2],"argv":argv}),"class":sys.argv[2],"argv":argv},
 "inputs":inputs,
}
with open(sys.argv[1],"w",encoding="utf-8",newline="\n") as f: json.dump(value,f,sort_keys=True); f.write("\n")
PY
}

mutate_request() {
  local source="$1" target="$2" expression="$3"
  "${py[@]}" - "$source" "$target" "$expression" "$tmp/repo" <<'PY'
import hashlib,json,sys
with open(sys.argv[1],encoding="utf-8") as f: value=json.load(f)
def h(item): return "sha256:"+hashlib.sha256(json.dumps(item,sort_keys=True,separators=(",", ":")).encode()).hexdigest()
def file_hash(path): return "sha256:"+hashlib.sha256(open(path,"rb").read()).hexdigest()
exec(sys.argv[3], {"__builtins__": {}}, {"value":value,"h":h,"file_hash":file_hash,"repo":sys.argv[4]})
with open(sys.argv[2],"w",encoding="utf-8",newline="\n") as f: json.dump(value,f,sort_keys=True); f.write("\n")
PY
}

required_request="$tmp/required.json"
cheap_request="$tmp/cheap.json"
pending_request="$tmp/pending.json"
history_request="$tmp/history.json"
write_request "$required_request" PURE_BOUNDED_READ_OR_VALIDATION MAINTAINER_QUALIFICATION
write_request "$cheap_request" PURE_BOUNDED_READ_OR_VALIDATION
write_request "$pending_request" PURE_BOUNDED_READ_OR_VALIDATION
history_event_id="iaevt-v1-$(printf 'a%.0s' {1..64})"
mutate_request "$pending_request" "$history_request" 'value["action"]={"identity":"action:query-history-then-resume","class":"QUERY_HISTORY_THEN_RESUME","argv":["route-trigger","QUERY_HISTORY_THEN_RESUME","'"$history_event_id"'"]}; value["action"]["digest"]=h(value["action"])'

mkdir -p "$tmp/evil-bin"
printf '#!/usr/bin/env bash\nprintf attacker-git-executed > "%s"\nexit 1\n' "$tmp/path-git-fired" > "$tmp/evil-bin/git"
chmod +x "$tmp/evil-bin/git"
cp "$tmp/evil-bin/git" "$tmp/evil-bin/git.EXE"
chmod +x "$tmp/evil-bin/git.EXE"
printf '#!/usr/bin/env bash\nexit 0\n' > "$tmp/evil-bin/sha256sum"
chmod +x "$tmp/evil-bin/sha256sum"
cp "$tmp/evil-bin/sha256sum" "$tmp/evil-bin/sha256sum.EXE"
chmod +x "$tmp/evil-bin/sha256sum.EXE"
"${py[@]}" - "$core" "$tmp/repo" "$tmp/evil-bin" >/dev/null <<'PY'
import importlib.util, os, pathlib, sys
spec=importlib.util.spec_from_file_location("route_transaction",sys.argv[1]); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
os.environ["PATH"]=sys.argv[3]+os.pathsep+os.environ["PATH"]
try: module.executable_evidence(pathlib.Path(sys.argv[2]),["sha256sum","baseline.txt"])
except SystemExit: pass
else: raise SystemExit("caller-controlled PATH executable was accepted as trusted")
PY
PATH="$tmp/evil-bin:$PATH" "${py[@]}" - "$core" "$tmp/repo" >/dev/null <<'PY'
import importlib.util,pathlib,sys
spec=importlib.util.spec_from_file_location("route_transaction",sys.argv[1]); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
try: module.current_ref(pathlib.Path(sys.argv[2]),"controller-cheap")
except SystemExit: pass
PY
[ ! -e "$tmp/path-git-fired" ] || fail "current_ref executed caller-controlled PATH git"
PATH="$tmp/evil-bin:$PATH" "${py[@]}" - "$core" "$tmp/repo" >/dev/null <<'PY'
import importlib.util,pathlib,sys
spec=importlib.util.spec_from_file_location("route_transaction",sys.argv[1]); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
try: module.current_controller(pathlib.Path(sys.argv[2]),"controller-cheap")
except SystemExit: pass
PY
[ ! -e "$tmp/path-git-fired" ] || fail "current_controller claim-run executed caller-controlled PATH git"
"${py[@]}" - "$core" <<'PY'
import importlib.util,os,sys
spec=importlib.util.spec_from_file_location("route_transaction",sys.argv[1]); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
os.environ["BASH_FUNC_git%%"]="() { :; }"
if any(key.startswith("BASH_FUNC_") for key in module.sanitized_action_environment()):
 raise SystemExit("exported Bash function survived action environment sanitization")
PY

printf '#!/usr/bin/env bash\nprintf fsmonitor-executed > "%s"\nexit 0\n' "$tmp/fsmonitor-fired" > "$tmp/hostile-fsmonitor"
chmod +x "$tmp/hostile-fsmonitor"
git -C "$tmp/repo" config core.fsmonitor "$tmp/hostile-fsmonitor"
"${py[@]}" - "$core" "$tmp/repo" <<'PY'
import importlib.util,pathlib,sys
spec=importlib.util.spec_from_file_location("route_transaction",sys.argv[1]); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
module.worktree_read_set(pathlib.Path(sys.argv[2]))
PY
git -C "$tmp/repo" config --unset core.fsmonitor
[ ! -e "$tmp/fsmonitor-fired" ] || fail "built-in read-set executed configured fsmonitor"

"${py[@]}" - "$core" "$claim" <<'PY'
import importlib.util,sys
spec=importlib.util.spec_from_file_location("route_transaction",sys.argv[1]); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
invalid=(
 [sys.argv[2],"--verify-resume-receipt"],
 [sys.argv[2],"--require-current-route","controller-cheap"],
 [sys.argv[2],"--verify-resume-receipt","refs/implementaudit/continuity-receipts/"+"a"*49+"/G0001@"+"0"*40],
)
if any(module.mechanical_action_class(argv)=="MECHANICAL_CURRENTNESS_ACTION" for argv in invalid):
 raise SystemExit("incomplete or impossible currentness argv was admitted")
PY

"${py[@]}" - "$core" <<'PY'
import importlib.util,sys
spec=importlib.util.spec_from_file_location("route_transaction",sys.argv[1]); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
git_diff=["git","--no-optional-locks","-c","core.fsmonitor=false","-c","diff.external=","diff","--no-ext-diff","--no-textconv","--ignore-submodules=all","--","baseline.txt"]
if module.mechanical_action_class(git_diff) is not None:
 raise SystemExit("Git diff remained an executable cheap-path action")
PY

printf 'printf inherited-env-executed > "%s"\n' "$tmp/bash-env-fired" > "$tmp/hostile-bash-env"
BASH_ENV="$tmp/hostile-bash-env" "${py[@]}" - "$core" "$tmp/repo" \
  "$claim" <<'PY'
import importlib.util,json,pathlib,sys
spec=importlib.util.spec_from_file_location("route_transaction",sys.argv[1]); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
repo=pathlib.Path(sys.argv[2]); argv=[sys.argv[3],"--require-current-continuity","controller-cheap"]
request={"action":{"argv":argv}}
module.execute_exact_action(repo,request,module.executable_evidence(repo,argv))
PY
[ ! -e "$tmp/bash-env-fired" ] || fail "BASH_ENV executed inside the exact admitted action environment"

# 1-5: omission, prose and projection are not authority; malformed authority blocks.
printf 'route obligation REQUIRED\n' > "$run_root/route-prose.txt"
cp "$run_root/STATE.md" "$tmp/state-before-projection-edit.md"
printf '\n| Route decision projection | NOT_REQUIRED |\n| Route decision record | invented |\n' >> "$run_root/STATE.md"
expect_blocked "prose/STATE cannot create authority" route controller-route route-red G0001 check --request "$required_request" >/dev/null
expect_observe_blocked "absence cannot create request-free authority" controller-route route-red G0001 >/dev/null
cp "$tmp/state-before-projection-edit.md" "$run_root/STATE.md"
junk="$(printf 'not-json\n' | git -C "$tmp/repo" hash-object -w --stdin)"
git -C "$tmp/repo" update-ref refs/implementaudit/route-decisions/controller-route "$junk"
expect_blocked "malformed current route record" route controller-route route-red G0001 check --request "$required_request" >/dev/null
expect_observe_blocked "malformed current route record" controller-route route-red G0001 >/dev/null
git -C "$tmp/repo" update-ref -d refs/implementaudit/route-decisions/controller-route

# 6-9 and 42-45: required/judgement classification, immutable obligation skeleton,
# exact current H0 boundary attribution and proof-layer honesty.
set +e
required_decide="$(route controller-route route-red G0001 decide --request "$required_request" --expected-record none 2>&1)"
required_status=$?
set -e
[ "$required_status" -eq 0 ] || fail "required decision failed: $required_decide"
assert_json "$required_decide" 'value["decision"] == "REQUIRED" and value["classification"] == "MECHANICALLY_REQUIRED" and value["route_state"] == "UNSATISFIED"'
assert_json "$required_decide" 'value["obligation_id"].startswith("sha256:") and value["route_transaction_id"].startswith("sha256:")'
assert_json "$required_decide" 'value["host_activation_proven"] is False and value["proof_layers"]["source_core"] == "PRESENT" and value["proof_layers"]["package"] == "UNVERIFIED"'
required_oid="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$required_decide")"
required_obligation="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["obligation_id"])' "$required_decide")"
required_transaction="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["route_transaction_id"])' "$required_decide")"
source_event_correlation() {
  local event_id="$1" attributed
  attributed="$(host validate-event --host-id codex --host-session-id route-red \
    --binding-generation G0001 --controller-id controller-route --claim-id "$claim_id" \
    --explicit-run-root "$run_root" --repository-identity "$repo_custody" \
    --git-common-directory-identity "$common_custody" --worktree-identity "$repo_custody" \
    --continuity-generation G0001 --continuity-receipt "$continuity_receipt" \
    --event-id "$event_id" --obligation-id "$required_obligation" \
    --route-transaction-id "$required_transaction")"
  "${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["correlation_id"])' "$attributed"
}
source_e1_correlation="$(source_event_correlation host:E1)"
source_e2_correlation="$(source_event_correlation host:E2)"
source_e3_correlation="$(source_event_correlation host:E3)"
required_check="$(expect_blocked "required route remains unsatisfied" route controller-route route-red G0001 check --request "$required_request")"
assert_json "$required_check" 'value["decision"] == "REQUIRED" and value["advance_allowed"] is False and value["route_state"] == "UNSATISFIED"'
set +e
required_snapshot_before="$(read_only_snapshot)"
required_observed="$(observe controller-route route-red G0001 2>&1)"
required_observed_status=$?
required_snapshot_after="$(read_only_snapshot)"
set -e
[ "$required_observed_status" -eq 3 ] || fail "request-free REQUIRED/UNSATISFIED did not retain the check exit class"
[ "$required_observed" = "$required_check" ] || fail "request-free REQUIRED/UNSATISFIED result differs from check"
[ "$required_snapshot_before" = "$required_snapshot_after" ] || fail "request-free REQUIRED/UNSATISFIED observation changed persistent state"
required_blob="$(git -C "$tmp/repo" cat-file blob "$required_oid")"
assert_json "$required_blob" 'value["child_lifecycle_owned"] is False and "child_open" not in value and "child_return" not in value and "completion" not in value'
assert_json "$required_blob" 'value["predecessor_record_oid"] is None and value["record_identity"].startswith("sha256:")'

# HC-H2B: the canonical MAINTAINER_QUALIFICATION obligation opens only with the
# mapped audit-implement bytes and immutable packet, visibly names that exact
# load, accepts the same live return, rereads currentness after return, and
# records exactly one governor decision.
route_packet="$tmp/route-packet.json"
child_return="$tmp/child-return.json"
governor_decision="$tmp/governor-decision.json"
"${py[@]}" - "$required_decide" "$route_packet" "$child_return" "$governor_decision" "$source_e1_correlation" <<'PY'
import hashlib,json,sys
decided=json.loads(sys.argv[1])
event={
 "schema":"implementaudit.source-event.v1",
 "source_identity":"host:E1",
 "provenance":{
  "schema":"implementaudit.source-event-provenance.v1",
  "event_id":"host:E1",
  "host_correlation_id":sys.argv[5],
 },
 "body":"perform the exact bounded route once",
 "kind":"one-shot-action",
 "reactivation":{"reopen":False,"target_changed":False,"invalidating_evidence":False},
}
packet={
 "schema":"implementaudit.route-packet.v1",
 "obligation_id":decided["obligation_id"],
 "route_transaction_id":decided["route_transaction_id"],
 "source_event":event,
 "target_identity":"audit-implement",
}
def write(path,value):
 raw=(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()
 open(path,"wb").write(raw)
 return "sha256:"+hashlib.sha256(raw).hexdigest()
packet_digest=write(sys.argv[2],packet)
returned={
 "schema":"implementaudit.child-return.v1",
 "obligation_id":decided["obligation_id"],
 "route_transaction_id":decided["route_transaction_id"],
 "packet_digest":packet_digest,
 "status":"RETURNED",
 "payload":{"result":"bounded child analysis"},
}
return_digest=write(sys.argv[3],returned)
decision={
 "schema":"implementaudit.governor-route-decision.v1",
 "obligation_id":decided["obligation_id"],
 "route_transaction_id":decided["route_transaction_id"],
 "return_digest":return_digest,
 "outcome":"SATISFIED",
 "reason":"governor adjudicated the exact live return",
}
write(sys.argv[4],decision)
PY

open_visible="$tmp/open-visible.txt"
opened="$(route controller-route route-red G0001 open --request "$required_request" \
  --expected-record "$required_oid" --packet "$route_packet" 2>"$open_visible")"
assert_json "$opened" 'value["status"] == "CHILD_OPEN" and value["decision"] == "REQUIRED" and value["route_state"] == "OPEN" and value["advance_allowed"] is False'
open_oid="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$opened")"
"${py[@]}" - "$opened" "$repo_root/skills/audit-implement/SKILL.md" "$route_packet" <<'PY'
import base64,json,sys
value=json.loads(sys.argv[1])
if base64.b64decode(value["delivery"]["child"]["bytes_b64"]) != open(sys.argv[2],"rb").read():
 raise SystemExit("mapped audit-implement child bytes were not delivered")
assert base64.b64decode(value["delivery"]["packet"]["bytes_b64"]) == open(sys.argv[3],"rb").read()
PY
mapfile -t open_visible_lines < "$open_visible"
[ "${#open_visible_lines[@]}" -eq 2 ] || fail "mapped child OPEN did not emit exactly two visible route lines"
[ "${open_visible_lines[0]: -1}" != $'\r' ] || open_visible_lines[0]="${open_visible_lines[0]%$'\r'}"
[ "${open_visible_lines[1]: -1}" != $'\r' ] || open_visible_lines[1]="${open_visible_lines[1]%$'\r'}"
[ "${open_visible_lines[0]}" = 'CHILD_SKILL_ROUTE=audit-implement' ] || fail "mapped child OPEN emitted the wrong route identity"
[ "${open_visible_lines[1]}" = "I'm using audit-implement to qualify the exact maintainer candidate after verified release currentness." ] || fail "mapped child OPEN emitted the wrong bounded reason"
open_blob="$(git -C "$tmp/repo" cat-file blob "$open_oid")"
assert_json "$open_blob" 'value["predecessor_record_oid"] == "'"$required_oid"'" and value["route_state"] == "OPEN" and value["child_lifecycle_owned"] is True and value["lifecycle"]["delivery"]'

returned="$(route controller-route route-red G0001 return --request "$required_request" \
  --expected-record "$open_oid" --return "$child_return")"
assert_json "$returned" 'value["status"] == "CHILD_RETURNED" and value["route_state"] == "RETURNED" and value["advance_allowed"] is False'
return_oid="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$returned")"
cp "$child_return" "$tmp/child-return.original.json"
printf '{"changed":true}\n' > "$child_return"
expect_blocked "changed post-return bytes cannot reach governor completion" \
  route controller-route route-red G0001 complete --request "$required_request" \
    --expected-record "$return_oid" --packet "$route_packet" --return "$child_return" \
    --decision "$governor_decision" >/dev/null
[ "$(git -C "$tmp/repo" rev-parse refs/implementaudit/route-decisions/controller-route)" = "$return_oid" ] || fail "failed return reread changed canonical route authority"
cp "$tmp/child-return.original.json" "$child_return"

completed="$(route controller-route route-red G0001 complete --request "$required_request" \
  --expected-record "$return_oid" --packet "$route_packet" --return "$child_return" \
  --decision "$governor_decision")"
assert_json "$completed" 'value["status"] == "ROUTE_COMPLETE" and value["decision"] == "REQUIRED" and value["route_state"] == "SATISFIED" and value["advance_allowed"] is True'
assert_json "$completed" 'value["governor_decision_count"] == 1 and value["post_return_currentness"] == "VERIFIED" and value["history_read_performed"] is False'
complete_oid="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$completed")"
complete_blob="$(git -C "$tmp/repo" cat-file blob "$complete_oid")"
assert_json "$complete_blob" 'value["predecessor_record_oid"] == "'"$return_oid"'" and value["lifecycle"]["governor_decision_count"] == 1 and value["route_state"] == "SATISFIED"'

completion_check="$(route controller-route route-red G0001 check --request "$required_request")"
assert_json "$completion_check" 'value["decision"] == "REQUIRED" and value["route_state"] == "SATISFIED" and value["advance_allowed"] is True'
completion_snapshot_before="$(read_only_snapshot)"
completion_observed="$(observe controller-route route-red G0001)"
completion_snapshot_after="$(read_only_snapshot)"
[ "$completion_observed" = "$completion_check" ] || fail "request-free REQUIRED/SATISFIED result differs from check"
[ "$completion_snapshot_before" = "$completion_snapshot_after" ] || fail "request-free REQUIRED/SATISFIED observation changed persistent state"
assert_json "$completion_observed" 'value["route_transaction_id"] == "'"$required_transaction"'" and value["obligation_id"] == "'"$required_obligation"'"'
completion_admitted="$(route controller-route route-red G0001 admit-current)"
assert_json "$completion_admitted" 'value["route_transaction_id"] == "'"$required_transaction"'" and value["obligation_id"] == "'"$required_obligation"'"'

# The activation-time causal join is real at every owner boundary: the
# request-free R0033 projection supplies the exact pair, H0 attributes that
# pair into its correlation digest, and H7A consumes both production results.
join_event=host:H7B-JOIN
join_attribution="$(host validate-event --host-id codex --host-session-id route-red \
  --binding-generation G0001 --controller-id controller-route --claim-id "$claim_id" \
  --explicit-run-root "$run_root" --repository-identity "$repo_custody" \
  --git-common-directory-identity "$common_custody" --worktree-identity "$repo_custody" \
  --continuity-generation G0001 --continuity-receipt "$continuity_receipt" \
  --event-id "$join_event" --obligation-id "$required_obligation" \
  --route-transaction-id "$required_transaction")"
assert_json "$join_attribution" 'value["status"] == "ATTRIBUTED" and value["obligation_id"] == "'"$required_obligation"'" and value["route_transaction_id"] == "'"$required_transaction"'" and value["correlation_id"].startswith("sha256:")'
"${py[@]}" - "$repo_root/skills/implementaudit/scripts/evaluate-turn-disposition.py" \
  "$completion_observed" "$join_attribution" "$run_root" "$repo_custody" \
  "$common_custody" "$continuity_receipt" "$join_event" <<'PY'
import copy,hashlib,importlib.util,json,sys
from pathlib import Path

evaluator_path,route_raw,binding_raw,run_root,repo,common,receipt,event_id=sys.argv[1:]
spec=importlib.util.spec_from_file_location("evaluate_turn_disposition",evaluator_path)
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
route=json.loads(route_raw)
binding_result=json.loads(binding_raw)
canonical_run_root=str(Path(run_root).resolve(strict=True))
canonical_repo=str(Path(repo).resolve(strict=True))
canonical_common=str(Path(common).resolve(strict=True))
correlation={
 "host_id":"codex","host_session_id":"route-red","binding_generation":"G0001",
 "controller_id":"controller-route","claim_id":"0123456789abcdef0123456789abcdef",
 "explicit_run_root":canonical_run_root,"repository_identity":canonical_repo,
 "git_common_directory_identity":canonical_common,"worktree_identity":canonical_repo,
 "applicable_continuity_generation":"G0001","applicable_continuity_receipt":receipt,
 "event_id":event_id,"turn_id":None,"tool_use_id":None,"agent_id":None,
 "obligation_id":route["obligation_id"],"route_transaction_id":route["route_transaction_id"],
}
binding={"correlation":correlation,"result":binding_result}
validated_binding=module.validate_binding(binding,canonical_run_root)
assert module.validate_route(route,validated_binding)==route

def rejects(label,mutate):
 candidate=copy.deepcopy(route); mutate(candidate)
 try:
  module.validate_route(candidate,validated_binding)
 except (module.InputError,module.DecisionBlocked):
  return
 raise SystemExit(f"H7A accepted {label} route transaction substitution")

rejects("swapped",lambda value:value.__setitem__("route_transaction_id",value["obligation_id"]))
rejects("foreign",lambda value:value.__setitem__("route_transaction_id","sha256:"+"5"*64))
rejects("missing",lambda value:value.pop("route_transaction_id"))
rejects("null-half",lambda value:value.__setitem__("route_transaction_id",None))
rejects("stale",lambda value:value.__setitem__("status","STALE"))
rejects("malformed",lambda value:value.__setitem__("route_transaction_id","not-a-transaction"))
rejects("caller-computed",lambda value:value.__setitem__("route_transaction_id","sha256:"+hashlib.sha256(b"caller-computed").hexdigest()))
rejects("record-OID-substituted",lambda value:value.__setitem__("route_transaction_id",value["record_oid"]))
def locally_appended(value):
 value.pop("route_transaction_id")
 value["route_transaction_id"]="sha256:"+hashlib.sha256(b"local-adapter").hexdigest()
rejects("locally-appended",locally_appended)
old_shape=copy.deepcopy(route); old_shape.pop("route_transaction_id")
try:
 module.validate_route(old_shape,validated_binding)
except module.InputError:
 pass
else:
 raise SystemExit("H7A accepted the old 19-key route result")
PY
"${py[@]}" - "$complete_blob" "$tmp" <<'PY'
import base64,copy,hashlib,json,sys
source=json.loads(sys.argv[1]); root=sys.argv[2]
def canonical(value): return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def artifact(raw): return {"bytes":len(raw),"digest":"sha256:"+hashlib.sha256(raw).hexdigest(),"bytes_b64":base64.b64encode(raw).decode()}
def artifact_value(value): return artifact(canonical(value)+b"\n")
def finish(name,value):
 base={key:item for key,item in value.items() if key!="record_identity"}
 value["record_identity"]="sha256:"+hashlib.sha256(canonical(base)).hexdigest()
 with open(f"{root}/proxy-{name}.json","wb") as handle: handle.write(canonical(value)+b"\n")

wrong_child=copy.deepcopy(source)
wrong_child["lifecycle"]["delivery"]["child"]={
 "identity":wrong_child["lifecycle"]["delivery"]["child"]["identity"],
 **artifact(b"not audit-state\n"),
}
finish("wrong-child",wrong_child)

invalid=copy.deepcopy(source)
invalid["lifecycle"]["delivery"]["child"]={"identity":"fake:audit-state",**artifact(b"not audit-state\n")}
invalid["lifecycle"]["delivery"]["packet"]=artifact(b"{}\n")
invalid["lifecycle"]["child_return"]=artifact(b"{}\n")
invalid["lifecycle"]["governor_decision"]=artifact(b"{}\n")
finish("invalid-bundle",invalid)

foreign=copy.deepcopy(source)
packet=json.loads(base64.b64decode(foreign["lifecycle"]["delivery"]["packet"]["bytes_b64"]))
returned=json.loads(base64.b64decode(foreign["lifecycle"]["child_return"]["bytes_b64"]))
decision=json.loads(base64.b64decode(foreign["lifecycle"]["governor_decision"]["bytes_b64"]))
foreign_obligation="sha256:"+"0"*64; foreign_transaction="sha256:"+"1"*64
packet["obligation_id"]=returned["obligation_id"]=decision["obligation_id"]=foreign_obligation
packet["route_transaction_id"]=returned["route_transaction_id"]=decision["route_transaction_id"]=foreign_transaction
foreign["lifecycle"]["delivery"]["packet"]=artifact_value(packet)
returned["packet_digest"]=foreign["lifecycle"]["delivery"]["packet"]["digest"]
foreign["lifecycle"]["child_return"]=artifact_value(returned)
decision["return_digest"]=foreign["lifecycle"]["child_return"]["digest"]
foreign["lifecycle"]["governor_decision"]=artifact_value(decision)
finish("foreign-bundle",foreign)

event_mismatch=copy.deepcopy(source)
packet=json.loads(base64.b64decode(event_mismatch["lifecycle"]["delivery"]["packet"]["bytes_b64"]))
returned=json.loads(base64.b64decode(event_mismatch["lifecycle"]["child_return"]["bytes_b64"]))
decision=json.loads(base64.b64decode(event_mismatch["lifecycle"]["governor_decision"]["bytes_b64"]))
packet["source_event"]["provenance"]["host_correlation_id"]="sha256:"+"2"*64
event_mismatch["lifecycle"]["delivery"]["packet"]=artifact_value(packet)
returned["packet_digest"]=event_mismatch["lifecycle"]["delivery"]["packet"]["digest"]
event_mismatch["lifecycle"]["child_return"]=artifact_value(returned)
decision["return_digest"]=event_mismatch["lifecycle"]["child_return"]["digest"]
event_mismatch["lifecycle"]["governor_decision"]=artifact_value(decision)
finish("event-attribution-mismatch",event_mismatch)

shortcut=copy.deepcopy(source)
shortcut["predecessor_record_oid"]=shortcut["lifecycle"]["required_record_oid"]
finish("shortcut-chain",shortcut)

mixed=copy.deepcopy(source)
mixed["mixed_version_member"]="forbidden"
finish("mixed-version",mixed)

wrong_controller=copy.deepcopy(source)
wrong_controller["controller_id"]="controller-foreign"
finish("wrong-controller",wrong_controller)

bad_identity=copy.deepcopy(source)
bad_identity["record_identity"]="sha256:"+"0"*64
with open(f"{root}/proxy-bad-identity.json","wb") as handle:
 handle.write(canonical(bad_identity)+b"\n")

malformed_lifecycle=copy.deepcopy(source)
malformed_lifecycle["lifecycle"]["state"]="OPEN"
finish("malformed-lifecycle",malformed_lifecycle)

for name,path,value in (
 ("foreign-claim",("claim_id",),"f"*32),
 ("foreign-run",("explicit_run_root",),source["explicit_run_root"]+"-foreign"),
 ("foreign-continuity-generation",("continuity_generation",),"G0002"),
 ("foreign-continuity-receipt",("continuity_receipt",),source["continuity_receipt"]+"-foreign"),
 ("foreign-boundary",("boundary","event_id"),"foreign-boundary"),
 ("foreign-scope",("scope","identity"),"foreign-scope"),
 ("foreign-action",("action","identity"),"foreign-action"),
 ("foreign-package",("package","head"),"0"*40),
 ("foreign-child-source",("child_source","digest"),"sha256:"+"0"*64),
 ("foreign-input",("inputs",0,"digest"),"sha256:"+"0"*64),
 ("foreign-host-correlation",("host_correlation_id",),"sha256:"+"0"*64),
):
 value_copy=copy.deepcopy(source)
 cursor=value_copy
 for member in path[:-1]: cursor=cursor[member]
 cursor[path[-1]]=value
 finish(name,value_copy)

with open(f"{root}/proxy-noncanonical.json","w",encoding="utf-8",newline="\n") as handle:
 json.dump(source,handle,sort_keys=True,indent=2,ensure_ascii=True)
 handle.write("\n")
duplicate_raw=b'{"schema":"duplicate",'+canonical(source)[1:]+b"\n"
with open(f"{root}/proxy-duplicate-member.json","wb") as handle:
 handle.write(duplicate_raw)
PY
for proxy_case in \
  wrong-child invalid-bundle foreign-bundle shortcut-chain mixed-version \
  event-attribution-mismatch wrong-controller bad-identity malformed-lifecycle \
  foreign-claim foreign-run \
  foreign-continuity-generation foreign-continuity-receipt foreign-boundary \
  foreign-scope foreign-action foreign-package foreign-child-source \
  foreign-input foreign-host-correlation noncanonical duplicate-member; do
  proxy_oid="$(git -C "$tmp/repo" hash-object -w "$tmp/proxy-$proxy_case.json")"
  git -C "$tmp/repo" update-ref refs/implementaudit/route-decisions/controller-route "$proxy_oid" "$complete_oid"
  expect_blocked "$proxy_case cannot satisfy full-byte route delivery" \
    route controller-route route-red G0001 check --request "$required_request" >/dev/null
  expect_observe_blocked "$proxy_case cannot satisfy request-free route delivery" \
    controller-route route-red G0001 >/dev/null
  git -C "$tmp/repo" update-ref refs/implementaudit/route-decisions/controller-route "$complete_oid" "$proxy_oid"
done
duplicate_completion="$(route controller-route route-red G0001 complete --request "$required_request" \
  --expected-record "$complete_oid" --packet "$route_packet" --return "$child_return" \
  --decision "$governor_decision")"
assert_json "$duplicate_completion" 'value["idempotent"] is True and value["record_oid"] == "'"$complete_oid"'" and value["governor_decision_count"] == 1'
[ "$(git -C "$tmp/repo" rev-parse refs/implementaudit/route-decisions/controller-route)" = "$complete_oid" ] || fail "idempotent completion minted a second route record"

# Compaction replay is source-event identity, not text equality. A satisfied
# one-shot E1 reconstructed with the same source identity is not reissued; E2
# retains a distinct identity even with identical text, but a terminal target
# remains a canonical no-op without explicit reactivation evidence.
event_e1="$tmp/event-e1.json"
event_e2="$tmp/event-e2.json"
event_e3="$tmp/event-e3-reactivate.json"
event_ambiguous="$tmp/event-ambiguous.json"
event_kind_conflict="$tmp/event-kind-conflict.json"
event_reactivation_conflict="$tmp/event-reactivation-conflict.json"
event_body_conflict="$tmp/event-body-conflict.json"
event_unbound="$tmp/event-unbound.json"
event_malformed="$tmp/event-malformed.json"
"${py[@]}" - "$route_packet" "$event_e1" "$event_e2" "$event_e3" "$event_ambiguous" \
  "$event_kind_conflict" "$event_reactivation_conflict" "$event_body_conflict" "$event_unbound" \
  "$source_e2_correlation" "$source_e3_correlation" <<'PY'
import json,sys
packet=json.load(open(sys.argv[1],encoding="utf-8"))
event=packet["source_event"]
for path,value in (
 (sys.argv[2],event),
 (sys.argv[3],{**event,"source_identity":"host:E2","provenance":{**event["provenance"],"event_id":"host:E2","host_correlation_id":sys.argv[10]}}),
 (sys.argv[4],{**event,"source_identity":"host:E3","provenance":{**event["provenance"],"event_id":"host:E3","host_correlation_id":sys.argv[11]},"reactivation":{**event["reactivation"],"reopen":True}}),
 (sys.argv[5],{key:value for key,value in event.items() if key!="provenance"}),
 (sys.argv[6],{**event,"kind":"standing-constraint"}),
 (sys.argv[7],{**event,"reactivation":{**event["reactivation"],"reopen":True}}),
 (sys.argv[8],{**event,"body":"conflicting reconstruction"}),
 (sys.argv[9],{**event,"source_identity":"host:UNBOUND","provenance":{**event["provenance"],"event_id":"host:UNBOUND","host_correlation_id":"sha256:"+"0"*64}}),
):
 with open(path,"w",encoding="utf-8",newline="\n") as handle:
  json.dump(value,handle,sort_keys=True,separators=(",",":"),ensure_ascii=False); handle.write("\n")
PY
printf '{malformed-json\n' > "$event_malformed"

replayed="$(route controller-route route-red G0001 replay --request "$required_request" \
  --expected-record "$complete_oid" --event "$event_e1")"
assert_json "$replayed" 'value["status"] == "REPLAY_NO_OP" and value["source_event_relation"] == "SAME_SOURCE" and value["record_oid"] == "'"$complete_oid"'"'
assert_json "$replayed" 'value["effects"] == {"instruction_rows":0,"route_transactions":0,"lifecycle_transitions":0,"mutation_authorizations":0,"task_dispatches":0,"external_effects":0}'
distinct="$(route controller-route route-red G0001 replay --request "$required_request" \
  --expected-record "$complete_oid" --event "$event_e2")"
assert_json "$distinct" 'value["status"] == "TERMINAL_NO_OP" and value["source_event_relation"] == "DISTINCT_SOURCE_SAME_BODY" and value["source_identity"] == "host:E2"'
assert_json "$distinct" 'value["target_state"] == "SATISFIED" and value["effects"]["instruction_rows"] == 0 and value["effects"]["external_effects"] == 0'
[ "$(git -C "$tmp/repo" rev-parse refs/implementaudit/route-decisions/controller-route)" = "$complete_oid" ] || fail "compaction replay mutated the canonical terminal route"

expect_ambiguous_replay() {
  local label="$1" event_path="$2" output status
  set +e
  output="$(route controller-route route-red G0001 replay --request "$required_request" \
    --expected-record "$complete_oid" --event "$event_path" 2>&1)"
  status=$?
  set -e
  [ "$status" -ne 0 ] || fail "$label did not STOP"
  assert_json "$output" 'value["status"] == "ambiguous" and value["stop"] is True and value["advance_allowed"] is False'
  assert_json "$output" 'value["effects"] == {"instruction_rows":0,"route_transactions":0,"lifecycle_transitions":0,"mutation_authorizations":0,"task_dispatches":0,"external_effects":0}'
}
expect_ambiguous_replay "same source with changed kind" "$event_kind_conflict"
expect_ambiguous_replay "same source with changed reactivation" "$event_reactivation_conflict"
expect_ambiguous_replay "same source with changed body" "$event_body_conflict"
expect_ambiguous_replay "unbound source identity" "$event_unbound"
expect_ambiguous_replay "missing reconstructed source artifact" "$tmp/event-missing.json"
expect_ambiguous_replay "malformed reconstructed source artifact" "$event_malformed"

set +e
reactivate="$(route controller-route route-red G0001 replay --request "$required_request" \
  --expected-record "$complete_oid" --event "$event_e3" 2>&1)"
reactivate_status=$?
set -e
[ "$reactivate_status" -ne 0 ] || fail "explicit reactivation evidence advanced the old terminal route"
assert_json "$reactivate" 'value["status"] == "NEW_SOURCE_REVIEW_REQUIRED" and value["advance_allowed"] is False and value["effects"]["route_transactions"] == 0'
set +e
ambiguous="$(route controller-route route-red G0001 replay --request "$required_request" \
  --expected-record "$complete_oid" --event "$event_ambiguous" 2>&1)"
ambiguous_status=$?
set -e
[ "$ambiguous_status" -ne 0 ] || fail "missing source provenance did not STOP"
assert_json "$ambiguous" 'value["status"] == "ambiguous" and value["stop"] is True and value["advance_allowed"] is False'

"${py[@]}" - "$core" <<'PY'
import importlib.util,sys
spec=importlib.util.spec_from_file_location("route_transaction",sys.argv[1]); module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
provenance={"schema":"implementaudit.source-event-provenance.v1","event_id":"host:S1","host_correlation_id":"sha256:"+"1"*64}
stored={"source_identity":"host:S1","provenance":provenance,"body":"keep applying","kind":"standing-constraint","status":"active","reactivation":{"reopen":False,"target_changed":False,"invalidating_evidence":False}}
incoming={"source_identity":"host:S1","provenance":provenance,"body":"keep applying","kind":"standing-constraint","reactivation":{"reopen":False,"target_changed":False,"invalidating_evidence":False}}
value=module.instruction_replay_status(stored,incoming,target_terminal=False)
assert value["status"]=="STANDING_APPLIES" and value["new_instruction_rows"]==0
PY

history_decide="$(route controller-history session-history G0001 decide --request "$history_request" --expected-record none)"
assert_json "$history_decide" 'value["decision"] == "REQUIRED" and value["classification"] == "JUDGEMENT_REQUIRED" and value["history_read_performed"] is False'
assert_json "$history_decide" 'value["history_query"] == {"schema":"implementaudit.history-query-request.v1","route":"QUERY_HISTORY_THEN_RESUME","requirement":"REQUIRED","evidence_ids":["'"$history_event_id"'"]}'

v3_receipt="$(promote_to_v3 controller-v3 "$v3_claim" "$v3_root" v3-ABC123 exact-v3-boundary-event)"
bind_host session-v3 controller-v3 "$v3_claim" "$v3_root" "$v3_receipt" activation-v3 G0002
v3_request="$tmp/v3-required.json"
mutate_request "$required_request" "$v3_request" 'value["boundary"]={"kind":"manual-resume","event_id":"exact-v3-boundary-event"}; value["boundary"]["digest"]=h(value["boundary"])'
unrelated_event_id="iaevt-v1-$(printf 'b%.0s' {1..64})"
unrelated_ref="refs/implementaudit/state-event-segments/v3-ABC123/G0002/00000000000000000001/$unrelated_event_id"
unrelated_oid="$(printf 'corrupt-unrelated-history' | git -C "$tmp/repo" hash-object -w --stdin)"
git -C "$tmp/repo" update-ref "$unrelated_ref" "$unrelated_oid"
set +e
v3_decide="$(route controller-v3 session-v3 G0001 decide --request "$v3_request" --expected-record none 2>&1)"
v3_decide_status=$?
set -e
[ "$v3_decide_status" -eq 0 ] || fail "verified v3 continuity was rejected by route authority: $v3_decide"
assert_json "$v3_decide" 'value["decision"] == "REQUIRED" and value["route_state"] == "UNSATISFIED" and value["history_read_performed"] is False'
v3_route_oid="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$v3_decide")"
v3_route_blob="$(git -C "$tmp/repo" cat-file blob "$v3_route_oid")"
assert_json "$v3_route_blob" 'value["continuity_generation"] == "G0002" and value["continuity_receipt"] == "'"$v3_receipt"'"'
[ "$(git -C "$tmp/repo" rev-parse "$unrelated_ref")" = "$unrelated_oid" ] || fail "routine v3 route recovery touched unrelated history"
set +e
v3_observed="$(observe controller-v3 session-v3 G0001 2>&1)"
v3_observed_status=$?
set -e
[ "$v3_observed_status" -eq 3 ] || fail "request-free v3 REQUIRED/UNSATISFIED changed its exit class"
assert_json "$v3_observed" 'value["decision"] == "REQUIRED" and value["advance_allowed"] is False and value["history_read_performed"] is False'
[ "$(git -C "$tmp/repo" rev-parse "$unrelated_ref")" = "$unrelated_oid" ] || fail "request-free v3 observation enumerated or touched unrelated history"

incomplete_request="$tmp/incomplete.json"
mutate_request "$pending_request" "$incomplete_request" 'value["inputs"][0]["digest"]="sha256:"+"0"*64'
pending_decide="$(route controller-pending session-pending G0001 decide --request "$incomplete_request" --expected-record none)"
assert_json "$pending_decide" 'value["decision"] == "PENDING" and value["advance_allowed"] is False and value["invalidators"]'
pending_oid="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$pending_decide")"
stale_snapshot_before="$(read_only_snapshot)"
stale_observed="$(expect_observe_blocked "stale retained input is lossy" controller-pending session-pending G0001)"
stale_snapshot_after="$(read_only_snapshot)"
assert_json "$stale_observed" 'value["advance_allowed"] is False and value["enforcement_available"] is False'
[ "$stale_snapshot_before" = "$stale_snapshot_after" ] || fail "lossy request-free observation changed persistent state"
set +e
mirror_check="$(route controller-pending session-pending G0001 check --request "$incomplete_request" --mirror-claim SATISFIED 2>&1)"
mirror_status=$?
set -e
[ "$mirror_status" -ne 0 ] || fail "ActiveGraph mirror claim advanced a canonical PENDING route"
assert_json "$mirror_check" 'value["decision"] == "PENDING" and value["advance_allowed"] is False and value["record_oid"] == "'"$pending_oid"'"'
assert_json "$mirror_check" 'value["mirror_claim"] == "SATISFIED" and value["mirror_status"] == "IGNORED_CONTRADICTION"'
[ "$(git -C "$tmp/repo" rev-parse refs/implementaudit/route-decisions/controller-pending)" = "$pending_oid" ] || fail "mirror claim mutated canonical route authority"
missing_request="$tmp/missing-input.json"
mutate_request "$pending_request" "$missing_request" 'value["inputs"]=[{"identity":"input:missing","path":"absent-input.txt","digest":"sha256:"+"0"*64},*value["inputs"]]'
missing_decide="$(route controller-pending session-pending G0001 decide --request "$missing_request" --expected-record "$pending_oid")"
pending_oid="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$missing_decide")"
missing_observed="$(expect_observe_blocked "omitted missing input is lossy" controller-pending session-pending G0001)"
assert_json "$missing_observed" 'value["advance_allowed"] is False and value["enforcement_available"] is False'
evil_request="$tmp/evil-basename.json"
mutate_request "$pending_request" "$evil_request" 'value["action"]["argv"]=["/tmp/evil/git","diff","--","baseline.txt"]; value["action"]["digest"]=h({"identity":value["action"]["identity"],"class":value["action"]["class"],"argv":value["action"]["argv"]})'
judgement_decide="$(route controller-pending session-pending G0001 decide --request "$evil_request" --expected-record "$pending_oid")"
assert_json "$judgement_decide" 'value["decision"] == "REQUIRED" and value["classification"] == "JUDGEMENT_REQUIRED" and value["advance_allowed"] is False'
judgement_oid="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$judgement_decide")"

# 10-15: every closed non-trigger class receives only a scoped current receipt.
printf 'read-set-v1\n' > "$tmp/repo/unlisted-observation.txt"
cheap_decide="$(route controller-cheap session-cheap G0001 decide --request "$cheap_request" --expected-record none)"
assert_json "$cheap_decide" 'value["decision"] == "NOT_REQUIRED" and value["classification"] == "MECHANICALLY_NOT_REQUIRED" and value["advance_allowed"] is False and value["admission_required"] is True'
assert_json "$cheap_decide" 'value["history_query"] is None and value["history_read_performed"] is False'
cheap_oid="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$cheap_decide")"
cheap_check="$(route controller-cheap session-cheap G0001 check --request "$cheap_request")"
assert_json "$cheap_check" 'value["decision"] == "NOT_REQUIRED" and value["advance_allowed"] is False and value["admission_required"] is True'
assert_json "$cheap_check" 'value["obligation_id"] is None and value["route_transaction_id"] is None'
set +e
cheap_snapshot_before="$(read_only_snapshot)"
cheap_observed="$(observe controller-cheap session-cheap G0001 2>&1)"
cheap_observed_status=$?
cheap_snapshot_after="$(read_only_snapshot)"
set -e
if [ "$cheap_observed_status" -ne 0 ]; then
  printf 'route-obligation-contract.test: request-free current-result operation is absent RED\n' >&2
  exit 1
fi
[ "$cheap_observed" = "$cheap_check" ] || fail "request-free NOT_REQUIRED result differs from check"
[ "$cheap_snapshot_before" = "$cheap_snapshot_after" ] || fail "request-free NOT_REQUIRED observation changed persistent state"
for rejected in \
  '--request|absent.json' '--request-path|absent.json' '--ref|refs/heads/main' \
  '--run-root|foreign-run' '--claim|foreign-claim' '--cwd|foreign-cwd' \
  '--target|foreign-target' '--transcript|foreign-transcript' \
  '--newest-run|true' '--mirror-claim|SATISFIED'; do
  IFS='|' read -r rejected_flag rejected_value <<< "$rejected"
  expect_observe_flag_rejected "$rejected_flag" "$rejected_flag" "$rejected_value"
done
mkdir -p "$tmp/wrong-cwd"
git -C "$tmp/wrong-cwd" init -q
set +e
wrong_cwd_observed="$({
  cd "$tmp/wrong-cwd"
  "${py[@]}" "$core" observe-current --controller controller-cheap \
    --store "$tmp/host-store" --host-id codex --host-session-id session-cheap \
    --binding-generation G0001
} 2>&1)"
wrong_cwd_observed_status=$?
set -e
[ "$wrong_cwd_observed_status" -ne 0 ] || fail "wrong cwd selected foreign request-free authority"
assert_json "$wrong_cwd_observed" 'value["advance_allowed"] is False and value["enforcement_available"] is False'
printf 'read-set-v2\n' > "$tmp/repo/unlisted-observation.txt"
expect_blocked "unlisted worktree read-set change expires receipt" route controller-cheap session-cheap G0001 check --request "$cheap_request" >/dev/null
expect_observe_blocked "request-free read-set change expires receipt" controller-cheap session-cheap G0001 >/dev/null
printf 'read-set-v1\n' > "$tmp/repo/unlisted-observation.txt"
route controller-cheap session-cheap G0001 check --request "$cheap_request" >/dev/null
wrapper_check="$(
  cd "$tmp/repo"
  bash "$claim" --require-current-route controller-cheap --store "$tmp/host-store" \
    --host-id codex --host-session-id session-cheap --binding-generation G0001
)"
assert_json "$wrapper_check" 'value["decision"] == "NOT_REQUIRED" and value["advance_allowed"] is False and value["admission_required"] is True'
for class in MECHANICAL_CURRENTNESS_ACTION EXACT_PACKAGE_OR_TOPOLOGY_VERIFICATION SAFE_STATUS_OR_CONTAINMENT EXACT_ALREADY_BOUND_DETERMINISTIC_ACTION; do
  candidate="$tmp/class-$class.json"
  write_request "$candidate" "$class"
  class_decide="$(route controller-cheap session-cheap G0001 decide --request "$candidate" --expected-record "$cheap_oid")"
  assert_json "$class_decide" "value[\"decision\"] == \"NOT_REQUIRED\" and value[\"classification\"] == \"MECHANICALLY_NOT_REQUIRED\""
  cheap_oid="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$class_decide")"
done
cheap_decide="$(route controller-cheap session-cheap G0001 decide --request "$cheap_request" --expected-record "$cheap_oid")"
cheap_oid="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$cheap_decide")"

# 16-29: every scope/currentness input is an expiry invalidator. These are
# check-time controls against one genuine cheap-path receipt.
declare -a mutations=(
  'value["scope"]["identity"]="scope:expanded"'
  'value["action"]["identity"]="action:next"'
  'value["inputs"][0]["digest"]="sha256:"+"1"*64'
  'value["boundary"]["event_id"]="successor-boundary"'
  'value["action"]["argv"]=["unknown-action"]'
  'value["action"]["class"]="SAFE_STATUS_OR_CONTAINMENT"'
  'value["evidence"]={"owner":{"status":"CURRENT"}}'
)
index=0
for mutation in "${mutations[@]}"; do
  index=$((index+1)); candidate="$tmp/expiry-$index.json"
  mutate_request "$cheap_request" "$candidate" "$mutation"
  expect_blocked "expiry invalidator $index" route controller-cheap session-cheap G0001 check --request "$candidate" >/dev/null
done
self_consistent_boundary="$tmp/expiry-self-consistent-boundary.json"
mutate_request "$cheap_request" "$self_consistent_boundary" 'value["boundary"]["event_id"]="caller-selected-boundary"; value["boundary"]["digest"]=h({"kind":value["boundary"]["kind"],"event_id":value["boundary"]["event_id"]})'
expect_blocked "self-consistent caller boundary cannot override live receipt" route controller-cheap session-cheap G0001 check --request "$self_consistent_boundary" >/dev/null
self_consistent_scope="$tmp/expiry-self-consistent-scope.json"
mutate_request "$cheap_request" "$self_consistent_scope" 'value["scope"]["identity"]="caller-selected-scope"; value["scope"]["digest"]=h({"identity":value["scope"]["identity"]})'
expect_blocked "self-consistent caller scope cannot override live next action" route controller-cheap session-cheap G0001 check --request "$self_consistent_scope" >/dev/null
# 30-33: active obligations cannot be downgraded, and every write is expected-old CAS.
expect_blocked "active obligation downgrade" route controller-route route-red G0001 decide --request "$cheap_request" --expected-record "$required_oid" >/dev/null
expect_blocked "stale CAS expected absence" route controller-cheap session-cheap G0001 decide --request "$cheap_request" --expected-record none >/dev/null
same_again="$(route controller-cheap session-cheap G0001 decide --request "$cheap_request" --expected-record "$cheap_oid")"
assert_json "$same_again" 'value["idempotent"] is True and value["record_oid"]'

# 34-41: controller/binding/continuity isolation and independent-scope behavior.
expect_blocked "foreign controller" route controller-route session-cheap G0001 check --request "$required_request" >/dev/null
expect_blocked "foreign session claim" route controller-cheap route-red G0001 check --request "$cheap_request" >/dev/null
expect_observe_blocked "request-free foreign controller binding" controller-route session-cheap G0001 >/dev/null
expect_observe_blocked "request-free foreign session binding" controller-cheap route-red G0001 >/dev/null
expect_observe_blocked "request-free absent host binding" controller-cheap session-unbound G0001 >/dev/null
independent="$(route controller-cheap session-cheap G0001 check --request "$cheap_request")"
assert_json "$independent" 'value["decision"] == "NOT_REQUIRED" and value["admission_required"] is True and value["advance_allowed"] is False'
# A non-cooperating ref replacement during the deliberately multi-owner check
# must be caught by the final current-ref fence, never return the old allow.
race_junk="$(printf 'race-replacement\n' | git -C "$tmp/repo" hash-object -w --stdin)"
set +e
route controller-cheap session-cheap G0001 check --request "$cheap_request" >"$tmp/race-check.out" 2>&1 &
race_pid=$!
sleep 0.1
git -C "$tmp/repo" update-ref refs/implementaudit/route-decisions/controller-cheap "$race_junk" "$cheap_oid"
wait "$race_pid"
race_status=$?
set -e
[ "$race_status" -ne 0 ] || fail "concurrent route-ref replacement returned stale NOT_REQUIRED authority"
git -C "$tmp/repo" update-ref refs/implementaudit/route-decisions/controller-cheap "$cheap_oid" "$race_junk"
set +e
observe controller-cheap session-cheap G0001 >"$tmp/race-observe-route.out" 2>&1 &
observe_route_pid=$!
sleep 0.1
git -C "$tmp/repo" update-ref refs/implementaudit/route-decisions/controller-cheap "$race_junk" "$cheap_oid"
wait "$observe_route_pid"
observe_route_status=$?
set -e
[ "$observe_route_status" -ne 0 ] || fail "request-free route-ref replacement returned stale NOT_REQUIRED authority"
git -C "$tmp/repo" update-ref refs/implementaudit/route-decisions/controller-cheap "$cheap_oid" "$race_junk"

cheap_controller_oid="$(git -C "$tmp/repo" rev-parse refs/implementaudit/controllers/controller-cheap)"
controller_race_junk="$(printf 'controller-race\n' | git -C "$tmp/repo" hash-object -w --stdin)"
set +e
observe controller-cheap session-cheap G0001 >"$tmp/race-observe-controller.out" 2>&1 &
observe_controller_pid=$!
sleep 0.1
git -C "$tmp/repo" update-ref refs/implementaudit/controllers/controller-cheap "$controller_race_junk" "$cheap_controller_oid"
wait "$observe_controller_pid"
observe_controller_status=$?
set -e
[ "$observe_controller_status" -ne 0 ] || fail "request-free controller replacement returned stale NOT_REQUIRED authority"
git -C "$tmp/repo" update-ref refs/implementaudit/controllers/controller-cheap "$cheap_controller_oid" "$controller_race_junk"

cp "$cheap_root/STATE.md" "$tmp/cheap-state-before-race.md"
set +e
observe controller-cheap session-cheap G0001 >"$tmp/race-observe-continuity.out" 2>&1 &
observe_continuity_pid=$!
sleep 0.1
printf '\ncontinuity-race\n' >> "$cheap_root/STATE.md"
wait "$observe_continuity_pid"
observe_continuity_status=$?
set -e
[ "$observe_continuity_status" -ne 0 ] || fail "request-free continuity replacement returned stale NOT_REQUIRED authority"
cp "$tmp/cheap-state-before-race.md" "$cheap_root/STATE.md"

cp "$tmp/repo/baseline.txt" "$tmp/baseline-before-race.txt"
set +e
observe controller-cheap session-cheap G0001 >"$tmp/race-observe-input.out" 2>&1 &
observe_input_pid=$!
sleep 0.1
printf 'input-race\n' >> "$tmp/repo/baseline.txt"
wait "$observe_input_pid"
observe_input_status=$?
set -e
[ "$observe_input_status" -ne 0 ] || fail "request-free input replacement returned stale NOT_REQUIRED authority"
cp "$tmp/baseline-before-race.txt" "$tmp/repo/baseline.txt"
old_transaction="$(git -C "$tmp/repo" cat-file blob "$cheap_oid" | "${py[@]}" -c 'import json,sys;print(json.load(sys.stdin)["route_transaction_id"])')"
host rebind --owner-id host-owner --host-id codex --host-session-id session-cheap \
  --expected-generation G0001 --reason binding-generation-control \
  --controller-id controller-cheap --claim-id "$cheap_claim" --explicit-run-root "$cheap_root" \
  --repository-identity "$tmp/repo" --git-common-directory-identity "$tmp/repo/.git" \
  --worktree-identity "$tmp/repo" --activation-event-id activation-cheap-g2 \
  --activation-receipt activation-cheap-g2 --continuity-generation G0001 \
  --continuity-receipt "$cheap_receipt" >/dev/null
expect_blocked "current binding generation expires prior receipt" route controller-cheap session-cheap G0002 check --request "$cheap_request" >/dev/null
expect_observe_blocked "request-free binding generation expires prior receipt" controller-cheap session-cheap G0002 >/dev/null
rebound_decide="$(route controller-cheap session-cheap G0002 decide --request "$cheap_request" --expected-record "$cheap_oid")"
rebound_oid="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$rebound_decide")"
assert_json "$rebound_decide" "value[\"decision\"] == \"NOT_REQUIRED\" and value[\"record_oid\"] != \"$cheap_oid\" and not value.get(\"idempotent\", False)"
rebound_transaction="$(git -C "$tmp/repo" cat-file blob "$rebound_oid" | "${py[@]}" -c 'import json,sys;print(json.load(sys.stdin)["route_transaction_id"])')"
[ "$old_transaction" != "$rebound_transaction" ] || fail "binding generation reused the route transaction identity"
route controller-cheap session-cheap G0002 check --request "$cheap_request" >/dev/null
cp -R "$tmp/host-store" "$tmp/host-store-before-ambiguity"
"${py[@]}" - "$tmp/host-store" <<'PY'
import hashlib,json,sys
from pathlib import Path
store=Path(sys.argv[1])
key=hashlib.sha256(b"codex\0session-cheap").hexdigest()
target=store/"bindings"/key[:2]/key/"binding.json"
value=json.loads(target.read_text(encoding="utf-8"))
value["records"][0]["status"]="ACTIVE"
value["records"][0]["supersession_or_tombstone_reason"]=None
target.write_text(json.dumps(value,sort_keys=True,separators=(",",":"))+"\n",encoding="utf-8",newline="\n")
PY
expect_observe_blocked "ambiguous H0 binding population" controller-cheap session-cheap G0002 >/dev/null
rm -rf "$tmp/host-store"
mv "$tmp/host-store-before-ambiguity" "$tmp/host-store"
observe controller-cheap session-cheap G0002 >/dev/null
current_action_oid="$rebound_oid"
for class in PURE_BOUNDED_READ_OR_VALIDATION MECHANICAL_CURRENTNESS_ACTION EXACT_PACKAGE_OR_TOPOLOGY_VERIFICATION SAFE_STATUS_OR_CONTAINMENT EXACT_ALREADY_BOUND_DETERMINISTIC_ACTION; do
  consume_request="$tmp/consume-$class.json"
  write_request "$consume_request" "$class"
  consume_decide="$(route controller-cheap session-cheap G0002 decide --request "$consume_request" --expected-record "$current_action_oid")"
  consume_decide_oid="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$consume_decide")"
  route controller-cheap session-cheap G0002 check --request "$consume_request" >/dev/null
  consumed="$(route controller-cheap session-cheap G0002 consume --request "$consume_request" --expected-record "$consume_decide_oid")"
  current_action_oid="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$consumed")"
  assert_json "$consumed" "value[\"status\"] == \"ACTION_COMPLETE\" and value[\"decision\"] == \"PENDING\" and value[\"advance_allowed\"] is False and value[\"action_executed\"] is True and value[\"action_result\"][\"exit_code\"] == 0 and value[\"consumed_record_oid\"] == \"$consume_decide_oid\""
  expect_blocked "completed $class action cannot replay" route controller-cheap session-cheap G0002 check --request "$consume_request" >/dev/null
done
consumed_oid="$current_action_oid"

# A process loss after admission consumption but before action completion must
# leave canonical PENDING/action-in-progress, never reusable NOT_REQUIRED.
truncate -s 268435456 "$tmp/repo/process-loss.bin"
loss_request="$tmp/process-loss.json"
write_request "$loss_request" EXACT_ALREADY_BOUND_DETERMINISTIC_ACTION
mutate_request "$loss_request" "$loss_request.next" 'value["action"]["argv"]=["sha256sum","process-loss.bin"]; value["action"]["digest"]=h({"identity":value["action"]["identity"],"class":value["action"]["class"],"argv":value["action"]["argv"]}); value["inputs"]=[{"identity":"input:repository","path":"process-loss.bin","digest":file_hash(repo+"/process-loss.bin")}]'
mv "$loss_request.next" "$loss_request"
loss_decide="$(route controller-cheap session-cheap G0002 decide --request "$loss_request" --expected-record "$consumed_oid")"
loss_decide_oid="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$loss_decide")"
(
  cd "$tmp/repo"
  exec "${py[@]}" "$core" consume --request "$loss_request" --expected-record "$loss_decide_oid" \
    --controller controller-cheap --store "$tmp/host-store" --host-id codex \
    --host-session-id session-cheap --binding-generation G0002
) >"$tmp/process-loss.out" 2>&1 &
loss_pid=$!
in_progress_oid=''
for _ in $(seq 1 1000); do
  candidate_oid="$(git -C "$tmp/repo" rev-parse --verify refs/implementaudit/route-decisions/controller-cheap)"
  candidate_blob="$(git -C "$tmp/repo" cat-file blob "$candidate_oid")"
  if assert_json "$candidate_blob" 'value["decision"] == "PENDING" and value["invalidators"] == ["action-in-progress"]' >/dev/null 2>&1; then
    in_progress_oid="$candidate_oid"
    kill -KILL "$loss_pid"
    break
  fi
  sleep 0.01
done
[ -n "$in_progress_oid" ] || fail "action-in-progress CAS was not observable before exact action completion"
set +e
wait "$loss_pid" 2>/dev/null
loss_status=$?
set -e
[ "$loss_status" -ne 0 ] || fail "process-loss control did not terminate the consumer"
[ "$(git -C "$tmp/repo" rev-parse refs/implementaudit/route-decisions/controller-cheap)" = "$in_progress_oid" ] || fail "process loss did not preserve canonical action-in-progress"
expect_blocked "process-loss action cannot replay" route controller-cheap session-cheap G0002 check --request "$loss_request" >/dev/null
expect_blocked "process-loss action cannot be re-minted" route controller-cheap session-cheap G0002 decide --request "$loss_request" --expected-record "$in_progress_oid" >/dev/null
assert_json "$required_check" 'value["advance_allowed"] is False'
expect_blocked "STATE pending cannot override required" route controller-history session-history G0001 check --request "$history_request" >/dev/null
assert_json "$required_blob" 'value["expires_on"] and "scope-expansion" in value["expires_on"] and "continuity-receipt-change" in value["expires_on"]'
assert_json "$judgement_decide" 'value["record_oid"] and value["decision"] == "REQUIRED"'

# G01-G16/G25/G35/G36/G40: exercise the closed child map through four fresh
# controller/run/receipt/binding lifecycles.  Every cross-target packet must
# fail before OPEN, while each sole mapped child must resolve and load its exact
# bytes, emit one bounded route statement, return only to the governor, and
# reach final request-free admission only after the one governor decision.
run_governed_child_case() {
  local case_id="$1" claim_local="$2" reason="$3" child="$4" visible_reason="$5"
  local successor_boundary="$6" successor_event="${case_id,,}-successor-boundary"
  local successor_mode="${7:-REQUIRED}"
  local package_mode="${8:-CURRENT_PACKAGE}"
  local rotation_mode="${9:-ONE_ROTATION}" first_rotation_event="$successor_event"
  local controller="controller-${case_id,,}" session="session-${case_id,,}"
  local run_name="${case_id,,}-ABC123" request="$tmp/${case_id,,}-request.json"
  local root="$repo_custody/.IMPLEMENTAUDIT/runs/$run_name" receipt decided required_record
  local ROUTE_CORE="${ROUTE_CORE_OVERRIDE:-$core}"
  local ACTIVE_CLAIM="${ROUTE_CLAIM_OVERRIDE:-$claim}"
  local package_source="${ROUTE_PACKAGE_SOURCE:-$repo_root/skills}"
  local package_root="$package_source" package_old_parent package_new_parent package_old package_new package_old_identity_json
  local obligation transaction attributed correlation target wrong_packet wrong_visible
  local wrong_output wrong_status packet returned_artifact decision_artifact opened open_record
  local open_visible returned_result return_record completed_result complete_record admitted
  local terminal_again same_current_request successor_receipt intermediate_receipt successor_request successor_decided
  local successor_required successor_obligation successor_transaction successor_attributed
  local successor_correlation successor_packet successor_return successor_decision successor_opened
  local successor_open_record successor_visible successor_returned successor_return_record
  local successor_completed successor_complete_record first_terminal_blob successor_required_blob successor_status
  local successor_generation=G0002

  if [ "$package_mode" = "PACKAGE_RELOCATED" ]; then
    package_old_parent="$tmp/${case_id,,}-package-old"
    package_new_parent="$tmp/${case_id,,}-package-new"
    mkdir -p "$package_old_parent" "$package_new_parent"
    cp -R "$package_source" "$package_old_parent/"
    cp -R "$package_source" "$package_new_parent/"
    package_old="$package_old_parent/skills"
    package_new="$package_new_parent/skills"
    ROUTE_CORE="$package_old/implementaudit/scripts/route-transaction.py"
    ACTIVE_CLAIM="$package_old/implementaudit/scripts/claim-run.sh"
    package_root="$package_old"
    package_old_identity_json="$("${py[@]}" -c 'import json,sys; from pathlib import Path; print(json.dumps(str(Path(sys.argv[1]).resolve())))' "$package_old/$child/SKILL.md")"
  fi

  receipt="$(make_run "$controller" "$run_name" "$claim_local" exact-boundary-event)"
  bind_host "$session" "$controller" "$claim_local" "$root" "$receipt" "activation-${case_id,,}"
  write_request "$request" PURE_BOUNDED_READ_OR_VALIDATION "$reason"
  set +e
  decided="$(route "$controller" "$session" G0001 decide --request "$request" --expected-record none 2>&1)"
  successor_status=$?
  set -e
  [ "$successor_status" -eq 0 ] || {
    printf 'route-obligation-contract.test: %s initial relocated-package setup failed: %s\n' "$case_id" "$decided" >&2
    exit 1
  }
  assert_json "$decided" 'value["decision"] == "REQUIRED" and value["route_state"] == "UNSATISFIED"'
  required_record="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$decided")"
  obligation="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["obligation_id"])' "$decided")"
  transaction="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["route_transaction_id"])' "$decided")"
  attributed="$(host validate-event --host-id codex --host-session-id "$session" \
    --binding-generation G0001 --controller-id "$controller" --claim-id "$claim_local" \
    --explicit-run-root "$root" --repository-identity "$repo_custody" \
    --git-common-directory-identity "$common_custody" --worktree-identity "$repo_custody" \
    --continuity-generation G0001 --continuity-receipt "$receipt" \
    --event-id "host:$case_id" --obligation-id "$obligation" \
    --route-transaction-id "$transaction")"
  correlation="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["correlation_id"])' "$attributed")"

  for target in audit-state audit-assess audit-implement audit-andon; do
    [ "$target" != "$child" ] || continue
    wrong_packet="$tmp/${case_id,,}-wrong-$target.json"
    "${py[@]}" - "$wrong_packet" "$obligation" "$transaction" "$correlation" "$case_id" "$target" <<'PY'
import hashlib,json,sys
path,obligation,transaction,correlation,event_id,target=sys.argv[1:]
value={
 "schema":"implementaudit.route-packet.v1","obligation_id":obligation,
 "route_transaction_id":transaction,"target_identity":target,
 "source_event":{"schema":"implementaudit.source-event.v1","source_identity":"host:"+event_id,
  "provenance":{"schema":"implementaudit.source-event-provenance.v1","event_id":"host:"+event_id,
   "host_correlation_id":correlation},"body":"cross-target refusal","kind":"one-shot-action",
  "reactivation":{"reopen":False,"target_changed":False,"invalidating_evidence":False}},
}

with open(path,"w",encoding="utf-8",newline="\n") as handle:
 json.dump(value,handle,sort_keys=True,separators=(",",":")); handle.write("\n")
PY
    wrong_visible="$tmp/${case_id,,}-wrong-$target.visible"
    set +e
    wrong_output="$(route "$controller" "$session" G0001 open --request "$request" \
      --expected-record "$required_record" --packet "$wrong_packet" 2>"$wrong_visible")"
    wrong_status=$?
    set -e
    [ "$wrong_status" -ne 0 ] || fail "$case_id cross-target $target reached OPEN"
    assert_json "$wrong_output" 'value["advance_allowed"] is False and value["enforcement_available"] is False'
    [ ! -s "$wrong_visible" ] || fail "$case_id cross-target $target emitted a route statement"
    [ "$(git -C "$tmp/repo" rev-parse "refs/implementaudit/route-decisions/$controller")" = "$required_record" ] ||
      fail "$case_id cross-target $target changed canonical route state"
  done

  packet="$tmp/${case_id,,}-packet.json"
  returned_artifact="$tmp/${case_id,,}-return.json"
  decision_artifact="$tmp/${case_id,,}-decision.json"
  "${py[@]}" - "$packet" "$returned_artifact" "$decision_artifact" "$obligation" \
    "$transaction" "$correlation" "$case_id" "$child" <<'PY'
import hashlib,json,sys
packet_path,return_path,decision_path,obligation,transaction,correlation,event_id,target=sys.argv[1:]
def write(path,value):
 raw=(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()
 open(path,"wb").write(raw)
 return "sha256:"+hashlib.sha256(raw).hexdigest()
packet={
 "schema":"implementaudit.route-packet.v1","obligation_id":obligation,
 "route_transaction_id":transaction,"target_identity":target,
 "source_event":{"schema":"implementaudit.source-event.v1","source_identity":"host:"+event_id,
  "provenance":{"schema":"implementaudit.source-event-provenance.v1","event_id":"host:"+event_id,
   "host_correlation_id":correlation},"body":"perform the mapped governed child once",
  "kind":"one-shot-action","reactivation":{"reopen":False,"target_changed":False,
   "invalidating_evidence":False}},
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

  expect_blocked "$case_id admitted before OPEN" route "$controller" "$session" G0001 admit-current >/dev/null
  open_visible="$tmp/${case_id,,}-open.visible"
  opened="$(route "$controller" "$session" G0001 open --request "$request" \
    --expected-record "$required_record" --packet "$packet" 2>"$open_visible")"
  assert_json "$opened" 'value["status"] == "CHILD_OPEN" and value["route_state"] == "OPEN"'
  open_record="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$opened")"
  "${py[@]}" - "$opened" "$package_root/$child/SKILL.md" "$child" <<'PY'
import base64,json,sys
from pathlib import Path
value=json.loads(sys.argv[1]); expected=open(sys.argv[2],"rb").read()
delivery=value["delivery"]["child"]
if Path(delivery["identity"]).resolve() != Path(sys.argv[2]).resolve() or base64.b64decode(delivery["bytes_b64"]) != expected:
 raise SystemExit("mapped child resolver/load bytes disagree")
PY
  mapfile -t open_visible_lines < "$open_visible"
  [ "${#open_visible_lines[@]}" -eq 2 ] || fail "$case_id did not emit exactly one two-line route"
  [ "${open_visible_lines[0]: -1}" != $'\r' ] || open_visible_lines[0]="${open_visible_lines[0]%$'\r'}"
  [ "${open_visible_lines[1]: -1}" != $'\r' ] || open_visible_lines[1]="${open_visible_lines[1]%$'\r'}"
  [ "${open_visible_lines[0]}" = "CHILD_SKILL_ROUTE=$child" ] || fail "$case_id emitted the wrong child identity"
  [ "${open_visible_lines[1]}" = "I'm using $child to $visible_reason." ] || fail "$case_id emitted the wrong bounded reason"
  expect_blocked "$case_id OPEN/process-loss state admitted" route "$controller" "$session" G0001 admit-current >/dev/null

  returned_result="$(route "$controller" "$session" G0001 return --request "$request" \
    --expected-record "$open_record" --return "$returned_artifact")"
  assert_json "$returned_result" 'value["status"] == "CHILD_RETURNED" and value["route_state"] == "RETURNED" and value["advance_allowed"] is False'
  return_record="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$returned_result")"
  expect_blocked "$case_id child-to-child payload bypassed governor" route "$controller" "$session" G0001 admit-current >/dev/null
  completed_result="$(route "$controller" "$session" G0001 complete --request "$request" \
    --expected-record "$return_record" --packet "$packet" --return "$returned_artifact" \
    --decision "$decision_artifact")"
  assert_json "$completed_result" 'value["status"] == "ROUTE_COMPLETE" and value["route_state"] == "SATISFIED" and value["governor_decision_count"] == 1'
  complete_record="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$completed_result")"
  admitted="$(cd "$tmp/repo" && bash "$ACTIVE_CLAIM" --require-current-route "$controller" \
    --store "$tmp/host-store" --host-id codex --host-session-id "$session" \
    --binding-generation G0001)"
  assert_json "$admitted" 'value["decision"] == "REQUIRED" and value["route_state"] == "SATISFIED" and value["advance_allowed"] is True'
  [ "$(git -C "$tmp/repo" rev-parse "refs/implementaudit/route-decisions/$controller")" = "$complete_record" ] ||
    fail "$case_id final admission changed canonical route state"

  # A terminal lifecycle is idempotent only for its exact current boundary.
  # A distinct request in the same currentness cannot replace it.
  terminal_again="$(route "$controller" "$session" G0001 decide --request "$request" \
    --expected-record "$complete_record")"
  assert_json "$terminal_again" 'value["idempotent"] is True and value["record_oid"] == "'"$complete_record"'" and value["route_state"] == "SATISFIED"'
  same_current_request="$tmp/${case_id,,}-same-currentness.json"
  mutate_request "$request" "$same_current_request" \
    'value["boundary"]={"kind":"new-session","event_id":"same-currentness-'"${case_id,,}"'"}; value["boundary"]["digest"]=h(value["boundary"])'
  expect_blocked "$case_id same currentness cannot replace terminal route" \
    route "$controller" "$session" G0001 decide --request "$same_current_request" \
      --expected-record "$complete_record" >/dev/null

  # Rotate the same controller/claim/run/session through the exact next
  # continuity and binding generation. The successor boundary is distinct and
  # must mint a fresh immutable REQUIRED/UNSATISFIED transaction whose direct
  # predecessor is the preserved first terminal record.
  first_terminal_blob="$(git -C "$tmp/repo" cat-file blob "$complete_record")"
  if [ "$package_mode" = "PACKAGE_RELOCATED" ]; then
    assert_json "$first_terminal_blob" 'value["lifecycle"]["delivery"]["child"]["identity"] == '"$package_old_identity_json"
  fi
  if [ "$rotation_mode" = "TWO_ROTATIONS" ]; then
    first_rotation_event="${case_id,,}-intermediate-boundary"
  fi
  successor_receipt="$(promote_to_v3 "$controller" "$claim_local" "$root" "$run_name" \
    "$first_rotation_event" "$successor_boundary")"
  intermediate_receipt="$successor_receipt"
  if [ "$rotation_mode" = "TWO_ROTATIONS" ]; then
    host rebind --owner-id host-owner --host-id codex --host-session-id "$session" \
      --expected-generation G0001 --reason terminal-route-intermediate-rotation \
      --controller-id "$controller" --claim-id "$claim_local" --explicit-run-root "$root" \
      --repository-identity "$tmp/repo" --git-common-directory-identity "$tmp/repo/.git" \
      --worktree-identity "$tmp/repo" --activation-event-id "activation-${case_id,,}-g2" \
      --activation-receipt "activation-${case_id,,}-g2" --continuity-generation G0002 \
      --continuity-receipt "$intermediate_receipt" >/dev/null
    successor_receipt="$(promote_v3_next "$controller" "$claim_local" "$root" "$run_name" \
      "$successor_event" "$successor_boundary" G0002 G0003)"
    successor_generation=G0003
  fi
  successor_request="$tmp/${case_id,,}-successor-request.json"
  if [ "$successor_mode" = "NOT_REQUIRED" ]; then
    mutate_request "$request" "$successor_request" \
      'value["boundary"]={"kind":"'"$successor_boundary"'","event_id":"'"$successor_event"'"}; value["boundary"]["digest"]=h(value["boundary"]); value["action"]={"identity":"action:successor-not-required","class":"PURE_BOUNDED_READ_OR_VALIDATION","argv":["route-read-snapshot"]}; value["action"]["digest"]=h(value["action"])'
  else
    mutate_request "$request" "$successor_request" \
      'value["boundary"]={"kind":"'"$successor_boundary"'","event_id":"'"$successor_event"'"}; value["boundary"]["digest"]=h(value["boundary"])'
  fi
  expect_blocked "$case_id stale predecessor binding cannot replace terminal route" \
    route "$controller" "$session" G0001 decide --request "$successor_request" \
      --expected-record "$complete_record" >/dev/null
  expect_blocked "$case_id absent successor binding cannot replace terminal route" \
    route "$controller" "$session" "$successor_generation" decide --request "$successor_request" \
      --expected-record "$complete_record" >/dev/null
  if [ "$rotation_mode" = "TWO_ROTATIONS" ]; then
    expect_blocked "$case_id intermediate binding cannot authorize the later continuity" \
      route "$controller" "$session" G0002 decide --request "$successor_request" \
        --expected-record "$complete_record" >/dev/null
    host rebind --owner-id host-owner --host-id codex --host-session-id "$session" \
      --expected-generation G0002 --reason terminal-route-successor \
      --controller-id "$controller" --claim-id "$claim_local" --explicit-run-root "$root" \
      --repository-identity "$tmp/repo" --git-common-directory-identity "$tmp/repo/.git" \
      --worktree-identity "$tmp/repo" --activation-event-id "activation-${case_id,,}-g3" \
      --activation-receipt "activation-${case_id,,}-g3" --continuity-generation G0003 \
      --continuity-receipt "$successor_receipt" >/dev/null
  else
    host rebind --owner-id host-owner --host-id codex --host-session-id "$session" \
      --expected-generation G0001 --reason terminal-route-successor \
      --controller-id "$controller" --claim-id "$claim_local" --explicit-run-root "$root" \
      --repository-identity "$tmp/repo" --git-common-directory-identity "$tmp/repo/.git" \
      --worktree-identity "$tmp/repo" --activation-event-id "activation-${case_id,,}-g2" \
      --activation-receipt "activation-${case_id,,}-g2" --continuity-generation G0002 \
      --continuity-receipt "$successor_receipt" >/dev/null
  fi
  expect_blocked "$case_id skipped binding generation cannot replace terminal route" \
    route "$controller" "$session" "G$(printf '%04X' "$((16#${successor_generation#G} + 1))")" decide --request "$successor_request" \
      --expected-record "$complete_record" >/dev/null

  # Supported replacement keeps the exact child bytes at a distinct installed
  # package root, while the predecessor's historical delivery path vanishes.
  # The unchanged implementation must fail closed before successor child OPEN.
  if [ "$package_mode" = "PACKAGE_RELOCATED" ]; then
    cmp -s "$package_old/$child/SKILL.md" "$package_new/$child/SKILL.md" ||
      fail "$case_id replacement package changed the governed child bytes"
    rm -rf -- "$package_old"
    [ ! -e "$package_old/$child/SKILL.md" ] ||
      fail "$case_id predecessor package path remained available after replacement"
    ROUTE_CORE="$package_new/implementaudit/scripts/route-transaction.py"
    ACTIVE_CLAIM="$package_new/implementaudit/scripts/claim-run.sh"
    package_root="$package_new"
  fi

  expect_blocked "$case_id foreign current session binding cannot replace terminal route" \
    route "$controller" "${session}-foreign" "$successor_generation" decide \
      --request "$successor_request" --expected-record "$complete_record" >/dev/null
  expect_blocked "$case_id stale route CAS cannot replace terminal route" \
    route "$controller" "$session" "$successor_generation" decide \
      --request "$successor_request" --expected-record "$required_record" >/dev/null

  if [ "$package_mode" = "PACKAGE_RELOCATED" ]; then
    mv "$package_new/$child/SKILL.md" "$package_new/$child/SKILL.md.missing-heldout"
    expect_blocked "$case_id missing current child cannot replace terminal route" \
      route "$controller" "$session" "$successor_generation" decide \
        --request "$successor_request" --expected-record "$complete_record" >/dev/null
    mv "$package_new/$child/SKILL.md.missing-heldout" "$package_new/$child/SKILL.md"
    cp "$package_new/$child/SKILL.md" "$package_new/$child/SKILL.md.changed-heldout"
    printf '\nR0033 changed-child held-out\n' >> "$package_new/$child/SKILL.md"
    expect_blocked "$case_id changed current child cannot replace terminal route" \
      route "$controller" "$session" "$successor_generation" decide \
        --request "$successor_request" --expected-record "$complete_record" >/dev/null
    mv "$package_new/$child/SKILL.md.changed-heldout" "$package_new/$child/SKILL.md"
  fi

  if [ "$rotation_mode" = "TWO_ROTATIONS" ]; then
    # These canonical proxy records must traverse terminal `decide`, the only
    # command that enables immutable historical custody.  The old package path
    # is already absent, while the equal-byte current child remains available.
    "${py[@]}" - "$tmp/repo" "$complete_record" "$tmp/${case_id,,}-terminal-tamper" <<'PY'
import base64
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

repo, source_oid, output_prefix = sys.argv[1:]
source = json.loads(subprocess.check_output(["git", "-C", repo, "cat-file", "blob", source_oid]))

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")

def digest(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()

def finish(name, value):
    base = {key: member for key, member in value.items() if key != "record_identity"}
    value["record_identity"] = digest(canonical(base))
    Path(f"{output_prefix}-{name}.json").write_bytes(canonical(value) + b"\n")

changed_bytes = copy.deepcopy(source)
child = changed_bytes["lifecycle"]["delivery"]["child"]
raw = base64.b64decode(child["bytes_b64"], validate=True) + b"\nM1 immutable child mutation"
child["bytes_b64"] = base64.b64encode(raw).decode("ascii")
child["digest"] = digest(raw)
changed_bytes["child_source"]["digest"] = child["digest"]
finish("bytes", changed_bytes)

changed_digest = copy.deepcopy(source)
changed_digest["lifecycle"]["delivery"]["child"]["digest"] = "sha256:" + "0" * 64
finish("digest", changed_digest)

changed_source = copy.deepcopy(source)
foreign_identity = changed_source["child_source"]["identity"] + "-foreign"
changed_source["child_source"]["identity"] = foreign_identity
changed_source["lifecycle"]["delivery"]["child"]["identity"] = foreign_identity
finish("source", changed_source)
PY
    for terminal_tamper in bytes digest source; do
      proxy_oid="$(git -C "$tmp/repo" hash-object -w "$tmp/${case_id,,}-terminal-tamper-$terminal_tamper.json")"
      git -C "$tmp/repo" update-ref "refs/implementaudit/route-decisions/$controller" "$proxy_oid" "$complete_record"
      expect_blocked "$case_id immutable terminal child $terminal_tamper tamper cannot re-enter" \
        route "$controller" "$session" "$successor_generation" decide \
          --request "$successor_request" --expected-record "$proxy_oid" >/dev/null
      [ "$(git -C "$tmp/repo" rev-parse "refs/implementaudit/route-decisions/$controller")" = "$proxy_oid" ] ||
        fail "$case_id immutable terminal child $terminal_tamper tamper changed the route ref"
      git -C "$tmp/repo" update-ref "refs/implementaudit/route-decisions/$controller" "$complete_record" "$proxy_oid"
    done

    "${py[@]}" - "$ROUTE_CORE" "$tmp/repo" "$complete_record" \
      "$successor_receipt" "$intermediate_receipt" "$controller" "$claim_local" "$run_name" <<'PY'
import contextlib
import importlib.util
import io
import json
import os
import subprocess
import sys
from pathlib import Path

core_path, repo_arg, terminal_record_oid, current_token, intermediate_token, controller, claim, run_name = sys.argv[1:]
repo = Path(repo_arg)
spec = importlib.util.spec_from_file_location("route_transaction_r0033", core_path)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

def git(*args, data=None, check=True):
    completed = subprocess.run(
        ["git", "-C", str(repo), *args], input=data, capture_output=True, check=False
    )
    if check and completed.returncode:
        raise AssertionError(completed.stderr.decode("utf-8", "replace"))
    return completed.stdout

def oid_for(data):
    return git("hash-object", "-w", "--stdin", data=data).decode("ascii").strip()

def ref_oid(ref):
    return git("rev-parse", "--verify", ref).decode("ascii").strip()

def update_ref(ref, oid, old=None):
    args = ["update-ref", ref, oid]
    if old is not None:
        args.append(old)
    git(*args)

def invoke(generation, receipt):
    module.validate_terminal_continuity_chain(
        repo,
        controller=controller,
        claim=claim,
        run_identity=run_name,
        terminal_generation=terminal_generation,
        terminal_receipt=terminal_token,
        current_generation=generation,
        current_receipt=receipt,
    )

def expect_failure(label, generation, receipt, expected_error=None):
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            invoke(generation, receipt)
    except SystemExit as exc:
        if exc.code != 2:
            raise AssertionError(f"{label}: wrong exit {exc.code}")
    else:
        raise AssertionError(f"{label}: malformed lineage was accepted")
    rendered = output.getvalue().strip()
    try:
        result = json.loads(rendered)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"{label}: failure was not one JSON object: {rendered!r}") from exc
    if result.get("status") != "UNAVAILABLE" or result.get("advance_allowed") is not False:
        raise AssertionError(f"{label}: failure was not fail-closed: {result!r}")
    if expected_error is not None and result.get("error") != expected_error:
        raise AssertionError(f"{label}: wrong predicate failed: {result!r}")
    if "Traceback" in rendered:
        raise AssertionError(f"{label}: traceback escaped")

terminal_record = json.loads(git("cat-file", "blob", terminal_record_oid))
terminal_generation = terminal_record["continuity_generation"]
terminal_token = terminal_record["continuity_receipt"]
current_ref, current_oid = current_token.split("@")
intermediate_ref, intermediate_oid = intermediate_token.split("@")
current_raw = git("cat-file", "blob", current_oid)
intermediate_raw = git("cat-file", "blob", intermediate_oid)

# Positive control: the exact live-equivalent two-rotation chain is accepted.
invoke("G0003", current_token)

# Compatibility control: the original exact-next rule accepts an exact
# canonical one-generation v2 receipt without applying the v3-chain grammar.
terminal_raw = git("cat-file", "blob", terminal_token.split("@")[1])
terminal_fields = terminal_raw.rstrip(b"\n").decode("utf-8").split("\t")
if len(terminal_fields) != 12 or terminal_fields[0] != "implementaudit.continuity-receipt.v2":
    raise AssertionError("exact-next v2 positive control requires the canonical v2 terminal fixture")
v2_fields = list(terminal_fields)
v2_fields[9] = "manual-resume"
v2_fields[10] = "G0002"
v2_fields[11] = "exact-next-v2-positive-control"
v2_raw = ("\t".join(v2_fields) + "\n").encode("utf-8")
v2_oid = oid_for(v2_raw)
update_ref(intermediate_ref, v2_oid, intermediate_oid)
try:
    invoke("G0002", f"{intermediate_ref}@{v2_oid}")
finally:
    update_ref(intermediate_ref, intermediate_oid, v2_oid)

git("update-ref", "-d", intermediate_ref, intermediate_oid)
try:
    expect_failure("missing intermediate ref", "G0003", current_token)
finally:
    update_ref(intermediate_ref, intermediate_oid)

objects_dir = Path(git("rev-parse", "--git-path", "objects").decode().strip())
if not objects_dir.is_absolute():
    objects_dir = repo / objects_dir
loose_object = objects_dir / intermediate_oid[:2] / intermediate_oid[2:]
held_object = loose_object.with_name(loose_object.name + ".r0033-heldout")
if not loose_object.is_file():
    raise AssertionError("missing-blob held-out requires the freshly written loose intermediate blob")
os.replace(loose_object, held_object)
try:
    expect_failure("missing intermediate blob", "G0003", current_token)
finally:
    os.replace(held_object, loose_object)

malformed_oid = oid_for(intermediate_raw[:-1] + b"\r\n")
update_ref(intermediate_ref, malformed_oid, intermediate_oid)
malformed_current_fields = current_raw[:-1].decode("utf-8").split("\t")
malformed_current_fields[17] = f"{intermediate_ref}@{malformed_oid}"
malformed_current_oid = oid_for(("\t".join(malformed_current_fields) + "\n").encode("utf-8"))
update_ref(current_ref, malformed_current_oid, current_oid)
try:
    expect_failure("noncanonical intermediate bytes", "G0003", f"{current_ref}@{malformed_current_oid}")
finally:
    update_ref(current_ref, current_oid, malformed_current_oid)
    update_ref(intermediate_ref, intermediate_oid, malformed_oid)

current_fields = current_raw[:-1].decode("utf-8").split("\t")
current_fields[17] = terminal_token
noncontiguous_raw = ("\t".join(current_fields) + "\n").encode("utf-8")
noncontiguous_oid = oid_for(noncontiguous_raw)
update_ref(current_ref, noncontiguous_oid, current_oid)
try:
    expect_failure("noncontiguous predecessor", "G0003", f"{current_ref}@{noncontiguous_oid}")
finally:
    update_ref(current_ref, current_oid, noncontiguous_oid)

terminal_ref, terminal_oid = terminal_token.split("@")
fork_terminal_oid = oid_for(b"R0033 canonical fork terminal object\n")
fork_terminal_token = f"{terminal_ref}@{fork_terminal_oid}"
fork_fields = intermediate_raw[:-1].decode("utf-8").split("\t")
fork_fields[17] = fork_terminal_token
fork_oid = oid_for(("\t".join(fork_fields) + "\n").encode("utf-8"))
fork_current_fields = current_raw[:-1].decode("utf-8").split("\t")
fork_current_fields[17] = f"{intermediate_ref}@{fork_oid}"
fork_current_oid = oid_for(("\t".join(fork_current_fields) + "\n").encode("utf-8"))
update_ref(terminal_ref, fork_terminal_oid, terminal_oid)
update_ref(intermediate_ref, fork_oid, intermediate_oid)
update_ref(current_ref, fork_current_oid, current_oid)
try:
    expect_failure(
        "predecessor field fork",
        "G0003",
        f"{current_ref}@{fork_current_oid}",
        "continuity receipt chain does not reach the terminal route receipt",
    )
finally:
    update_ref(current_ref, current_oid, fork_current_oid)
    update_ref(intermediate_ref, intermediate_oid, fork_oid)
    update_ref(terminal_ref, terminal_oid, fork_terminal_oid)

for field_index, label in ((1, "foreign controller"), (2, "foreign claim"), (3, "foreign run")):
    foreign_fields = intermediate_raw[:-1].decode("utf-8").split("\t")
    foreign_fields[field_index] += "-foreign"
    foreign_oid = oid_for(("\t".join(foreign_fields) + "\n").encode("utf-8"))
    update_ref(intermediate_ref, foreign_oid, intermediate_oid)
    foreign_current_fields = current_raw[:-1].decode("utf-8").split("\t")
    foreign_current_fields[17] = f"{intermediate_ref}@{foreign_oid}"
    foreign_current_oid = oid_for(("\t".join(foreign_current_fields) + "\n").encode("utf-8"))
    update_ref(current_ref, foreign_current_oid, current_oid)
    try:
        expect_failure(label, "G0003", f"{current_ref}@{foreign_current_oid}")
    finally:
        update_ref(current_ref, current_oid, foreign_current_oid)
        update_ref(intermediate_ref, intermediate_oid, foreign_oid)

expect_failure("same generation", terminal_generation, terminal_token)
expect_failure("backward generation", "G0000", "refs/implementaudit/continuity-receipts/%s/G0000@%s" % (controller, "0" * 40))
PY
  fi

  if [ "$rotation_mode" = "TWO_ROTATIONS" ]; then
    local race_core_backup="$tmp/${case_id,,}-route-core-before-race.py"
    local race_barrier="$tmp/${case_id,,}-lineage-race" race_output="$tmp/${case_id,,}-lineage-race.out"
    local terminal_receipt terminal_ref terminal_oid race_foreign_oid race_pid race_status race_result
    cp "$ROUTE_CORE" "$race_core_backup"
    "${py[@]}" - "$ROUTE_CORE" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
source = path.read_text(encoding="utf-8")
needle = '''        completed = subprocess.run(
            [str(trusted_host_executable(repo, "git")), "update-ref", ref_name(args.controller), new_oid, expected_oid],
'''
if source.count(needle) != 1:
    raise SystemExit("R0033 lineage race fixture lost the unique route-decision CAS insertion point")
barrier = '''        test_barrier = os.environ.get("IMPLEMENTAUDIT_R0033_TEST_BARRIER")
        if test_barrier:
            barrier_path = Path(test_barrier)
            barrier_path.mkdir(parents=True, exist_ok=True)
            (barrier_path / "validated").touch()
            for _ in range(500):
                if (barrier_path / "release").is_file():
                    break
                time.sleep(0.02)
            else:
                raise RuntimeError("R0033 lineage race barrier timed out")
'''
path.write_text(source.replace(needle, barrier + needle), encoding="utf-8", newline="\n")
PY
    mkdir "$race_barrier"
    terminal_receipt="$(${py[@]} -c 'import json,sys; print(json.loads(sys.argv[1])["continuity_receipt"])' "$first_terminal_blob")"
    terminal_ref="${terminal_receipt%@*}"
    terminal_oid="${terminal_receipt##*@}"
    race_foreign_oid="$(printf 'R0033 terminal lineage race replacement\n' | git -C "$tmp/repo" hash-object -w --stdin)"
    set +e
    IMPLEMENTAUDIT_R0033_TEST_BARRIER="$race_barrier" \
      route "$controller" "$session" "$successor_generation" decide \
        --request "$successor_request" --expected-record "$complete_record" >"$race_output" 2>&1 &
    race_pid=$!
    set -e
    for _ in {1..500}; do
      [ -f "$race_barrier/validated" ] && break
      kill -0 "$race_pid" 2>/dev/null || break
      sleep 0.02
    done
    [ -f "$race_barrier/validated" ] || {
      wait "$race_pid" || true
      mv "$race_core_backup" "$ROUTE_CORE"
      fail "$case_id lineage race did not reach the validation-to-CAS barrier"
    }
    git -C "$tmp/repo" update-ref "$terminal_ref" "$race_foreign_oid" "$terminal_oid"
    : > "$race_barrier/release"
    set +e
    wait "$race_pid"
    race_status=$?
    set -e
    git -C "$tmp/repo" update-ref "$terminal_ref" "$terminal_oid" "$race_foreign_oid"
    mv "$race_core_backup" "$ROUTE_CORE"
    race_result="$(<"$race_output")"
    [ "$race_status" -ne 0 ] ||
      fail "$case_id lineage validation-to-CAS race returned advancement authority"
    assert_json "$race_result" 'value["status"] == "UNAVAILABLE" and value["advance_allowed"] is False and value["enforcement_available"] is False'
    [ "$(git -C "$tmp/repo" rev-parse "refs/implementaudit/route-decisions/$controller")" = "$complete_record" ] ||
      fail "$case_id lineage validation-to-CAS race was not exactly compensated"
  fi

  set +e
  successor_decided="$(route "$controller" "$session" "$successor_generation" decide --request "$successor_request" \
    --expected-record "$complete_record" 2>&1)"
  successor_status=$?
  set -e
  if [ "$successor_status" -ne 0 ]; then
    printf 'route-obligation-contract.test: terminal-route re-entry causal RED: %s\n' "$successor_decided" >&2
    exit 1
  fi
  if [ "$successor_mode" = "NOT_REQUIRED" ]; then
    assert_json "$successor_decided" 'value["decision"] == "NOT_REQUIRED" and value["obligation_id"] is None and value["route_state"] is None and value["predecessor_record_oid"] == "'"$complete_record"'"'
    successor_required="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$successor_decided")"
    successor_required_blob="$(git -C "$tmp/repo" cat-file blob "$successor_required")"
    assert_json "$successor_required_blob" 'value["child_lifecycle_owned"] is False and "lifecycle" not in value and value["child_source"]["identity"] == "R0033:NOT_REQUIRED:NO_CHILD"'
    [ "$(git -C "$tmp/repo" cat-file blob "$complete_record")" = "$first_terminal_blob" ] ||
      fail "$case_id NOT_REQUIRED successor mutated the first terminal record"
    return
  fi
  assert_json "$successor_decided" 'value["decision"] == "REQUIRED" and value["route_state"] == "UNSATISFIED" and value["predecessor_record_oid"] == "'"$complete_record"'" and not value.get("idempotent", False)'
  successor_required="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$successor_decided")"
  successor_obligation="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["obligation_id"])' "$successor_decided")"
  successor_transaction="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["route_transaction_id"])' "$successor_decided")"
  successor_required_blob="$(git -C "$tmp/repo" cat-file blob "$successor_required")"
  assert_json "$successor_required_blob" 'value["predecessor_record_oid"] == "'"$complete_record"'" and value["child_lifecycle_owned"] is False and "lifecycle" not in value and value["continuity_generation"] == "'"$successor_generation"'"'
  [ "$(git -C "$tmp/repo" cat-file blob "$complete_record")" = "$first_terminal_blob" ] ||
    fail "$case_id successor decision mutated the first terminal record"

  successor_attributed="$(host validate-event --host-id codex --host-session-id "$session" \
    --binding-generation "$successor_generation" --controller-id "$controller" --claim-id "$claim_local" \
    --explicit-run-root "$root" --repository-identity "$repo_custody" \
    --git-common-directory-identity "$common_custody" --worktree-identity "$repo_custody" \
    --continuity-generation "$successor_generation" --continuity-receipt "$successor_receipt" \
    --event-id "host:$case_id:successor" --obligation-id "$successor_obligation" \
    --route-transaction-id "$successor_transaction")"
  successor_correlation="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["correlation_id"])' "$successor_attributed")"
  successor_packet="$tmp/${case_id,,}-successor-packet.json"
  successor_return="$tmp/${case_id,,}-successor-return.json"
  successor_decision="$tmp/${case_id,,}-successor-decision.json"
  "${py[@]}" - "$successor_packet" "$successor_return" "$successor_decision" \
    "$successor_obligation" "$successor_transaction" "$successor_correlation" "$case_id" "$child" <<'PY'
import hashlib,json,sys
packet_path,return_path,decision_path,obligation,transaction,correlation,event_id,target=sys.argv[1:]
def write(path,value):
 raw=(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()
 open(path,"wb").write(raw)
 return "sha256:"+hashlib.sha256(raw).hexdigest()
packet={
 "schema":"implementaudit.route-packet.v1","obligation_id":obligation,
 "route_transaction_id":transaction,"target_identity":target,
 "source_event":{"schema":"implementaudit.source-event.v1","source_identity":"host:"+event_id+":successor",
  "provenance":{"schema":"implementaudit.source-event-provenance.v1","event_id":"host:"+event_id+":successor",
   "host_correlation_id":correlation},"body":"perform the exact successor governed child once",
  "kind":"one-shot-action","reactivation":{"reopen":False,"target_changed":False,
   "invalidating_evidence":False}},
}
packet_digest=write(packet_path,packet)
returned={"schema":"implementaudit.child-return.v1","obligation_id":obligation,
 "route_transaction_id":transaction,"packet_digest":packet_digest,"status":"RETURNED",
 "payload":{"result":"bounded successor child analysis"}}
return_digest=write(return_path,returned)
decision={"schema":"implementaudit.governor-route-decision.v1","obligation_id":obligation,
 "route_transaction_id":transaction,"return_digest":return_digest,"outcome":"SATISFIED",
 "reason":"governor reconciled the exact successor child return"}
write(decision_path,decision)
PY

  successor_visible="$tmp/${case_id,,}-successor-open.visible"
  successor_opened="$(route "$controller" "$session" "$successor_generation" open --request "$successor_request" \
    --expected-record "$successor_required" --packet "$successor_packet" 2>"$successor_visible")"
  assert_json "$successor_opened" 'value["status"] == "CHILD_OPEN" and value["route_state"] == "OPEN"'
  successor_open_record="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$successor_opened")"
  "${py[@]}" - "$successor_opened" "$package_root/$child/SKILL.md" <<'PY'
import base64,json,sys
value=json.loads(sys.argv[1])
if base64.b64decode(value["delivery"]["child"]["bytes_b64"]) != open(sys.argv[2],"rb").read():
 raise SystemExit("successor mapped child bytes were not delivered")
PY
  mapfile -t successor_visible_lines < "$successor_visible"
  [ "${#successor_visible_lines[@]}" -eq 2 ] || fail "$case_id successor did not emit exactly one two-line route"
  [ "${successor_visible_lines[0]: -1}" != $'\r' ] || successor_visible_lines[0]="${successor_visible_lines[0]%$'\r'}"
  [ "${successor_visible_lines[1]: -1}" != $'\r' ] || successor_visible_lines[1]="${successor_visible_lines[1]%$'\r'}"
  [ "${successor_visible_lines[0]}" = "CHILD_SKILL_ROUTE=$child" ] || fail "$case_id successor emitted the wrong child identity"
  [ "${successor_visible_lines[1]}" = "I'm using $child to $visible_reason." ] || fail "$case_id successor emitted the wrong bounded reason"
  expect_blocked "$case_id OPEN successor cannot be replaced" \
    route "$controller" "$session" "$successor_generation" decide --request "$same_current_request" \
      --expected-record "$successor_open_record" >/dev/null

  successor_returned="$(route "$controller" "$session" "$successor_generation" return --request "$successor_request" \
    --expected-record "$successor_open_record" --return "$successor_return")"
  assert_json "$successor_returned" 'value["status"] == "CHILD_RETURNED" and value["route_state"] == "RETURNED"'
  successor_return_record="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$successor_returned")"
  expect_blocked "$case_id RETURNED successor cannot be replaced" \
    route "$controller" "$session" "$successor_generation" decide --request "$same_current_request" \
      --expected-record "$successor_return_record" >/dev/null
  successor_completed="$(route "$controller" "$session" "$successor_generation" complete --request "$successor_request" \
    --expected-record "$successor_return_record" --packet "$successor_packet" \
    --return "$successor_return" --decision "$successor_decision")"
  assert_json "$successor_completed" 'value["status"] == "ROUTE_COMPLETE" and value["route_state"] == "SATISFIED" and value["governor_decision_count"] == 1'
  successor_complete_record="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$successor_completed")"
  admitted="$(cd "$tmp/repo" && bash "$ACTIVE_CLAIM" --require-current-route "$controller" \
    --store "$tmp/host-store" --host-id codex --host-session-id "$session" \
    --binding-generation "$successor_generation")"
  assert_json "$admitted" 'value["record_oid"] == "'"$successor_complete_record"'" and value["route_state"] == "SATISFIED" and value["advance_allowed"] is True'
  [ "$(git -C "$tmp/repo" cat-file blob "$complete_record")" = "$first_terminal_blob" ] ||
    fail "$case_id second lifecycle mutated the first terminal record"
}

# G07/G08: a host-compaction successor may abandon an incomplete prior child
# lifecycle only when the same governed object advances by exactly one
# continuity generation and exactly one H0 binding generation. The immutable
# OPEN/RETURNED record remains evidence, but none of its child bytes, return,
# decision, transaction or obligation authority crosses into the fresh
# STALE_CONTEXT_RECONSTRUCTION transaction.
run_active_compaction_recovery_case() {
  local case_id="$1" active_state="$2" claim_local="$3"
  local package_mode="${4:-CURRENT_PACKAGE}"
  local controller="controller-${case_id,,}" session="session-${case_id,,}"
  local run_name="${case_id,,}-ABC123"
  local root="$repo_custody/.IMPLEMENTAUDIT/runs/$run_name"
  local ROUTE_CORE="${ROUTE_CORE_OVERRIDE:-$core}"
  local ACTIVE_CLAIM="${ROUTE_CLAIM_OVERRIDE:-$claim}"
  local package_source="${ROUTE_PACKAGE_SOURCE:-$repo_root/skills}"
  local package_root="$package_source" package_old_parent package_new_parent package_old package_new
  local old_request="$tmp/${case_id,,}-old-request.json" recovery_request="$tmp/${case_id,,}-recovery-request.json"
  local wrong_reason_request="$tmp/${case_id,,}-wrong-reason-request.json"
  local malformed_request="$tmp/${case_id,,}-malformed-request.json"
  local receipt decided required_record obligation transaction attributed correlation
  local old_packet="$tmp/${case_id,,}-old-packet.json" old_return="$tmp/${case_id,,}-old-return.json"
  local old_decision="$tmp/${case_id,,}-old-decision.json" opened open_record returned active_record active_blob
  local successor_receipt recovery_decided recovery_required recovery_obligation recovery_transaction
  local recovery_attributed recovery_correlation recovery_packet="$tmp/${case_id,,}-recovery-packet.json"
  local recovery_return="$tmp/${case_id,,}-recovery-return.json" recovery_decision="$tmp/${case_id,,}-recovery-decision.json"
  local recovery_opened recovery_open_record recovery_returned recovery_return_record recovery_completed recovery_complete_record admitted

  if [ "$package_mode" = "PACKAGE_RELOCATED" ]; then
    package_old_parent="$tmp/${case_id,,}-active-package-old"
    package_new_parent="$tmp/${case_id,,}-active-package-new"
    mkdir -p "$package_old_parent" "$package_new_parent"
    cp -R "$package_source" "$package_old_parent/"
    cp -R "$package_source" "$package_new_parent/"
    package_old="$package_old_parent/skills"
    package_new="$package_new_parent/skills"
    ROUTE_CORE="$package_old/implementaudit/scripts/route-transaction.py"
    ACTIVE_CLAIM="$package_old/implementaudit/scripts/claim-run.sh"
    package_root="$package_old"
  fi

  receipt="$(make_run "$controller" "$run_name" "$claim_local" "${case_id,,}-old-boundary")"
  bind_host "$session" "$controller" "$claim_local" "$root" "$receipt" "activation-${case_id,,}"
  write_request "$old_request" PURE_BOUNDED_READ_OR_VALIDATION IMMUTABLE_INDEPENDENT_REVIEW
  mutate_request "$old_request" "$old_request.next" \
    'value["boundary"]={"kind":"new-session","event_id":"'"${case_id,,}"'-old-boundary"}; value["boundary"]["digest"]=h(value["boundary"])'
  mv "$old_request.next" "$old_request"
  decided="$(route "$controller" "$session" G0001 decide --request "$old_request" --expected-record none)"
  required_record="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$decided")"
  obligation="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["obligation_id"])' "$decided")"
  transaction="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["route_transaction_id"])' "$decided")"
  attributed="$(host validate-event --host-id codex --host-session-id "$session" \
    --binding-generation G0001 --controller-id "$controller" --claim-id "$claim_local" \
    --explicit-run-root "$root" --repository-identity "$repo_custody" \
    --git-common-directory-identity "$common_custody" --worktree-identity "$repo_custody" \
    --continuity-generation G0001 --continuity-receipt "$receipt" \
    --event-id "host:$case_id:old" --obligation-id "$obligation" --route-transaction-id "$transaction")"
  correlation="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["correlation_id"])' "$attributed")"
  "${py[@]}" - "$old_packet" "$old_return" "$old_decision" "$obligation" "$transaction" "$correlation" "$case_id" <<'PY'
import hashlib,json,sys
packet_path,return_path,decision_path,obligation,transaction,correlation,event_id=sys.argv[1:]
def write(path,value):
 raw=(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()
 open(path,"wb").write(raw)
 return "sha256:"+hashlib.sha256(raw).hexdigest()
packet={"schema":"implementaudit.route-packet.v1","obligation_id":obligation,
 "route_transaction_id":transaction,"target_identity":"audit-assess",
 "source_event":{"schema":"implementaudit.source-event.v1","source_identity":"host:"+event_id+":old",
  "provenance":{"schema":"implementaudit.source-event-provenance.v1","event_id":"host:"+event_id+":old",
   "host_correlation_id":correlation},"body":"perform the pre-compaction review once",
  "kind":"one-shot-action","reactivation":{"reopen":False,"target_changed":False,"invalidating_evidence":False}}}
packet_digest=write(packet_path,packet)
returned={"schema":"implementaudit.child-return.v1","obligation_id":obligation,
 "route_transaction_id":transaction,"packet_digest":packet_digest,"status":"RETURNED",
 "payload":{"result":"pre-compaction review return must remain historical"}}
return_digest=write(return_path,returned)
write(decision_path,{"schema":"implementaudit.governor-route-decision.v1","obligation_id":obligation,
 "route_transaction_id":transaction,"return_digest":return_digest,"outcome":"SATISFIED",
 "reason":"this pre-compaction decision must never complete the recovery route"})
PY
  opened="$(route "$controller" "$session" G0001 open --request "$old_request" \
    --expected-record "$required_record" --packet "$old_packet" 2>"$tmp/${case_id,,}-old-open.visible")"
  open_record="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$opened")"
  active_record="$open_record"
  if [ "$active_state" = RETURNED ]; then
    returned="$(route "$controller" "$session" G0001 return --request "$old_request" \
      --expected-record "$open_record" --return "$old_return")"
    active_record="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$returned")"
  fi
  active_blob="$(git -C "$tmp/repo" cat-file blob "$active_record")"
  assert_json "$active_blob" 'value["route_state"] == "'"$active_state"'" and value["lifecycle"]["state"] == "'"$active_state"'" and value["lifecycle"]["source_event_status"] == "active" and value["lifecycle"]["governor_decision_count"] == 0'

  # A distinct request in the same live context cannot discard active child
  # work, even when it names the recovery reason.
  mutate_request "$old_request" "$recovery_request" \
    'value["action"]={"identity":"action:stale_context_reconstruction","class":"PURE_BOUNDED_READ_OR_VALIDATION","argv":["route-trigger","STALE_CONTEXT_RECONSTRUCTION"]}; value["action"]["digest"]=h(value["action"])'

  # Model an exact cachebuster/install relocation after the active record was
  # written. The historical audit-assess bytes are identical, but their old
  # absolute identity no longer exists. Only the later-boundary recovery decide
  # may read that immutable delivery; every ordinary path remains strict-current.
  if [ "$package_mode" = "PACKAGE_RELOCATED" ]; then
    cmp -s "$package_old/audit-assess/SKILL.md" "$package_new/audit-assess/SKILL.md" ||
      fail "$case_id relocated active child bytes changed"
    rm -rf -- "$package_old"
    [ ! -e "$package_old/audit-assess/SKILL.md" ] ||
      fail "$case_id predecessor active package path remained available"
    ROUTE_CORE="$package_new/implementaudit/scripts/route-transaction.py"
    ACTIVE_CLAIM="$package_new/implementaudit/scripts/claim-run.sh"
    package_root="$package_new"
  fi

  expect_blocked "$case_id same-context active replacement" \
    route "$controller" "$session" G0001 decide --request "$recovery_request" --expected-record "$active_record" >/dev/null
  if [ "$package_mode" = "PACKAGE_RELOCATED" ]; then
    expect_blocked "$case_id relocated active lifecycle cannot pass ordinary check" \
      route "$controller" "$session" G0001 check --request "$old_request" >/dev/null
    expect_blocked "$case_id relocated active lifecycle cannot pass ordinary open" \
      route "$controller" "$session" G0001 open --request "$old_request" \
        --expected-record "$active_record" --packet "$old_packet" >/dev/null
    expect_blocked "$case_id relocated active lifecycle cannot pass ordinary admission" \
      route "$controller" "$session" G0001 admit-current >/dev/null
  fi

  successor_receipt="$(promote_to_v3 "$controller" "$claim_local" "$root" "$run_name" \
    "${case_id,,}-compact-boundary" host-reported-compaction)"
  mutate_request "$recovery_request" "$recovery_request.next" \
    'value["boundary"]={"kind":"host-reported-compaction","event_id":"'"${case_id,,}"'-compact-boundary"}; value["boundary"]["digest"]=h(value["boundary"])'
  mv "$recovery_request.next" "$recovery_request"
  host rebind --owner-id host-owner --host-id codex --host-session-id "$session" \
    --expected-generation G0001 --reason active-route-compaction-successor \
    --controller-id "$controller" --claim-id "$claim_local" --explicit-run-root "$root" \
    --repository-identity "$tmp/repo" --git-common-directory-identity "$tmp/repo/.git" \
    --worktree-identity "$tmp/repo" --activation-event-id "activation-${case_id,,}-g2" \
    --activation-receipt "activation-${case_id,,}-g2" --continuity-generation G0002 \
    --continuity-receipt "$successor_receipt" >/dev/null

  expect_blocked "$case_id stale binding generation cannot recover active lifecycle" \
    route "$controller" "$session" G0001 decide --request "$recovery_request" --expected-record "$active_record" >/dev/null
  expect_blocked "$case_id skipped binding generation cannot recover active lifecycle" \
    route "$controller" "$session" G0003 decide --request "$recovery_request" --expected-record "$active_record" >/dev/null
  expect_blocked "$case_id foreign session cannot recover active lifecycle" \
    route "$controller" "${session}-foreign" G0002 decide --request "$recovery_request" --expected-record "$active_record" >/dev/null
  expect_blocked "$case_id foreign controller cannot recover active lifecycle" \
    route "${controller}-foreign" "$session" G0002 decide --request "$recovery_request" --expected-record "$active_record" >/dev/null

  mutate_request "$recovery_request" "$wrong_reason_request" \
    'value["action"]={"identity":"action:immutable_independent_review","class":"PURE_BOUNDED_READ_OR_VALIDATION","argv":["route-trigger","IMMUTABLE_INDEPENDENT_REVIEW"]}; value["action"]["digest"]=h(value["action"])'
  expect_blocked "$case_id different reason and child cannot recover active lifecycle" \
    route "$controller" "$session" G0002 decide --request "$wrong_reason_request" --expected-record "$active_record" >/dev/null
  mutate_request "$recovery_request" "$malformed_request" \
    'value["boundary"]["digest"]="sha256:"+"0"*64'
  expect_blocked "$case_id malformed boundary provenance cannot recover active lifecycle" \
    route "$controller" "$session" G0002 decide --request "$malformed_request" --expected-record "$active_record" >/dev/null

  cp "$tmp/repo/baseline.txt" "$tmp/${case_id,,}-baseline"
  printf 'stale recovery input\n' >> "$tmp/repo/baseline.txt"
  expect_blocked "$case_id stale observed inputs cannot recover active lifecycle" \
    route "$controller" "$session" G0002 decide --request "$recovery_request" --expected-record "$active_record" >/dev/null
  cp "$tmp/${case_id,,}-baseline" "$tmp/repo/baseline.txt"

  if [ "$package_mode" = "PACKAGE_RELOCATED" ]; then
    # Historical custody is semantic, not permissive: every byte identity and
    # the original required-record binding remain exact even though the path is
    # no longer the current cache path.
    "${py[@]}" - "$tmp/repo" "$active_record" "$tmp/${case_id,,}-active-tamper" <<'PY'
import base64
import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path

repo, source_oid, output_prefix = sys.argv[1:]
source = json.loads(subprocess.check_output(["git", "-C", repo, "cat-file", "blob", source_oid]))

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")

def digest(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()

def finish(name, value):
    base = {key: member for key, member in value.items() if key != "record_identity"}
    value["record_identity"] = digest(canonical(base))
    Path(f"{output_prefix}-{name}.json").write_bytes(canonical(value) + b"\n")

changed_bytes = copy.deepcopy(source)
child = changed_bytes["lifecycle"]["delivery"]["child"]
raw = base64.b64decode(child["bytes_b64"], validate=True) + b"\nM1 active historical mutation"
child["bytes_b64"] = base64.b64encode(raw).decode("ascii")
child["bytes"] = len(raw)
child["digest"] = digest(raw)
changed_bytes["child_source"]["digest"] = child["digest"]
finish("bytes", changed_bytes)

changed_digest = copy.deepcopy(source)
changed_digest["lifecycle"]["delivery"]["child"]["digest"] = "sha256:" + "0" * 64
finish("digest", changed_digest)

missing_identity = copy.deepcopy(source)
del missing_identity["lifecycle"]["delivery"]["child"]["identity"]
finish("missing", missing_identity)

foreign_identity = copy.deepcopy(source)
foreign = foreign_identity["child_source"]["identity"] + "-foreign"
foreign_identity["child_source"]["identity"] = foreign
foreign_identity["lifecycle"]["delivery"]["child"]["identity"] = foreign
finish("foreign", foreign_identity)

malformed_identity = copy.deepcopy(source)
malformed_identity["child_source"]["identity"] = ""
malformed_identity["lifecycle"]["delivery"]["child"]["identity"] = ""
finish("malformed", malformed_identity)
PY
    for active_tamper in bytes digest missing foreign malformed; do
      proxy_oid="$(git -C "$tmp/repo" hash-object -w "$tmp/${case_id,,}-active-tamper-$active_tamper.json")"
      git -C "$tmp/repo" update-ref "refs/implementaudit/route-decisions/$controller" "$proxy_oid" "$active_record"
      expect_blocked "$case_id active historical child $active_tamper tamper cannot recover" \
        route "$controller" "$session" G0002 decide --request "$recovery_request" \
          --expected-record "$proxy_oid" >/dev/null
      [ "$(git -C "$tmp/repo" rev-parse "refs/implementaudit/route-decisions/$controller")" = "$proxy_oid" ] ||
        fail "$case_id active historical child $active_tamper tamper changed the route ref"
      git -C "$tmp/repo" update-ref "refs/implementaudit/route-decisions/$controller" "$active_record" "$proxy_oid"
    done
  fi

  set +e
  recovery_decided="$(route "$controller" "$session" G0002 decide --request "$recovery_request" \
    --expected-record "$active_record" 2>&1)"
  recovery_status=$?
  set -e
  if [ "$recovery_status" -ne 0 ]; then
    printf 'route-obligation-contract.test: active-route recovery causal RED (%s/%s): %s\n' \
      "$case_id" "$active_state" "$recovery_decided" >&2
    exit 1
  fi
  assert_json "$recovery_decided" 'value["decision"] == "REQUIRED" and value["route_state"] == "UNSATISFIED" and value["predecessor_record_oid"] == "'"$active_record"'"'
  recovery_required="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$recovery_decided")"
  recovery_obligation="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["obligation_id"])' "$recovery_decided")"
  recovery_transaction="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["route_transaction_id"])' "$recovery_decided")"
  [ "$(git -C "$tmp/repo" cat-file blob "$active_record")" = "$active_blob" ] || fail "$case_id recovery mutated the prior active record"
  [ "$recovery_obligation" != "$obligation" ] || fail "$case_id recovery inherited the old obligation identity"
  [ "$recovery_transaction" != "$transaction" ] || fail "$case_id recovery inherited the old transaction identity"
  recovery_blob="$(git -C "$tmp/repo" cat-file blob "$recovery_required")"
  assert_json "$recovery_blob" 'value["child_lifecycle_owned"] is False and "lifecycle" not in value and value["child_source"]["identity"].replace("\\", "/").endswith("/audit-state/SKILL.md") and value["continuity_generation"] == "G0002" and value["host_binding_generation"] == "G0002"'

  # The abandoned record is immutable history only. Its return/completion bytes
  # cannot advance or satisfy the fresh recovery obligation.
  expect_blocked "$case_id old active record cannot accept a late return" \
    route "$controller" "$session" G0002 return --request "$old_request" \
      --expected-record "$active_record" --return "$old_return" >/dev/null
  expect_blocked "$case_id fresh obligation cannot reuse the old completion" \
    route "$controller" "$session" G0002 complete --request "$recovery_request" \
      --expected-record "$recovery_required" --packet "$old_packet" --return "$old_return" --decision "$old_decision" >/dev/null
  expect_blocked "$case_id ordinary work remains blocked before recovery return" \
    route "$controller" "$session" G0002 admit-current >/dev/null

  recovery_attributed="$(host validate-event --host-id codex --host-session-id "$session" \
    --binding-generation G0002 --controller-id "$controller" --claim-id "$claim_local" \
    --explicit-run-root "$root" --repository-identity "$repo_custody" \
    --git-common-directory-identity "$common_custody" --worktree-identity "$repo_custody" \
    --continuity-generation G0002 --continuity-receipt "$successor_receipt" \
    --event-id "host:$case_id:recovery" --obligation-id "$recovery_obligation" \
    --route-transaction-id "$recovery_transaction")"
  recovery_correlation="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["correlation_id"])' "$recovery_attributed")"
  "${py[@]}" - "$recovery_packet" "$recovery_return" "$recovery_decision" \
    "$recovery_obligation" "$recovery_transaction" "$recovery_correlation" "$case_id" <<'PY'
import hashlib,json,sys
packet_path,return_path,decision_path,obligation,transaction,correlation,event_id=sys.argv[1:]
def write(path,value):
 raw=(json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode()
 open(path,"wb").write(raw)
 return "sha256:"+hashlib.sha256(raw).hexdigest()
packet={"schema":"implementaudit.route-packet.v1","obligation_id":obligation,
 "route_transaction_id":transaction,"target_identity":"audit-state",
 "source_event":{"schema":"implementaudit.source-event.v1","source_identity":"host:"+event_id+":recovery",
  "provenance":{"schema":"implementaudit.source-event-provenance.v1","event_id":"host:"+event_id+":recovery",
   "host_correlation_id":correlation},"body":"reconstruct only the fresh post-compaction state",
  "kind":"one-shot-action","reactivation":{"reopen":False,"target_changed":False,"invalidating_evidence":False}}}
packet_digest=write(packet_path,packet)
returned={"schema":"implementaudit.child-return.v1","obligation_id":obligation,
 "route_transaction_id":transaction,"packet_digest":packet_digest,"status":"RETURNED",
 "payload":{"result":"fresh bounded audit-state return","requested_next_child":"audit-assess"}}
return_digest=write(return_path,returned)
write(decision_path,{"schema":"implementaudit.governor-route-decision.v1","obligation_id":obligation,
 "route_transaction_id":transaction,"return_digest":return_digest,"outcome":"SATISFIED",
 "reason":"governor accepted only the fresh audit-state return"})
PY
  recovery_opened="$(route "$controller" "$session" G0002 open --request "$recovery_request" \
    --expected-record "$recovery_required" --packet "$recovery_packet" 2>"$tmp/${case_id,,}-recovery-open.visible")"
  if [ "$package_mode" = "PACKAGE_RELOCATED" ]; then
    "${py[@]}" - "$recovery_opened" "$package_root/audit-state/SKILL.md" <<'PY'
import base64,json,sys
from pathlib import Path
value=json.loads(sys.argv[1]); delivery=value["delivery"]["child"]
expected_path=Path(sys.argv[2]).resolve(); expected=expected_path.read_bytes()
if Path(delivery["identity"]).resolve() != expected_path or base64.b64decode(delivery["bytes_b64"], validate=True) != expected:
 raise SystemExit("fresh recovery did not load current installed audit-state bytes")
PY
  fi
  recovery_open_record="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$recovery_opened")"
  recovery_returned="$(route "$controller" "$session" G0002 return --request "$recovery_request" \
    --expected-record "$recovery_open_record" --return "$recovery_return")"
  recovery_return_record="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$recovery_returned")"
  expect_blocked "$case_id child return cannot route directly to its requested child" \
    route "$controller" "$session" G0002 admit-current >/dev/null
  recovery_completed="$(route "$controller" "$session" G0002 complete --request "$recovery_request" \
    --expected-record "$recovery_return_record" --packet "$recovery_packet" \
    --return "$recovery_return" --decision "$recovery_decision")"
  recovery_complete_record="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$recovery_completed")"
  admitted="$(route "$controller" "$session" G0002 admit-current)"
  assert_json "$admitted" 'value["record_oid"] == "'"$recovery_complete_record"'" and value["route_state"] == "SATISFIED" and value["governor_decision_count"] == 1 and value["advance_allowed"] is True'
  [ "$(git -C "$tmp/repo" cat-file blob "$active_record")" = "$active_blob" ] || fail "$case_id recovery completion mutated the prior active record"
}

if [ -z "${R0033_CASE_FILTER:-}" ] || [ "$R0033_CASE_FILTER" = G01 ]; then
run_governed_child_case G01 55555555555555555555555555555555 \
  STALE_CONTEXT_RECONSTRUCTION audit-state \
  'rehydrate bounded current state after the exact stale-context boundary' \
  host-reported-compaction REQUIRED PACKAGE_RELOCATED
fi
if [ -z "${R0033_CASE_FILTER:-}" ] || [ "$R0033_CASE_FILTER" = G02 ]; then
run_governed_child_case G02 66666666666666666666666666666666 \
  IMMUTABLE_INDEPENDENT_REVIEW audit-assess \
  'independently assess the exact immutable review packet' \
  new-session REQUIRED PACKAGE_RELOCATED
fi
if [ -z "${R0033_CASE_FILTER:-}" ] || [ "$R0033_CASE_FILTER" = G03 ]; then
run_governed_child_case G03 77777777777777777777777777777777 \
  MAINTAINER_QUALIFICATION audit-implement \
  'qualify the exact maintainer candidate after verified release currentness' \
  handoff-resume REQUIRED PACKAGE_RELOCATED
fi
if [ -z "${R0033_CASE_FILTER:-}" ] || [ "$R0033_CASE_FILTER" = G04 ]; then
run_governed_child_case G04 88888888888888888888888888888888 \
  NONTRIVIAL_ANDON_DIAGNOSIS audit-andon \
  'diagnose the established nontrivial Andon within its authority ceiling' \
  manual-resume REQUIRED PACKAGE_RELOCATED
fi
if [ -z "${R0033_CASE_FILTER:-}" ] || [ "$R0033_CASE_FILTER" = G05 ]; then
run_governed_child_case G05 99999999999999999999999999999999 \
  STALE_CONTEXT_RECONSTRUCTION audit-state \
  'rehydrate bounded current state after the exact stale-context boundary' \
  manual-resume NOT_REQUIRED PACKAGE_RELOCATED
fi
if [ -z "${R0033_CASE_FILTER:-}" ] || [ "$R0033_CASE_FILTER" = G06 ]; then
run_governed_child_case G06 aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa \
  STALE_CONTEXT_RECONSTRUCTION audit-state \
  'rehydrate bounded current state after the exact stale-context boundary' \
  host-reported-compaction REQUIRED PACKAGE_RELOCATED TWO_ROTATIONS
fi
if [ -z "${R0033_CASE_FILTER:-}" ] || [ "$R0033_CASE_FILTER" = G07 ]; then
  run_active_compaction_recovery_case G07 OPEN bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb PACKAGE_RELOCATED
fi
if [ -z "${R0033_CASE_FILTER:-}" ] || [ "$R0033_CASE_FILTER" = G08 ]; then
  run_active_compaction_recovery_case G08 RETURNED cccccccccccccccccccccccccccccccc
fi

# The pure R0033 owner validator remains usable for a read-only C03 projection
# after event attribution is tombstoned, while every R0033 effect path refuses.
host tombstone --owner-id host-owner --host-id codex --host-session-id route-red \
  --expected-generation G0001 --reason route-owner-read-only-control >/dev/null
expect_blocked "tombstoned session cannot authorize a new route effect" \
  route controller-route route-red G0001 check --request "$required_request" >/dev/null
tombstone_snapshot_before="$(read_only_snapshot)"
expect_observe_blocked "tombstoned session cannot authorize request-free observation" \
  controller-route route-red G0001 >/dev/null
tombstone_snapshot_after="$(read_only_snapshot)"
[ "$tombstone_snapshot_before" = "$tombstone_snapshot_after" ] || fail "tombstoned request-free observation changed persistent state"
set +e
pure_tombstoned="$("${py[@]}" - "$core" "$tmp/repo" controller-route <<'PY'
import importlib.util,json
from pathlib import Path
import sys
path,repo,controller=sys.argv[1:]
spec=importlib.util.spec_from_file_location("route_transaction_pure_control",path)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
print(json.dumps(module.validate_pure_current_route(Path(repo),controller),sort_keys=True))
PY
)"
pure_tombstoned_status=$?
set -e
[ "$pure_tombstoned_status" -eq 0 ] || fail "pure R0033 read-only validation required live R003A attribution: $pure_tombstoned"
current_required_oid="$(git -C "$tmp/repo" rev-parse refs/implementaudit/route-decisions/controller-route)"
assert_json "$pure_tombstoned" 'value["record_oid"] == "'"$current_required_oid"'" and value["controller_id"] == "controller-route"'

emit_route_summary
