#!/usr/bin/env bash
# R36: black-box acceptance family for the observation-bound mutation helper.
#
# The helper is intentionally absent at this RED checkpoint.  --fixture-self-check
# proves the byte/topology fixtures independently; the normal entry point then
# fails specifically on the missing authoritative helper.  Once the helper is
# added, this file remains a real caller of its frozen CLI, not a JSON oracle.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
helper="$repo_root/skills/implementaudit/scripts/apply-observed-mutation.sh"
if [ -n "${R36_HELPER:-}" ] && [ "$R36_HELPER" != "$helper" ]; then
  printf 'observation-bound-mutation-integrity: refusing non-canonical helper path: %s\n' "$R36_HELPER" >&2
  exit 1
fi
if [ -n "${PYTHON:-}" ]; then
  python_bin="$PYTHON"
elif command -v python >/dev/null 2>&1; then
  python_bin="python"
elif command -v python3 >/dev/null 2>&1; then
  # Git Bash on Windows commonly exposes its configured Python as python3.
  python_bin="python3"
else
  printf 'observation-bound-mutation-integrity: missing Python interpreter (tried PYTHON, python, python3)\n' >&2
  exit 1
fi

tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT
fixture_repo="$tmp/repository"
run_root="$fixture_repo/.IMPLEMENTAUDIT/r36-test-run"

fail() { printf 'observation-bound-mutation-integrity: %s\n' "$*" >&2; exit 1; }

# The first implementation must preserve this externally observable map.  The
# numbers are deliberately defined here, before production code exists.
exit_for_status() {
  case "$1" in
    COMMITTED|NO_CHANGE) printf '0' ;;
    REJECTED_NO_MUTATION) printf '64' ;;
    CONFLICT_REBASE) printf '65' ;;
    MUTATION_FAILED_NO_STATE_CHANGE) printf '70' ;;
    MUTATION_FAILED_ROLLED_BACK) printf '71' ;;
    POST_STATE_MISMATCH_ROLLED_BACK) printf '72' ;;
    RECOVERY_REQUIRED) printf '73' ;;
    ROLLBACK_CONFLICT) printf '74' ;;
    ROLLBACK_FAILED_WITH_RESIDUE) printf '75' ;;
    POST_COMMIT_DRIFT) printf '76' ;;
    UNSUPPORTED_OWNER_DECISION) printf '77' ;;
    *) fail "no exit mapping for status $1" ;;
  esac
}

write_b64() {
  local path="$1" encoded="$2"
  "$python_bin" - "$path" "$encoded" <<'PY'
import base64
import sys
from pathlib import Path

path = Path(sys.argv[1])
path.parent.mkdir(parents=True, exist_ok=True)
path.write_bytes(base64.b64decode(sys.argv[2]))
PY
}

assert_b64() {
  local label="$1" path="$2" encoded="$3"
  "$python_bin" - "$label" "$path" "$encoded" <<'PY'
import base64
import sys
from pathlib import Path

label, path, encoded = sys.argv[1:]
actual = Path(path).read_bytes()
expected = base64.b64decode(encoded)
if actual != expected:
    raise SystemExit(f"{label}: bytes differ: got={actual!r} want={expected!r}")
PY
}

setup_fixture_tree() {
  rm -rf -- "$fixture_repo"
  mkdir -p "$fixture_repo" "$run_root" "$fixture_repo/artifacts"
  write_b64 "$fixture_repo/target" 'QUJDREU='
  write_b64 "$fixture_repo/unchanged-sibling" 'U0lCTElORw=='
  write_b64 "$fixture_repo/crlf" 'b25lDQp0d28NCnRocmVlDQo='
  write_b64 "$fixture_repo/unicode" 'cHJlZml4LeKCrC3kuK3mloctc3VmZml4'
  write_b64 "$fixture_repo/binary" 'AAH/f0JJTg0K'
  write_b64 "$fixture_repo/a" 'QQ=='
  write_b64 "$fixture_repo/b" 'Qg=='
  write_b64 "$fixture_repo/equal-one" 'U0FNRQ=='
  write_b64 "$fixture_repo/equal-two" 'U0FNRQ=='
  ln "$fixture_repo/unchanged-sibling" "$fixture_repo/hardlink-target"
  "$python_bin" - "$fixture_repo" <<'PY'
import os
import sys
from pathlib import Path

root = Path(sys.argv[1])
try:
    os.symlink('target', root / 'final-link')
    (root / 'parent-real').mkdir()
    (root / 'parent-real' / 'child').write_bytes(b'child')
    os.symlink('parent-real', root / 'parent-link', target_is_directory=True)
    (root / '.symlink-supported').write_text('yes\n', encoding='ascii')
except (NotImplementedError, OSError):
    (root / '.symlink-supported').write_text('no\n', encoding='ascii')
PY
}

