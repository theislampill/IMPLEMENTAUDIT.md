#!/usr/bin/env bash
# R36 black-box state-family acceptance.  The fixture and mutant self-checks
# keep the oracle honest independently of the canonical production helper.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
canonical_helper="$repo_root/skills/implementaudit/scripts/apply-observed-mutation.sh"
helper="$canonical_helper"
if [ -n "${PYTHON:-}" ]; then python_bin="$PYTHON"
elif command -v python >/dev/null 2>&1; then python_bin=python
elif command -v python3 >/dev/null 2>&1; then python_bin=python3
else printf 'observation-bound-mutation-integrity: Python is required\n' >&2; exit 1; fi
tmp="$(mktemp -d)"
owned_background_pids=()
owned_release_path=
cleanup_test_state() {
  local pid ticks
  [ -z "$owned_release_path" ] || : >"$owned_release_path" 2>/dev/null || true
  for pid in "${owned_background_pids[@]}"; do
    ticks=0
    while kill -0 "$pid" 2>/dev/null && [ "$ticks" -lt 250 ]; do sleep .02; ticks=$((ticks+1)); done
    if kill -0 "$pid" 2>/dev/null; then kill "$pid" 2>/dev/null || true; fi
    wait "$pid" 2>/dev/null || true
  done
  rm -rf -- "$tmp"
}
trap cleanup_test_state EXIT
fixture_repo="$tmp/repository"
run_root="$fixture_repo/.IMPLEMENTAUDIT/r36"
outside="$tmp/existing-outside-target"
phase_counter=0
prepared_phase=
prepared_step=1
helper_api=v2

fail() { printf 'observation-bound-mutation-integrity: %s\n' "$*" >&2; exit 1; }
status_exit() { case "$1" in COMMITTED|NO_CHANGE) echo 0;; REJECTED_NO_MUTATION) echo 64;; CONFLICT_REBASE) echo 65;; MUTATION_FAILED_NO_STATE_CHANGE) echo 70;; MUTATION_FAILED_ROLLED_BACK) echo 71;; POST_STATE_MISMATCH_ROLLED_BACK) echo 72;; RECOVERY_REQUIRED) echo 73;; ROLLBACK_CONFLICT) echo 74;; ROLLBACK_FAILED_WITH_RESIDUE) echo 75;; POST_COMMIT_DRIFT) echo 76;; UNSUPPORTED_OWNER_DECISION) echo 77;; *) fail "unknown status $1";; esac; }
wait_bounded() { local pid="$1" label="$2" ticks=0; while kill -0 "$pid" 2>/dev/null && [ "$ticks" -lt 500 ]; do sleep .02; ticks=$((ticks+1)); done; if kill -0 "$pid" 2>/dev/null; then kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; fail "$label timed out"; fi; wait "$pid" || true; }

write_hex() { "$python_bin" - "$1" "$2" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]); p.parent.mkdir(parents=True,exist_ok=True); p.write_bytes(bytes.fromhex(sys.argv[2]))
PY
}
assert_hex() { "$python_bin" - "$1" "$2" "$3" <<'PY'
import os,stat,sys
from pathlib import Path
label,path,want=sys.argv[1:]
if want == '@DIRECTORY':
 if not Path(path).is_dir(): raise SystemExit(f'{label}: expected a retained directory')
 raise SystemExit(0)
if want == '@SYMLINK_PATH':
 p=Path(path)
 if not any(q.is_symlink() for q in (p,*p.parents)): raise SystemExit(f'{label}: expected final or ancestor symlink')
 raise SystemExit(0)
p=Path(path)
try: mode=p.lstat().st_mode
except FileNotFoundError: mode=None
got=p.read_bytes() if mode is not None and stat.S_ISREG(mode) else None
expected=bytes.fromhex(want) if want != '-' else None
if got != expected: raise SystemExit(f'{label}: got={got!r} want={expected!r}')
PY
}
artifact() { local name="$1" hex="$2"; local p="$fixture_repo/artifacts/$name"; write_hex "$p" "$hex"; printf '%s\n' "$p"; }

setup() {
  local controller="${1:-}" claim_args=('r36-observation-bound-mutation')
  rm -rf -- "$fixture_repo"
  mkdir -p "$fixture_repo/artifacts"
  git -C "$fixture_repo" init -q
  git -C "$fixture_repo" config user.email r36-fixture@example.invalid
  git -C "$fixture_repo" config user.name r36-fixture
  printf 'R36 fixture repository\n' > "$fixture_repo/fixture-seed"
  git -C "$fixture_repo" add fixture-seed
  git -C "$fixture_repo" commit -q -m fixture
  [ -z "$controller" ] || claim_args=(--controller "$controller" 'r36-observation-bound-mutation')
  run_root="$(cd "$fixture_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs bash "$repo_root/skills/implementaudit/scripts/claim-run.sh" "${claim_args[@]}")"
  run_root="$fixture_repo/$run_root"
  for promised in STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md; do
    cp "$repo_root/skills/implementaudit/templates/$promised" "$run_root/$promised"
  done
  sed -i '/^| 1 |  |  | - |  |  |  | open |$/d' "$run_root/ROADMAP.md"
  if [ -n "$controller" ]; then
    "$python_bin" - "$run_root/STATE.md" "${run_root#$fixture_repo/}" \
      "$(git -C "$fixture_repo" rev-parse HEAD)" "$(git -C "$fixture_repo" rev-parse 'HEAD^{tree}')" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]); run,head,tree=sys.argv[2:]
s=p.read_text(encoding='utf-8')
s=s.replace('| Run root |  |',f'| Run root | `{run}` |')
s=s.replace('| Next action |  |','| Next action | exercise governed mutation under current continuity |')
anchor='| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|'
row=f'| e1 | new-session | 2026-08-13T00:00:00Z | repo at `{head}` / `{tree}` | yes | fixture reconciliation complete |'
p.write_text(s.replace(anchor,anchor+'\n'+row),encoding='utf-8')
PY
    receipt="$(cd "$fixture_repo" && bash "$repo_root/skills/implementaudit/scripts/claim-run.sh" \
      --resume-controller "$controller" --boundary new-session --epoch e1)" \
      || fail 'controller fixture continuity receipt mint failed'
    (cd "$fixture_repo" && bash "$repo_root/skills/implementaudit/scripts/claim-run.sh" \
      --verify-resume-receipt "$receipt") >/dev/null \
      || fail 'controller fixture continuity receipt verification failed'
  fi
  write_hex "$fixture_repo/target" 4142434445
  write_hex "$fixture_repo/a" 41; write_hex "$fixture_repo/b" 42
  write_hex "$fixture_repo/equal-one" 53414d45; write_hex "$fixture_repo/equal-two" 53414d45
  write_hex "$fixture_repo/sibling" 5349424c494e47; ln "$fixture_repo/sibling" "$fixture_repo/hardlink"
  write_hex "$fixture_repo/crlf" 6f6e650d0a74776f0d0a74687265650d0a
  write_hex "$fixture_repo/unicode" 7072656669782de282ac2de4b8ade696872d737566666978
  write_hex "$fixture_repo/binary" 0001ff7f42494e0d0a
  write_hex "$outside" 4f555453494445
  "$python_bin" - "$fixture_repo" <<'PY'
import os,sys
from pathlib import Path
r=Path(sys.argv[1])
try:
 os.symlink('target',r/'final-link'); (r/'real').mkdir(); (r/'real'/'child').write_bytes(b'child'); os.symlink('real',r/'parent-link',target_is_directory=True); (r/'symlink-capability').write_text('yes')
except OSError: (r/'symlink-capability').write_text('no')
PY
}

# Build authority from the independently expected operation and paths.  The
# helper receives only the phase/step selector plus operation evidence; it
# never receives the operation, source, or destination as caller authority.
prepare_authority() {
  local operation="$1" source="$2" destination="$3" phase_file run_rel
  phase_counter=$((phase_counter + 1)); prepared_phase="$phase_counter"; prepared_step=1
  run_rel="${run_root#$fixture_repo/}"
  mkdir -p "$run_root/phases"
  phase_file="$run_root/phases/phase-$prepared_phase.md"
  "$python_bin" - "$repo_root/fixtures/phase-validation/valid-full-spec.md" "$phase_file" "$run_rel" "$prepared_phase" "$operation" "$source" "$destination" <<'PY'
import json,sys
from pathlib import Path
source_file,out,run_rel,phase_text,operation,source,destination=sys.argv[1:]
phase=int(phase_text); destination=None if destination=='-' else destination
text=Path(source_file).read_text(encoding='utf-8')
text=text.replace('Phase: 1 of 3',f'Phase: {phase} of {phase}')
text=text.replace('Run root: .IMPLEMENTAUDIT/runs/add-settings-Xy9Zq1',f'Run root: {run_rel}')
text=text.replace('Baseline ref: abc123def456','Baseline ref: HEAD')
text=text.replace('Owner/source: src/routes/settings.ts','Owner/source: issue:#167')
authority=json.dumps({'operation':operation,'source':source,'destination':destination},separators=(',',':'))
needle='- Step 1: Create the settings route — target: src/routes/settings.ts (registerSettingsRoutes); change: add GET /api/settings handler behind requireAuth from src/middleware/auth.ts; verify: npm run build; expected: exit 0 with no errors'
text=text.replace(needle,needle+'\n  mutation-authority: '+authority)
paths=sorted([source]+([] if destination is None else [destination]),key=lambda x:x.encode())
scope=json.dumps({'in':paths,'out':['README.md']},separators=(',',':'))
text=text.replace('In scope: src/routes/settings.ts, tests/settings.test.ts, src/app.ts','In scope: R36 fixture mutation evidence\nMutation scope: '+scope)
Path(out).write_text(text,encoding='utf-8')
PY
  printf '| %s | R36 observation-bound mutation fixture |\n' "$prepared_phase" >> "$run_root/ROADMAP.md"
  if [ -f "$run_root/.controller" ]; then
    local controller epoch receipt
    controller="$(sed -n 's/^controller_id=//p' "$run_root/.controller")"
    epoch="e$((phase_counter + 1))"
    "$python_bin" - "$run_root/STATE.md" "$epoch" \
      "$(git -C "$fixture_repo" rev-parse HEAD)" "$(git -C "$fixture_repo" rev-parse 'HEAD^{tree}')" <<'PY'
import re,sys
from pathlib import Path
p=Path(sys.argv[1]); epoch,head,tree=sys.argv[2:]
s=p.read_text(encoding='utf-8')
s=re.sub(r'^Current epoch: .+$',f'Current epoch: {epoch}',s,flags=re.M)
s=re.sub(r'^\| Next action \|.*\|$',f'| Next action | execute phase {epoch[1:]} under refreshed continuity |',s,flags=re.M)
anchor='| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|'
row=f'| {epoch} | manual-resume | 2026-08-13T00:01:00Z | repo at `{head}` / `{tree}` | yes | phase authority and roadmap reconciled |'
p.write_text(s.replace(anchor,anchor+'\n'+row),encoding='utf-8')
PY
    receipt="$(cd "$fixture_repo" && bash "$repo_root/skills/implementaudit/scripts/claim-run.sh" \
      --resume-controller "$controller" --boundary manual-resume --epoch "$epoch")" \
      || fail 'phase continuity receipt mint failed'
    (cd "$fixture_repo" && bash "$repo_root/skills/implementaudit/scripts/claim-run.sh" \
      --verify-resume-receipt "$receipt") >/dev/null \
      || fail 'phase continuity receipt verification failed'
  fi
  bash "$repo_root/skills/implementaudit/scripts/validate-phase.sh" --mutation-authority "$phase_file" --phase "$prepared_phase" --step "$prepared_step" --repo-root "$fixture_repo" --run-root "$run_root" >/dev/null || fail "authority factory produced invalid phase $prepared_phase"
}

write_window_intent() {
  local state="$1" surface="$2" chain="$run_root/background/window-chain"
  local opened receipt closing_receipt opening_sha closing_sha closed_at=none
  mkdir -p "$chain"
  opened="$(git -C "$fixture_repo" rev-parse HEAD)"
  receipt="$chain/opening-identities.nul"
  (cd "$fixture_repo" && bash "$repo_root/skills/implementaudit/scripts/repo-state.sh" \
    window-identities --records --surface "$surface" >"$receipt") \
    || fail 'R36 window fixture opening receipt failed'
  opening_sha="$(sha256sum "$receipt" | awk '{print $1}')"
  closing_receipt="$chain/closing-identities.nul"; closing_sha=none
  if [ "$state" = closed ]; then
    touch "$chain/chain.done"
    (cd "$fixture_repo" && bash "$repo_root/skills/implementaudit/scripts/repo-state.sh" \
      window-identities --records --surface "$surface" >"$closing_receipt") \
      || fail 'R36 window fixture closing receipt failed'
    closing_sha="$(sha256sum "$closing_receipt" | awk '{print $1}')"
    closed_at="$opened"
  fi
  printf '%s\n' \
    'command: r36-window-fixture' \
    'owner/source: tests/observation-bound-mutation-integrity.test.sh' \
    'expected_completion_marker: chain.done' \
    'abort_containment_plan: fixture-only' \
    'poll_budget: 3' \
    'terminal_signal: chain.done' \
    'expected_duration: 20m' \
    'transport_timeout: 10m' \
    'launch_mode: detached' \
    'verification_window:' \
    "  - surfaces: [$surface]" \
    "    opened_at: $opened" \
    "    closed_at: $closed_at" \
    '    chain: window-chain' \
    "    state: $state" \
    '    opening_identity_receipt: opening-identities.nul' \
    "    opening_identity_sha256: $opening_sha" \
    "    closing_identity_receipt: $([ "$state" = closed ] && printf closing-identities.nul || printf none)" \
    "    closing_identity_sha256: $closing_sha" \
    >"$chain/launch-intent.md"
}

write_prepared_window_intent() {
  local surface="$1" chain="$run_root/background/window-chain"
  mkdir -p "$chain"
  printf '%s\n' \
    'verification_window:' \
    "  - surfaces: [$surface]" \
    '    opened_at: none' \
    '    closed_at: none' \
    '    chain: window-chain' \
    '    state: prepared' \
    '    opening_identity_receipt: none' \
    '    opening_identity_sha256: none' \
    '    closing_identity_receipt: none' \
    '    closing_identity_sha256: none' \
    >"$chain/launch-intent.md"
}

window_interlock_heldouts() {
  local pre cand derived barrier helper_pid transition_pid helper_exit transition_exit intent
  setup; write_window_intent open target
  pre="$(artifact window-open-pre 4142434445)"; cand="$(artifact window-open-candidate 4e4557)"
  invoke R36-WINDOW-open-intersection UNSUPPORTED_OWNER_DECISION replace target - "$cand" 4142434445 --preimage "$pre" --candidate "$cand"
  [ ! -e "$run_root/mutation-transactions" ] \
    || fail 'R36-WINDOW-open-intersection created transaction state before window refusal'

  setup; write_window_intent open 'docs/**'
  pre="$(artifact window-disjoint-pre 4142434445)"; cand="$(artifact window-disjoint-candidate 4e4557)"
  invoke R36-WINDOW-open-disjoint COMMITTED replace target - "$cand" 4e4557 --preimage "$pre" --candidate "$cand"

  setup; write_window_intent closed target
  pre="$(artifact window-closed-pre 4142434445)"; cand="$(artifact window-closed-candidate 4e4557)"
  invoke R36-WINDOW-closed COMMITTED replace target - "$cand" 4e4557 --preimage "$pre" --candidate "$cand"

  setup; mkdir -p "$run_root/background/window-chain"; printf 'verification_window: malformed\n' >"$run_root/background/window-chain/launch-intent.md"
  pre="$(artifact window-malformed-pre 4142434445)"; cand="$(artifact window-malformed-candidate 4e4557)"
  invoke R36-WINDOW-malformed UNSUPPORTED_OWNER_DECISION replace target - "$cand" 4142434445 --preimage "$pre" --candidate "$cand"

  # The R02 prepared→open publication cannot enter between R36's complete
  # intent scan and its product mutation: both governed writers hold the same
  # persistent gate. The opening receipt therefore captures the committed
  # post-state, never a stale pre-mutation identity.
  setup; write_prepared_window_intent target
  pre="$(artifact window-race-pre 4142434445)"; cand="$(artifact window-race-candidate 4e4557)"
  prepare_authority replace target -; derived="$(instrumented_helper)"; barrier="$tmp/window-scan-race"; mkdir "$barrier"
  IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR="$barrier" IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=window-scan-race \
    bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$prepared_phase" --step 1 --preimage "$pre" --candidate "$cand" \
    >"$barrier/helper.out" 2>"$barrier/helper.err" & helper_pid=$!
  owned_background_pids=("$helper_pid"); owned_release_path="$barrier/release"
  for _ in $(seq 1 500); do [ -f "$barrier/scanned" ] && break; kill -0 "$helper_pid" 2>/dev/null || break; sleep .02; done
  [ -f "$barrier/scanned" ] || { wait_bounded "$helper_pid" 'R36 window-scan helper'; fail 'R36 window-scan race did not reach protected boundary'; }
  [ ! -e "$run_root/mutation-transactions" ] || fail 'R36 window-scan race created transaction state before protected scan completed'
  intent="$run_root/background/window-chain/launch-intent.md"
  (cd "$fixture_repo" && bash "$repo_root/skills/implementaudit/scripts/check-evidence-anchor.sh" \
    --window-transition open "$intent" --entry 1 --repo-root "$fixture_repo") \
    >"$barrier/transition.out" 2>"$barrier/transition.err" & transition_pid=$!
  owned_background_pids+=("$transition_pid")
  sleep .2
  kill -0 "$transition_pid" 2>/dev/null || fail 'R36 window transition bypassed the held governed gate'
  [ ! -s "$barrier/transition.out" ] || fail 'R36 window transition published before mutation gate release'
  touch "$barrier/release"
  set +e; wait "$helper_pid"; helper_exit=$?; wait "$transition_pid"; transition_exit=$?; set -e
  owned_background_pids=(); owned_release_path=
  [ "$helper_exit" -eq 0 ] || fail "R36 window-scan helper exit=$helper_exit stderr=$(<"$barrier/helper.err")"
  [ "$transition_exit" -eq 0 ] || fail "R36 window transition exit=$transition_exit stderr=$(<"$barrier/transition.err")"
  assert_hex R36-WINDOW-race-target "$fixture_repo/target" 4e4557
  case_now="$(git -C "$fixture_repo" rev-parse HEAD)"
  (cd "$fixture_repo" && bash "$repo_root/skills/implementaudit/scripts/check-evidence-anchor.sh" --window "$intent" --now "$case_now") >/dev/null \
    || fail 'R36 window transition captured stale pre-mutation identity'
}
fixture_self_check() {
  setup
  # JSON paths are host-native (for example a Windows drive path under Git
  # Bash); containment is canonical rather than a POSIX string-prefix test.
  assert_reported_fixture_path "$fixture_repo/artifacts/../target" || fail 'fixture alternate-spelling containment failed'
  "$python_bin" - "$fixture_repo" <<'PY'
import os,sys
from pathlib import Path
r=Path(sys.argv[1])
assert (r/'target').read_bytes()==b'ABCDE'
assert (r/'crlf').read_bytes()==b'one\r\ntwo\r\nthree\r\n'
assert (r/'unicode').read_bytes()=='prefix-€-中文-suffix'.encode()
assert (r/'binary').read_bytes()==b'\0\1\xff\x7fBIN\r\n'
assert os.stat(r/'sibling').st_ino==os.stat(r/'hardlink').st_ino
claim=(r/'.IMPLEMENTAUDIT'/'runs')
assert len(list(claim.glob('r36-observation-bound-mutation-*/.claimed')))==1
print('R36_FIXTURE_SELF_CHECK=PASS bytes=raw topology=hardlink,symlink-or-declared-unsupported')
PY
}

unsupported_external_gate_replacement_evidence() {
  "$python_bin" - "$tmp" <<'PY'
import os,sys
from pathlib import Path
if os.name == 'nt':
 print('R36_POSIX_GATE_REPLACEMENT=NOT_APPLICABLE')
 raise SystemExit(0)
import fcntl
root=Path(sys.argv[1])/'posix-gate-replacement'; root.mkdir()
gate=root/'namespace.gate'; gate.write_bytes(b'old')
old=os.open(gate,os.O_RDWR); fcntl.flock(old,fcntl.LOCK_EX)
old_identity=os.fstat(old)
replacement=root/'replacement'; replacement.write_bytes(b'new'); os.replace(replacement,gate)
new=os.open(gate,os.O_RDWR); fcntl.flock(new,fcntl.LOCK_EX|fcntl.LOCK_NB)
new_identity=os.fstat(new)
if (old_identity.st_dev,old_identity.st_ino)==(new_identity.st_dev,new_identity.st_ino):
 raise SystemExit('replacement did not create the required distinct inode witness')
fcntl.flock(new,fcntl.LOCK_UN); os.close(new); fcntl.flock(old,fcntl.LOCK_UN); os.close(old)
print('R36_POSIX_GATE_REPLACEMENT=UNSUPPORTED_EXTERNAL_WRITER_WITNESS')
PY
}

