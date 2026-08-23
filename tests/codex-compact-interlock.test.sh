#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
adapter="$repo_root/skills/implementaudit/scripts/codex-compact-interlock.py"
binding_core="$repo_root/skills/implementaudit/scripts/host-session-binding.py"
claim_helper="$repo_root/skills/implementaudit/scripts/claim-run.sh"
hook_config="$repo_root/hooks/hooks.json"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

fail() {
  printf 'codex-compact-interlock.test: %s\n' "$*" >&2
  exit 1
}

py=()
if command -v python >/dev/null 2>&1; then py=(python)
elif command -v python3 >/dev/null 2>&1; then py=(python3)
elif command -v py >/dev/null 2>&1; then py=(py -3)
else fail 'Python 3 is required'; fi

[ -f "$adapter" ] || fail 'HC-H1 RED: compact interlock adapter is absent'
[ -f "$hook_config" ] || fail 'HC-H1 RED: default Codex hook definition is absent'

manifest_windows_command="$(
"${py[@]}" - "$hook_config" <<'PY'
import json
import sys
from pathlib import Path

value = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
assert set(value) == {"hooks"}
assert set(value["hooks"]) == {"SessionStart"}
session_start = value.get("hooks", {}).get("SessionStart")
assert isinstance(session_start, list) and len(session_start) == 1
entry = session_start[0]
assert set(entry) == {"matcher", "hooks"}
assert entry.get("matcher") == "^compact$"
commands = entry.get("hooks")
assert isinstance(commands, list) and len(commands) == 1
command = commands[0]
assert set(command) == {"type", "command", "commandWindows", "statusMessage"}
assert command.get("type") == "command"
assert command.get("statusMessage") == "Protecting IMPLEMENTAUDIT continuity"
assert command.get("command") == (
    'python3 "${PLUGIN_ROOT}/skills/implementaudit/scripts/'
    'codex-compact-interlock.py"'
)
assert command.get("commandWindows") == (
    'C:\\Windows\\py.exe -3 "%PLUGIN_ROOT%\\skills\\implementaudit\\scripts\\'
    'codex-compact-interlock.py"'
)
print(command["commandWindows"])
PY
)" || fail 'default Codex hook definition is not exact'

assert_result() {
  local raw="$1" expression="$2" label="$3"
  "${py[@]}" - "$raw" "$expression" <<'PY' || fail "$label"
import json
import sys

value = json.loads(sys.argv[1])
assert value.get("schema") == "implementaudit.codex-compact-interlock-result.v1"
assert eval(sys.argv[2], {"__builtins__": {}}, {"value": value})
PY
}

run_hook() {
  local plugin_data="$1" payload="$2" cwd="$3" output status
  set +e
  output="$(cd "$cwd" && GIT_DIR="$tmp/foreign-git-dir" GIT_WORK_TREE="$hostile" \
    GIT_CONFIG_GLOBAL="$tmp/foreign-git-config" \
    SystemRoot="$tmp/foreign-system-root" \
    PLUGIN_ROOT="$repo_root" PLUGIN_DATA="$plugin_data" \
    "${py[@]}" "$adapter" <<<"$payload" 2>"$tmp/hook.err")"
  status=$?
  set -e
  [ "$status" -eq 0 ] || fail "hook command exited $status: $(cat "$tmp/hook.err")"
  [ ! -s "$tmp/hook.err" ] || fail "hook command leaked diagnostic output: $(cat "$tmp/hook.err")"
  printf '%s\n' "$output"
}

hostile="$tmp/hostile-cwd"
mkdir -p "$hostile/.IMPLEMENTAUDIT/runs/newest"
printf 'controller_id=foreign\nclaim_id=foreign\n' > "$hostile/.IMPLEMENTAUDIT/runs/newest/STATE.md"

# The actual Windows manifest transport must reach the adapter before the
# adapter can harden its own child environment. Codex selects commandWindows on
# Windows and runs it through cmd.exe. A hostile bare `python3.cmd` on PATH is
# the causal held-out: selecting it would produce no hook decision at all.
hostile_bin="$tmp/hostile-bin"
manifest_data="$tmp/manifest-plugin-data"
mkdir -p "$hostile_bin"
surrogate_selected="$tmp/python3-surrogate-selected"
surrogate_selected_windows="$(cygpath -w "$surrogate_selected")"
printf '@echo off\r\n> "%s" echo selected\r\nexit /b 0\r\n' \
  "$surrogate_selected_windows" > "$hostile_bin/python3.cmd"