fixture_self_check() {
  setup_fixture_tree
  "$python_bin" - "$fixture_repo" <<'PY'
import os
import sys
from pathlib import Path

root = Path(sys.argv[1])
assert (root / 'target').read_bytes() == b'ABCDE'
assert (root / 'crlf').read_bytes() == b'one\r\ntwo\r\nthree\r\n'
assert (root / 'unicode').read_bytes() == 'prefix-€-中文-suffix'.encode('utf-8')
assert (root / 'binary').read_bytes() == b'\x00\x01\xff\x7fBIN\r\n'
assert os.stat(root / 'unchanged-sibling').st_ino == os.stat(root / 'hardlink-target').st_ino
if (root / '.symlink-supported').read_text(encoding='ascii').strip() == 'yes':
    assert (root / 'final-link').is_symlink()
    assert (root / 'parent-link').is_symlink()
print('R36_FIXTURE_SELF_CHECK=PASS bytes=5 topology=hardlink,symlink-or-declared-unsupported')
PY
}

assert_contract_response() {
  local label="$1" expected_status="$2" expected_operation="$3" expected_exit="$4" output="$5"
  "$python_bin" - "$label" "$expected_status" "$expected_operation" "$expected_exit" "$output" <<'PY'
import json
import sys

label, status, operation, exit_code, output = sys.argv[1:]
lines = [line for line in output.splitlines() if line.strip()]
if len(lines) != 1:
    raise SystemExit(f"{label}: expected exactly one JSON output line, got {len(lines)}: {output!r}")
try:
    record = json.loads(lines[0])
except json.JSONDecodeError as exc:
    raise SystemExit(f"{label}: output is not JSON: {exc}")
required = {'schema', 'operation', 'status', 'source_path', 'destination_path', 'targets'}
missing = sorted(required - record.keys())
if missing:
    raise SystemExit(f"{label}: missing contract fields: {missing}")
if record['schema'] != 'implementaudit.observation_bound_mutation.v1':
    raise SystemExit(f"{label}: wrong schema: {record['schema']!r}")
if record['operation'] != operation or record['status'] != status:
    raise SystemExit(f"{label}: got operation/status {record['operation']!r}/{record['status']!r}")
if int(exit_code) == 0 and status not in {'COMMITTED', 'NO_CHANGE'}:
    raise SystemExit(f"{label}: non-success status returned exit zero")
PY
}

invoke_case() {
  local label="$1" expected_status="$2" operation="$3" target="$4"
  shift 4
  local expected_exit output actual_exit
  expected_exit="$(exit_for_status "$expected_status")"
  set +e
  output="$(bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" \
    --operation "$operation" --target "$target" "$@" 2>&1)"
  actual_exit=$?
  set -e
  [ "$actual_exit" -eq "$expected_exit" ] ||
    fail "$label: exit $actual_exit, expected $expected_exit; output: $output"
  assert_contract_response "$label" "$expected_status" "$operation" "$expected_exit" "$output"
  last_output="$output"
}

# A test-only environmental fault selector is a black-box outcome seam: the
# names are plan-level transaction outcomes, never lock-file or helper-internal
# details.  It is needed to reach crash boundaries deterministically without
# racing the filesystem scheduler.
invoke_fault_case() {
  local label="$1" fault="$2" expected_status="$3" operation="$4" target="$5"
  shift 5
  local expected_exit output actual_exit
  expected_exit="$(exit_for_status "$expected_status")"
  set +e
  output="$(IMPLEMENTAUDIT_R36_TEST_FAULT="$fault" bash "$helper" \
    --repo-root "$fixture_repo" --run-root "$run_root" --operation "$operation" \
    --target "$target" "$@" 2>&1)"
  actual_exit=$?
  set -e
  [ "$actual_exit" -eq "$expected_exit" ] ||
    fail "$label: exit $actual_exit, expected $expected_exit; output: $output"
  assert_contract_response "$label" "$expected_status" "$operation" "$expected_exit" "$output"
  last_output="$output"
}