# The fault/rendezvous driver is mechanically derived from the authoritative
# helper.  Production contains only inert structural hook markers; this copy
# receives test-only code by insertion and is never installed or packaged.
instrumented_helper() {
  local derived="$tmp/instrumented-apply-observed-mutation.sh"
  "$python_bin" - "$canonical_helper" "$derived" <<'PY' || return 1
import sys
from pathlib import Path
canonical=Path(sys.argv[1]); source=canonical.read_text(encoding='utf-8')
script_dir_line='script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"'
derived_dir_line='script_dir='+repr(str(canonical.parent))
if source.count(script_dir_line) != 1: raise SystemExit('R36 sibling-script locator count is not exactly one')
source=source.replace(script_dir_line,derived_dir_line)
needle='    # R36_INSTRUMENT_INSERT\n'
if source.count(needle) != 1: raise SystemExit('R36 instrument marker count is not exactly one')
insert="""    # test-only insertion: absent from authoritative helper after strip\n    global bar,fault\n    if phase == 'pre-transaction':\n        import os\n        bar=os.getenv('IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR')\n        fault=os.getenv('IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE')\n        delay_mutated=os.getenv('IMPLEMENTAUDIT_R36_TEST_DELAY_MUTATED')=='1'\n        if delay_mutated:\n            original_notify=notify_mutated; delayed=[]\n            def queue_mutated(callback,path,effect): delayed.append((callback,path,effect))\n            globals()['notify_mutated']=queue_mutated\n        if fault == 'io-after-displacement':\n            original_open=Path.open\n            def fail_stage_open(self,*args,**kwargs):\n                if self.name == 'stage.bin' and args and 'x' in args[0]: raise OSError(28,'injected ENOSPC')\n                return original_open(self,*args,**kwargs)\n            Path.open=fail_stage_open\n        original_os_fsync=os.fsync; file_state={'authority_failed':False,'result_failed':False,'owner_failed':False}\n        def fail_selected_file_fsync(fd):\n            authority_fault=fault in {'authority-file-fsync','authority-cleanup-fails','authority-result-fsync-fails'} and path_identity(AUTHORITY).get('kind')=='regular' and not file_state['authority_failed']\n            result_fault=fault=='authority-result-fsync-fails' and file_state['authority_failed'] and path_identity(RESULT).get('kind')=='regular' and not file_state['result_failed']\n            owner_fault=fault=='lock-owner-file-fsync' and any(path_identity(p/'owner').get('kind')=='regular' for p in lock_paths) and not file_state['owner_failed']\n            if authority_fault:\n                file_state['authority_failed']=True; raise OSError(28,'injected authority file fsync failure')\n            if result_fault:\n                file_state['result_failed']=True; raise OSError(28,'injected result file fsync failure')\n            if owner_fault:\n                file_state['owner_failed']=True; raise OSError(28,'injected lock owner file fsync failure')\n            return original_os_fsync(fd)\n        os.fsync=fail_selected_file_fsync\n        if fault in {'authority-cleanup-fails','authority-result-fsync-fails'}:\n            original_unlink=os.unlink\n            def fail_authority_unlink(path):\n                if Path(path)==AUTHORITY: raise OSError(13,'injected authority cleanup failure')\n                return original_unlink(path)\n            os.unlink=fail_authority_unlink\n        original_sync=sync_directory_raw; injected={'done':False}\n        def fail_selected_sync(path):\n            trigger=(fault=='fsync-after-displacement' and path_identity(BACKUP).get('kind')=='regular' and path_identity(SOURCE).get('kind')=='absent') or (fault=='fsync-after-destination' and operation=='move' and path_identity(DESTINATION).get('kind')=='regular') or (fault=='init-authority-fsync' and path==TX and path_identity(AUTHORITY).get('kind')=='regular') or (fault=='lock-root-parent-fsync' and path==LOCK_PARENT and path_identity(LOCK_ROOT).get('kind')=='directory') or (fault=='lock-mkdir-parent-fsync' and path==LOCK_ROOT and any(path_identity(p).get('kind')=='directory' for p in lock_paths))\n            if trigger and not injected['done']:\n                injected['done']=True; raise OSError(28,'injected directory fsync failure')\n            value=original_sync(path)\n            if delay_mutated and delayed:\n                pending=list(delayed); delayed.clear()\n                for callback,item,effect in pending: original_notify(callback,item,effect)\n            return value\n        globals()['sync_directory_raw']=fail_selected_sync\n    if phase == 'move-destination-published' and fault == 'move-after-destination':\n        b=Path(bar); b.mkdir(parents=True,exist_ok=True); (b/'paused').touch()\n        for _ in range(500):\n            if (b/'release').exists(): return\n            time.sleep(.02)\n        raise RuntimeError('timeout')\n"""
extra="""    if phase == 'pre-transaction' and fault == 'terminal-result-fsync-after-rollback-failure':\n        original_extra_open=Path.open; original_extra_link=os.link; original_extra_fsync=os.fsync\n        def fail_stage_write(self,*args,**kwargs):\n            if self.name == 'stage.bin' and args and 'x' in args[0]: raise OSError(28,'injected stage write failure')\n            return original_extra_open(self,*args,**kwargs)\n        def fail_rollback_link(source,destination,*args,**kwargs):\n            if Path(source)==BACKUP and Path(destination)==SOURCE: raise OSError(5,'injected rollback link failure')\n            return original_extra_link(source,destination,*args,**kwargs)\n        def fail_terminal_result_fsync(fd):\n            if path_identity(RESULT).get('kind')=='regular': raise OSError(28,'injected terminal result fsync failure')\n            return original_extra_fsync(fd)\n        Path.open=fail_stage_write; os.link=fail_rollback_link; os.fsync=fail_terminal_result_fsync\n    if phase == 'locks-acquired' and fault in {'lock-aba','lock-release-destination-race'}:\n        b=Path(bar); b.mkdir(parents=True,exist_ok=True)\n        if fault == 'lock-release-destination-race': (b/'lock-path').write_text(str(held[-1]['released_path']),encoding='utf-8')\n        (b/'paused').touch()\n        for _ in range(500):\n            if (b/'release').exists(): return\n            time.sleep(.02)\n        raise RuntimeError('timeout')\n"""
extra2="""    if phase == 'pre-transaction' and fault in {'lock-post-check-race','lock-release-record-race','lock-directory-aba'}:\n        def pause_release_race(lock_path):\n            lock_path=Path(lock_path); b=Path(bar); b.mkdir(parents=True,exist_ok=True); (b/'lock-path').write_text(str(lock_path),encoding='utf-8'); (b/'owner-token').write_text(owner,encoding='ascii'); (b/'paused').touch()\n            for _ in range(500):\n                if (b/'release').exists(): return\n                time.sleep(.02)\n            raise RuntimeError('timeout')\n        globals()['pause_release_race']=pause_release_race\n    if phase == 'pre-transaction' and fault == 'lock-directory-aba-peer':\n        def pause_peer(name,release):\n            b=Path(bar); b.mkdir(parents=True,exist_ok=True); (b/name).touch()\n            for _ in range(500):\n                if (b/release).exists(): return\n                time.sleep(.02)\n            raise RuntimeError('timeout')\n        globals()['pause_peer']=pause_peer\n    if phase == 'locks-acquired' and fault == 'lock-directory-aba': globals()['pause_release_race'](held[-1]['public_path'])\n    if phase == 'locks-acquired' and fault == 'lock-directory-aba-peer': globals()['pause_peer']('acquired','replace')\n    if phase == 'lock-release-mismatch' and fault == 'lock-directory-aba-peer': globals()['pause_peer']('mismatch','finish')\n    if phase == 'lock-release-published' and fault == 'lock-post-check-race': globals()['pause_release_race'](held[-1]['public_path'])\n    if phase == 'lock-release-published' and fault == 'lock-release-record-race': globals()['pause_release_race'](held[-1]['released_path'])\n"""
extra3="""    if phase == 'pre-transaction' and fault == 'gate-unlock-fails':\n        if os.name == 'nt':\n            original_gate_unlock=msvcrt.locking\n            def fail_gate_unlock(fd,mode,count):\n                if mode == msvcrt.LK_UNLCK: raise OSError(5,'injected gate unlock failure')\n                return original_gate_unlock(fd,mode,count)\n            msvcrt.locking=fail_gate_unlock\n        else:\n            original_gate_unlock=fcntl.flock\n            def fail_gate_unlock(fd,op):\n                if op == fcntl.LOCK_UN: raise OSError(5,'injected gate unlock failure')\n                return original_gate_unlock(fd,op)\n            fcntl.flock=fail_gate_unlock\n"""
extra4="""    if phase == 'window-scan-complete' and fault == 'window-scan-race':\n        b=Path(bar); b.mkdir(parents=True,exist_ok=True); (b/'scanned').touch()\n        for _ in range(500):\n            if (b/'release').exists(): return\n            time.sleep(.02)\n        raise RuntimeError('timeout')\n"""
extra5="""    if phase == 'pre-transaction' and fault == 'same-authority-pretransaction': wait('ready')\n"""
Path(sys.argv[2]).write_text(source.replace(needle,needle+insert+extra+extra2+extra3+extra4+extra5),encoding='utf-8')
PY
  chmod +x "$derived" || return 1
  "$python_bin" - "$canonical_helper" "$derived" <<'PY' || return 1
import sys
from pathlib import Path
canonical,derived=map(Path,sys.argv[1:]); text=derived.read_text(encoding='utf-8')
script_dir_line='script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"'
derived_dir_line='script_dir='+repr(str(canonical.parent))
insert="""    # test-only insertion: absent from authoritative helper after strip\n    global bar,fault\n    if phase == 'pre-transaction':\n        import os\n        bar=os.getenv('IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR')\n        fault=os.getenv('IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE')\n        delay_mutated=os.getenv('IMPLEMENTAUDIT_R36_TEST_DELAY_MUTATED')=='1'\n        if delay_mutated:\n            original_notify=notify_mutated; delayed=[]\n            def queue_mutated(callback,path,effect): delayed.append((callback,path,effect))\n            globals()['notify_mutated']=queue_mutated\n        if fault == 'io-after-displacement':\n            original_open=Path.open\n            def fail_stage_open(self,*args,**kwargs):\n                if self.name == 'stage.bin' and args and 'x' in args[0]: raise OSError(28,'injected ENOSPC')\n                return original_open(self,*args,**kwargs)\n            Path.open=fail_stage_open\n        original_os_fsync=os.fsync; file_state={'authority_failed':False,'result_failed':False,'owner_failed':False}\n        def fail_selected_file_fsync(fd):\n            authority_fault=fault in {'authority-file-fsync','authority-cleanup-fails','authority-result-fsync-fails'} and path_identity(AUTHORITY).get('kind')=='regular' and not file_state['authority_failed']\n            result_fault=fault=='authority-result-fsync-fails' and file_state['authority_failed'] and path_identity(RESULT).get('kind')=='regular' and not file_state['result_failed']\n            owner_fault=fault=='lock-owner-file-fsync' and any(path_identity(p/'owner').get('kind')=='regular' for p in lock_paths) and not file_state['owner_failed']\n            if authority_fault:\n                file_state['authority_failed']=True; raise OSError(28,'injected authority file fsync failure')\n            if result_fault:\n                file_state['result_failed']=True; raise OSError(28,'injected result file fsync failure')\n            if owner_fault:\n                file_state['owner_failed']=True; raise OSError(28,'injected lock owner file fsync failure')\n            return original_os_fsync(fd)\n        os.fsync=fail_selected_file_fsync\n        if fault in {'authority-cleanup-fails','authority-result-fsync-fails'}:\n            original_unlink=os.unlink\n            def fail_authority_unlink(path):\n                if Path(path)==AUTHORITY: raise OSError(13,'injected authority cleanup failure')\n                return original_unlink(path)\n            os.unlink=fail_authority_unlink\n        original_sync=sync_directory_raw; injected={'done':False}\n        def fail_selected_sync(path):\n            trigger=(fault=='fsync-after-displacement' and path_identity(BACKUP).get('kind')=='regular' and path_identity(SOURCE).get('kind')=='absent') or (fault=='fsync-after-destination' and operation=='move' and path_identity(DESTINATION).get('kind')=='regular') or (fault=='init-authority-fsync' and path==TX and path_identity(AUTHORITY).get('kind')=='regular') or (fault=='lock-root-parent-fsync' and path==LOCK_PARENT and path_identity(LOCK_ROOT).get('kind')=='directory') or (fault=='lock-mkdir-parent-fsync' and path==LOCK_ROOT and any(path_identity(p).get('kind')=='directory' for p in lock_paths))\n            if trigger and not injected['done']:\n                injected['done']=True; raise OSError(28,'injected directory fsync failure')\n            value=original_sync(path)\n            if delay_mutated and delayed:\n                pending=list(delayed); delayed.clear()\n                for callback,item,effect in pending: original_notify(callback,item,effect)\n            return value\n        globals()['sync_directory_raw']=fail_selected_sync\n    if phase == 'move-destination-published' and fault == 'move-after-destination':\n        b=Path(bar); b.mkdir(parents=True,exist_ok=True); (b/'paused').touch()\n        for _ in range(500):\n            if (b/'release').exists(): return\n            time.sleep(.02)\n        raise RuntimeError('timeout')\n"""
extra="""    if phase == 'pre-transaction' and fault == 'terminal-result-fsync-after-rollback-failure':\n        original_extra_open=Path.open; original_extra_link=os.link; original_extra_fsync=os.fsync\n        def fail_stage_write(self,*args,**kwargs):\n            if self.name == 'stage.bin' and args and 'x' in args[0]: raise OSError(28,'injected stage write failure')\n            return original_extra_open(self,*args,**kwargs)\n        def fail_rollback_link(source,destination,*args,**kwargs):\n            if Path(source)==BACKUP and Path(destination)==SOURCE: raise OSError(5,'injected rollback link failure')\n            return original_extra_link(source,destination,*args,**kwargs)\n        def fail_terminal_result_fsync(fd):\n            if path_identity(RESULT).get('kind')=='regular': raise OSError(28,'injected terminal result fsync failure')\n            return original_extra_fsync(fd)\n        Path.open=fail_stage_write; os.link=fail_rollback_link; os.fsync=fail_terminal_result_fsync\n    if phase == 'locks-acquired' and fault in {'lock-aba','lock-release-destination-race'}:\n        b=Path(bar); b.mkdir(parents=True,exist_ok=True)\n        if fault == 'lock-release-destination-race': (b/'lock-path').write_text(str(held[-1]['released_path']),encoding='utf-8')\n        (b/'paused').touch()\n        for _ in range(500):\n            if (b/'release').exists(): return\n            time.sleep(.02)\n        raise RuntimeError('timeout')\n"""
extra2="""    if phase == 'pre-transaction' and fault in {'lock-post-check-race','lock-release-record-race','lock-directory-aba'}:\n        def pause_release_race(lock_path):\n            lock_path=Path(lock_path); b=Path(bar); b.mkdir(parents=True,exist_ok=True); (b/'lock-path').write_text(str(lock_path),encoding='utf-8'); (b/'owner-token').write_text(owner,encoding='ascii'); (b/'paused').touch()\n            for _ in range(500):\n                if (b/'release').exists(): return\n                time.sleep(.02)\n            raise RuntimeError('timeout')\n        globals()['pause_release_race']=pause_release_race\n    if phase == 'pre-transaction' and fault == 'lock-directory-aba-peer':\n        def pause_peer(name,release):\n            b=Path(bar); b.mkdir(parents=True,exist_ok=True); (b/name).touch()\n            for _ in range(500):\n                if (b/release).exists(): return\n                time.sleep(.02)\n            raise RuntimeError('timeout')\n        globals()['pause_peer']=pause_peer\n    if phase == 'locks-acquired' and fault == 'lock-directory-aba': globals()['pause_release_race'](held[-1]['public_path'])\n    if phase == 'locks-acquired' and fault == 'lock-directory-aba-peer': globals()['pause_peer']('acquired','replace')\n    if phase == 'lock-release-mismatch' and fault == 'lock-directory-aba-peer': globals()['pause_peer']('mismatch','finish')\n    if phase == 'lock-release-published' and fault == 'lock-post-check-race': globals()['pause_release_race'](held[-1]['public_path'])\n    if phase == 'lock-release-published' and fault == 'lock-release-record-race': globals()['pause_release_race'](held[-1]['released_path'])\n"""
extra3="""    if phase == 'pre-transaction' and fault == 'gate-unlock-fails':\n        if os.name == 'nt':\n            original_gate_unlock=msvcrt.locking\n            def fail_gate_unlock(fd,mode,count):\n                if mode == msvcrt.LK_UNLCK: raise OSError(5,'injected gate unlock failure')\n                return original_gate_unlock(fd,mode,count)\n            msvcrt.locking=fail_gate_unlock\n        else:\n            original_gate_unlock=fcntl.flock\n            def fail_gate_unlock(fd,op):\n                if op == fcntl.LOCK_UN: raise OSError(5,'injected gate unlock failure')\n                return original_gate_unlock(fd,op)\n            fcntl.flock=fail_gate_unlock\n"""
extra4="""    if phase == 'window-scan-complete' and fault == 'window-scan-race':\n        b=Path(bar); b.mkdir(parents=True,exist_ok=True); (b/'scanned').touch()\n        for _ in range(500):\n            if (b/'release').exists(): return\n            time.sleep(.02)\n        raise RuntimeError('timeout')\n"""
extra5="""    if phase == 'pre-transaction' and fault == 'same-authority-pretransaction': wait('ready')\n"""
if text.replace(insert,'').replace(extra,'').replace(extra2,'').replace(extra3,'').replace(extra4,'').replace(extra5,'').replace(derived_dir_line,script_dir_line) != canonical.read_text(encoding='utf-8'): raise SystemExit('instrumented copy does not strip byte-equal')
PY
  printf '%s\n' "$derived"
}