hostile_bin_windows="$(cygpath -w "$hostile_bin")"
repo_root_windows="$(cygpath -w "$repo_root")"
manifest_data_windows="$(cygpath -w "$manifest_data")"
set +e
manifest_output="$(cd "$hostile" && \
  PATH="$hostile_bin_windows" PLUGIN_ROOT="$repo_root_windows" \
  PLUGIN_DATA="$manifest_data_windows" \
  HC_H1_COMMAND_WINDOWS="$manifest_windows_command" \
  MSYS2_ARG_CONV_EXCL='*' \
  /c/Windows/System32/WindowsPowerShell/v1.0/powershell.exe \
  -NoProfile -NonInteractive \
  -Command '$input | & $env:ComSpec /Q /D /C $env:HC_H1_COMMAND_WINDOWS' \
  <<<'{"session_id":"session-manifest","cwd":"ignored","hook_event_name":"SessionStart","source":"compact"}' \
  2>"$tmp/manifest.err")"
manifest_status=$?
set -e
[ "$manifest_status" -eq 0 ] \
  || fail "manifest command exited $manifest_status: $(cat "$tmp/manifest.err")"
[ ! -s "$tmp/manifest.err" ] \
  || fail "manifest command leaked diagnostics: $(cat "$tmp/manifest.err")"
assert_result "$manifest_output" \
  'value["status"] == "UNBOUND" and value["continue"] is True' \
  'HC-H1 RED: ambient PATH bypassed the manifest adapter transport'
[ ! -e "$surrogate_selected" ] \
  || fail 'HC-H1 RED: commandWindows selected ambient python3.cmd'
[ ! -e "$manifest_data" ] || fail 'manifest held-out created absent binding state'

# Non-compact SessionStart values are strict no-ops and must not inspect or
# create PLUGIN_DATA state.
for source in startup resume clear; do
  absent_nontrigger="$tmp/nontrigger-$source"
  result="$(run_hook "$absent_nontrigger" \
    "{\"session_id\":\"session-a\",\"cwd\":\"$hostile\",\"transcript_path\":\"$tmp/transcript\",\"hook_event_name\":\"SessionStart\",\"source\":\"$source\"}" \
    "$hostile")"
  assert_result "$result" 'value["status"] == "IGNORED" and value["continue"] is True' \
    "$source SessionStart was not ignored"
  [ ! -e "$absent_nontrigger" ] || fail "$source SessionStart created PLUGIN_DATA state"
done

# Compact without PLUGIN_DATA is a fail-closed stop.  An exact absent store or
# binding is the admitted zero-scan non-trigger and remains zero-create.
set +u
missing_data_output="$(cd "$hostile" && env -u PLUGIN_DATA PLUGIN_ROOT="$repo_root" \
  "${py[@]}" "$adapter" <<<'{"session_id":"session-a","cwd":"ignored","hook_event_name":"SessionStart","source":"compact"}')"
missing_data_status=$?
set -u
[ "$missing_data_status" -eq 0 ] || fail 'missing PLUGIN_DATA did not return a hook decision'
assert_result "$missing_data_output" 'value["status"] == "BLOCKED" and value["continue"] is False' \
  'missing PLUGIN_DATA did not fail closed'

absent_data="$tmp/absent-plugin-data"
absent_result="$(run_hook "$absent_data" \
  '{"session_id":"session-a","cwd":"ignored","hook_event_name":"SessionStart","source":"compact"}' \
  "$hostile")"
assert_result "$absent_result" 'value["status"] == "UNBOUND" and value["continue"] is True' \
  'absent binding was not a zero-scan non-trigger'
[ ! -e "$absent_data" ] || fail 'absent binding lookup created a store'

# Construct one genuine controller/run/current receipt and bind it to the
# fixed Codex namespace plus the host-supplied session id in the existing H0
# store.  Target state and the store remain sibling custody planes.
target_repo="$tmp/target-repo"
plugin_data="$tmp/plugin-data"
store="$plugin_data/host-session-binding-v1"
mkdir -p "$target_repo" "$plugin_data"
git -C "$target_repo" init -q
git -C "$target_repo" config user.name 'HC-H1 fixture'
git -C "$target_repo" config user.email 'hc-h1@example.invalid'
printf 'fixture\n' > "$target_repo/product.txt"
git -C "$target_repo" add product.txt
git -C "$target_repo" commit -qm 'HC-H1 fixture'
run_rel="$(cd "$target_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs \
  bash "$claim_helper" --controller hc-h1-controller 'HC-H1 compact fixture' 2>/dev/null)" \
  || fail 'could not establish the governed fixture controller'