response_field() {
  local field="$1"
  "$python_bin" - "$field" "$last_output" <<'PY'
import json
import sys

field, output = sys.argv[1:]
record = json.loads(output)
value = record.get(field)
if not isinstance(value, str) or not value:
    raise SystemExit(f"missing non-empty {field} in terminal response")
print(value)
PY
}

make_artifact() {
  local name="$1" encoded="$2"
  local path="$fixture_repo/artifacts/$name"
  write_b64 "$path" "$encoded"
  printf '%s\n' "$path"
}

run_concurrent_moves() {
  local barrier="$tmp/concurrency-barrier"
  rm -rf -- "$barrier"
  mkdir -p "$barrier"
  local pre_a pre_b
  pre_a="$(make_artifact concurrent-a-preimage 'QQ==')"
  pre_b="$(make_artifact concurrent-b-preimage 'Qg==')"
  (
    : > "$barrier/a-ready"
    while [ ! -f "$barrier/release" ]; do sleep 0.02; done
    set +e
    bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --operation move \
      --target a --preimage "$pre_a" --destination destination >"$barrier/a.out" 2>&1
    printf '%s\n' "$?" > "$barrier/a.exit"
  ) &
  local pid_a=$!
  (
    : > "$barrier/b-ready"
    while [ ! -f "$barrier/release" ]; do sleep 0.02; done
    set +e
    bash "$helper" --repo-root "$fixture_repo" --run-root "$run_root" --operation move \
      --target b --preimage "$pre_b" --destination destination >"$barrier/b.out" 2>&1
    printf '%s\n' "$?" > "$barrier/b.exit"
  ) &
  local pid_b=$!
  local ticks=0
  while { [ ! -f "$barrier/a-ready" ] || [ ! -f "$barrier/b-ready" ]; } && [ "$ticks" -lt 250 ]; do
    sleep 0.02
    ticks=$((ticks + 1))
  done
  [ -f "$barrier/a-ready" ] && [ -f "$barrier/b-ready" ] || fail 'R36-CONCURRENCY: start barrier timed out'
  : > "$barrier/release"
  wait "$pid_a" || true
  wait "$pid_b" || true
  "$python_bin" - "$barrier" <<'PY'
import json
import sys
from pathlib import Path

barrier = Path(sys.argv[1])
records = []
for name in ('a', 'b'):
    code = int((barrier / f'{name}.exit').read_text(encoding='ascii').strip())
    lines = [line for line in (barrier / f'{name}.out').read_text(encoding='utf-8').splitlines() if line.strip()]
    if len(lines) != 1:
        raise SystemExit(f'R36-CONCURRENCY: {name} emitted {len(lines)} lines')
    record = json.loads(lines[0])
    records.append((code, record['status']))
if sorted(records) != [(0, 'COMMITTED'), (65, 'CONFLICT_REBASE')]:
    raise SystemExit(f'R36-CONCURRENCY: expected one commit and one rebase conflict, got {records!r}')
PY
}