identity_json() { "$python_bin" - "$1" <<'PY'
import hashlib,json,stat,sys
from pathlib import Path
p=Path(sys.argv[1])
try:
 unsafe=any(q.is_symlink() for q in (p,*p.parents))
 mode=p.lstat().st_mode
except FileNotFoundError: unsafe=True; mode=0
if unsafe or not stat.S_ISREG(mode): print('null')
else:
 b=p.read_bytes(); print(json.dumps({'sha256':hashlib.sha256(b).hexdigest(),'byte_length':len(b)},separators=(',',':')))
PY
}
post_identities_json() { "$python_bin" - "$fixture_repo" "$1" "$2" <<'PY'
import json,stat,sys
from pathlib import Path
import hashlib
r,target,dest=map(str,sys.argv[1:])
def ident(path):
 p=Path(path)
 try:
  unsafe=any(q.is_symlink() for q in (p,*p.parents)); mode=p.lstat().st_mode
 except FileNotFoundError: return None
 if unsafe or not stat.S_ISREG(mode): return None
 b=p.read_bytes(); return {'sha256':hashlib.sha256(b).hexdigest(),'byte_length':len(b)}
d={target:ident(Path(r)/target)}
if dest != '-': d[dest]=ident(Path(r)/dest)
print(json.dumps(d,separators=(',',':')))
PY
}
assert_response_v1() { "$python_bin" - "$@" <<'PY'
import json,sys
label,status,operation,source,dest,targets,pre,candidate,post,post_identities,out=sys.argv[1:]
lines=[x for x in out.splitlines() if x.strip()]
if len(lines)!=1: raise SystemExit(f'{label}: expected one stdout JSON object, got {len(lines)}')
r=json.loads(lines[0]); required={'schema','operation','status','source_path','destination_path','targets','pre_identity','candidate_identity','post_identity','post_identities','token','journal_path','residue_paths'}
if set(r)!=required: raise SystemExit(f'{label}: schema keys differ: got={sorted(r)}')
want={'schema':'implementaudit.observation_bound_mutation.v1','operation':operation,'status':status,'source_path':source,'destination_path':None if dest=='-' else dest,'targets':json.loads(targets),'pre_identity':json.loads(pre),'candidate_identity':json.loads(candidate),'post_identity':json.loads(post),'post_identities':json.loads(post_identities)}
for k,v in want.items():
 if r[k]!=v: raise SystemExit(f'{label}: {k} got={r[k]!r} want={v!r}')
residual={'RECOVERY_REQUIRED','ROLLBACK_CONFLICT','ROLLBACK_FAILED_WITH_RESIDUE','POST_COMMIT_DRIFT'}
if status in residual:
 if not isinstance(r['token'],str) or not r['token'] or not isinstance(r['journal_path'],str) or not r['journal_path'] or not isinstance(r['residue_paths'],list) or not r['residue_paths'] or not all(isinstance(x,str) and x for x in r['residue_paths']): raise SystemExit(f'{label}: residual status lacks token/journal/residue')
else:
 if r['token'] is not None or r['journal_path'] is not None or r['residue_paths'] != []: raise SystemExit(f'{label}: non-residual status leaked recovery state')
print(json.dumps({'token':r['token'],'journal_path':r['journal_path'],'residue_paths':r['residue_paths']}))
PY
}
assert_response_v2() { "$python_bin" - "$@" "$fixture_repo" <<'PY'
import hashlib,json,re,sys
from pathlib import Path,PurePosixPath
label,status,operation,source,dest,pre,candidate,post,post_identities,phase,step,out_path,fixture_root=sys.argv[1:]
out=Path(out_path).read_text(encoding='utf-8')
lines=[x for x in out.splitlines() if x.strip()]
if len(lines)!=1: raise SystemExit(f'{label}: expected one stdout JSON object, got {len(lines)}')
r=json.loads(lines[0]); required={'schema','transaction_id','claim_id','phase','step','authority_binding_sha256','coordination_scope','operation','status','reason_code','source_path','destination_path','pre_identities','candidate_identities','post_identities','planned_effect_set','planned_effect_set_sha256','actual_effect_set','residue'}
if set(r)!=required: raise SystemExit(f'{label}: v2 schema keys differ: got={sorted(r)}')
if r['schema']!='implementaudit.observation_bound_mutation.v2' or r['status']!=status or r['operation']!=operation: raise SystemExit(f'{label}: schema/status/operation mismatch')
if r['coordination_scope']!='GOVERNED_HELPER_ROUTED_WRITERS_ONLY': raise SystemExit(f'{label}: coordination scope overclaims writer exclusion: {r.get("coordination_scope")!r}')
if r['source_path']!=source or r['destination_path']!=(None if dest=='-' else dest): raise SystemExit(f'{label}: phase-derived paths mismatch')
if r['phase']!=int(phase) or r['step']!=int(step): raise SystemExit(f'{label}: phase/step mismatch')
if not re.fullmatch(r'[0-9a-f]{32}',r['claim_id']) or not re.fullmatch(r'[0-9a-f]{64}',r['authority_binding_sha256']): raise SystemExit(f'{label}: claim/authority binding malformed')
def simple(value):
 if value is None or value.get('kind')=='absent': return None
 if value.get('kind')!='regular': return None
 return {'sha256':value.get('sha256'),'byte_length':value.get('byte_length')}
def keyed(rows):
 if not isinstance(rows,list): raise SystemExit(f'{label}: identity set is not a list')
 out={}
 for row in rows:
  if set(row)!= {'path','identity'} or row['path'] in out: raise SystemExit(f'{label}: malformed/duplicate identity row')
  out[row['path']]=simple(row['identity'])
 return out
pre_rows=keyed(r['pre_identities']); cand_rows=keyed(r['candidate_identities']); post_rows=keyed(r['post_identities'])
if pre_rows.get(source)!=json.loads(pre): raise SystemExit(f'{label}: pre identity mismatch {pre_rows!r}')
want_candidate=json.loads(candidate)
if want_candidate is not None and want_candidate not in cand_rows.values(): raise SystemExit(f'{label}: candidate identity mismatch {cand_rows!r}')
want_post=json.loads(post_identities)
if post_rows != want_post: raise SystemExit(f'{label}: post identity set mismatch got={post_rows!r} want={want_post!r}')
planned=r['planned_effect_set']
if not isinstance(planned,list): raise SystemExit(f'{label}: planned effects are not a list')
seen=set(); allowed={}; roles={}
for row in planned:
 if set(row)!= {'scope','path','roles','allowed_effects','retention'}: raise SystemExit(f'{label}: malformed planned effect')
 key=(row['scope'],row['path'])
 if key in seen or row['roles']!=sorted(set(row['roles'])) or row['allowed_effects']!=sorted(set(row['allowed_effects'])): raise SystemExit(f'{label}: noncanonical planned effect')
 seen.add(key); allowed[key]=set(row['allowed_effects']); roles[key]=set(row['roles'])
digest=hashlib.sha256(json.dumps(planned,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
if r['planned_effect_set_sha256']!=digest: raise SystemExit(f'{label}: planned-effect digest mismatch')
actual_by={}
actual_rows={}
for index,row in enumerate(r['actual_effect_set'],1):
 if set(row)!= {'sequence','scope','path','effect','before','after','outcome'}: raise SystemExit(f'{label}: malformed actual effect')
 if row['sequence']!=index or row['outcome'] not in {'applied','not-applied'}: raise SystemExit(f'{label}: noncanonical actual-effect sequence/outcome')
 if row['effect'] not in allowed.get((row['scope'],row['path']),set()): raise SystemExit(f'{label}: actual effect escaped planned set: {row!r}')
 actual_rows.setdefault((row['scope'],row['path']),[]).append(row)
 if row['outcome']=='applied': actual_by.setdefault((row['scope'],row['path']),[]).append(row['effect'])
if status in {'COMMITTED','MUTATION_FAILED_ROLLED_BACK','POST_STATE_MISMATCH_ROLLED_BACK','RECOVERY_REQUIRED','ROLLBACK_CONFLICT','ROLLBACK_FAILED_WITH_RESIDUE','POST_COMMIT_DRIFT'}:
 if not isinstance(r['transaction_id'],str) or not r['transaction_id']: raise SystemExit(f'{label}: effectful result lacks transaction id')
if status in {'RECOVERY_REQUIRED','ROLLBACK_CONFLICT','ROLLBACK_FAILED_WITH_RESIDUE','POST_COMMIT_DRIFT'}:
 if not isinstance(r['residue'],list) or not r['residue']: raise SystemExit(f'{label}: blocking result lacks residue')
else:
 if r['residue']!=[]: raise SystemExit(f'{label}: terminal clean result retained residue')
 if r['transaction_id'] is not None:
  for key,path_roles in roles.items():
   effects=actual_by.get(key,[])
   required=None
   if 'path-lock' in path_roles and 'mkdir' in effects: required='replace'
   elif 'journal' in path_roles and 'replace' in effects: required='unlink'
   elif 'journal-temp' in path_roles and 'create' in effects: required='replace'
   elif 'backup' in path_roles and any(x in effects for x in ('link','replace')): required='unlink'
   elif 'stage' in path_roles and 'create' in effects: required='unlink'
   elif 'result' in path_roles: required='fsync'
   if required is not None and required not in effects: raise SystemExit(f'{label}: clean result omitted {required} for {key}')
  released=sum('replace' in actual_by.get(key,[]) for key,value in roles.items() if 'path-lock' in value)
  retained=sum('replace' in actual_by.get(key,[]) for key,value in roles.items() if 'released-lock-record' in value)
  if released!=retained: raise SystemExit(f'{label}: durable lock-release mismatch: released={released} retained={retained}')
if r['transaction_id'] is not None and planned:
 result_paths=[key[1] for key,value in roles.items() if 'result' in value]
 if len(result_paths)!=1: raise SystemExit(f'{label}: missing unique result owner')
 result_file=Path(fixture_root)/PurePosixPath(result_paths[0])
 if not result_file.is_file() or json.loads(result_file.read_text(encoding='utf-8'))!=r: raise SystemExit(f'{label}: durable result.json missing or differs from stdout')
 for key,rows in actual_rows.items():
  for row in rows:
   if row['outcome']!='applied' or row['effect'] not in {'create','mkdir','link','replace','unlink','rmdir'}: continue
   parent=('repo',str(PurePosixPath(row['path']).parent))
   later=[x for x in actual_rows.get(parent,[]) if x['outcome']=='applied' and x['effect']=='fsync' and x['sequence']>row['sequence']]
   if not later: raise SystemExit(f'{label}: mutation lacks later parent-directory fsync: {row!r}')
 journal_temp=[row for key,value in roles.items() if 'journal-temp' in value for row in actual_rows.get(key,[]) if row['outcome']=='applied']
 if journal_temp:
  effects=[row['effect'] for row in journal_temp]
  if effects[:3]!=['create','write','fsync'] or 'replace' not in effects[3:]: raise SystemExit(f'{label}: journal physical write ordering incomplete: {effects!r}')
 result_rows=[row for key,value in roles.items() if 'result' in value for row in actual_rows.get(key,[]) if row['outcome']=='applied']
 if [row['effect'] for row in result_rows] != ['create','write','fsync']: raise SystemExit(f'{label}: result physical write ordering incomplete')
print(json.dumps({'transaction_id':r['transaction_id'],'planned_effect_set':planned,'residue':r['residue']}))
PY
}

# invoke asserts independently expected bytes; it does not derive pass criteria
# from helper output.  Arguments: label status op target destination candidate-file expected-post-hex, then helper args.
invoke() {
  local label="$1" status="$2" op="$3" target="$4" dest="$5" candidate="$6" expected="$7"; shift 7
  local source_path="$fixture_repo/$target" post_path="$fixture_repo/$target"
  # A committed move publishes at destination. Every rejected/conflict move
  # must instead prove the original source survived unchanged; deletion proves
  # absence at its actual source path, never at a detached sentinel.
  [ "$op" = move ] && [ "$status" = "COMMITTED" ] && post_path="$fixture_repo/$dest"
  local pre candidate_id post post_identities targets expected_exit stdout stderr actual offset region replacement constructed fault_stage forbidden=0
  pre="$(identity_json "$source_path")"; candidate_id="$(identity_json "$candidate")"
  if [ "$op" = patch ]; then
    offset= region= replacement=
    local argv=("$@") i
    for ((i=0; i<${#argv[@]}; i++)); do case "${argv[$i]}" in --offset) offset="${argv[$((i+1))]}";; --region) region="${argv[$((i+1))]}";; --replacement) replacement="${argv[$((i+1))]}";; esac; done
    constructed="$tmp/$label.constructed"
    if "$python_bin" - "$source_path" "$offset" "$region" "$replacement" "$constructed" <<'PY'
import sys
from pathlib import Path
source,offset_text,region,replacement,out=sys.argv[1:]
try: offset=int(offset_text)
except ValueError: raise SystemExit(1)
current=Path(source).read_bytes(); observed=Path(region).read_bytes(); new=Path(replacement).read_bytes()
if offset < 0 or not observed or current[offset:offset+len(observed)] != observed: raise SystemExit(1)
Path(out).write_bytes(current[:offset]+new+current[offset+len(observed):])
PY
    then candidate_id="$(identity_json "$constructed")"; else candidate_id=null; fi
  fi
  if [ "$dest" = - ]; then targets="[\"$target\"]"; else targets="[\"$target\",\"$dest\"]"; fi
  expected_exit="$(status_exit "$status")"; stdout="$tmp/$label.out"; stderr="$tmp/$label.err"
  [ "$op" = recover ] && forbidden=1
  local item; for item in "$@"; do
    case "$item" in --operation|--target|--destination|--journal|--token|--arbitrary-mutator) forbidden=1;; esac
  done
  if [ "$helper_api" = v2 ] && [ "$forbidden" -eq 1 ]; then
    if [ "$op" = recover ]; then
      set +e; bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --operation recover "$@" >"$stdout" 2>"$stderr"; actual=$?; set -e
    else
      prepare_authority "$op" "$target" "$dest"
      set +e; bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$prepared_phase" --step "$prepared_step" "$@" >"$stdout" 2>"$stderr"; actual=$?; set -e
    fi
    [ "$actual" -eq 64 ] || fail "$label: forbidden caller authority exit=$actual expected=64 stderr=$(<"$stderr")"
    assert_hex "$label visible state" "$post_path" "$expected"
    last_record='{}'
    return
  fi
  fault_stage="${IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE:-}"
  set +e
  if [ "$helper_api" = v2 ]; then
    prepare_authority "$op" "$target" "$dest"
    local evidence_args=("$@")
    if [ -n "$fault_stage" ]; then IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE="$fault_stage" bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$prepared_phase" --step "$prepared_step" "${evidence_args[@]}" >"$stdout" 2>"$stderr"; actual=$?
    else bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$prepared_phase" --step "$prepared_step" "${evidence_args[@]}" >"$stdout" 2>"$stderr"; actual=$?; fi
  elif [ -n "$fault_stage" ]; then IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE="$fault_stage" bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --operation "$op" --target "$target" "$@" >"$stdout" 2>"$stderr"; actual=$?
  else bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --operation "$op" --target "$target" "$@" >"$stdout" 2>"$stderr"; actual=$?; fi
  set -e
  [ "$actual" -eq "$expected_exit" ] || fail "$label: exit=$actual expected=$expected_exit stderr=$(<"$stderr")"
  [ -s "$stdout" ] || fail "$label: helper emitted no JSON stderr=$(<"$stderr")"
  post="$(identity_json "$post_path")"; post_identities="$(post_identities_json "$target" "$dest")"
  if [ "$helper_api" = v2 ]; then last_record="$(assert_response_v2 "$label" "$status" "$op" "$target" "$dest" "$pre" "$candidate_id" "$post" "$post_identities" "$prepared_phase" "$prepared_step" "$stdout")"
  else last_record="$(assert_response_v1 "$label" "$status" "$op" "$target" "$dest" "$targets" "$pre" "$candidate_id" "$post" "$post_identities" "$(<"$stdout")")"; fi
  assert_hex "$label visible state" "$post_path" "$expected"
}

# Test-only deterministic fault boundary.  The requested fault selects the
# injected failure, but it does not prove where it occurred: an independent
# observer reads the target while the call is paused.  The helper's only test
# synchronisation surface is a content-free `paused` file; it cannot satisfy
# the stage assertion by writing a claimed JSON outcome.
invoke_fault() {
  local stage="$1"; shift; local barrier="$tmp/fault-$stage" stdout="$tmp/fault-$stage.out" stderr="$tmp/fault-$stage.err" pid ticks=0 actual
  local label="$1" status="$2" op="$3" target="$4" dest="$5" candidate="$6" expected="$7" pre candidate_id post post_ids targets
  local canonical_saved="$helper" instrumented
  shift 7
  instrumented="$(instrumented_helper)"; helper="$instrumented"
  prepare_authority "$op" "$target" "$dest"
  local evidence_args=("$@")
  pre="$(identity_json "$fixture_repo/$target")"; candidate_id="$(identity_json "$candidate")"
  [ "$dest" = - ] && targets="[\"$target\"]" || targets="[\"$target\",\"$dest\"]"
  [ "$op" = patch ] && fail 'fault fixture only supports whole-file operations'
  rm -rf -- "$barrier"; mkdir "$barrier"
  # This actor is deliberately outside the helper process.  Its observations
  # (and, for mismatch/unsupported, its short owned write/restore transition)
  # are task evidence rather than helper-supplied fault claims.
  (set +e; IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR="$barrier" IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE="$stage" bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$prepared_phase" --step "$prepared_step" "${evidence_args[@]}" >"$stdout" 2>"$stderr"; echo $? >"$barrier/exit") & pid=$!
  while [ ! -f "$barrier/paused" ] && [ "$ticks" -lt 500 ]; do sleep .02; ticks=$((ticks+1)); done
  [ "$ticks" -lt 500 ] || { wait_bounded "$pid" "R36-$stage fault helper"; fail "R36-$stage did not pause for external stage observation; exit=$([ -f "$barrier/exit" ] && cat "$barrier/exit" || printf missing) stdout=$(<"$stdout") stderr=$(<"$stderr")"; }
  if [ "$stage" = after-publication ]; then
    "$python_bin" - "$fixture_repo/target" "$barrier/publication.snapshot" <<'PY'
import hashlib,json,sys
from pathlib import Path
b=Path(sys.argv[1]).read_bytes(); Path(sys.argv[2]).write_text(json.dumps({'published_sha256':hashlib.sha256(b).hexdigest(),'published_bytes':len(b)}),encoding='utf-8')
PY
  fi
  "$python_bin" - "$fixture_repo/target" "$barrier/observed.json" "$stage" <<'PY'
import hashlib,json,stat,sys
from pathlib import Path
p=Path(sys.argv[1]); out=Path(sys.argv[2]); stage=sys.argv[3]
try:
 mode=p.lstat().st_mode
 exists=stat.S_ISREG(mode)
 data=p.read_bytes() if exists else None
except FileNotFoundError:
 exists=False; data=None
record={'exists':exists,'sha256':None if data is None else hashlib.sha256(data).hexdigest(),'byte_length':None if data is None else len(data)}
out.write_text(json.dumps(record,sort_keys=True),encoding='utf-8')
PY
  # The post-mismatch and unsupported actors now retain their bytes throughout
  # release.  A helper which merely reads a caller label cannot pass: it must
  # observe the task-owned state before `continue-after-external` is granted.
  if [ "$stage" = post-state-mismatch ] || [ "$stage" = unsupported-external-writer ]; then
    "$python_bin" - "$fixture_repo/target" "$barrier/$stage.transition" "$barrier/$stage.before" "$stage" <<'PY'
import hashlib,json,sys
from pathlib import Path
t=Path(sys.argv[1]); out=Path(sys.argv[2]); saved=Path(sys.argv[3]); stage=sys.argv[4]
before=t.read_bytes(); injected=b'MISMATCH-ACTOR' if stage=='post-state-mismatch' else b'UNSUPPORTED-WRITER'
saved.write_bytes(before); t.write_bytes(injected); during=t.read_bytes()
out.write_text(json.dumps({'before_sha256':hashlib.sha256(before).hexdigest(),'during_sha256':hashlib.sha256(during).hexdigest(),'actor':stage},sort_keys=True),encoding='utf-8')
PY
    [ "$stage" != unsupported-external-writer ] || : >"$barrier/external-writer-created"
  fi
  : >"$barrier/release"
  if [ "$stage" = post-state-mismatch ] || [ "$stage" = unsupported-external-writer ]; then
    ticks=0; while [ ! -f "$barrier/observed-after-external" ] && kill -0 "$pid" 2>/dev/null && [ "$ticks" -lt 500 ]; do sleep .02; ticks=$((ticks+1)); done
    [ "$ticks" -lt 500 ] || { wait_bounded "$pid" "R36-$stage external observation"; fail "R36-$stage did not observe externally held state"; }
    "$python_bin" - "$fixture_repo/target" "$barrier/continuation.snapshot" <<'PY'
import hashlib,json,sys
from pathlib import Path
b=Path(sys.argv[1]).read_bytes(); Path(sys.argv[2]).write_text(json.dumps({'sha256':hashlib.sha256(b).hexdigest(),'byte_length':len(b)}),encoding='utf-8')
PY
    : >"$barrier/continue-after-external"
  fi
  wait_bounded "$pid" "R36-$stage fault helper"; actual="$(<"$barrier/exit")"
  [ "$actual" -eq "$(status_exit "$status")" ] || fail "R36-$stage exit=$actual expected $(status_exit "$status") stderr=$(<"$stderr")"
  post="$(identity_json "$fixture_repo/$target")"; post_ids="$(post_identities_json "$target" "$dest")"
  last_record="$(assert_response_v2 "$label" "$status" "$op" "$target" "$dest" "$pre" "$candidate_id" "$post" "$post_ids" "$prepared_phase" "$prepared_step" "$stdout")"
  assert_hex "$label visible state" "$fixture_repo/$target" "$expected"
  "$python_bin" - "$barrier/observed.json" "$stage" <<'PY'
import json,sys
from pathlib import Path
record=json.loads(Path(sys.argv[1]).read_text(encoding='utf-8')); stage=sys.argv[2]
expected={
 'pre-displacement': {'exists': True, 'sha256': 'f0393febe8baaa55e32f7be2a7cc180bf34e52137d99e056c817a9c07b8f239a','byte_length':5},
 'after-displacement': {'exists': False, 'sha256': None,'byte_length':None},
 'after-publication': {'exists': True, 'sha256': 'a253ff09c5a8678e1fd1962b2c329245e139e45f9cc6ced4e5d7ad42c4108fc0','byte_length':3},
 'post-state-mismatch': {'exists': True, 'sha256': 'a253ff09c5a8678e1fd1962b2c329245e139e45f9cc6ced4e5d7ad42c4108fc0','byte_length':3},
 'unsupported-external-writer': {'exists': True, 'sha256': 'f0393febe8baaa55e32f7be2a7cc180bf34e52137d99e056c817a9c07b8f239a','byte_length':5},
}[stage]
if record != expected: raise SystemExit(f'fault stage observation mismatch: {record!r}')
PY
  if [ "$stage" = after-publication ]; then
    "$python_bin" - "$barrier/publication.snapshot" <<'PY'
import json,sys
r=json.loads(open(sys.argv[1],encoding='utf-8').read())
if r != {'published_sha256':'a253ff09c5a8678e1fd1962b2c329245e139e45f9cc6ced4e5d7ad42c4108fc0','published_bytes':3}: raise SystemExit(f'bad publication snapshot: {r!r}')
PY
  elif [ "$stage" = post-state-mismatch ] || [ "$stage" = unsupported-external-writer ]; then
    "$python_bin" - "$barrier/$stage.transition" "$stage" <<'PY'
import json,sys
r=json.loads(open(sys.argv[1],encoding='utf-8').read()); stage=sys.argv[2]
want_before='a253ff09c5a8678e1fd1962b2c329245e139e45f9cc6ced4e5d7ad42c4108fc0' if stage=='post-state-mismatch' else 'f0393febe8baaa55e32f7be2a7cc180bf34e52137d99e056c817a9c07b8f239a'
if r['actor'] != stage or r['before_sha256'] != want_before or r['during_sha256'] == want_before: raise SystemExit(f'bad externally-held transition: {r!r}')
PY
    # The continuation snapshot is made before the task grants the second
    # release gate.  If the helper exits instead, its terminal state above is
    # still checked exactly; either route proves the actor was not restored
    # before continuation became possible.
    if [ -f "$barrier/observed-after-external" ]; then
      "$python_bin" - "$barrier/continuation.snapshot" "$stage" <<'PY'
import hashlib,json,sys
r=json.loads(open(sys.argv[1],encoding='utf-8').read()); stage=sys.argv[2]
b=b'MISMATCH-ACTOR' if stage=='post-state-mismatch' else b'UNSUPPORTED-WRITER'
want={'sha256':hashlib.sha256(b).hexdigest(),'byte_length':len(b)}
if r != want: raise SystemExit(f'helper observation did not overlap injected state: {r!r}')
PY
    else
      [ -f "$barrier/exit" ] || fail "R36-$stage neither observed external state nor exited"
    fi
    "$python_bin" - "$fixture_repo/target" "$barrier/$stage.before" "$barrier/$stage.transition" "$stage" <<'PY'
import hashlib,json,sys
from pathlib import Path
t=Path(sys.argv[1]); saved=Path(sys.argv[2]); out=Path(sys.argv[3]); stage=sys.argv[4]
injected=b'MISMATCH-ACTOR' if stage=='post-state-mismatch' else b'UNSUPPORTED-WRITER'
current=t.read_bytes(); restored=current==injected
if restored: t.write_bytes(saved.read_bytes())
r=json.loads(out.read_text(encoding='utf-8')); r.update({'terminal_sha256':hashlib.sha256(current).hexdigest(),'actor_restored_after_exit':restored})
out.write_text(json.dumps(r,sort_keys=True),encoding='utf-8')
PY
    # Post-mismatch has already rolled back; unsupported deliberately leaves
    # the external writer's bytes alone until this task-owned cleanup.
    assert_hex "$label task-owned-actor-cleanup" "$fixture_repo/target" 4142434445
  fi
  [ "$stage" != unsupported-external-writer ] || [ -f "$barrier/external-writer-created" ] || fail 'R36 unsupported cell did not use external writer'
  helper="$canonical_saved"
}

residual_field() { "$python_bin" - "$last_record" "$1" "$fixture_repo" <<'PY'
import json,sys
from pathlib import Path
r=json.loads(sys.argv[1]); field=sys.argv[2]; root=Path(sys.argv[3])
if 'planned_effect_set' in r:
 if field=='token': v=r['transaction_id']
 elif field=='journal_path':
  rows=[x for x in r['planned_effect_set'] if 'journal' in x['roles']]
  if len(rows)!=1: raise SystemExit('missing unique journal plan')
  p=Path(rows[0]['path']); v=str(p if p.is_absolute() else root/p)
 else: raise SystemExit('unknown v2 residual field')
else: v=r[field]
if not isinstance(v,str) or not v: raise SystemExit('missing residual field')
print(v)
PY
}
assert_retained_recovery_paths() { "$python_bin" - "$last_record" "$fixture_repo" <<'PY'
import json,sys
from pathlib import Path
record=json.loads(sys.argv[1]); root=Path(sys.argv[2]).resolve()
if 'planned_effect_set' in record:
 rows=[x for x in record['planned_effect_set'] if 'journal' in x['roles']]
 paths=[Path(rows[0]['path'])] if len(rows)==1 else []
 paths += [Path(x['path']) for x in record['residue']]
 for raw in paths:
  p=(raw if raw.is_absolute() else root/raw).resolve()
  if root not in p.parents or not p.exists(): raise SystemExit(f'missing retained v2 recovery path: {p}')
 raise SystemExit(0)
for field in ('journal_path',):
 p=Path(record[field]).resolve()
 if root not in p.parents or not p.exists(): raise SystemExit(f'missing retained {field}: {p}')
for raw in record['residue_paths']:
 p=Path(raw).resolve()
 if root not in p.parents or not p.exists(): raise SystemExit(f'missing retained residue: {p}')
PY
}
assert_reported_fixture_path() { "$python_bin" - "$fixture_repo" "$1" <<'PY'
import sys
from pathlib import Path
root=Path(sys.argv[1]).resolve(); path=Path(sys.argv[2]).resolve()
if root not in path.parents or not path.exists():
 raise SystemExit(f'reported path is not a retained fixture path: {path}')
PY
}

mutant_self_check() {
  setup
  helper_api=v1
  local fake="$tmp/golden-helper.sh" pre candidate derived
  pre="$(artifact mutant-pre 4142434445)"; candidate="$(artifact mutant-candidate 4e4557)"
  cat >"$fake" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
root=; target=; operation=; candidate=; arbitrary=0; status="${R36_SELF_STATUS:-COMMITTED}"; while [ "$#" -gt 0 ]; do case "$1" in --repo-root)root="$2";shift 2;;--target) target="$2";shift 2;;--operation)operation="$2";shift 2;;--candidate|--replacement)candidate="$2";shift 2;;--arbitrary-mutator)arbitrary=1;shift 2;;*)shift;;esac;done
[ "$arbitrary" = 0 ] || printf PWNED > "$root/sentinel"
python3 - "$root/$target" "$target" "$operation" "$candidate" "$status" <<'PY'
import hashlib,json,sys
t,p,o,c,s=sys.argv[1:]; b=open(t,'rb').read(); ident={'sha256':hashlib.sha256(b).hexdigest(),'byte_length':len(b)}; ci=None if not c else {'sha256':hashlib.sha256(open(c,'rb').read()).hexdigest(),'byte_length':len(open(c,'rb').read())}
print(json.dumps({'schema':'implementaudit.observation_bound_mutation.v1','operation':o,'status':s,'source_path':p,'destination_path':None,'targets':[p],'pre_identity':ident,'candidate_identity':ci,'post_identity':ident,'post_identities':{p:ident},'token':None,'journal_path':None,'residue_paths':[]}))
PY
case "$status" in COMMITTED|NO_CHANGE) exit 0;; REJECTED_NO_MUTATION) exit 64;; MUTATION_FAILED_NO_STATE_CHANGE) exit 70;; MUTATION_FAILED_ROLLED_BACK) exit 71;; POST_STATE_MISMATCH_ROLLED_BACK) exit 72;; UNSUPPORTED_OWNER_DECISION) exit 77;; *) exit 1;; esac
SH
  chmod +x "$fake"; helper="$fake"
  if (invoke R36-MUTANT COMMITTED replace target - "$candidate" 4e4557 --preimage "$pre" --candidate "$candidate") 2>"$tmp/mutant.err"; then fail 'R36 mutant golden-status helper escaped byte assertion'; fi
  grep -Fq 'visible state' "$tmp/mutant.err" || fail 'R36 mutant was not killed by the independent byte assertion'
  # Status 70/71/72/77 have executable, exit-specific schema discriminators;
  # they are test self-coherence probes, not a substitute for the real helper.
  for status in MUTATION_FAILED_NO_STATE_CHANGE MUTATION_FAILED_ROLLED_BACK POST_STATE_MISMATCH_ROLLED_BACK UNSUPPORTED_OWNER_DECISION; do
    R36_SELF_STATUS="$status" invoke "R36-MUTANT-$status" "$status" replace target - "$candidate" 4142434445 --preimage "$pre" --candidate "$candidate"
  done
  # Mechanism mutant: queue every on_mutated callback until the following
  # directory sync. An authority file-fsync failure occurs first, so the
  # delayed callback cannot establish clean ownership and must be killed by
  # the exact residue/terminal discriminator.
  setup; pre="$(artifact delayed-callback-pre 4142434445)"; candidate="$(artifact delayed-callback-candidate 4e4557)"; derived="$(instrumented_helper)"
  prepare_authority replace target -; local delayed_out="$tmp/delayed-callback.out" delayed_err="$tmp/delayed-callback.err" delayed_exit
  set +e; IMPLEMENTAUDIT_R36_TEST_DELAY_MUTATED=1 IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=authority-file-fsync bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$prepared_phase" --step 1 --preimage "$pre" --candidate "$candidate" >"$delayed_out" 2>"$delayed_err"; delayed_exit=$?; set -e
  assert_hex R36-MUTANT-delayed-callback-source "$fixture_repo/target" 4142434445
  if [ "$delayed_exit" -eq 70 ] && "$python_bin" - "$delayed_out" "$run_root" <<'PY'