run_root="$target_repo/$run_rel"
claim_id="$(sed -n 's/^claim_id=//p' "$run_root/.claimed")"
for file in STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md; do
  cp "$repo_root/skills/implementaudit/templates/$file" "$run_root/$file"
done
head="$(git -C "$target_repo" rev-parse HEAD)"
tree="$(git -C "$target_repo" rev-parse 'HEAD^{tree}')"
"${py[@]}" - "$run_root/STATE.md" "$run_rel" "$head" "$tree" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
run, head, tree = sys.argv[2:]
text = path.read_text(encoding="utf-8")
text = text.replace("| Run root |  |", f"| Run root | `{run}` |")
text = text.replace("| Next action |  |", "| Next action | resume after verified compact boundary |")
anchor = "| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|"
row = f"| G0001 | new-session | 2026-08-22T00:00:00Z | repo at `{head}` / `{tree}` | yes | fixture current |"
path.write_text(text.replace(anchor, anchor + "\n" + row), encoding="utf-8")
PY
receipt="$(cd "$target_repo" && bash "$claim_helper" --resume-controller hc-h1-controller \
  --boundary new-session --epoch G0001)" || fail 'could not mint the fixture continuity receipt'
[ "$(cd "$target_repo" && bash "$claim_helper" --require-current-continuity hc-h1-controller)" = "$receipt" ] \
  || fail 'fixture continuity receipt is not current'
common="$(cd "$(git -C "$target_repo" rev-parse --path-format=absolute --git-common-dir)" && pwd -P)"
worktree="$(cd "$target_repo" && pwd -P)"

"${py[@]}" "$binding_core" --store "$store" init --owner-id host-owner >/dev/null
"${py[@]}" "$binding_core" --store "$store" bind \
  --owner-id host-owner --host-id codex --host-session-id session-a \
  --controller-id hc-h1-controller --claim-id "$claim_id" \
  --explicit-run-root "$run_root" --repository-identity "$worktree" \
  --git-common-directory-identity "$common" --worktree-identity "$worktree" \
  --activation-event-id activation-a --activation-receipt activation-receipt-a \
  --continuity-generation G0001 --continuity-receipt "$receipt" >/dev/null

# A malformed or untrusted existing store is not equivalent to an absent
# binding.  It must stop without guessing from cwd or newest-run bait.
bad_data="$tmp/bad-plugin-data"
cp -R "$plugin_data" "$bad_data"
printf '{"schema":"foreign"}\n' > "$bad_data/host-session-binding-v1/owner.json"
bad_result="$(run_hook "$bad_data" \
  '{"session_id":"session-a","cwd":"ignored","hook_event_name":"SessionStart","source":"compact"}' \
  "$hostile")"
assert_result "$bad_result" 'value["status"] == "BLOCKED" and value["continue"] is False' \
  'malformed existing binding state did not fail closed'
[ "$(git -C "$target_repo" rev-parse --verify refs/implementaudit/continuity-receipts/hc-h1-controller/G0001)" = "${receipt##*@}" ] \
  || fail 'malformed store handling changed governed currentness'

# A different host session cannot borrow the sole binding.
foreign_session="$(run_hook "$plugin_data" \
  '{"session_id":"session-foreign","cwd":"ignored","hook_event_name":"SessionStart","source":"compact"}' \
  "$hostile")"
assert_result "$foreign_session" 'value["status"] == "UNBOUND" and value["continue"] is True' \
  'foreign session borrowed another session binding'

event='{"session_id":"session-a","cwd":"C:/attacker/ignored","transcript_path":"C:/attacker/transcript.jsonl","hook_event_name":"SessionStart","source":"compact"}'
first="$(run_hook "$plugin_data" "$event" "$hostile")"
assert_result "$first" 'value["status"] == "INVALIDATED" and value["continue"] is False and value["invalidation"].startswith("refs/implementaudit/continuity-invalidations/hc-h1-controller@")' \
  'exact compact event did not invalidate and stop'