run_state_family() {
  local preimage candidate region replacement

  # C1/C2/C3: observation completeness, currentness, and representation.
  setup_fixture_tree
  preimage="$(make_artifact partial-preimage 'QUJD')"
  candidate="$(make_artifact replacement 'Wg==')"
  invoke_case R36-C1 REJECTED_NO_MUTATION replace target --preimage "$preimage" --candidate "$candidate"
  assert_b64 R36-C1-target-preserved "$fixture_repo/target" 'QUJDREU='

  setup_fixture_tree
  preimage="$(make_artifact stale-preimage 'QUJDREU=')"
  write_b64 "$fixture_repo/target" 'SU5URVJWRU5JTkctV1JJVEU='
  invoke_case R36-C2 CONFLICT_REBASE replace target --preimage "$preimage" --candidate "$candidate"
  assert_b64 R36-C2-intervening-bytes-preserved "$fixture_repo/target" 'SU5URVJWRU5JTkctV1JJVEU='

  setup_fixture_tree
  for kind in transformed defaulted reference-only; do
    preimage="$(make_artifact "$kind-preimage" 'QUJD')"
    invoke_case "R36-C3-$kind" REJECTED_NO_MUTATION replace target --preimage "$preimage" --candidate "$candidate"
    assert_b64 "R36-C3-$kind-target-preserved" "$fixture_repo/target" 'QUJDREU='
  done

  # C4: an executable argument is not part of the helper contract and must not run.
  setup_fixture_tree
  write_b64 "$fixture_repo/sentinel" 'U0VOVElORUw='
  preimage="$(make_artifact arbitrary-command-preimage 'QUJDREU=')"
  invoke_case R36-C4 REJECTED_NO_MUTATION replace target --preimage "$preimage" --candidate "$candidate" \
    --arbitrary-mutator "sh -c 'printf compromised > sentinel'"
  assert_b64 R36-C4-sentinel-preserved "$fixture_repo/sentinel" 'U0VOVElORUw='

  # Raw-byte fidelity: CRLF, multibyte UTF-8 and non-text bytes.
  setup_fixture_tree
  region="$(make_artifact crlf-region 'dHdvDQo=')"
  replacement="$(make_artifact crlf-replacement 'VFdPDQo=')"
  invoke_case R36-B1 COMMITTED patch crlf --offset 5 --region "$region" --replacement "$replacement"
  assert_b64 R36-B1-crlf "$fixture_repo/crlf" 'b25lDQpUV08NCnRocmVlDQo='

  setup_fixture_tree
  region="$(make_artifact unicode-region '4oKsLeS4reaWhw==')"
  replacement="$(make_artifact unicode-replacement '8J+YgA==')"
  invoke_case R36-B2 COMMITTED patch unicode --offset 7 --region "$region" --replacement "$replacement"
  assert_b64 R36-B2-unicode-complement "$fixture_repo/unicode" 'cHJlZml4LfCfmIBzdWZmaXg='

  setup_fixture_tree
  preimage="$(make_artifact binary-preimage 'AAH/f0JJTg0K')"
  candidate="$(make_artifact binary-candidate '/wAAQklOLQ==')"
  invoke_case R36-B3 COMMITTED replace binary --preimage "$preimage" --candidate "$candidate"
  assert_b64 R36-B3-binary-replace "$fixture_repo/binary" '/wAAQklOLQ=='
  preimage="$(make_artifact binary-delete-preimage '/wAAQklOLQ==')"
  invoke_case R36-B4 COMMITTED delete binary --preimage "$preimage"
  [ ! -e "$fixture_repo/binary" ] || fail 'R36-B4: binary delete retained target'

  setup_fixture_tree
  preimage="$(make_artifact binary-move-preimage 'AAH/f0JJTg0K')"
  invoke_case R36-B5 COMMITTED move binary --preimage "$preimage" --destination binary-destination
  [ ! -e "$fixture_repo/binary" ] || fail 'R36-B5: binary move retained source'
  assert_b64 R36-B5-binary-move "$fixture_repo/binary-destination" 'AAH/f0JJTg0K'

  # Alias and lexical scope controls: no sibling, hardlink, symlink or outside widening.
  setup_fixture_tree
  preimage="$(make_artifact hardlink-preimage 'U0lCTElORw==')"
  candidate="$(make_artifact hardlink-candidate 'TkVX')"
  invoke_case R36-T1 COMMITTED replace hardlink-target --preimage "$preimage" --candidate "$candidate"
  assert_b64 R36-T1-target "$fixture_repo/hardlink-target" 'TkVX'
  assert_b64 R36-T1-sibling-byte-preserved "$fixture_repo/unchanged-sibling" 'U0lCTElORw=='

  setup_fixture_tree
  preimage="$(make_artifact equal-preimage 'U0FNRQ==')"
  invoke_case R36-T2 COMMITTED replace equal-one --preimage "$preimage" --candidate "$candidate"
  assert_b64 R36-T2-distinct-equal-path-preserved "$fixture_repo/equal-two" 'U0FNRQ=='
  if [ "$(cat "$fixture_repo/.symlink-supported")" = yes ]; then
    invoke_case R36-T3 REJECTED_NO_MUTATION replace final-link --preimage "$preimage" --candidate "$candidate"
    invoke_case R36-T4 REJECTED_NO_MUTATION replace parent-link/child --preimage "$preimage" --candidate "$candidate"
  fi
  invoke_case R36-T5 REJECTED_NO_MUTATION replace ../outside --preimage "$preimage" --candidate "$candidate"

  # Cheap and false-positive controls.
  setup_fixture_tree
  assert_b64 R36-P1-read-only "$fixture_repo/target" 'QUJDREU='
  : > "$fixture_repo/disposable-created-outside-helper"
  [ -f "$fixture_repo/disposable-created-outside-helper" ] || fail 'R36-P2: ordinary disposable creation failed'
  preimage="$(make_artifact no-change-preimage 'QUJDREU=')"
  candidate="$(make_artifact no-change-candidate 'QUJDREU=')"
  invoke_case R36-P3 NO_CHANGE replace target --preimage "$preimage" --candidate "$candidate"
  printf 'diagnostic: truncated unrelated log\n' > "$fixture_repo/diagnostic.log"
  invoke_case R36-P4 NO_CHANGE replace target --preimage "$preimage" --candidate "$candidate"
  candidate="$(make_artifact transformed-candidate 'TkVX')"
  invoke_case R36-P5 COMMITTED replace target --preimage "$preimage" --candidate "$candidate"
  assert_b64 R36-P5-authoritative-preimage "$fixture_repo/target" 'TkVX'

  # Deterministic simultaneous start; expected result does not depend on winner identity.
  setup_fixture_tree
  run_concurrent_moves
  [ -f "$fixture_repo/destination" ] || fail 'R36-CONCURRENCY: destination was not created'
  [ ! -e "$fixture_repo/a" ] || [ ! -e "$fixture_repo/b" ] || fail 'R36-CONCURRENCY: both sources remained'

  # A recovery record is public terminal evidence.  A forged owner token must
  # not delete it, unlock it, or alter the target set.
  setup_fixture_tree
  preimage="$(make_artifact lock-owner-preimage 'QUJDREU=')"
  candidate="$(make_artifact lock-owner-candidate 'TkVX')"
  invoke_fault_case R36-L1-owner-record recovery-required RECOVERY_REQUIRED replace target \
    --preimage "$preimage" --candidate "$candidate"
  journal="$(response_field journal_path)"
  owner_token="$(response_field token)"
  case "$journal" in "$fixture_repo"/*) ;; *) fail "R36-L1: journal escapes fixture repository: $journal" ;; esac
  [ -e "$journal" ] || fail 'R36-L1: recovery record was not retained'
  invoke_case R36-L1-forged-owner REJECTED_NO_MUTATION recover target \
    --journal "$journal" --token "forged-$owner_token"
  [ -e "$journal" ] || fail 'R36-L1: forged owner removed recovery record'

  # Outcome-level crash/rollback family.  The test does not inspect journals,
  # locks or staging names; it asserts only terminal status and visible bytes.
  for spec in \
    'pre-displacement:MUTATION_FAILED_NO_STATE_CHANGE:QUJDREU=' \
    'after-displacement:MUTATION_FAILED_ROLLED_BACK:QUJDREU=' \
    'after-publication:MUTATION_FAILED_ROLLED_BACK:QUJDREU=' \
    'post-state-mismatch:POST_STATE_MISMATCH_ROLLED_BACK:QUJDREU=' \
    'rollback-conflict:ROLLBACK_CONFLICT:SU5URVJWRU5JTkctV0JJTk5FUg==' \
    'rollback-residue:ROLLBACK_FAILED_WITH_RESIDUE:SU5URVJWRU5JTkctV0JJTk5FUg==' \
    'post-commit-drift:POST_COMMIT_DRIFT:SU5URVJWRU5JTkctV0JJTk5FUg==' \
    'unsupported-external-writer:UNSUPPORTED_OWNER_DECISION:QUJDREU='; do
    IFS=: read -r fault status expected <<<"$spec"
    setup_fixture_tree
    preimage="$(make_artifact rollback-preimage 'QUJDREU=')"
    candidate="$(make_artifact rollback-candidate 'TkVX')"
    invoke_fault_case "R36-R-$fault" "$fault" "$status" replace target --preimage "$preimage" --candidate "$candidate"
    assert_b64 "R36-R-$fault-visible-state" "$fixture_repo/target" "$expected"
  done

  printf 'observation-bound-mutation-integrity: PASS state-family=R36-C1..C4,bytes,topology,concurrency,rollback,cheap-controls\n'
}

if [ "${1:-}" = '--fixture-self-check' ]; then
  fixture_self_check
  exit 0
fi

fixture_self_check
if [ ! -f "$helper" ] || [ -L "$helper" ]; then
  printf 'observation-bound-mutation-integrity: RED missing authoritative helper: %s\n' "$helper" >&2
  exit 1
fi
bash -n "$helper" || fail "helper Bash syntax is invalid: $helper"
run_state_family