import json,sys
from pathlib import Path
try: r=json.load(open(sys.argv[1],encoding='utf-8'))
except Exception: raise SystemExit(1)
root=Path(sys.argv[2]); authority=list((root/'mutation-transactions').glob('*/authority.json'))
raise SystemExit(0 if r.get('status')=='MUTATION_FAILED_NO_STATE_CHANGE' and not r.get('residue') and not authority else 1)
PY
  then fail 'R36 delayed-callback mutant escaped ownership-before-durability discriminator'; fi
  write_hex "$fixture_repo/sentinel" 53414645
  set +e; R36_SELF_STATUS=REJECTED_NO_MUTATION bash "$fake" --repo-root "$fixture_repo" --run-root "$run_root" --operation replace --target target --preimage "$pre" --candidate "$candidate" --arbitrary-mutator 'ignored' >/dev/null; local arbitrary_exit=$?; set -e
  [ "$arbitrary_exit" -eq 64 ] || fail 'R36 mutant arbitrary-command status did not use refusal exit'
  assert_hex R36-MUTANT-C4-sentinel "$fixture_repo/sentinel" 50574e4544
  # Held-out bank.  These are six different executable bad helpers, not names
  # looped over one no-op.  Each first proves that it performed its named bad
  # behaviour, then runs the focused acceptance discriminator that kills it.
  setup; candidate="$(artifact mutant-copy-candidate 4e4557)"; fake="$tmp/mutant-copy-vs-move.sh"
  cat >"$fake" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
root= target= destination=; while [ "$#" -gt 0 ]; do case "$1" in --repo-root) root="$2"; shift 2;; --target) target="$2"; shift 2;; --destination) destination="$2"; shift 2;; *) shift;; esac; done
cp -- "$root/$target" "$root/$destination"
SH
  chmod +x "$fake"; bash "$fake" --repo-root "$fixture_repo" --operation move --target target --destination destination
  assert_hex R36-MUTANT-copy-destination "$fixture_repo/destination" 4142434445
  if (assert_hex R36-MUTANT-copy-vs-move-killed "$fixture_repo/target" -) 2>"$tmp/mutant-copy.err"; then fail 'copy-vs-move mutant escaped source-absence discriminator'; fi

  setup; candidate="$(artifact mutant-lock-candidate 4e4557)"; fake="$tmp/mutant-incomplete-target-set-lock.sh"
  cat >"$fake" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
root= target= destination= candidate=; while [ "$#" -gt 0 ]; do case "$1" in --repo-root) root="$2"; shift 2;; --target) target="$2"; shift 2;; --destination) destination="$2"; shift 2;; --candidate) candidate="$2"; shift 2;; *) shift;; esac; done
mkdir -p "$root/.IMPLEMENTAUDIT/only-source.lock"; mv -- "$root/$target" "$root/$destination"
python3 - "$root" "$target" "$destination" "$candidate" <<'PY'
import hashlib,json,sys
from pathlib import Path
r,t,d,c=map(str,sys.argv[1:]); ident=lambda b:{'sha256':hashlib.sha256(b).hexdigest(),'byte_length':len(b)}
old=ident(b'ABCDE'); new=ident(Path(c).read_bytes())
print(json.dumps({'schema':'implementaudit.observation_bound_mutation.v1','operation':'move','status':'COMMITTED','source_path':t,'destination_path':d,'targets':[t],'pre_identity':old,'candidate_identity':new,'post_identity':new,'post_identities':{t:None,d:new},'token':None,'journal_path':None,'residue_paths':[]},separators=(',',':')))
PY
SH
  chmod +x "$fake"; pre="$(artifact mutant-lock-pre 4142434445)"; mutant_pre_id="$(identity_json "$fixture_repo/target")"; response="$(bash "$fake" --repo-root "$fixture_repo" --operation move --target target --destination destination --candidate "$candidate")"
  [ -d "$fixture_repo/.IMPLEMENTAUDIT/only-source.lock" ] && [ ! -e "$fixture_repo/.IMPLEMENTAUDIT/destination.lock" ] || fail 'incomplete-lock mutant did not exhibit one-slot locking'
  if (assert_response_v1 R36-MUTANT-incomplete-target-set-lock COMMITTED move target destination '["target","destination"]' "$mutant_pre_id" "$(identity_json "$candidate")" "$(identity_json "$fixture_repo/destination")" "$(post_identities_json target destination)" "$response") 2>"$tmp/mutant-lock.err"; then fail 'incomplete target-set mutant escaped schema discriminator'; fi

  setup; candidate="$(artifact mutant-race-candidate 4e4557)"; fake="$tmp/mutant-check-use-race.sh"; barrier="$tmp/mutant-check-use-race"; mkdir "$barrier"
  cat >"$fake" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
root= target= candidate=; while [ "$#" -gt 0 ]; do case "$1" in --repo-root) root="$2"; shift 2;; --target) target="$2"; shift 2;; --candidate) candidate="$2"; shift 2;; *) shift;; esac; done
cmp -s "$root/$target" "$root/$target"; : >"$R36_MUTANT_BARRIER/checked"; while [ ! -f "$R36_MUTANT_BARRIER/release" ]; do sleep .02; done
cp -- "$candidate" "$root/$target"
SH
  chmod +x "$fake"; R36_MUTANT_BARRIER="$barrier" bash "$fake" --repo-root "$fixture_repo" --operation replace --target target --candidate "$candidate" & pid=$!
  ticks=0; while [ ! -f "$barrier/checked" ] && [ "$ticks" -lt 250 ]; do sleep .02; ticks=$((ticks+1)); done; [ "$ticks" -lt 250 ] || fail 'check-use mutant did not reach check barrier'
  write_hex "$fixture_repo/target" 4452494654; : >"$barrier/release"; wait_bounded "$pid" 'check-use mutant'
  assert_hex R36-MUTANT-check-use-observed-write "$fixture_repo/target" 4e4557
  if (assert_hex R36-MUTANT-check-use-killed "$fixture_repo/target" 4452494654) 2>"$tmp/mutant-race.err"; then fail 'check-use mutant escaped currentness discriminator'; fi

  setup; if [ "$(cat "$fixture_repo/symlink-capability")" = yes ]; then candidate="$(artifact mutant-link-candidate 4e4557)"; fake="$tmp/mutant-symlink-dereference.sh"
    cat >"$fake" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
root= target= candidate=; while [ "$#" -gt 0 ]; do case "$1" in --repo-root) root="$2"; shift 2;; --target) target="$2"; shift 2;; --candidate) candidate="$2"; shift 2;; *) shift;; esac; done
cp -- "$candidate" "$root/$target"
SH
    chmod +x "$fake"; bash "$fake" --repo-root "$fixture_repo" --operation replace --target final-link --candidate "$candidate"
    assert_hex R36-MUTANT-symlink-referent "$fixture_repo/target" 4e4557
    if (assert_hex R36-MUTANT-symlink-killed "$fixture_repo/target" 4142434445) 2>"$tmp/mutant-symlink.err"; then fail 'symlink dereference mutant escaped referent discriminator'; fi
  fi

  setup; candidate="$(artifact mutant-residue-candidate 4e4557)"; fake="$tmp/mutant-fictitious-residue.sh"
  cat >"$fake" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
root= target= candidate=; while [ "$#" -gt 0 ]; do case "$1" in --repo-root) root="$2"; shift 2;; --target) target="$2"; shift 2;; --candidate) candidate="$2"; shift 2;; *) shift;; esac; done
python3 - "$root" "$target" "$candidate" <<'PY'
import hashlib,json,sys
from pathlib import Path
r,t,c=map(str,sys.argv[1:]); ident=lambda b:{'sha256':hashlib.sha256(b).hexdigest(),'byte_length':len(b)}; old=ident(Path(r,t).read_bytes()); new=ident(Path(c).read_bytes())
print(json.dumps({'schema':'implementaudit.observation_bound_mutation.v1','operation':'replace','status':'ROLLBACK_CONFLICT','source_path':t,'destination_path':None,'targets':[t],'pre_identity':old,'candidate_identity':new,'post_identity':old,'post_identities':{t:old},'token':'fiction','journal_path':r+'/missing-journal','residue_paths':[r+'/missing-residue']},separators=(',',':')))
PY
exit 74
SH
  chmod +x "$fake"; pre="$(artifact mutant-residue-pre 4142434445)"; set +e; response="$(bash "$fake" --repo-root "$fixture_repo" --operation replace --target target --candidate "$candidate")"; actual=$?; set -e
  [ "$actual" -eq 74 ] || fail 'fictitious residue mutant did not emit rollback-conflict exit'
  last_record="$(assert_response_v1 R36-MUTANT-fictitious-residue ROLLBACK_CONFLICT replace target - '["target"]' "$(identity_json "$fixture_repo/target")" "$(identity_json "$candidate")" "$(identity_json "$fixture_repo/target")" "$(post_identities_json target -)" "$response")"
  if (assert_retained_recovery_paths) 2>"$tmp/mutant-residue.err"; then fail 'fictitious residue mutant escaped retained-path discriminator'; fi

  setup; candidate="$(artifact mutant-rollback-candidate 4e4557)"; fake="$tmp/mutant-fake-rollback.sh"
  cat >"$fake" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
root= target= candidate=; while [ "$#" -gt 0 ]; do case "$1" in --repo-root) root="$2"; shift 2;; --target) target="$2"; shift 2;; --candidate) candidate="$2"; shift 2;; *) shift;; esac; done
cp -- "$candidate" "$root/$target"; exit 71
SH
  chmod +x "$fake"; set +e; bash "$fake" --repo-root "$fixture_repo" --operation replace --target target --candidate "$candidate"; actual=$?; set -e
  [ "$actual" -eq 71 ] || fail 'fake rollback mutant did not emit rollback exit'
  assert_hex R36-MUTANT-fake-rollback-visible "$fixture_repo/target" 4e4557
  if (assert_hex R36-MUTANT-fake-rollback-killed "$fixture_repo/target" 4142434445) 2>"$tmp/mutant-rollback.err"; then fail 'fake rollback mutant escaped restoration discriminator'; fi
  helper="$canonical_helper"; helper_api=v2
  printf 'R36_MUTANT_SELF_CHECK=PASS golden-json-without-mutation=killed\n'
}

concurrent_destination() {
  setup
  local pa pb barrier="$tmp/barrier-destination"; pa="$(artifact a-pre 41)"; pb="$(artifact b-pre 42)"; rm -rf "$barrier"; mkdir "$barrier"
  local pid_a pid_b phase_a phase_b
  prepare_authority move a destination; phase_a="$prepared_phase"
  prepare_authority move b destination; phase_b="$prepared_phase"
  for source in a b; do (
    : >"$barrier/$source.ready"; while [ ! -f "$barrier/release" ]; do sleep .02; done
    phase="$phase_b"; [ "$source" = a ] && phase="$phase_a"
    set +e; bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$phase" --step 1 --preimage "$( [ "$source" = a ] && echo "$pa" || echo "$pb" )" >"$barrier/$source.out" 2>"$barrier/$source.err"; echo $? >"$barrier/$source.exit"
  ) &
  [ "$source" = a ] && pid_a=$! || pid_b=$!
  done
  local ticks=0; while { [ ! -f "$barrier/a.ready" ] || [ ! -f "$barrier/b.ready" ]; } && [ "$ticks" -lt 250 ]; do sleep .02; ticks=$((ticks+1)); done
  [ "$ticks" -lt 250 ] || fail 'R36-CONCURRENCY destination barrier timeout'; : >"$barrier/release"; wait_bounded "$pid_a" 'R36-CONCURRENCY writer a'; wait_bounded "$pid_b" 'R36-CONCURRENCY writer b'
  "$python_bin" - "$barrier" "$fixture_repo" <<'PY'
import json,sys
from pathlib import Path
b,r=map(Path,sys.argv[1:]); rows=[]
for n in ('a','b'):
 code=int((b/f'{n}.exit').read_text()); rec=json.loads((b/f'{n}.out').read_text()); rows.append((n,code,rec['status'],rec.get('reason_code'),rec.get('residue'),(b/f'{n}.err').read_text()))
# Both loser timings are valid: overlap after transaction entry is a rebase
# conflict; a winner that publishes first is rejected at the no-effect
# destination preflight. Neither may retain residue or mutate the losing source.
winners=[x for x in rows if x[1:3]==(0,'COMMITTED')]
losers=[x for x in rows if (x[1:4] in {(65,'CONFLICT_REBASE','TARGET_LOCK_BUSY'),(65,'CONFLICT_REBASE','PREIMAGE_DRIFT'),(65,'CONFLICT_REBASE','DESTINATION_EXISTS'),(64,'REJECTED_NO_MUTATION','DESTINATION_EXISTS')}) and x[4]==[]]
if len(winners)!=1 or len(losers)!=1: raise SystemExit(f'R36-CONCURRENCY statuses {rows!r}')
winner=next(row[0] for row in rows if row[2]=='COMMITTED'); loser='b' if winner=='a' else 'a'
if (r/'destination').read_bytes()!=winner.upper().encode() or (r/loser).read_bytes()!=loser.upper().encode() or (r/winner).exists(): raise SystemExit('R36-CONCURRENCY filesystem postcondition failed')
(b/'winner').write_text(winner,encoding='ascii'); (b/'loser').write_text(loser,encoding='ascii')
PY
  # Probe the actual target sets after the losing contender exits: its source
  # and the contested destination must both be reusable, not merely a disjoint file.
  local winner loser destination_pre destination_candidate loser_pre loser_candidate loser_hex
  winner="$(<"$barrier/winner")"; loser="$(<"$barrier/loser")"
  destination_pre="$(artifact destination-reuse-pre "$( [ "$winner" = "a" ] && printf 41 || printf 42 )")"
  destination_candidate="$(artifact destination-reuse-candidate 44)"
  invoke R36-CONCURRENCY-destination-reuse COMMITTED replace destination - "$destination_candidate" 44 --preimage "$destination_pre" --candidate "$destination_candidate"
  loser_hex=42; [ "$loser" = a ] && loser_hex=41
  loser_pre="$(artifact loser-reuse-pre "$loser_hex")"; loser_candidate="$(artifact loser-reuse-candidate 4c)"
  invoke R36-CONCURRENCY-loser-reuse COMMITTED replace "$loser" - "$loser_candidate" 4c --preimage "$loser_pre" --candidate "$loser_candidate"
}

opposing_moves() {
  setup
  local pa pb barrier="$tmp/barrier-opposing"; pa="$(artifact opposing-a 41)"; pb="$(artifact opposing-b 42)"; rm -rf "$barrier"; mkdir "$barrier"
  local pid_a pid_b phase_a phase_b
  prepare_authority move a b; phase_a="$prepared_phase"
  prepare_authority move b a; phase_b="$prepared_phase"
  for source in a b; do (
    : >"$barrier/$source.ready"; while [ ! -f "$barrier/release" ]; do sleep .02; done
    destination=b; [ "$source" = b ] && destination=a
    pre="$pb"; [ "$source" = a ] && pre="$pa"
    phase="$phase_b"; [ "$source" = a ] && phase="$phase_a"
    set +e; bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$phase" --step 1 --preimage "$pre" >"$barrier/$source.out" 2>"$barrier/$source.err"; echo $? >"$barrier/$source.exit"
  ) &
  [ "$source" = a ] && pid_a=$! || pid_b=$!
  done
  local ticks=0; while { [ ! -f "$barrier/a.ready" ] || [ ! -f "$barrier/b.ready" ]; } && [ "$ticks" -lt 250 ]; do sleep .02; ticks=$((ticks+1)); done
  [ "$ticks" -lt 250 ] || fail 'R36-OPPOSING barrier timeout'; : >"$barrier/release"; wait_bounded "$pid_a" 'R36-OPPOSING writer a'; wait_bounded "$pid_b" 'R36-OPPOSING writer b'
  "$python_bin" - "$barrier" "$fixture_repo" <<'PY'
import json,sys
from pathlib import Path
b,r=map(Path,sys.argv[1:])
for n in ('a','b'):
 if int((b/f'{n}.exit').read_text()) != 64 or json.loads((b/f'{n}.out').read_text())['status'] != 'REJECTED_NO_MUTATION': raise SystemExit('R36-OPPOSING did not fail closed')
if (r/'a').read_bytes()!=b'A' or (r/'b').read_bytes()!=b'B': raise SystemExit('R36-OPPOSING changed either source')
PY
}

