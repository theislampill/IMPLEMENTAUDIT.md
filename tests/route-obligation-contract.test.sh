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
(
  cd "$tmp/repo"
  bash "$claim" --invalidate-continuity controller-route --boundary new-session --event exact-boundary-event >/dev/null
)
continuity_receipt="$(
  cd "$tmp/repo"
  bash "$claim" --resume-controller controller-route --boundary new-session --epoch G0001
)"

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
  shift 3
  (
    unset BASH_XTRACEFD
    cd "$tmp/repo"
    "${py[@]}" "$core" "$@" --controller "$controller" --store "$tmp/host-store" \
      --host-id codex --host-session-id "$session" --binding-generation "$generation"
  )
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
  (
    cd "$tmp/repo"
    bash "$claim" --invalidate-continuity "$controller" --boundary new-session --event "$event_id" >/dev/null
    bash "$claim" --resume-controller "$controller" --boundary new-session --epoch G0001
  )
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
  local invalidation invalidation_oid head tree state_sha road_sha graph_sha
  local manifest_raw manifest_oid manifest_sha pointer_ref marker_ref pointer_oid receipt receipt_oid marker_oid
  invalidation="$(cd "$tmp/repo" && bash "$claim" --invalidate-continuity "$controller" --boundary manual-resume --event "$event")"
  invalidation_oid="${invalidation##*@}"
  head="$(git -C "$tmp/repo" rev-parse HEAD)"; tree="$(git -C "$tmp/repo" rev-parse 'HEAD^{tree}')"
  "${py[@]}" - "$root/STATE.md" "$head" "$tree" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]); head,tree=sys.argv[2:]
s=p.read_text(encoding="utf-8").replace("Current epoch: G0001","Current epoch: G0002")
anchor=f"| G0001 | new-session | 2026-08-20T00:00:00Z | {head} {tree} | yes | exact H2A boundary |"
row=f"| G0002 | manual-resume | 2026-08-20T00:05:00Z | {head} {tree} | yes | exact v3 route boundary |"
if s.count(anchor)!=1: raise SystemExit("v3 fixture lost its G0001 anchor")
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
  receipt="$(cd "$tmp/repo" && bash "$claim" --resume-controller "$controller" --boundary manual-resume --epoch G0002)"
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
cp "$tmp/state-before-projection-edit.md" "$run_root/STATE.md"
junk="$(printf 'not-json\n' | git -C "$tmp/repo" hash-object -w --stdin)"
git -C "$tmp/repo" update-ref refs/implementaudit/route-decisions/controller-route "$junk"
expect_blocked "malformed current route record" route controller-route route-red G0001 check --request "$required_request" >/dev/null
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
required_check="$(expect_blocked "required route remains unsatisfied" route controller-route route-red G0001 check --request "$required_request")"
assert_json "$required_check" 'value["decision"] == "REQUIRED" and value["advance_allowed"] is False and value["route_state"] == "UNSATISFIED"'
required_blob="$(git -C "$tmp/repo" cat-file blob "$required_oid")"
assert_json "$required_blob" 'value["child_lifecycle_owned"] is False and "child_open" not in value and "child_return" not in value and "completion" not in value'
assert_json "$required_blob" 'value["predecessor_record_oid"] is None and value["record_identity"].startswith("sha256:")'