first_token="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["invalidation"])' "$first")"
first_oid="${first_token##*@}"
[ "$(git -C "$target_repo" rev-parse --verify refs/implementaudit/continuity-invalidations/hc-h1-controller)" = "$first_oid" ] \
  || fail 'adapter output is not bound to the visible invalidation ref'
if (cd "$target_repo" && bash "$claim_helper" --require-current-continuity hc-h1-controller) >/dev/null 2>&1; then
  fail 'old currentness remained valid after compact invalidation'
fi

duplicate="$(run_hook "$plugin_data" "$event" "$hostile")"
assert_result "$duplicate" 'value["status"] == "INVALIDATED" and value["continue"] is False' \
  'same compact boundary was not idempotently stopped'
[ "$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["invalidation"])' "$duplicate")" = "$first_token" ] \
  || fail 'same compact boundary minted a second invalidation'

# Invalid JSON, control-character identity and oversized input all stop without
# changing the already visible exact invalidation.
for hostile_event in \
  '{' \
  '{"session_id":"bad\u000asession","cwd":"ignored","hook_event_name":"SessionStart","source":"compact"}'; do
  blocked="$(run_hook "$plugin_data" "$hostile_event" "$hostile")"
  assert_result "$blocked" 'value["status"] == "BLOCKED" and value["continue"] is False' \
    'malformed or control-character hook input did not fail closed'
done
oversized="$("${py[@]}" -c 'import json;print(json.dumps({"session_id":"x"*70000,"cwd":"ignored","hook_event_name":"SessionStart","source":"compact"}))')"
blocked="$(run_hook "$plugin_data" "$oversized" "$hostile")"
assert_result "$blocked" 'value["status"] == "BLOCKED" and value["continue"] is False' \
  'oversized hook input did not fail closed'
[ "$(git -C "$target_repo" rev-parse --verify refs/implementaudit/continuity-invalidations/hc-h1-controller)" = "$first_oid" ] \
  || fail 'hostile hook input changed the exact invalidation'

# A fresh governed successor receipt plus expected-generation H0 rebind creates
# a distinct compact event.  Reusing the first event identity would strand the
# new generation behind the old idempotency result.
"${py[@]}" - "$run_root/STATE.md" "$head" "$tree" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
head, tree = sys.argv[2:]
text = path.read_text(encoding="utf-8")
text = text.replace("Current epoch: G0001", "Current epoch: G0002")
anchor = f"| G0001 | new-session | 2026-08-22T00:00:00Z | repo at `{head}` / `{tree}` | yes | fixture current |"
row = f"| G0002 | host-reported-compaction | 2026-08-22T00:01:00Z | repo at `{head}` / `{tree}` | yes | compact reconciled |"
if text.count(anchor) != 1:
    raise SystemExit("fixture lost the G0001 continuity row")
path.write_text(text.replace(anchor, anchor + "\n" + row), encoding="utf-8")
PY
printf '\nFresh compact successor reconciled.\n' >> "$run_root/ROADMAP.md"
receipt_two="$(cd "$target_repo" && bash "$claim_helper" \
  --resume-controller hc-h1-controller --boundary host-reported-compaction \
  --epoch G0002)" || fail 'could not mint post-compact successor receipt'
"${py[@]}" "$binding_core" --store "$store" rebind \
  --expected-generation G0001 --reason compact-successor \
  --owner-id host-owner --host-id codex --host-session-id session-a \
  --controller-id hc-h1-controller --claim-id "$claim_id" \
  --explicit-run-root "$run_root" --repository-identity "$worktree" \
  --git-common-directory-identity "$common" --worktree-identity "$worktree" \
  --activation-event-id activation-a2 --activation-receipt activation-receipt-a2 \
  --continuity-generation G0002 --continuity-receipt "$receipt_two" >/dev/null
second="$(run_hook "$plugin_data" "$event" "$hostile")"
assert_result "$second" 'value["status"] == "INVALIDATED" and value["continue"] is False' \
  'post-successor compact did not invalidate and stop'
second_token="$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["invalidation"])' "$second")"
[ "$second_token" != "$first_token" ] \
  || fail 'post-successor compact reused the prior invalidation token'
[ "$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["event_id"])' "$second")" != \
    "$("${py[@]}" -c 'import json,sys;print(json.loads(sys.argv[1])["event_id"])' "$first")" ] \
  || fail 'post-successor compact reused the prior event identity'

printf 'codex-compact-interlock.test: ok (fixed namespace + H0 binding + compact stop)\n'