canonical_observation_races() {
  # The helper publishes an `observed` barrier only after it captured the
  # supplied preimage/current target, so these external writes are genuinely
  # after observation rather than setup-time stale fixtures.
  local label mode pre barrier pid actual stdout stderr source_pre source_post post_set canonical_saved="$helper" instrumented
  instrumented="$(instrumented_helper)"; helper="$instrumented"
  for mode in source destination; do
    setup; label="R36-RACE-$mode"; pre="$(artifact "$mode-pre" 4142434445)"; barrier="$tmp/barrier-race-$mode"; mkdir "$barrier"; stdout="$tmp/$label.out"; stderr="$tmp/$label.err"; source_pre="$(identity_json "$fixture_repo/target")"
    prepare_authority move target destination; local race_phase="$prepared_phase"
    (set +e; IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR="$barrier" bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$race_phase" --step 1 --preimage "$pre" >"$stdout" 2>"$stderr"; echo $? >"$barrier/exit") & pid=$!
    local ticks=0; while [ ! -f "$barrier/observed" ] && [ "$ticks" -lt 500 ]; do sleep .02; ticks=$((ticks+1)); done
    [ "$ticks" -lt 500 ] || fail "$label did not acknowledge post-observation barrier"
    if [ "$mode" = source ]; then write_hex "$fixture_repo/target" 4c41544552; else write_hex "$fixture_repo/destination" 45585445524e414c; fi
    : >"$barrier/release"; wait_bounded "$pid" "$label helper"; actual="$(<"$barrier/exit")"
    [ "$actual" -eq 65 ] || fail "$label exit $actual, expected stale conflict 65"
    source_post="$(identity_json "$fixture_repo/target")"; post_set="$(post_identities_json target destination)"
    last_record="$(assert_response_v2 "$label" CONFLICT_REBASE move target destination "$source_pre" "$(identity_json "$pre")" "$source_post" "$post_set" "$race_phase" 1 "$stdout")"
    if [ "$mode" = source ]; then assert_hex "$label-source" "$fixture_repo/target" 4c41544552; assert_hex "$label-destination" "$fixture_repo/destination" -
    else assert_hex "$label-source" "$fixture_repo/target" 4142434445; assert_hex "$label-destination" "$fixture_repo/destination" 45585445524e414c; fi
  done
  helper="$canonical_saved"
}

external_drift_and_recovery() {
  # The actor is external to the helper.  It waits for an actual publication of
  # candidate bytes, then recreates the target with winner bytes; no requested
  # outcome/fault-name is supplied to the helper.
  setup
  local pre candidate barrier="$tmp/barrier-drift" stdout="$tmp/drift.out" stderr="$tmp/drift.err" pre_id
  pre="$(artifact drift-pre 4142434445)"
  pre_id="$(identity_json "$fixture_repo/target")"
  candidate="$fixture_repo/artifacts/drift-candidate"
  "$python_bin" - "$candidate" <<'PY'
import sys
from pathlib import Path
Path(sys.argv[1]).write_bytes(b'N' * (8 * 1024 * 1024))
PY
  rm -rf "$barrier"; mkdir "$barrier"
  (
    : >"$barrier/actor-ready"; while [ ! -f "$barrier/release" ]; do sleep .02; done
    "$python_bin" - "$fixture_repo/target" "$candidate" "$barrier/actor-fired" <<'PY'
import hashlib,sys,time
from pathlib import Path
t,c,f=map(Path,sys.argv[1:]); wanted=hashlib.sha256(c.read_bytes()).digest()
for _ in range(1000):
    try:
        if t.exists() and hashlib.sha256(t.read_bytes()).digest()==wanted:
            t.write_bytes(b'EXTERNAL-WINNER')
            f.write_text('fired\n',encoding='ascii')
            raise SystemExit(0)
    except (FileNotFoundError, PermissionError):
        # Windows may briefly deny access while the helper publishes/replaces
        # the target.  That transient state is not the actor's terminal result.
        pass
    time.sleep(.005)
raise SystemExit('candidate publication was not observed')
PY
  ) &
  local actor=$! helper_pid ticks=0 actual status post record journal token
  while [ ! -f "$barrier/actor-ready" ] && [ "$ticks" -lt 250 ]; do sleep .02; ticks=$((ticks+1)); done
  [ "$ticks" -lt 250 ] || fail 'R36-DRIFT actor barrier timeout'
  : >"$barrier/release"
  prepare_authority replace target -; local drift_phase="$prepared_phase"
  (set +e; bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$drift_phase" --step 1 --preimage "$pre" --candidate "$candidate" >"$stdout" 2>"$stderr"; echo $? >"$barrier/helper.exit") & helper_pid=$!
  wait_bounded "$helper_pid" 'R36-DRIFT helper'
  actual="$(<"$barrier/helper.exit")"
  wait_bounded "$actor" 'R36-DRIFT actor'
  [ -f "$barrier/actor-fired" ] || fail 'R36-DRIFT actor did not fire'
  status="$($python_bin - "$stdout" <<'PY'
import json,sys
print(json.loads(open(sys.argv[1],encoding='utf-8').read())['status'])
PY
)"
  [ "$status" = ROLLBACK_CONFLICT ] || fail "R36-DRIFT status $status, expected ROLLBACK_CONFLICT"
  [ "$actual" -eq "$(status_exit ROLLBACK_CONFLICT)" ] || fail "R36-DRIFT exit/status mismatch"
  post="$(identity_json "$fixture_repo/target")"
  last_record="$(assert_response_v2 R36-DRIFT "$status" replace target - "$pre_id" "$(identity_json "$candidate")" "$post" "$(post_identities_json target -)" "$drift_phase" 1 "$stdout")"
  assert_hex R36-DRIFT-winner "$fixture_repo/target" 45585445524e414c2d57494e4e4552
  journal="$(residual_field journal_path)"; token="$(residual_field token)"
  assert_retained_recovery_paths
  assert_reported_fixture_path "$journal"
  # Wrong token must not delete the journal, mutate winner bytes, or consume the lock/recovery authority.
  invoke R36-DRIFT-forged REJECTED_NO_MUTATION recover target - - 45585445524e414c2d57494e4e4552 --journal "$journal" --token "forged-$token"
  assert_reported_fixture_path "$journal"
  # A token-looking, externally crafted journal/backup cannot become recovery
  # authority or consume either external file.
  local crafted_backup="$tmp/crafted-backup" crafted_journal="$tmp/crafted-journal.json" crafted_token='crafted-token'
  write_hex "$crafted_backup" 41545441434b
  "$python_bin" - "$crafted_journal" "$crafted_backup" "$crafted_token" <<'PY'
import json,sys
from pathlib import Path
j,b,t=sys.argv[1:]; Path(j).write_text(json.dumps({'token':t,'target':'target','backup':b,'pre_identity':{'sha256':'x','byte_length':6},'candidate_identity':None}),encoding='utf-8')
PY
  invoke R36-DRIFT-crafted-journal REJECTED_NO_MUTATION recover target - - 45585445524e414c2d57494e4e4552 --journal "$crafted_journal" --token "$crafted_token"
  assert_hex R36-DRIFT-crafted-backup-intact "$crafted_backup" 41545441434b; [ -e "$crafted_journal" ] || fail 'crafted journal was consumed'
  # A caller can make a byte-consistent journal, backup, token-shaped names,
  # and even a linked would-be authority record in the claimed run.  Portable
  # same-principal storage does not establish who created those files, so none
  # of them may authorize automatic mutation.
  local internal_token='internal-token' internal_backup="$run_root/.r36-backup-internal-token" internal_journal="$run_root/.r36-journal-internal-token.json" internal_authority="$run_root/.r36-authority-internal-token"
  write_hex "$internal_backup" 41545441434b
  ln -s "$outside" "$internal_authority" 2>/dev/null || { printf 'authority-link-fallback\n' >"$internal_authority"; }
  "$python_bin" - "$internal_journal" "$internal_backup" "$internal_token" "$internal_authority" <<'PY'
import hashlib,json,sys
from pathlib import Path
j,b,t,a=sys.argv[1:]; raw=Path(b).read_bytes(); ident={'sha256':hashlib.sha256(raw).hexdigest(),'byte_length':len(raw)}
authority=Path(a).read_bytes(); ah=hashlib.sha256(authority).hexdigest()
Path(j).write_text(json.dumps({'token':t,'target':'target','backup':b,'pre_identity':ident,'candidate_identity':None,'authority_hash':ah}),encoding='utf-8')
PY
  invoke R36-DRIFT-internal-forgery REJECTED_NO_MUTATION recover target - - 45585445524e414c2d57494e4e4552 --journal "$internal_journal" --token "$internal_token"
  assert_hex R36-DRIFT-internal-backup-intact "$internal_backup" 41545441434b; [ -e "$internal_journal" ] || fail 'internal forged journal was consumed'
  [ -L "$internal_authority" ] && assert_hex R36-DRIFT-internal-linked-authority-referent "$outside" 4f555453494445
  # Even a correct token is manual/owner-gated custody on portable
  # same-principal filesystems: this helper never auto-recovers it.
  invoke R36-DRIFT-correct-token REJECTED_NO_MUTATION recover target - - 45585445524e414c2d57494e4e4552 --target target --journal "$journal" --token "$token"
  assert_reported_fixture_path "$journal"
  assert_hex R36-DRIFT-correct-token-winner "$fixture_repo/target" 45585445524e414c2d57494e4e4552
}

true_kill_requires_manual_custody() {
  # A SIGKILL cannot emit a terminal JSON object.  The durable, pre-existing
  # journal is therefore the only truthful recovery-required report: it must
  # survive with the displaced preimage and owned lock set, while the public
  # recover CLI stays a non-mutating/manual-custody gate.
  setup
  local pre cand derived barrier="$tmp/true-kill" stdout="$tmp/true-kill.out" stderr="$tmp/true-kill.err" pid ticks=0 journal backup token record
  pre="$(artifact true-kill-pre 4142434445)"; cand="$(artifact true-kill-candidate 4e4557)"
  derived="$(instrumented_helper)" || fail 'R36 true-kill could not derive instrumented helper'
  prepare_authority replace target -; local kill_phase="$prepared_phase"
  rm -rf "$barrier"; mkdir "$barrier"
  IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR="$barrier" IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=after-displacement bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$kill_phase" --step 1 --preimage "$pre" --candidate "$cand" >"$stdout" 2>"$stderr" & pid=$!
  while [ ! -f "$barrier/paused" ] && kill -0 "$pid" 2>/dev/null && [ "$ticks" -lt 500 ]; do sleep .02; ticks=$((ticks+1)); done
  [ "$ticks" -lt 500 ] || { wait_bounded "$pid" 'R36 true-kill helper'; fail 'R36 true-kill never reached durable displacement'; }
  kill -9 "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true
  [ ! -e "$fixture_repo/target" ] || fail 'R36 true-kill retained target after displacement'
  journal="$(find "$run_root/mutation-transactions" -mindepth 2 -maxdepth 2 -type f -name journal.json -print -quit)"
  backup="${journal%/journal.json}/backup.bin"
  [ -n "$journal" ] && [ -n "$backup" ] || fail 'R36 true-kill did not retain journal and backup'
  assert_hex R36-TRUE-KILL-backup "$backup" 4142434445
  record="$($python_bin - "$journal" <<'PY'
import json,sys
r=json.load(open(sys.argv[1],encoding='utf-8'))
if r.get('schema') != 'implementaudit.observation-bound-mutation.journal.v2': raise SystemExit(f'journal schema is not v2: {r!r}')
if r.get('status') != 'DISPLACEMENT_DURABLE': raise SystemExit(f'journal displacement state missing: {r!r}')
if not isinstance(r.get('transaction_id'),str) or not r['transaction_id']: raise SystemExit('journal transaction id missing')
if not any(x.get('path','').endswith('/backup.bin') for x in r.get('residue',[])): raise SystemExit(f'journal backup residue missing: {r!r}')
print(r['transaction_id'])
PY
)" || fail 'R36 true-kill journal is not a durable recovery-required record'
  token="$record"
  find "$fixture_repo/.IMPLEMENTAUDIT/.r36-locks" -mindepth 1 -maxdepth 1 -type d -print -quit | grep -q . || fail 'R36 true-kill did not retain lock ownership'
  invoke R36-TRUE-KILL-manual-gate REJECTED_NO_MUTATION recover target - - - --journal "$journal" --token "$token"
  [ ! -e "$fixture_repo/target" ] || fail 'R36 true-kill recover mutated target'
  [ -e "$journal" ] && [ -e "$backup" ] || fail 'R36 true-kill recover consumed custody'
}

interrupted_move_requires_manual_custody() {
  # This is the narrow move crash window: destination has acquired an exact
  # hard-link before source removal.  A kill must leave explained dual names,
  # not silently turn that window into an unjournaled copy.
  setup
  local pre derived barrier="$tmp/move-after-destination" stdout="$tmp/move-after-destination.out" stderr="$tmp/move-after-destination.err" pid ticks=0 journal token
  pre="$(artifact move-crash-pre 4142434445)"; derived="$(instrumented_helper)" || fail 'R36 move-crash could not derive instrumented helper'
  prepare_authority move target destination; local move_crash_phase="$prepared_phase"
  rm -rf "$barrier"; mkdir "$barrier"
  IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR="$barrier" IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=move-after-destination bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$move_crash_phase" --step 1 --preimage "$pre" >"$stdout" 2>"$stderr" & pid=$!
  while [ ! -f "$barrier/paused" ] && kill -0 "$pid" 2>/dev/null && [ "$ticks" -lt 500 ]; do sleep .02; ticks=$((ticks+1)); done
  [ -f "$barrier/paused" ] || { wait_bounded "$pid" 'R36 move-crash helper'; fail 'R36 move-crash never reached destination-published window'; }
  assert_hex R36-MOVE-CRASH-source-visible "$fixture_repo/target" 4142434445
  assert_hex R36-MOVE-CRASH-destination-visible "$fixture_repo/destination" 4142434445
  journal="$(find "$run_root/mutation-transactions" -mindepth 2 -maxdepth 2 -type f -name journal.json -print -quit)"
  [ -n "$journal" ] || fail 'R36 move-crash has no durable journal before destination publication'
  token="$($python_bin - "$journal" "$fixture_repo" <<'PY'
import hashlib,json,sys
from pathlib import Path
j,repo=map(Path,sys.argv[1:]); r=json.loads(j.read_text(encoding='utf-8')); a=json.loads((j.parent/'authority.json').read_text(encoding='utf-8'))
want={'sha256':hashlib.sha256(b'ABCDE').hexdigest(),'byte_length':5}
if a.get('operation') != 'move' or a.get('source') != 'target' or a.get('destination') != 'destination': raise SystemExit(f'move authority route incorrect: {a!r}')
pre={x['path']:{k:v for k,v in x['identity'].items() if k in ('sha256','byte_length')} for x in r.get('pre_identities',[])}
cand=[{k:v for k,v in x['identity'].items() if k in ('sha256','byte_length')} for x in r.get('candidate_identities',[])]
if pre.get('target') != want or want not in cand: raise SystemExit(f'move journal byte identities incorrect: {r!r}')
if r.get('status') != 'PUBLICATION_DURABLE' or not any(x.get('path')=='destination' for x in r.get('residue',[])): raise SystemExit(f'move custody disposition missing: {r!r}')
print(r['transaction_id'])
PY
)" || fail 'R36 move-crash journal was not a truthful custody record'
  find "$fixture_repo/.IMPLEMENTAUDIT/.r36-locks" -mindepth 1 -maxdepth 1 -type d -print -quit | grep -q . || fail 'R36 move-crash did not retain owned locks'
  kill -9 "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true
  invoke R36-MOVE-CRASH-manual-gate REJECTED_NO_MUTATION recover target destination - 4142434445 --destination destination --journal "$journal" --token "$token"
  assert_hex R36-MOVE-CRASH-recover-source "$fixture_repo/target" 4142434445
  assert_hex R36-MOVE-CRASH-recover-destination "$fixture_repo/destination" 4142434445
  [ -e "$journal" ] || fail 'R36 move-crash recover consumed journal'
  setup; pre="$(artifact move-clean-pre 4142434445)"; invoke R36-MOVE-CLEAN COMMITTED move target destination "$pre" 4142434445 --preimage "$pre"
  if [ -n "$(find "$run_root/mutation-transactions" -mindepth 2 -maxdepth 2 -type f -name journal.json -print -quit)" ]; then
    fail 'R36 successful move retained a journal'
  fi
  return 0
}

gate_domain_self_check() {
  local pre cand
  # A structurally replaced or aliased gate is detected before product
  # mutation and routes to the existing owner-decision boundary. The constant
  # coordination scope does not claim arbitrary same-principal exclusion.
  setup; mkdir -p "$fixture_repo/.IMPLEMENTAUDIT/.r36-locks"; printf '\0' >"$fixture_repo/.IMPLEMENTAUDIT/.r36-locks/namespace.gate"; ln "$fixture_repo/.IMPLEMENTAUDIT/.r36-locks/namespace.gate" "$fixture_repo/.IMPLEMENTAUDIT/.r36-locks/namespace.gate.external-alias"
  pre="$(artifact gate-domain-pre 4142434445)"; cand="$(artifact gate-domain-candidate 4e4557)"
  invoke R36-GATE-DOMAIN UNSUPPORTED_OWNER_DECISION replace target - "$cand" 4142434445 --preimage "$pre" --candidate "$cand"
  "$python_bin" - "$tmp/R36-GATE-DOMAIN.out" "$fixture_repo" "$run_root" <<'PY' || fail 'R36-GATE-DOMAIN lacked exact pre-effect owner-decision evidence'
import copy,json,os,re,sys
from pathlib import Path,PurePosixPath
r=json.load(open(sys.argv[1],encoding='utf-8'))
if r['reason_code']!='WRITER_DOMAIN_BREACH' or r['coordination_scope']!='GOVERNED_HELPER_ROUTED_WRITERS_ONLY': raise SystemExit(r)
if r['residue']!=[]: raise SystemExit(f'pre-product refusal retained unresolved residue: {r["residue"]!r}')
repo=Path(os.path.abspath(sys.argv[2])); run=Path(os.path.abspath(sys.argv[3]))
def relative(path):
 absolute=Path(os.path.abspath(path))
 try: value=absolute.relative_to(repo).as_posix()
 except ValueError: raise SystemExit(f'expected evidence path escapes repository: {absolute}')
 canonical=PurePosixPath(value)
 if str(canonical)!=value or value in {'','.'} or any(part in {'','.','..'} for part in canonical.parts): raise SystemExit(f'noncanonical expected evidence path: {value!r}')
 return value
def independent_allowed(record):
 transaction=record.get('transaction_id')
 if transaction is None:
  if record.get('planned_effect_set')!=[] or record.get('actual_effect_set')!=[]: raise ValueError('preflight refusal claimed transaction effects without a transaction')
  return {}
 match=re.fullmatch(r'([0-9a-f]{32})-p([1-9][0-9]*)-s([1-9][0-9]*)',transaction) if isinstance(transaction,str) else None
 if match is None: raise ValueError(f'malformed transaction identity: {transaction!r}')
 if type(record.get('phase')) is not int or type(record.get('step')) is not int: raise ValueError('phase/step are not integers')
 if int(match.group(2))!=record['phase'] or int(match.group(3))!=record['step']: raise ValueError(f'transaction phase/step mismatch: {transaction!r}')
 tx_parent=Path(os.path.abspath(run/'mutation-transactions')); tx=tx_parent/transaction
 if tx.parent!=tx_parent or tx.name!=transaction or any(separator in transaction for separator in ('/','\\')): raise ValueError(f'transaction is not a direct child: {transaction!r}')
 allowed={
  relative(run):{'fsync'},
  relative(tx_parent):{'mkdir','fsync'},
  relative(tx):{'mkdir','fsync'},
  relative(tx/'authority.json'):{'create','write','fsync'},
  relative(tx/'released-locks'):{'mkdir','fsync'},
  relative(tx/'result.json'):{'create','write','fsync'},
  relative(tx/'result.tmp'):{'create','write','fsync','replace','unlink'},
  relative(repo/'.IMPLEMENTAUDIT'):{'fsync'},
  relative(repo/'.IMPLEMENTAUDIT'/'.r36-locks'):{'mkdir','fsync'},
  relative(repo/'.IMPLEMENTAUDIT'/'.r36-locks'/'namespace.gate'):{'create','write','fsync'},
 }
 if len(allowed)!=10: raise ValueError('independent allowed path map contains an alias/duplicate')
 return allowed
def evidence_only(record):
 allowed=independent_allowed(record)
 planned={}
 for declaration in record['planned_effect_set']:
  path=PurePosixPath(declaration['path'])
  if str(path)!=declaration['path'] or declaration['path']=='' or any(part in {'','..'} for part in path.parts): raise ValueError(f'noncanonical planned path: {declaration!r}')
  key=(declaration['scope'],declaration['path'])
  if key in planned: raise ValueError(f'duplicate planned path: {key!r}')
  planned[key]=declaration
 accepted=[]
 seen=set()
 for effect in record['actual_effect_set']:
  if effect['outcome']!='applied': continue
  path=PurePosixPath(effect['path'])
  if str(path)!=effect['path'] or effect['path'] in {'','.'} or any(part in {'','.','..'} for part in path.parts): raise ValueError(f'noncanonical applied path: {effect!r}')
  identity=(effect['scope'],effect['path'],effect['effect'],effect['sequence'])
  if identity in seen: raise ValueError(f'duplicate applied effect row: {effect!r}')
  seen.add(identity)
  declaration=planned.get((effect['scope'],effect['path']))
  if declaration is None: raise ValueError(f'undeclared applied effect: {effect!r}')
  if effect['scope']!='repo' or effect['path'] not in allowed or effect['effect'] not in allowed[effect['path']]: raise ValueError(f'non-evidence path/operation: {effect!r}')
  if effect['effect'] not in declaration['allowed_effects']: raise ValueError(f'applied effect contradicts planned declaration: {effect!r}')
  accepted.append((effect['path'],effect['effect']))
 return accepted
accepted=evidence_only(r)
if r['transaction_id'] is None:
 if accepted or r['planned_effect_set'] or r['actual_effect_set']: raise SystemExit('preflight refusal was not effect-empty')
 mutant=copy.deepcopy(r); mutant['actual_effect_set']=[{'sequence':1,'scope':'repo','path':r['source_path'],'effect':'write','before':None,'after':None,'outcome':'applied'}]
 try: evidence_only(mutant)
 except ValueError: pass
 else: raise SystemExit('effect-empty preflight oracle accepted an applied product mutation')
 print('R36_GATE_DOMAIN_ORACLE=PASS preflight-effect-empty')
 raise SystemExit(0)
mutant=copy.deepcopy(r); stage=next(x for x in mutant['planned_effect_set'] if 'stage' in x['roles'])
mutant['actual_effect_set'].append({'sequence':len(mutant['actual_effect_set'])+1,'scope':stage['scope'],'path':stage['path'],'effect':'create','before':{'kind':'absent'},'after':{'kind':'regular'},'outcome':'applied'})
try: evidence_only(mutant)
except ValueError: pass
else: raise SystemExit('closed evidence-role oracle accepted an applied stage mutation')
relabel=copy.deepcopy(r); target=next(x for x in relabel['planned_effect_set'] if x['path']==r['source_path'])
target['roles']=['authority']; target['allowed_effects']=sorted(set(target['allowed_effects'])|{'write'})
relabel['actual_effect_set'].append({'sequence':len(relabel['actual_effect_set'])+1,'scope':target['scope'],'path':target['path'],'effect':'write','before':r['pre_identities'][0]['identity'],'after':r['pre_identities'][0]['identity'],'outcome':'applied'})
try: evidence_only(relabel)
except ValueError: pass
else: raise SystemExit('independent path oracle accepted helper-relabeled product mutation')
identity_mutants={
 'traversal':'../outside',
 'phase-mismatch':re.sub(r'-p[1-9][0-9]*-',f'-p{r["phase"]+1}-',r['transaction_id']),
 'leading-zero':re.sub(r'-p[1-9][0-9]*-',f'-p0{r["phase"]}-',r['transaction_id']),
 'malformed':r['transaction_id'].replace('-s','-step',1),
}
for label,transaction in identity_mutants.items():
 identity_mutant=copy.deepcopy(r); identity_mutant['transaction_id']=transaction
 try: evidence_only(identity_mutant)
 except ValueError: pass
 else: raise SystemExit(f'independent transaction oracle accepted {label}: {transaction!r}')
print('R36_GATE_DOMAIN_APPLIED_EVIDENCE_PATHS='+json.dumps(sorted(set(accepted)),separators=(',',':')))
PY
}