# HC-H2B: the canonical REQUIRED obligation opens only with the exact full
# audit-state bytes and immutable packet, accepts the same live return, rereads
# currentness after return, and records exactly one governor decision.
route_packet="$tmp/route-packet.json"
child_return="$tmp/child-return.json"
governor_decision="$tmp/governor-decision.json"
"${py[@]}" - "$required_decide" "$route_packet" "$child_return" "$governor_decision" <<'PY'
import hashlib,json,sys
decided=json.loads(sys.argv[1])
event={
 "schema":"implementaudit.source-event.v1",
 "source_identity":"host:E1",
 "provenance":"host-event",
 "body":"perform the exact bounded route once",
 "kind":"one-shot-action",
 "reactivation":{"reopen":False,"target_changed":False,"invalidating_evidence":False},
}
packet={
 "schema":"implementaudit.route-packet.v1",
 "obligation_id":decided["obligation_id"],
 "route_transaction_id":decided["route_transaction_id"],
 "source_event":event,
 "target_identity":"target:hc-h2b",
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

opened="$(route controller-route route-red G0001 open --request "$required_request" \
  --expected-record "$required_oid" --packet "$route_packet")"
assert_json "$opened" 'value["status"] == "CHILD_OPEN" and value["decision"] == "REQUIRED" and value["route_state"] == "OPEN" and value["advance_allowed"] is False'
open_oid="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$opened")"
"${py[@]}" - "$opened" "$repo_root/skills/audit-state/SKILL.md" "$route_packet" <<'PY'
import base64,json,sys
value=json.loads(sys.argv[1])
assert base64.b64decode(value["delivery"]["child"]["bytes_b64"]) == open(sys.argv[2],"rb").read()
assert base64.b64decode(value["delivery"]["packet"]["bytes_b64"]) == open(sys.argv[3],"rb").read()
PY
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
proxy_oid="$(printf '%s' "$complete_blob" | "${py[@]}" -c '
import base64,hashlib,json,sys
value=json.load(sys.stdin)
value["lifecycle"]["delivery"]["packet"]["bytes_b64"]=base64.b64encode(b"{}\n").decode()
base={key:item for key,item in value.items() if key!="record_identity"}
raw=json.dumps(base,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
value["record_identity"]="sha256:"+hashlib.sha256(raw).hexdigest()
print(json.dumps(value,sort_keys=True,separators=(",",":")))
' | git -C "$tmp/repo" hash-object -w --stdin)"
git -C "$tmp/repo" update-ref refs/implementaudit/route-decisions/controller-route "$proxy_oid" "$complete_oid"
expect_blocked "packet hash proxy cannot satisfy full-byte route delivery" \
  route controller-route route-red G0001 check --request "$required_request" >/dev/null
git -C "$tmp/repo" update-ref refs/implementaudit/route-decisions/controller-route "$complete_oid" "$proxy_oid"
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
"${py[@]}" - "$route_packet" "$event_e1" "$event_e2" "$event_e3" "$event_ambiguous" <<'PY'
import json,sys
packet=json.load(open(sys.argv[1],encoding="utf-8"))
event=packet["source_event"]
for path,value in (
 (sys.argv[2],event),
 (sys.argv[3],{**event,"source_identity":"host:E2"}),
 (sys.argv[4],{**event,"source_identity":"host:E3","reactivation":{**event["reactivation"],"reopen":True}}),
 (sys.argv[5],{key:value for key,value in event.items() if key!="provenance"}),
):
 with open(path,"w",encoding="utf-8",newline="\n") as handle:
  json.dump(value,handle,sort_keys=True,separators=(",",":"),ensure_ascii=False); handle.write("\n")
PY

replayed="$(route controller-route route-red G0001 replay --request "$required_request" \
  --expected-record "$complete_oid" --event "$event_e1")"
assert_json "$replayed" 'value["status"] == "REPLAY_NO_OP" and value["source_event_relation"] == "SAME_SOURCE" and value["record_oid"] == "'"$complete_oid"'"'
assert_json "$replayed" 'value["effects"] == {"instruction_rows":0,"route_transactions":0,"lifecycle_transitions":0,"mutation_authorizations":0,"task_dispatches":0,"external_effects":0}'
distinct="$(route controller-route route-red G0001 replay --request "$required_request" \
  --expected-record "$complete_oid" --event "$event_e2")"
assert_json "$distinct" 'value["status"] == "TERMINAL_NO_OP" and value["source_event_relation"] == "DISTINCT_SOURCE_SAME_BODY" and value["source_identity"] == "host:E2"'
assert_json "$distinct" 'value["target_state"] == "SATISFIED" and value["effects"]["instruction_rows"] == 0 and value["effects"]["external_effects"] == 0'
[ "$(git -C "$tmp/repo" rev-parse refs/implementaudit/route-decisions/controller-route)" = "$complete_oid" ] || fail "compaction replay mutated the canonical terminal route"
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
stored={"source_identity":"host:S1","body":"keep applying","kind":"standing-constraint","status":"active","reactivation":{"reopen":False,"target_changed":False,"invalidating_evidence":False}}
incoming={"source_identity":"host:S1","body":"keep applying","kind":"standing-constraint","reactivation":{"reopen":False,"target_changed":False,"invalidating_evidence":False}}
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

incomplete_request="$tmp/incomplete.json"
mutate_request "$pending_request" "$incomplete_request" 'value["inputs"][0]["digest"]="sha256:"+"0"*64'
pending_decide="$(route controller-pending session-pending G0001 decide --request "$incomplete_request" --expected-record none)"
assert_json "$pending_decide" 'value["decision"] == "PENDING" and value["advance_allowed"] is False and value["invalidators"]'
pending_oid="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$pending_decide")"
set +e
mirror_check="$(route controller-pending session-pending G0001 check --request "$incomplete_request" --mirror-claim SATISFIED 2>&1)"
mirror_status=$?
set -e
[ "$mirror_status" -ne 0 ] || fail "ActiveGraph mirror claim advanced a canonical PENDING route"
assert_json "$mirror_check" 'value["decision"] == "PENDING" and value["advance_allowed"] is False and value["record_oid"] == "'"$pending_oid"'"'
assert_json "$mirror_check" 'value["mirror_claim"] == "SATISFIED" and value["mirror_status"] == "IGNORED_CONTRADICTION"'
[ "$(git -C "$tmp/repo" rev-parse refs/implementaudit/route-decisions/controller-pending)" = "$pending_oid" ] || fail "mirror claim mutated canonical route authority"
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
printf 'read-set-v2\n' > "$tmp/repo/unlisted-observation.txt"
expect_blocked "unlisted worktree read-set change expires receipt" route controller-cheap session-cheap G0001 check --request "$cheap_request" >/dev/null
printf 'read-set-v1\n' > "$tmp/repo/unlisted-observation.txt"
route controller-cheap session-cheap G0001 check --request "$cheap_request" >/dev/null
wrapper_check="$(
  cd "$tmp/repo"
  bash "$claim" --require-current-route controller-cheap --store "$tmp/host-store" \
    --host-id codex --host-session-id session-cheap --binding-generation G0001 \
    --request "$cheap_request"
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
old_transaction="$(git -C "$tmp/repo" cat-file blob "$cheap_oid" | "${py[@]}" -c 'import json,sys;print(json.load(sys.stdin)["route_transaction_id"])')"
host rebind --owner-id host-owner --host-id codex --host-session-id session-cheap \
  --expected-generation G0001 --reason binding-generation-control \
  --controller-id controller-cheap --claim-id "$cheap_claim" --explicit-run-root "$cheap_root" \
  --repository-identity "$tmp/repo" --git-common-directory-identity "$tmp/repo/.git" \
  --worktree-identity "$tmp/repo" --activation-event-id activation-cheap-g2 \
  --activation-receipt activation-cheap-g2 --continuity-generation G0001 \
  --continuity-receipt "$cheap_receipt" >/dev/null
expect_blocked "current binding generation expires prior receipt" route controller-cheap session-cheap G0002 check --request "$cheap_request" >/dev/null
rebound_decide="$(route controller-cheap session-cheap G0002 decide --request "$cheap_request" --expected-record "$cheap_oid")"
rebound_oid="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["record_oid"])' "$rebound_decide")"
assert_json "$rebound_decide" "value[\"decision\"] == \"NOT_REQUIRED\" and value[\"record_oid\"] != \"$cheap_oid\" and not value.get(\"idempotent\", False)"
rebound_transaction="$(git -C "$tmp/repo" cat-file blob "$rebound_oid" | "${py[@]}" -c 'import json,sys;print(json.load(sys.stdin)["route_transaction_id"])')"
[ "$old_transaction" != "$rebound_transaction" ] || fail "binding generation reused the route transaction identity"
route controller-cheap session-cheap G0002 check --request "$cheap_request" >/dev/null
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

printf 'route-obligation-contract.test: ok (61/61 live H2A cases + HC-H2B route/return/completion/replay held-out; first RED preserved)\n'