causal_review_heldouts() {
  local pre cand derived stdout stderr actual phase barrier pid a b ticks region repl tx

  # A real write syscall failure after displacement must restore the exact
  # preimage and emit a terminal result rather than escaping through traceback.
  setup; pre="$(artifact io-pre 4142434445)"; cand="$(artifact io-candidate 4e4557)"; derived="$(instrumented_helper)"
  prepare_authority replace target -; phase="$prepared_phase"; stdout="$tmp/io.out"; stderr="$tmp/io.err"
  set +e; IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=io-after-displacement bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$phase" --step 1 --preimage "$pre" --candidate "$cand" >"$stdout" 2>"$stderr"; actual=$?; set -e
  [ "$actual" -eq 71 ] || fail "R36-IO exit=$actual expected=71 stderr=$(<"$stderr")"
  assert_hex R36-IO-restored "$fixture_repo/target" 4142434445
  tx="$($python_bin - "$stdout" <<'PY'
import json,sys
r=json.load(open(sys.argv[1],encoding='utf-8'))
if r['status']!='MUTATION_FAILED_ROLLED_BACK' or r['reason_code']!='IO_FAILURE': raise SystemExit(r)
print(r['transaction_id'])
PY
)" || fail 'R36-IO lacked terminal rollback JSON'
  [ -f "$run_root/mutation-transactions/$tx/result.json" ] || fail 'R36-IO lacked durable result.json'

  # The mutating syscall owns the state transition even when the immediately
  # following durability sync fails. Replace must therefore roll back from the
  # displaced backup rather than treating the source as untouched.
  setup; pre="$(artifact replace-sync-pre 4142434445)"; cand="$(artifact replace-sync-candidate 4e4557)"; derived="$(instrumented_helper)"
  prepare_authority replace target -; phase="$prepared_phase"; stdout="$tmp/replace-sync.out"; stderr="$tmp/replace-sync.err"
  set +e; IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=fsync-after-displacement bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$phase" --step 1 --preimage "$pre" --candidate "$cand" >"$stdout" 2>"$stderr"; actual=$?; set -e
  [ "$actual" -eq 71 ] || fail "R36-REPLACE-SYNC exit=$actual expected=71 stderr=$(<"$stderr")"
  assert_hex R36-REPLACE-SYNC-restored "$fixture_repo/target" 4142434445
  tx="$($python_bin - "$stdout" <<'PY'
import json,sys
r=json.load(open(sys.argv[1],encoding='utf-8'))
if r['status']!='MUTATION_FAILED_ROLLED_BACK' or r['reason_code']!='IO_FAILURE': raise SystemExit(r)
print(r['transaction_id'])
PY
)" || fail 'R36-REPLACE-SYNC lacked terminal rollback JSON'
  [ -f "$run_root/mutation-transactions/$tx/result.json" ] || fail 'R36-REPLACE-SYNC lacked durable result.json'

  # Move publication begins at the successful hard-link syscall. A following
  # directory-sync failure must remove that published name and report rollback.
  setup; pre="$(artifact move-sync-pre 4142434445)"; derived="$(instrumented_helper)"
  prepare_authority move target destination; phase="$prepared_phase"; stdout="$tmp/move-sync.out"; stderr="$tmp/move-sync.err"
  set +e; IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=fsync-after-destination bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$phase" --step 1 --preimage "$pre" >"$stdout" 2>"$stderr"; actual=$?; set -e
  [ "$actual" -eq 71 ] || fail "R36-MOVE-SYNC exit=$actual expected=71 stderr=$(<"$stderr")"
  assert_hex R36-MOVE-SYNC-source "$fixture_repo/target" 4142434445
  assert_hex R36-MOVE-SYNC-destination "$fixture_repo/destination" -
  tx="$($python_bin - "$stdout" <<'PY'
import json,sys
r=json.load(open(sys.argv[1],encoding='utf-8'))
if r['status']!='MUTATION_FAILED_ROLLED_BACK' or r['reason_code']!='IO_FAILURE': raise SystemExit(r)
print(r['transaction_id'])
PY
)" || fail 'R36-MOVE-SYNC lacked terminal rollback JSON'
  [ -f "$run_root/mutation-transactions/$tx/result.json" ] || fail 'R36-MOVE-SYNC lacked durable result.json'

  # Transaction custody creation is itself an I/O boundary. Failure to make
  # authority durable must emit F70 JSON and leave the target bytes untouched.
  # A pre-existing transaction parent belongs to the run, not this failed
  # transaction, so its continued existence is not rollback residue.
  setup; pre="$(artifact init-sync-pre 4142434445)"; cand="$(artifact init-sync-candidate 4e4557)"; derived="$(instrumented_helper)"
  mkdir -p "$run_root/mutation-transactions"
  prepare_authority replace target -; phase="$prepared_phase"; stdout="$tmp/init-sync.out"; stderr="$tmp/init-sync.err"
  set +e; IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=init-authority-fsync bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$phase" --step 1 --preimage "$pre" --candidate "$cand" >"$stdout" 2>"$stderr"; actual=$?; set -e
  [ "$actual" -eq 70 ] || fail "R36-INIT-SYNC exit=$actual expected=70 stderr=$(<"$stderr")"
  assert_hex R36-INIT-SYNC-source "$fixture_repo/target" 4142434445
  "$python_bin" - "$stdout" <<'PY' || fail 'R36-INIT-SYNC lacked F70 terminal JSON'
import json,sys
r=json.load(open(sys.argv[1],encoding='utf-8'))
if r['status']!='MUTATION_FAILED_NO_STATE_CHANGE' or r['reason_code']!='INITIALISATION_IO_FAILURE': raise SystemExit(r)
if r['residue']: raise SystemExit(f'unexpected initialisation residue: {r["residue"]!r}')
PY
  [ -d "$run_root/mutation-transactions" ] || fail 'R36-INIT-SYNC removed pre-existing transaction parent'
  [ -z "$(find "$run_root/mutation-transactions" -mindepth 1 -print -quit)" ] || fail 'R36-INIT-SYNC retained owned transaction custody after clean F70'

  # File creation is already a mutation. Authority ownership must be known
  # before its file fsync so a failure cannot leave an unreported authority.
  setup; pre="$(artifact authority-file-pre 4142434445)"; cand="$(artifact authority-file-candidate 4e4557)"; derived="$(instrumented_helper)"
  prepare_authority replace target -; phase="$prepared_phase"; stdout="$tmp/authority-file.out"; stderr="$tmp/authority-file.err"
  set +e; IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=authority-file-fsync bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$phase" --step 1 --preimage "$pre" --candidate "$cand" >"$stdout" 2>"$stderr"; actual=$?; set -e
  [ "$actual" -eq 70 ] || fail "R36-AUTHORITY-FILE exit=$actual expected=70 stderr=$(<"$stderr")"
  assert_hex R36-AUTHORITY-FILE-source "$fixture_repo/target" 4142434445
  "$python_bin" - "$stdout" <<'PY' || fail 'R36-AUTHORITY-FILE lacked clean F70 JSON'
import json,sys
r=json.load(open(sys.argv[1],encoding='utf-8'))
if r['status']!='MUTATION_FAILED_NO_STATE_CHANGE' or r['reason_code']!='INITIALISATION_IO_FAILURE' or r['residue']: raise SystemExit(r)
PY
  [ -z "$(find "$run_root/mutation-transactions" -mindepth 1 -print -quit 2>/dev/null)" ] || fail 'R36-AUTHORITY-FILE retained unowned authority/transaction state'

  # If owned authority cleanup fails, TX is retained as custody and result.json
  # must durably bind the exact authority/TX residue before stdout reports F75.
  setup; pre="$(artifact authority-residue-pre 4142434445)"; cand="$(artifact authority-residue-candidate 4e4557)"; derived="$(instrumented_helper)"
  prepare_authority replace target -; phase="$prepared_phase"; stdout="$tmp/authority-residue.out"; stderr="$tmp/authority-residue.err"
  set +e; IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=authority-cleanup-fails bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$phase" --step 1 --preimage "$pre" --candidate "$cand" >"$stdout" 2>"$stderr"; actual=$?; set -e
  [ "$actual" -eq 75 ] || fail "R36-AUTHORITY-RESIDUE exit=$actual expected=75 stderr=$(<"$stderr")"
  assert_hex R36-AUTHORITY-RESIDUE-source "$fixture_repo/target" 4142434445
  tx="$($python_bin - "$stdout" <<'PY'
import json,sys
r=json.load(open(sys.argv[1],encoding='utf-8')); paths={x['path'] for x in r['residue']}
if r['status']!='ROLLBACK_FAILED_WITH_RESIDUE' or r['reason_code']!='INITIALISATION_IO_FAILURE': raise SystemExit(r)
if not any(x.endswith('/authority.json') for x in paths) or not any('/mutation-transactions/' in x and not x.endswith('.json') for x in paths): raise SystemExit(paths)
print(r['transaction_id'])
PY
  )" || fail 'R36-AUTHORITY-RESIDUE lacked exact F75 residue JSON'
  [ -f "$run_root/mutation-transactions/$tx/result.json" ] || fail 'R36-AUTHORITY-RESIDUE lacked durable result.json'
  "$python_bin" - "$stdout" "$run_root/mutation-transactions/$tx/result.json" <<'PY' || fail 'R36-AUTHORITY-RESIDUE durable result differs from stdout'
import json,sys
if json.load(open(sys.argv[1],encoding='utf-8')) != json.load(open(sys.argv[2],encoding='utf-8')): raise SystemExit(1)
PY

  # Result persistence can itself fail after creating result.json. Stdout must
  # then add that uncertain result file to the residue instead of overclaiming
  # a durable terminal receipt.
  setup; pre="$(artifact authority-result-pre 4142434445)"; cand="$(artifact authority-result-candidate 4e4557)"; derived="$(instrumented_helper)"
  prepare_authority replace target -; phase="$prepared_phase"; stdout="$tmp/authority-result.out"; stderr="$tmp/authority-result.err"
  set +e; IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=authority-result-fsync-fails bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$phase" --step 1 --preimage "$pre" --candidate "$cand" >"$stdout" 2>"$stderr"; actual=$?; set -e
  [ "$actual" -eq 75 ] || fail "R36-AUTHORITY-RESULT exit=$actual expected=75 stderr=$(<"$stderr")"
  assert_hex R36-AUTHORITY-RESULT-source "$fixture_repo/target" 4142434445
  "$python_bin" - "$stdout" <<'PY' || fail 'R36-AUTHORITY-RESULT lacked truthful persistence-failure residue'
import json,sys
r=json.load(open(sys.argv[1],encoding='utf-8')); paths={x['path'] for x in r['residue']}
if r['status']!='ROLLBACK_FAILED_WITH_RESIDUE': raise SystemExit(r)
for suffix in ('/authority.json','/result.json'):
 if not any(x.endswith(suffix) for x in paths): raise SystemExit(paths)
if not any('/mutation-transactions/' in x and not x.endswith('.json') for x in paths): raise SystemExit(paths)
PY

  # Each acquired lock enters the same JSON boundary. The persistent lock root
  # and namespace gate are now established by claim-run before any window can
  # open, so their creation-fsync fault belongs to the claim producer rather
  # than this mutation consumer.
  for a in lock-mkdir-parent-fsync lock-owner-file-fsync; do
    setup; pre="$(artifact "$a-pre" 4142434445)"; cand="$(artifact "$a-candidate" 4e4557)"; derived="$(instrumented_helper)"
    prepare_authority replace target -; phase="$prepared_phase"; stdout="$tmp/$a.out"; stderr="$tmp/$a.err"
    set +e; IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE="$a" bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$phase" --step 1 --preimage "$pre" --candidate "$cand" >"$stdout" 2>"$stderr"; actual=$?; set -e
    local expected_lock_exit=70; [ "$a" = lock-mkdir-parent-fsync ] && expected_lock_exit=75
    [ "$actual" -eq "$expected_lock_exit" ] || fail "R36-$a exit=$actual expected=$expected_lock_exit stderr=$(<"$stderr")"
    assert_hex "R36-$a-source" "$fixture_repo/target" 4142434445
    "$python_bin" - "$stdout" "$a" <<'PY' || fail "R36-$a lacked truthful JSON boundary"
import json,sys
r=json.load(open(sys.argv[1],encoding='utf-8')); fault=sys.argv[2]
if fault == 'lock-mkdir-parent-fsync':
 suffix='.lock'
 if r['status']!='ROLLBACK_FAILED_WITH_RESIDUE' or r['reason_code']!='IO_FAILURE' or not any(x['path'].endswith(suffix) for x in r['residue']): raise SystemExit(r)
elif r['status']!='MUTATION_FAILED_NO_STATE_CHANGE' or r['reason_code']!='IO_FAILURE' or r['residue']: raise SystemExit(r)
PY
    if [ "$a" = lock-owner-file-fsync ]; then [ -z "$(find "$fixture_repo/.IMPLEMENTAUDIT/.r36-locks" -mindepth 1 ! -name namespace.gate -print -quit 2>/dev/null)" ] || fail "R36-$a retained lock residue"; fi
  done

  # F75 is already the terminal fallback. A combined source failure, rollback
  # failure, and result fsync failure must still emit exactly one non-recursive
  # JSON result and expose the uncertain result file with retained source state.
  setup; pre="$(artifact terminal-f75-pre 4142434445)"; cand="$(artifact terminal-f75-candidate 4e4557)"; derived="$(instrumented_helper)"
  prepare_authority replace target -; phase="$prepared_phase"; stdout="$tmp/terminal-f75.out"; stderr="$tmp/terminal-f75.err"
  set +e; IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=terminal-result-fsync-after-rollback-failure bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$phase" --step 1 --preimage "$pre" --candidate "$cand" >"$stdout" 2>"$stderr"; actual=$?; set -e
  [ "$actual" -eq 75 ] || fail "R36-TERMINAL-F75 exit=$actual expected=75 stderr=$(<"$stderr")"
  [ -z "$(<"$stderr")" ] || fail "R36-TERMINAL-F75 emitted non-JSON diagnostic: $(<"$stderr")"
  assert_hex R36-TERMINAL-F75-source "$fixture_repo/target" -
  "$python_bin" - "$stdout" <<'PY' || fail 'R36-TERMINAL-F75 lacked one truthful terminal JSON'
import json,sys
lines=[x for x in open(sys.argv[1],encoding='utf-8').read().splitlines() if x.strip()]
if len(lines)!=1: raise SystemExit(lines)
r=json.loads(lines[0]); paths={x['path'] for x in r['residue']}
if r['status']!='ROLLBACK_FAILED_WITH_RESIDUE' or r['reason_code']!='RESULT_PERSISTENCE_FAILURE': raise SystemExit(r)
for suffix in ('/backup.bin','/journal.json','/result.json'):
 if not any(x.endswith(suffix) for x in paths): raise SystemExit(paths)
PY

  # Gate release is part of terminal adjudication. A release failure must
  # replace provisional success with one F75 JSON rather than print success
  # and then escape through the outer finally block.
  setup; pre="$(artifact gate-unlock-pre 4142434445)"; cand="$(artifact gate-unlock-candidate 4e4557)"; derived="$(instrumented_helper)"
  prepare_authority replace target -; phase="$prepared_phase"; stdout="$tmp/gate-unlock.out"; stderr="$tmp/gate-unlock.err"
  set +e; IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=gate-unlock-fails bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$phase" --step 1 --preimage "$pre" --candidate "$cand" >"$stdout" 2>"$stderr"; actual=$?; set -e
  [ "$actual" -eq 75 ] || fail "R36-GATE-UNLOCK exit=$actual expected=75 stderr=$(<"$stderr") stdout=$(<"$stdout")"
  [ -z "$(<"$stderr")" ] || fail "R36-GATE-UNLOCK emitted traceback/diagnostic: $(<"$stderr")"
  assert_hex R36-GATE-UNLOCK-source "$fixture_repo/target" 4e4557
  "$python_bin" - "$stdout" "$run_root" <<'PY' || fail 'R36-GATE-UNLOCK lacked one truthful terminal JSON'
import json,sys
from pathlib import Path
lines=[x for x in open(sys.argv[1],encoding='utf-8').read().splitlines() if x.strip()]
if len(lines)!=1: raise SystemExit(lines)
r=json.loads(lines[0]); paths={x['path'] for x in r['residue']}
if r['status']!='ROLLBACK_FAILED_WITH_RESIDUE' or r['reason_code']!='GATE_RELEASE_FAILURE': raise SystemExit(r)
if not any(x.endswith('/.r36-locks/namespace.gate') for x in paths): raise SystemExit(paths)
durable=Path(sys.argv[2])/'mutation-transactions'/r['transaction_id']/'result.json'
if not durable.is_file() or json.loads(durable.read_text(encoding='utf-8'))!=r: raise SystemExit('durable gate-release adjudication differs from stdout')
PY

  gate_domain_self_check

  # ABA replacement with the same visible owner token is not ownership. Lock
  # release preserves the whole directory as a durable transaction record; it
  # never deletes the actor's object after a separate identity comparison.
  setup; pre="$(artifact lock-aba-pre 4142434445)"; cand="$(artifact lock-aba-candidate 4e4557)"; derived="$(instrumented_helper)"; barrier="$tmp/lock-aba"; mkdir "$barrier"
  prepare_authority replace target -; phase="$prepared_phase"; stdout="$tmp/lock-aba.out"; stderr="$tmp/lock-aba.err"
  (set +e; IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR="$barrier" IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=lock-aba bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$phase" --step 1 --preimage "$pre" --candidate "$cand" >"$stdout" 2>"$stderr"; echo $? >"$barrier/exit") & pid=$!
  ticks=0; while [ ! -f "$barrier/paused" ] && [ "$ticks" -lt 500 ]; do sleep .02; ticks=$((ticks+1)); done; [ "$ticks" -lt 500 ] || { wait_bounded "$pid" 'R36 lock ABA helper'; fail 'R36 lock ABA did not reach acquired-lock barrier'; }
  local aba_owner aba_inode aba_token
  aba_owner="$(find "$fixture_repo/.IMPLEMENTAUDIT/.r36-locks" -mindepth 2 -maxdepth 2 -type f -name owner -print -quit)"; [ -n "$aba_owner" ] || fail 'R36 lock ABA found no acquired owner'
  aba_token="$(<"$aba_owner")"
  aba_inode="$($python_bin - "$aba_owner" <<'PY'
import os,sys
from pathlib import Path
p=Path(sys.argv[1]); data=p.read_bytes(); replacement=p.with_name('owner.external-replacement'); replacement.write_bytes(data); os.replace(replacement,p); print(os.lstat(p).st_ino)
PY
)" || fail 'R36 lock ABA could not replace owner identity'
  : >"$barrier/release"; wait_bounded "$pid" 'R36 lock ABA helper'
  [ "$(<"$barrier/exit")" -eq 75 ] || fail "R36 lock ABA exit=$(<"$barrier/exit") expected=75 stderr=$(<"$stderr")"
  assert_hex R36-lock-ABA-source "$fixture_repo/target" 4e4557
  "$python_bin" - "$stdout" "$fixture_repo" "$aba_inode" "$aba_token" <<'PY' || fail 'R36 lock ABA lacked preserved durable release record'
import json,os,sys
from pathlib import Path
r=json.load(open(sys.argv[1],encoding='utf-8')); root=Path(sys.argv[2]); inode=int(sys.argv[3]); token=sys.argv[4].encode(); paths={x['path'] for x in r['residue']}
if r['status']!='ROLLBACK_FAILED_WITH_RESIDUE': raise SystemExit(r)
owners=[root/path for path in paths if path.endswith('/owner')]
matches=[p for p in owners if p.is_file() and os.lstat(p).st_ino==inode and p.read_bytes()==token]
if len(matches)!=1 or matches[0].parent.relative_to(root).as_posix() not in paths: raise SystemExit({'paths':paths,'matches':matches})
PY

  # Once the owned lock has been moved out of the public acquisition namespace,
  # an actor may create a new public lock. Release must not touch that object.
  setup; pre="$(artifact lock-race-pre 4142434445)"; cand="$(artifact lock-race-candidate 4e4557)"; derived="$(instrumented_helper)"; barrier="$tmp/lock-post-check"; mkdir "$barrier"
  prepare_authority replace target -; phase="$prepared_phase"; stdout="$tmp/lock-post-check.out"; stderr="$tmp/lock-post-check.err"
  (set +e; IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR="$barrier" IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=lock-post-check-race bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$phase" --step 1 --preimage "$pre" --candidate "$cand" >"$stdout" 2>"$stderr"; echo $? >"$barrier/exit") & pid=$!
  ticks=0; while [ ! -f "$barrier/paused" ] && [ "$ticks" -lt 500 ]; do sleep .02; ticks=$((ticks+1)); done; [ "$ticks" -lt 500 ] || {
    wait_bounded "$pid" 'R36 lock post-check helper'
    local timeout_exit timeout_stdout timeout_stderr
    timeout_exit="$(<"$barrier/exit")"; timeout_stdout="$(<"$stdout")"; timeout_stderr="$(<"$stderr")"
    fail "R36 lock post-check race did not reach destructive seam exit=$timeout_exit stdout=$timeout_stdout stderr=$timeout_stderr"
  }
  local race_lock race_owner race_inode race_token
  race_lock="$(<"$barrier/lock-path")"; race_owner="$race_lock/owner"; race_token="$(<"$barrier/owner-token")"
  race_inode="$($python_bin - "$race_lock" "$race_token" <<'PY'
import os,sys
from pathlib import Path
lock=Path(sys.argv[1]); token=sys.argv[2].encode('ascii'); lock.mkdir(parents=True,exist_ok=True); owner=lock/'owner'; replacement=lock/'owner.external-replacement'; replacement.write_bytes(token); os.replace(replacement,owner); print(os.lstat(owner).st_ino)
PY
)" || fail 'R36 lock post-check actor could not install replacement'
  : >"$barrier/release"; wait_bounded "$pid" 'R36 lock post-check helper'
  [ "$(<"$barrier/exit")" -eq 0 ] || fail "R36 lock post-check exit=$(<"$barrier/exit") expected=0 stderr=$(<"$stderr")"
  [ -d "$race_lock" ] && [ -f "$race_owner" ] || fail 'R36 lock post-check actor lock/owner was deleted'
  [ "$(<"$race_owner")" = "$race_token" ] || fail 'R36 lock post-check actor token changed'
  [ "$(stat -c %i "$race_owner")" = "$race_inode" ] || fail 'R36 lock post-check actor identity changed'
  "$python_bin" - "$stdout" <<'PY' || fail 'R36 lock post-check race did not remain a clean commit'
import json,sys
r=json.load(open(sys.argv[1],encoding='utf-8'))
if r['status']!='COMMITTED' or r['residue']!=[]: raise SystemExit(r)
PY

  # The durable released-lock record is evidence, not a cleanup target. An
  # actor replacing its owner after publication must survive byte-for-byte and
  # by identity; there is no inner compare-then-unlink seam.
  setup; pre="$(artifact lock-record-pre 4142434445)"; cand="$(artifact lock-record-candidate 4e4557)"; derived="$(instrumented_helper)"; barrier="$tmp/lock-release-record"; mkdir "$barrier"
  prepare_authority replace target -; phase="$prepared_phase"; stdout="$tmp/lock-release-record.out"; stderr="$tmp/lock-release-record.err"
  (set +e; IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR="$barrier" IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=lock-release-record-race bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$phase" --step 1 --preimage "$pre" --candidate "$cand" >"$stdout" 2>"$stderr"; echo $? >"$barrier/exit") & pid=$!
  ticks=0; while [ ! -f "$barrier/paused" ] && [ "$ticks" -lt 500 ]; do sleep .02; ticks=$((ticks+1)); done; [ "$ticks" -lt 500 ] || { wait_bounded "$pid" 'R36 released-lock helper'; fail 'R36 released-lock race did not reach publication seam'; }
  local record_lock record_owner record_inode record_token
  record_lock="$(<"$barrier/lock-path")"; record_owner="$record_lock/owner"; record_token="$(<"$barrier/owner-token")"
  record_inode="$($python_bin - "$record_owner" "$record_token" <<'PY'
import os,sys
from pathlib import Path
owner=Path(sys.argv[1]); token=sys.argv[2].encode('ascii'); replacement=owner.with_name('owner.external-replacement'); replacement.write_bytes(token); os.replace(replacement,owner); print(os.lstat(owner).st_ino)
PY
)" || fail 'R36 released-lock actor could not install replacement'
  : >"$barrier/release"; wait_bounded "$pid" 'R36 released-lock helper'
  [ "$(<"$barrier/exit")" -eq 75 ] || fail "R36 released-lock exit=$(<"$barrier/exit") expected=75 stderr=$(<"$stderr")"
  "$python_bin" - "$stdout" "$fixture_repo" "$record_inode" "$record_token" <<'PY' || fail 'R36 released-lock actor was not restored and reported'
import json,os,sys
from pathlib import Path
r=json.load(open(sys.argv[1],encoding='utf-8')); root=Path(sys.argv[2]); inode=int(sys.argv[3]); token=sys.argv[4].encode(); paths={x['path'] for x in r['residue']}
owners=[root/path for path in paths if path.endswith('/owner')]; matches=[p for p in owners if p.is_file() and os.lstat(p).st_ino==inode and p.read_bytes()==token]
if r['status']!='ROLLBACK_FAILED_WITH_RESIDUE' or len(matches)!=1 or matches[0].parent.relative_to(root).as_posix() not in paths: raise SystemExit({'record':r,'matches':matches})
PY

  # An actor that preoccupies the deterministic release-record destination is
  # not overwritten. Atomic no-replace retains both the actor directory and
  # the still-public owned lock, producing blocking residue after the product
  # mutation rather than deleting either object.
  setup; pre="$(artifact lock-release-destination-pre 4142434445)"; cand="$(artifact lock-release-destination-candidate 4e4557)"; derived="$(instrumented_helper)"; barrier="$tmp/lock-release-destination"; mkdir "$barrier"
  prepare_authority replace target -; phase="$prepared_phase"; stdout="$tmp/lock-release-destination.out"; stderr="$tmp/lock-release-destination.err"
  (set +e; IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR="$barrier" IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=lock-release-destination-race bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$phase" --step 1 --preimage "$pre" --candidate "$cand" >"$stdout" 2>"$stderr"; echo $? >"$barrier/exit") & pid=$!
  ticks=0; while [ ! -f "$barrier/paused" ] && [ "$ticks" -lt 500 ]; do sleep .02; ticks=$((ticks+1)); done; [ "$ticks" -lt 500 ] || { wait_bounded "$pid" 'R36 released-lock destination helper'; fail 'R36 released-lock destination race did not reach acquired-lock seam'; }
  local occupied_lock occupied_owner occupied_inode
  occupied_lock="$(<"$barrier/lock-path")"; occupied_owner="$occupied_lock/owner"; mkdir "$occupied_lock"; printf 'external-release-owner' >"$occupied_owner"; occupied_inode="$(stat -c %i "$occupied_owner")"
  : >"$barrier/release"; wait_bounded "$pid" 'R36 released-lock destination helper'
  [ "$(<"$barrier/exit")" -eq 75 ] || fail "R36 released-lock destination exit=$(<"$barrier/exit") expected=75 stderr=$(<"$stderr")"
  assert_hex R36-lock-release-destination-source "$fixture_repo/target" 4e4557
  [ "$(<"$occupied_owner")" = 'external-release-owner' ] || fail 'R36 released-lock destination actor bytes changed'
  [ "$(stat -c %i "$occupied_owner")" = "$occupied_inode" ] || fail 'R36 released-lock destination actor identity changed'
  "$python_bin" - "$stdout" "$fixture_repo" "$occupied_owner" <<'PY' || fail 'R36 released-lock destination lacked owned-lock residue distinction'
import json,sys
from pathlib import Path
r=json.load(open(sys.argv[1],encoding='utf-8')); root=Path(sys.argv[2]); actor=Path(sys.argv[3]); residue={x['path'] for x in r['residue']}; actor_relative=actor.relative_to(root).as_posix()
if r['status']!='ROLLBACK_FAILED_WITH_RESIDUE' or r['reason_code']!='IO_FAILURE' or actor_relative in residue: raise SystemExit(r)
if not any(path.startswith('.IMPLEMENTAUDIT/.r36-locks/') for path in residue): raise SystemExit(residue)
PY

  # Replacing the whole public lock directory after acquisition must not move
  # the actor directory into transaction custody and report success. The moved
  # identity is adjudicated under the unchanged governed-writer gate and restored
  # without replacing either an actor-owned public or release path.
  setup; pre="$(artifact lock-directory-aba-pre 4142434445)"; cand="$(artifact lock-directory-aba-candidate 4e4557)"; derived="$(instrumented_helper)"; barrier="$tmp/lock-directory-aba"; mkdir "$barrier"
  prepare_authority replace target -; phase="$prepared_phase"; stdout="$tmp/lock-directory-aba.out"; stderr="$tmp/lock-directory-aba.err"
  (set +e; IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR="$barrier" IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=lock-directory-aba bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$phase" --step 1 --preimage "$pre" --candidate "$cand" >"$stdout" 2>"$stderr"; echo $? >"$barrier/exit") & pid=$!
  ticks=0; while [ ! -f "$barrier/paused" ] && [ "$ticks" -lt 500 ]; do sleep .02; ticks=$((ticks+1)); done; [ "$ticks" -lt 500 ] || { wait_bounded "$pid" 'R36 whole-directory ABA helper'; fail 'R36 whole-directory ABA did not reach acquired-lock seam'; }
  local directory_lock directory_owner directory_inode directory_token
  directory_lock="$(<"$barrier/lock-path")"; directory_token="$(<"$barrier/owner-token")"; mv "$directory_lock" "$directory_lock.original"; mkdir "$directory_lock"; directory_owner="$directory_lock/owner"; printf '%s' "$directory_token" >"$directory_owner"; directory_inode="$(stat -c %i "$directory_owner")"
  : >"$barrier/release"; wait_bounded "$pid" 'R36 whole-directory ABA helper'
  [ "$(<"$barrier/exit")" -eq 75 ] || fail "R36 whole-directory ABA exit=$(<"$barrier/exit") expected=75 stderr=$(<"$stderr")"
  assert_hex R36-lock-directory-ABA-source "$fixture_repo/target" 4e4557
  [ -f "$directory_owner" ] && [ "$(<"$directory_owner")" = "$directory_token" ] || fail 'R36 whole-directory ABA actor bytes were not restored'
  [ "$(stat -c %i "$directory_owner")" = "$directory_inode" ] || fail 'R36 whole-directory ABA actor identity changed'
  [ -d "$directory_lock.original" ] && [ -f "$directory_lock.original/owner" ] || fail 'R36 whole-directory ABA displaced original lock disappeared'
  "$python_bin" - "$stdout" "$fixture_repo" "$directory_lock" <<'PY' || fail 'R36 whole-directory ABA lacked truthful blocking residue'
import json,sys
from pathlib import Path
r=json.load(open(sys.argv[1],encoding='utf-8')); root=Path(sys.argv[2]); lock=Path(sys.argv[3]); paths={x['path'] for x in r['residue']}
relative=lock.relative_to(root).as_posix()
if r['status']!='ROLLBACK_FAILED_WITH_RESIDUE' or relative not in paths: raise SystemExit(r)
PY

  # A later governed peer cannot enter the acquisition namespace while the
  # first helper adjudicates and restores a whole-directory substitution. It
  # blocks on the unchanged governed-writer gate, then observes the restored
  # public lock as busy.
  setup; pre="$(artifact gate-peer-pre 4142434445)"; cand="$(artifact gate-peer-candidate 4e4557)"; derived="$(instrumented_helper)"; barrier="$tmp/gate-peer"; mkdir "$barrier"
  prepare_authority replace target -; local gate_phase_a="$prepared_phase"; stdout="$tmp/gate-peer-a.out"; stderr="$tmp/gate-peer-a.err"
  (set +e; IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR="$barrier" IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=lock-directory-aba-peer bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$gate_phase_a" --step 1 --preimage "$pre" --candidate "$cand" >"$stdout" 2>"$stderr"; echo $? >"$barrier/a.exit") & local gate_pid_a=$!
  ticks=0; while [ ! -f "$barrier/acquired" ] && [ "$ticks" -lt 500 ]; do sleep .02; ticks=$((ticks+1)); done; [ "$ticks" -lt 500 ] || { wait_bounded "$gate_pid_a" 'R36 gate first helper'; fail 'R36 gate first helper did not acquire locks'; }
  local gate_lock gate_owner gate_token gate_inode
  gate_lock="$fixture_repo/.IMPLEMENTAUDIT/.r36-locks/$($python_bin - <<'PY'
import hashlib
print(hashlib.sha256(b'target').hexdigest() + '.lock')
PY
)"; gate_owner="$gate_lock/owner"; [ -f "$gate_owner" ] || fail 'R36 gate first helper did not acquire the shared target lock'; gate_token="$(<"$gate_owner")"; mv "$gate_lock" "$gate_lock.original"; mkdir "$gate_lock"; printf '%s' "$gate_token" >"$gate_lock/owner"; gate_inode="$(stat -c %i "$gate_lock/owner")"; : >"$barrier/replace"
  ticks=0; while [ ! -f "$barrier/mismatch" ] && [ "$ticks" -lt 500 ]; do sleep .02; ticks=$((ticks+1)); done; [ "$ticks" -lt 500 ] || { : >"$barrier/finish"; wait_bounded "$gate_pid_a" 'R36 gate first helper'; fail 'R36 gate first helper did not reach mismatch adjudication'; }
  local peer_pre peer_cand peer_stdout peer_stderr gate_pid_b reoccupied_inode
  peer_pre="$(artifact gate-peer-second-pre 4e4557)"; peer_cand="$(artifact gate-peer-second-candidate 50454552)"; prepare_authority replace target -; local gate_phase_b="$prepared_phase"; peer_stdout="$tmp/gate-peer-b.out"; peer_stderr="$tmp/gate-peer-b.err"
  (set +e; bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$gate_phase_b" --step 1 --preimage "$peer_pre" --candidate "$peer_cand" >"$peer_stdout" 2>"$peer_stderr"; echo $? >"$barrier/b.exit") & gate_pid_b=$!
  sleep .2; kill -0 "$gate_pid_b" 2>/dev/null || fail 'R36 governed peer did not remain excluded by namespace gate'; [ ! -f "$barrier/b.exit" ] || fail 'R36 governed peer completed inside protected restore window'
  mkdir "$gate_lock"; printf 'public-reoccupier' >"$gate_lock/owner"; reoccupied_inode="$(stat -c %i "$gate_lock/owner")"
  : >"$barrier/finish"; wait_bounded "$gate_pid_a" 'R36 gate first helper'; wait_bounded "$gate_pid_b" 'R36 gate second helper'
  [ "$(<"$barrier/a.exit")" -eq 75 ] || fail "R36 gate first exit=$(<"$barrier/a.exit") expected=75 stderr=$(<"$stderr")"
  [ "$(<"$barrier/b.exit")" -eq 65 ] || fail "R36 gate peer exit=$(<"$barrier/b.exit") expected=65 stderr=$(<"$peer_stderr")"
  assert_hex R36-gate-peer-source "$fixture_repo/target" 4e4557
  [ -f "$gate_lock/owner" ] && [ "$(<"$gate_lock/owner")" = public-reoccupier ] && [ "$(stat -c %i "$gate_lock/owner")" = "$reoccupied_inode" ] || fail 'R36 gate restore clobbered public reoccupation'
  "$python_bin" - "$stdout" "$fixture_repo" "$gate_inode" "$gate_token" <<'PY' || fail 'R36 gate restore did not preserve moved actor lock'
import json,os,sys
from pathlib import Path
r=json.load(open(sys.argv[1],encoding='utf-8')); root=Path(sys.argv[2]); inode=int(sys.argv[3]); token=sys.argv[4].encode(); paths={x['path'] for x in r['residue']}; owners=[root/path for path in paths if path.endswith('/owner')]
matches=[p for p in owners if p.is_file() and os.lstat(p).st_ino==inode and p.read_bytes()==token]
if r['status']!='ROLLBACK_FAILED_WITH_RESIDUE' or len(matches)!=1: raise SystemExit({'record':r,'matches':matches})
PY
  "$python_bin" - "$peer_stdout" <<'PY' || fail 'R36 governed peer did not report public lock conflict after gate release'
import json,sys
r=json.load(open(sys.argv[1],encoding='utf-8'))
if r['status']!='CONFLICT_REBASE' or r['reason_code']!='TARGET_LOCK_BUSY' or r['residue']!=[]: raise SystemExit(r)
PY

  # Internal transaction and lock custody paths may be absent or ordinary
  # directories only; symlink/reparse redirection fails before mutation.
  setup; mkdir "$tmp/tx-outside"; rm -rf "$run_root/mutation-transactions"; "$python_bin" - "$tmp/tx-outside" "$run_root/mutation-transactions" <<'PY' 2>/dev/null && {
import os,sys
os.symlink(sys.argv[1],sys.argv[2],target_is_directory=True)
PY
    pre="$(artifact tx-link-pre 4142434445)"; cand="$(artifact tx-link-candidate 4e4557)"; prepare_authority replace target -; set +e; stdout="$(bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$prepared_phase" --step 1 --preimage "$pre" --candidate "$cand")"; actual=$?; set -e
    [ "$actual" -eq 64 ] || fail 'R36 internal transaction symlink was not rejected'; assert_hex R36-tx-link-target "$fixture_repo/target" 4142434445; [ -z "$(find "$tmp/tx-outside" -mindepth 1 -print -quit)" ] || fail 'R36 transaction symlink escaped custody'
  }
  setup; mkdir "$tmp/lock-outside"; "$python_bin" - "$tmp/lock-outside" "$fixture_repo/.IMPLEMENTAUDIT/.r36-locks" <<'PY' 2>/dev/null && {
import os,sys
os.symlink(sys.argv[1],sys.argv[2],target_is_directory=True)
PY
    pre="$(artifact lock-link-pre 4142434445)"; cand="$(artifact lock-link-candidate 4e4557)"; prepare_authority replace target -; set +e; stdout="$(bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$prepared_phase" --step 1 --preimage "$pre" --candidate "$cand")"; actual=$?; set -e
    [ "$actual" -eq 64 ] || fail 'R36 internal lock symlink was not rejected'; assert_hex R36-lock-link-target "$fixture_repo/target" 4142434445; [ -z "$(find "$tmp/lock-outside" -mindepth 1 -print -quit)" ] || fail 'R36 lock symlink escaped custody'
  }

  # Patch authority is bound to the full observed representation, not merely
  # equal bytes: an inode replacement after observation must conflict.
  setup; derived="$(instrumented_helper)"; region="$(artifact heldout-region 4243)"; repl="$(artifact heldout-repl 5859)"; prepare_authority patch target -; phase="$prepared_phase"; barrier="$tmp/patch-race"; mkdir "$barrier"; stdout="$tmp/patch-race.out"; stderr="$tmp/patch-race.err"
  (set +e; IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR="$barrier" bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$phase" --step 1 --offset 1 --region "$region" --replacement "$repl" >"$stdout" 2>"$stderr"; echo $? >"$barrier/exit") & pid=$!
  ticks=0; while [ ! -f "$barrier/observed" ] && [ "$ticks" -lt 500 ]; do sleep .02; ticks=$((ticks+1)); done; [ "$ticks" -lt 500 ] || fail 'R36 patch heldout did not reach observation barrier'
  local before_inode after_inode; before_inode="$(stat -c %i "$fixture_repo/target")"; write_hex "$fixture_repo/target.replacement" 4142434445; mv "$fixture_repo/target.replacement" "$fixture_repo/target"; after_inode="$(stat -c %i "$fixture_repo/target")"; [ "$before_inode" != "$after_inode" ] || fail 'R36 patch heldout did not change inode'; : >"$barrier/release"; wait_bounded "$pid" 'R36 patch heldout'; [ "$(<"$barrier/exit")" -eq 65 ] || fail "R36 patch same-byte representation drift did not conflict: $(<"$stderr")"; assert_hex R36-patch-heldout "$fixture_repo/target" 4142434445

  setup; derived="$(instrumented_helper)"; pre="$(artifact link-count-pre 4142434445)"; cand="$(artifact link-count-candidate 4e4557)"; prepare_authority replace target -; phase="$prepared_phase"; barrier="$tmp/link-count-race"; mkdir "$barrier"; stdout="$tmp/link-count.out"; stderr="$tmp/link-count.err"
  (set +e; IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR="$barrier" bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$phase" --step 1 --preimage "$pre" --candidate "$cand" >"$stdout" 2>"$stderr"; echo $? >"$barrier/exit") & pid=$!
  ticks=0; while [ ! -f "$barrier/observed" ] && [ "$ticks" -lt 500 ]; do sleep .02; ticks=$((ticks+1)); done; [ "$ticks" -lt 500 ] || fail 'R36 link-count heldout did not reach observation barrier'; ln "$fixture_repo/target" "$fixture_repo/topology-sibling"; [ "$(stat -c %h "$fixture_repo/target")" -gt 1 ] || fail 'R36 link-count heldout did not change nlink'; : >"$barrier/release"; wait_bounded "$pid" 'R36 link-count heldout'; [ "$(<"$barrier/exit")" -eq 65 ] || fail 'R36 same-byte link-count drift did not conflict'; assert_hex R36-link-count-heldout "$fixture_repo/target" 4142434445

  # One phase/step is one deterministic transaction. Two peers receive JSON;
  # exactly one may commit and the other reports the replay/in-progress conflict.
  setup; derived="$(instrumented_helper)"; pre="$(artifact same-authority-pre 4142434445)"; cand="$(artifact same-authority-candidate 4e4557)"; prepare_authority replace target -; phase="$prepared_phase"; barrier="$tmp/same-authority"; mkdir -p "$barrier/a" "$barrier/b"
  for a in a b; do (set +e; IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR="$barrier/$a" IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=same-authority-pretransaction bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$phase" --step 1 --preimage "$pre" --candidate "$cand" >"$barrier/$a.out" 2>"$barrier/$a.err"; echo $? >"$barrier/$a.exit") & [ "$a" = a ] && pid=$! || b=$!; done
  ticks=0; while { [ ! -f "$barrier/a/ready" ] || [ ! -f "$barrier/b/ready" ]; } && [ "$ticks" -lt 500 ]; do sleep .02; ticks=$((ticks+1)); done; [ "$ticks" -lt 500 ] || fail 'R36 same-authority peers did not both reach the pre-transaction barrier'; : >"$barrier/a/release"; : >"$barrier/b/release"; wait_bounded "$pid" 'R36 same-authority a'; wait_bounded "$b" 'R36 same-authority b'
  "$python_bin" - "$barrier" <<'PY' || fail 'R36 same-authority did not produce one commit and one JSON conflict'
import json,sys
from pathlib import Path
b=Path(sys.argv[1]); rows=[]
for n in ('a','b'):
 raw=(b/f'{n}.out').read_text(); err=(b/f'{n}.err').read_text(); code=int((b/f'{n}.exit').read_text())
 try: status=json.loads(raw)['status']
 except Exception as exc: raise SystemExit({'actor':n,'exit':code,'stdout':raw,'stderr':err,'parse_error':str(exc)})
 rows.append((code,status))
if sorted(rows)!=[(0,'COMMITTED'),(65,'CONFLICT_REBASE')]: raise SystemExit(rows)
PY

  # Lexical aliases do not become acceptable merely because abspath resolves
  # them to the claimed repository.
  setup; pre="$(artifact alias-pre 4142434445)"; cand="$(artifact alias-candidate 4e4557)"; prepare_authority replace target -; set +e; stdout="$(bash "$helper" --repo-root "$fixture_repo/." --run-root "$run_root" --phase "$prepared_phase" --step 1 --preimage "$pre" --candidate "$cand" 2>/dev/null)"; actual=$?; set -e
  [ "$actual" -eq 64 ] && [ -z "$stdout" ] || fail 'R36 lexical repository alias was normalised before strict claim validation'
}

controller_stale_heldout() {
  local controller=s3e-w02-stale old_claim successor pre cand stdout stderr actual
  setup "$controller"
  old_claim="$(sed -n 's/^claim_id=//p' "$run_root/.claimed")"
  pre="$(artifact controller-stale-pre 4142434445)"; cand="$(artifact controller-stale-candidate 4e4557)"
  prepare_authority replace target -
  successor="$(cd "$fixture_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs bash "$repo_root/skills/implementaudit/scripts/claim-run.sh" --controller "$controller" --supersede-claim "$old_claim" 's3e w02 successor' 2>/dev/null)" || fail 'S3E-W02 successor transfer fixture failed'
  [ -f "$fixture_repo/$successor/.claimed" ] || fail 'S3E-W02 successor root is absent'
  stdout="$tmp/controller-stale.out"; stderr="$tmp/controller-stale.err"
  set +e; bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$prepared_phase" --step 1 --preimage "$pre" --candidate "$cand" >"$stdout" 2>"$stderr"; actual=$?; set -e
  if [ "$actual" -eq 0 ]; then fail 'S3E-W02 RED: stale controller reached governed mutation sink'; fi
  [ "$actual" -eq 77 ] || fail "S3E-W02 stale controller exit=$actual expected=77 stderr=$(<"$stderr")"
  assert_hex S3E-W02-stale-controller "$fixture_repo/target" 4142434445
  "$python_bin" - "$stdout" <<'PY' || fail 'S3E-W02 stale controller refusal is not explicit'
import json,sys
from pathlib import Path
r=json.loads(Path(sys.argv[1]).read_text())
assert r['status']=='UNSUPPORTED_OWNER_DECISION' and r['reason_code']=='STALE_CONTROLLER_CUSTODY'
assert r['transaction_id'] is None and r['actual_effect_set']==[]
PY
  setup s3e-w02-malformed
  pre="$(artifact controller-malformed-pre 4142434445)"; cand="$(artifact controller-malformed-candidate 4e4557)"
  prepare_authority replace target -
  printf 'controller_id=s3e-w02-malformed \n' >"$run_root/.controller"
  set +e; bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$prepared_phase" --step 1 --preimage "$pre" --candidate "$cand" >"$tmp/S3E-W02-malformed.out" 2>"$tmp/S3E-W02-malformed.err"; actual=$?; set -e
  [ "$actual" -eq 77 ] || fail "S3E-W02 malformed controller exit=$actual expected=77"
  assert_hex S3E-W02-malformed "$fixture_repo/target" 4142434445
  "$python_bin" - "$tmp/S3E-W02-malformed.out" <<'PY' || fail 'S3E-W02 malformed controller record lacked named refusal'
import json,sys
from pathlib import Path
assert json.loads(Path(sys.argv[1]).read_text())['reason_code']=='STALE_CONTROLLER_CUSTODY'
PY
}

post_compaction_continuity_heldout() {
  local controller=s3e-continuity claim controller_oid marker marker_ref pre cand stdout stderr actual
  setup "$controller"
  claim="$(sed -n 's/^claim_id=//p' "$run_root/.claimed")"
  controller_oid="$(git -C "$fixture_repo" rev-parse "refs/implementaudit/controllers/$controller")"
  marker_ref="refs/implementaudit/continuity-invalidations/$controller"
  pre="$(artifact continuity-pre 4142434445)"; cand="$(artifact continuity-candidate 4e4557)"
  prepare_authority replace target -
  marker="$(printf 'implementaudit.continuity-invalidation.v1\t%s\t%s\t%s\thost-reported-compaction\tincident-e13\n' \
    "$controller" "$controller_oid" "$claim" | git -C "$fixture_repo" hash-object -w --stdin)"
  git -C "$fixture_repo" update-ref "$marker_ref" "$marker"
  stdout="$tmp/continuity.out"; stderr="$tmp/continuity.err"
  set +e; bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$prepared_phase" --step 1 --preimage "$pre" --candidate "$cand" >"$stdout" 2>"$stderr"; actual=$?; set -e
  if [ "$actual" -eq 0 ]; then
    fail 'POST_COMPACTION_WITHOUT_FRESH_CONTINUITY false-greened governed mutation'
  fi
  [ "$actual" -eq 77 ] || fail "post-compaction continuity refusal exit=$actual expected=77 stderr=$(<"$stderr")"
  assert_hex post-compaction-continuity "$fixture_repo/target" 4142434445
  [ ! -e "$run_root/mutation-transactions" ] || fail 'post-compaction continuity refusal created transaction state'
  "$python_bin" - "$stdout" <<'PY' || fail 'post-compaction continuity refusal is not explicit'
import json,sys
from pathlib import Path
r=json.loads(Path(sys.argv[1]).read_text())
assert r['status']=='UNSUPPORTED_OWNER_DECISION' and r['reason_code']=='STALE_CONTINUITY_RECEIPT'
assert r['transaction_id'] is None and r['actual_effect_set']==[]
PY
}

post_compaction_marker_deletion_heldout() {
  local controller=s3e-continuity-marker-deletion claim controller_oid marker marker_ref pre cand stdout stderr actual sibling
  setup "$controller"
  claim="$(sed -n 's/^claim_id=//p' "$run_root/.claimed")"
  controller_oid="$(git -C "$fixture_repo" rev-parse "refs/implementaudit/controllers/$controller")"
  marker_ref="refs/implementaudit/continuity-invalidations/$controller"
  pre="$(artifact continuity-marker-pre 4142434445)"; cand="$(artifact continuity-marker-candidate 4e4557)"
  prepare_authority replace target -
  marker="$(printf 'implementaudit.continuity-invalidation.v1\t%s\t%s\t%s\thost-reported-compaction\tincident-e13\n' \
    "$controller" "$controller_oid" "$claim" | git -C "$fixture_repo" hash-object -w --stdin)"
  git -C "$fixture_repo" update-ref "$marker_ref" "$marker"
  sibling="$(cd "$fixture_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs bash "$repo_root/skills/implementaudit/scripts/claim-run.sh" \
    --controller s3e-continuity-sibling 's3e continuity sibling')" || fail 'sibling controller fixture failed'
  [ -f "$fixture_repo/$sibling/.claimed" ] || fail 'sibling controller root is absent'
  rm "$run_root/.controller"
  stdout="$tmp/continuity-marker-deletion.out"; stderr="$tmp/continuity-marker-deletion.err"
  set +e; bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$prepared_phase" --step 1 --preimage "$pre" --candidate "$cand" >"$stdout" 2>"$stderr"; actual=$?; set -e
  if [ "$actual" -eq 0 ]; then
    fail 'POST_COMPACTION_WITHOUT_FRESH_CONTINUITY marker deletion false-greened governed mutation'
  fi
  [ "$actual" -eq 77 ] || fail "post-compaction marker-deletion refusal exit=$actual expected=77 stderr=$(<"$stderr")"
  assert_hex post-compaction-marker-deletion "$fixture_repo/target" 4142434445
  [ ! -e "$run_root/mutation-transactions" ] || fail 'post-compaction marker-deletion refusal created transaction state'
  "$python_bin" - "$stdout" <<'PY' || fail 'post-compaction marker-deletion refusal is not explicit'
import json,sys
from pathlib import Path
r=json.loads(Path(sys.argv[1]).read_text())
assert r['status']=='UNSUPPORTED_OWNER_DECISION' and r['reason_code']=='STALE_CONTROLLER_CUSTODY'
assert r['transaction_id'] is None and r['actual_effect_set']==[]
PY
}

controller_transfer_race_heldout() {
  local controller=s3e-w02-race old_claim pre cand derived barrier helper_pid transfer_pid ticks helper_rc transfer_rc current
  setup "$controller"; old_claim="$(sed -n 's/^claim_id=//p' "$run_root/.claimed")"
  pre="$(artifact controller-race-pre 4142434445)"; cand="$(artifact controller-race-candidate 4e4557)"
  prepare_authority replace target -; derived="$(instrumented_helper)"; barrier="$tmp/controller-transfer-race"; mkdir "$barrier"
  (IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR="$barrier" IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=lock-aba bash "$derived" --repo-root "$fixture_repo" --run-root "$run_root" --phase "$prepared_phase" --step 1 --preimage "$pre" --candidate "$cand" >"$barrier/helper.out" 2>"$barrier/helper.err") & helper_pid=$!
  owned_background_pids=("$helper_pid"); owned_release_path="$barrier/release"
  ticks=0; while [ ! -f "$barrier/paused" ] && [ "$ticks" -lt 500 ]; do sleep .02; ticks=$((ticks+1)); done
  [ -f "$barrier/paused" ] || fail "S3E-W02 controller race did not reach protected mutation boundary: $(<"$barrier/helper.err")"
  (cd "$fixture_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs bash "$repo_root/skills/implementaudit/scripts/claim-run.sh" --controller "$controller" --supersede-claim "$old_claim" 's3e w02 raced successor' >"$barrier/transfer.out" 2>"$barrier/transfer.err") & transfer_pid=$!
  owned_background_pids+=("$transfer_pid")
  for _ in $(seq 1 100); do [ ! -s "$barrier/transfer.out" ] || break; sleep .02; done
  if [ -s "$barrier/transfer.out" ]; then
    : >"$barrier/release"; wait "$helper_pid" || true; wait "$transfer_pid" || true
    owned_background_pids=(); owned_release_path=
    fail 'S3E-W02 RED: controller transfer raced protected mutation'
  fi
  : >"$barrier/release"; set +e; wait "$helper_pid"; helper_rc=$?; wait "$transfer_pid"; transfer_rc=$?; set -e
  owned_background_pids=(); owned_release_path=
  [ "$helper_rc" -eq 0 ] || fail "S3E-W02 protected mutation failed before transfer: $helper_rc $(<"$barrier/helper.err")"
  [ "$transfer_rc" -eq 0 ] || fail "S3E-W02 serialized transfer failed: $transfer_rc $(<"$barrier/transfer.err")"
  assert_hex S3E-W02-controller-race "$fixture_repo/target" 4e4557
  for promised in STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md; do cp "$repo_root/skills/implementaudit/templates/$promised" "$fixture_repo/$(<"$barrier/transfer.out")/$promised"; done
  current="$(cd "$fixture_repo" && bash "$repo_root/skills/implementaudit/scripts/claim-run.sh" --current-controller "$controller")" || fail 'S3E-W02 raced successor is not current'
  [ "$(printf '%s' "$current" | cut -f4)" = "$(sed -n 's/^claim_id=//p' "$fixture_repo/$(<"$barrier/transfer.out")/.claimed")" ] || fail 'S3E-W02 transfer result and current controller differ'
}

state_family() {
  local pre cand region repl
  setup; pre="$(artifact c1-pre 414243)"; cand="$(artifact c1-candidate 5a)"; invoke R36-C1 REJECTED_NO_MUTATION replace target - "$cand" 4142434445 --preimage "$pre" --candidate "$cand"
  setup; pre="$(artifact c2-pre 4142434445)"; cand="$(artifact c2-candidate 5a)"; write_hex "$fixture_repo/target" 494e54455256454e494e47; invoke R36-C2 CONFLICT_REBASE replace target - "$cand" 494e54455256454e494e47 --preimage "$pre" --candidate "$cand"
  # C3 is intentionally collapsed into the actual invariant: a byte-equal,
  # complete current preimage is the only qualifying observation.
  setup; pre="$(artifact c3-partial 414243)"; cand="$(artifact c3-candidate 5a)"; invoke R36-C3 REJECTED_NO_MUTATION replace target - "$cand" 4142434445 --preimage "$pre" --candidate "$cand"
  setup; pre="$(artifact c4-pre 4142434445)"; cand="$(artifact c4-candidate 5a)"; write_hex "$fixture_repo/sentinel" 53414645; mutator="$fixture_repo/artifacts/operative-mutator.sh"; "$python_bin" - "$mutator" "$fixture_repo/sentinel" <<'PY'
import os,sys
from pathlib import Path
p=Path(sys.argv[1]); p.write_text('#!/usr/bin/env bash\nprintf PWNED > "$1"\n',encoding='utf-8'); os.chmod(p,0o700)
PY
  invoke R36-C4 REJECTED_NO_MUTATION replace target - "$cand" 4142434445 --preimage "$pre" --candidate "$cand" --arbitrary-mutator "$mutator" "$fixture_repo/sentinel"; assert_hex R36-C4-sentinel "$fixture_repo/sentinel" 53414645
  # Ambient test labels are inert to the authoritative helper. Only the
  # mechanically derived, unshipped driver may consume them.
  setup; pre="$(artifact ambient-pre 4142434445)"; cand="$(artifact ambient-candidate 4e4557)"; IMPLEMENTAUDIT_R36_TEST_FAULT_STAGE=after-publication IMPLEMENTAUDIT_R36_TEST_BARRIER_DIR="$tmp/ambient-inert" invoke R36-AMBIENT-inert COMMITTED replace target - "$cand" 4e4557 --preimage "$pre" --candidate "$cand"
  setup; region="$(artifact crlf-region 74776f0d0a)"; repl="$(artifact crlf-repl 54574f0d0a)"; invoke R36-B1 COMMITTED patch crlf - "$repl" 6f6e650d0a54574f0d0a74687265650d0a --offset 5 --region "$region" --replacement "$repl"
  setup; region="$(artifact unicode-region e282ac2de4b8ade69687)"; repl="$(artifact unicode-repl f09f9880)"; invoke R36-B2 COMMITTED patch unicode - "$repl" 7072656669782df09f98802d737566666978 --offset 7 --region "$region" --replacement "$repl"
  setup; region="$(artifact split-region e2)"; repl="$(artifact split-repl 58)"; invoke R36-B2-split COMMITTED patch unicode - "$repl" 7072656669782d5882ac2de4b8ade696872d737566666978 --offset 7 --region "$region" --replacement "$repl"
  setup; region="$(artifact empty-region '')"; repl="$(artifact empty-repl 58)"; invoke R36-B2-empty REJECTED_NO_MUTATION patch target - "$repl" 4142434445 --offset 0 --region "$region" --replacement "$repl"
  # Canonical helper fault stages exercise concrete terminal families and
  # byte restoration at each transaction boundary.
  setup; pre="$(artifact fault-pre-displacement 4142434445)"; cand="$(artifact fault-candidate 4e4557)"; invoke_fault pre-displacement R36-F70 MUTATION_FAILED_NO_STATE_CHANGE replace target - "$cand" 4142434445 --preimage "$pre" --candidate "$cand"
  setup; pre="$(artifact fault-after-displacement 4142434445)"; cand="$(artifact fault-candidate 4e4557)"; invoke_fault after-displacement R36-F71a MUTATION_FAILED_ROLLED_BACK replace target - "$cand" 4142434445 --preimage "$pre" --candidate "$cand"
  setup; pre="$(artifact fault-after-publication 4142434445)"; cand="$(artifact fault-candidate 4e4557)"; invoke_fault after-publication R36-F71b MUTATION_FAILED_ROLLED_BACK replace target - "$cand" 4142434445 --preimage "$pre" --candidate "$cand"
  setup; pre="$(artifact fault-post-mismatch 4142434445)"; cand="$(artifact fault-candidate 4e4557)"; invoke_fault post-state-mismatch R36-F72 POST_STATE_MISMATCH_ROLLED_BACK replace target - "$cand" 4142434445 --preimage "$pre" --candidate "$cand"
  setup; pre="$(artifact fault-unsupported 4142434445)"; cand="$(artifact fault-candidate 4e4557)"; invoke_fault unsupported-external-writer R36-F77 UNSUPPORTED_OWNER_DECISION replace target - "$cand" 554e535550504f525445442d575249544552 --preimage "$pre" --candidate "$cand"
  setup; pre="$(artifact binary-pre 0001ff7f42494e0d0a)"; cand="$(artifact binary-candidate ff0042494e2d)"; invoke R36-B3 COMMITTED replace binary - "$cand" ff0042494e2d --preimage "$pre" --candidate "$cand"; pre="$(artifact binary-delete-pre ff0042494e2d)"; invoke R36-B4 COMMITTED delete binary - - - --preimage "$pre"; setup; pre="$(artifact binary-move-pre 0001ff7f42494e0d0a)"; invoke R36-B5 COMMITTED move binary binary-destination "$pre" 0001ff7f42494e0d0a --preimage "$pre"; assert_hex R36-B5-source-absent "$fixture_repo/binary" -; assert_hex R36-B5-destination "$fixture_repo/binary-destination" 0001ff7f42494e0d0a
  setup; pre="$(artifact hard-pre 5349424c494e47)"; cand="$(artifact hard-candidate 4e4557)"; invoke R36-T1 COMMITTED replace hardlink - "$cand" 4e4557 --preimage "$pre" --candidate "$cand"; assert_hex R36-T1-sibling "$fixture_repo/sibling" 5349424c494e47
  setup; pre="$(artifact equal-pre 53414d45)"; cand="$(artifact equal-candidate 4e4557)"; invoke R36-T1-equal COMMITTED replace equal-one - "$cand" 4e4557 --preimage "$pre" --candidate "$cand"; assert_hex R36-T1-equal-other "$fixture_repo/equal-two" 53414d45
  setup; pre="$(artifact scope-pre 4142434445)"; cand="$(artifact scope-candidate 4e4557)"; invoke R36-T2 REJECTED_NO_MUTATION replace target - "$cand" 4142434445 --preimage "$pre" --candidate "$cand" --target ../existing-outside-target; [ "$(cat "$fixture_repo/symlink-capability")" = yes ] && { pre="$(artifact link-pre 4142434445)"; invoke R36-T3 REJECTED_NO_MUTATION replace final-link - "$cand" @SYMLINK_PATH --preimage "$pre" --candidate "$cand"; assert_hex R36-T3-outside-referent "$fixture_repo/target" 4142434445; pre="$(artifact parent-pre 6368696c64)"; invoke R36-T4 REJECTED_NO_MUTATION replace parent-link/child - "$cand" @SYMLINK_PATH --preimage "$pre" --candidate "$cand"; assert_hex R36-T4-ancestor-outside-referent "$fixture_repo/real/child" 6368696c64; }
  setup; pre="$(artifact reference-pre 4142434445)"; ln -s "$(basename "$pre")" "$fixture_repo/artifacts/reference-preimage" 2>/dev/null || true; if [ -L "$fixture_repo/artifacts/reference-preimage" ]; then cand="$(artifact reference-candidate 4e4557)"; invoke R36-T5 REJECTED_NO_MUTATION replace target - "$cand" 4142434445 --preimage "$fixture_repo/artifacts/reference-preimage" --candidate "$cand"; fi
  setup; pre="$(artifact stale-delete-pre 414243)"; invoke R36-D1 REJECTED_NO_MUTATION delete target - - 4142434445 --preimage "$pre"; pre="$(artifact stale-move-pre 414243)"; invoke R36-D2 REJECTED_NO_MUTATION move target absent-destination "$pre" 4142434445 --preimage "$pre"; assert_hex R36-D2-destination-absent "$fixture_repo/absent-destination" -
  setup; pre="$(artifact stale-move-full-pre 4142434445)"; write_hex "$fixture_repo/target" 4c41544552; invoke R36-D2-currentness CONFLICT_REBASE move target absent-destination "$pre" 4c41544552 --preimage "$pre"; assert_hex R36-D2-currentness-destination-absent "$fixture_repo/absent-destination" -
  setup; pre="$(artifact move-pre 4142434445)"; write_hex "$fixture_repo/existing-destination" 455849535453; invoke R36-D3 REJECTED_NO_MUTATION move target existing-destination "$pre" 4142434445 --preimage "$pre"; assert_hex R36-D3-destination "$fixture_repo/existing-destination" 455849535453
  setup; pre="$(artifact same-pre 4142434445)"; invoke R36-D4 REJECTED_NO_MUTATION move target absent-destination "$pre" 4142434445 --preimage "$pre" --destination target
  setup; mkdir "$fixture_repo/directory-target"; pre="$(artifact regular-pre 4142434445)"; cand="$(artifact regular-candidate 4e4557)"; invoke R36-D5 REJECTED_NO_MUTATION replace directory-target - "$cand" @DIRECTORY --preimage "$pre" --candidate "$cand"
  # Cheap controls are not helper triggers: read-only inspection, disposable
  # task-owned creation, and unrelated diagnostics leave the named bytes alone.
  setup; assert_hex R36-P1-read-only "$fixture_repo/target" 4142434445; : > "$run_root/disposable"; [ -f "$run_root/disposable" ] || fail 'R36-P1 disposable creation failed'
  setup; local run_relative="${run_root#$fixture_repo/}"; write_hex "$run_root/untracked" 554e545241434b4544; pre="$(artifact untracked-partial 554e54)"; cand="$(artifact untracked-candidate 4e4557)"; invoke R36-P2 REJECTED_NO_MUTATION replace "$run_relative/untracked" - "$cand" 554e545241434b4544 --preimage "$pre" --candidate "$cand"
  setup; printf 'diagnostic: truncated unrelated output\n' > "$fixture_repo/unrelated.log"; pre="$(artifact unrelated-pre 4142434445)"; cand="$(artifact unrelated-same 4142434445)"; invoke R36-P3 NO_CHANGE replace target - "$cand" 4142434445 --preimage "$pre" --candidate "$cand"
  concurrent_destination
  opposing_moves
  canonical_observation_races
  external_drift_and_recovery
  true_kill_requires_manual_custody
  interrupted_move_requires_manual_custody
  causal_review_heldouts
  printf 'observation-bound-mutation-integrity: PASS R36 state family\n'
}

case "${1:-}" in
  --post-compaction-marker-deletion-heldout) post_compaction_marker_deletion_heldout; printf 'HOST_NEUTRAL_CONTINUITY_MARKER_DELETION_HELDOUT=PASS\n'; exit 0;;
  --post-compaction-continuity-heldout) post_compaction_continuity_heldout; printf 'HOST_NEUTRAL_CONTINUITY_HELDOUT=PASS\n'; exit 0;;
  --controller-stale-heldout) controller_stale_heldout; printf 'S3E_W02_STALE_CONTROLLER_HELDOUT=PASS\n'; exit 0;;
  --controller-transfer-race-heldout) controller_transfer_race_heldout; printf 'S3E_W02_CONTROLLER_TRANSFER_RACE_HELDOUT=PASS\n'; exit 0;;
  --window-interlock-heldouts) fixture_self_check; window_interlock_heldouts; printf 'R36_WINDOW_INTERLOCK_HELDOUTS=PASS\n'; exit 0;;
  --concurrent-destination-heldout) fixture_self_check; concurrent_destination; printf 'R36_CONCURRENT_DESTINATION_HELDOUT=PASS\n'; exit 0;;
  --external-drift-heldout) fixture_self_check; external_drift_and_recovery; printf 'R36_EXTERNAL_DRIFT_HELDOUT=PASS\n'; exit 0;;
  --true-kill-heldout) fixture_self_check; true_kill_requires_manual_custody; printf 'R36_TRUE_KILL_HELDOUT=PASS\n'; exit 0;;
  --fixture-self-check) fixture_self_check; exit 0;;
  --mutant-self-check) fixture_self_check; mutant_self_check; exit 0;;
  --gate-domain-self-check) fixture_self_check; gate_domain_self_check; exit 0;;
  --review-heldouts) fixture_self_check; unsupported_external_gate_replacement_evidence; bash -n "$canonical_helper"; concurrent_destination; causal_review_heldouts; window_interlock_heldouts; printf 'R36_REVIEW_HELDOUTS=PASS\n'; exit 0;;
esac
fixture_self_check
unsupported_external_gate_replacement_evidence
if [ -n "${R36_HELPER:-}" ] && [ "$R36_HELPER" != "$canonical_helper" ]; then fail "refusing non-canonical helper path: $R36_HELPER"; fi
if [ ! -f "$canonical_helper" ] || [ -L "$canonical_helper" ]; then printf 'observation-bound-mutation-integrity: RED missing authoritative helper: %s\n' "$canonical_helper" >&2; exit 1; fi
bash -n "$canonical_helper" || fail 'canonical helper has invalid Bash syntax'
instrumented_helper >/dev/null || fail 'R36 instrumented-copy derivation failed'
state_family
