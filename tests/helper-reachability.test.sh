#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
checker="$repo_root/scripts/check-helper-reachability.sh"

if [ ! -f "$checker" ]; then
  printf 'helper-reachability.test: missing checker: %s\n' "$checker" >&2
  exit 1
fi

tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT

make_candidate() {
  local name="$1"
  local candidate="$tmp/$name"
  mkdir -p "$candidate/scripts" "$candidate/package" "$candidate/tests" \
    "$candidate/fixtures/scarce-resource-rehearsal" \
    "$candidate/fixtures/run-root-example/phases"
  cp -R "$repo_root/skills" "$candidate/skills"
  cp "$repo_root/scripts/package-contract.py" "$candidate/scripts/package-contract.py"
  cp "$repo_root/package/implementaudit-package.json" "$candidate/package/implementaudit-package.json"
  cp "$repo_root/tests/scarce-resource-rehearsal-contract.test.sh" "$candidate/tests/"
  cp "$repo_root/fixtures/scarce-resource-rehearsal/cases.json" \
    "$candidate/fixtures/scarce-resource-rehearsal/"
  cp "$repo_root/fixtures/run-root-example/phases/phase-1.md" \
    "$candidate/fixtures/run-root-example/phases/"
  cp -R "$repo_root/.codex-plugin" "$repo_root/.claude-plugin" "$candidate/"
  git -C "$candidate" init --quiet
  git -C "$candidate" add .
  printf '%s\n' "$candidate"
}

expect_fail() {
  local label="$1" pattern="$2" candidate="$3" output
  git -C "$candidate" add -A
  if output="$(bash "$checker" --census-only --repo-root "$candidate" 2>&1)"; then
    printf 'helper-reachability.test: %s unexpectedly passed\n' "$label" >&2
    exit 1
  fi
  if ! grep -Fq -- "$pattern" <<<"$output"; then
    printf 'helper-reachability.test: %s failed for the wrong reason\n%s\n' "$label" "$output" >&2
    exit 1
  fi
}

mutate_route() {
  local candidate="$1" helper="$2" column="$3" value="$4"
  python - \
    "$candidate/skills/implementaudit/references/repo-state-comparison.md" \
    "$helper" "$column" "$value" <<'PY'
import sys
from pathlib import Path

path, helper, column_text, value = sys.argv[1:]
column = int(column_text)
lines = Path(path).read_text(encoding="utf-8").splitlines()
prefix = f"helper-route: scripts/{helper}|"
matches = [index for index, line in enumerate(lines) if line.startswith(prefix)]
if len(matches) != 1:
    raise SystemExit(f"expected one route row for {helper}, got {len(matches)}")
parts = lines[matches[0]].split("|")
parts[column] = value
lines[matches[0]] = "|".join(parts)
Path(path).write_text("\n".join(lines) + "\n", encoding="utf-8")
PY
}

delete_route() {
  local candidate="$1" helper="$2"
  python - \
    "$candidate/skills/implementaudit/references/repo-state-comparison.md" \
    "$helper" <<'PY'
import sys
from pathlib import Path

path, helper = sys.argv[1:]
lines = Path(path).read_text(encoding="utf-8").splitlines()
prefix = f"helper-route: scripts/{helper}|"
kept = [line for line in lines if not line.startswith(prefix)]
if len(kept) != len(lines) - 1:
    raise SystemExit(f"expected one route row for {helper}")
Path(path).write_text("\n".join(kept) + "\n", encoding="utf-8")
PY
}

ordered_replacement_modes() {
  local evidence="${1:-$tmp/ordered-modes}" saved_tmp="$tmp"
  mkdir -p "$evidence"
  tmp="$evidence/fixtures"
  mkdir -p "$tmp"
  local name candidate
  for name in current missing-route missing-parser missing-dispatch; do
    candidate="$(make_candidate "ordered-$name")"
    python - "$candidate" "$name" <<'PY_ORDERED_MODE_EDIT'
import sys
from pathlib import Path
root, name = Path(sys.argv[1]), sys.argv[2]
path = root / 'skills/implementaudit/references/repo-state-comparison.md'
if name == 'missing-route':
    text = path.read_text()
    prefix = 'helper-mode: apply-observed-mutation.sh|--batch-apply|'
    kept = [line for line in text.splitlines(True) if not line.startswith(prefix)]
    assert len(kept) == len(text.splitlines(True)) - 1
    path.write_text(''.join(kept))
elif name in ('missing-parser', 'missing-dispatch'):
    path = root / 'skills/implementaudit/scripts/apply-observed-mutation.sh'
    text = path.read_text()
    anchor = ('parser.add_argument("--batch-apply", dest="apply_replacements")\n' if name == 'missing-parser'
              else 'if args.apply_replacements is not None:\n    replacement_batch_apply()\n')
    assert text.count(anchor) == 1
    path.write_text(text.replace(anchor, ''))
PY_ORDERED_MODE_EDIT
    git -C "$candidate" add -A
    python - "$checker" "$candidate" "$evidence" "$name" <<'PY_ORDERED_MODE_CHECK'
import hashlib, json, subprocess, sys
from pathlib import Path
checker, candidate, directory, name = sys.argv[1:]
out = Path(directory)
argv = ['bash', checker, '--census-only', '--repo-root', candidate]
result = subprocess.run(argv, capture_output=True)
(out / (name + '.stdout.bin')).write_bytes(result.stdout)
(out / (name + '.stderr.bin')).write_bytes(result.stderr)
record = {'argv': argv, 'returncode': result.returncode,
          'stdout_sha256': hashlib.sha256(result.stdout).hexdigest(), 'stderr_sha256': hashlib.sha256(result.stderr).hexdigest()}
(out / (name + '.json')).write_text(json.dumps(record, indent=2) + '\n')
if name == 'current':
    assert result.returncode == 0 and b'HELPER_REACHABILITY_CENSUS=PASS' in result.stdout and b'modes=25/25' in result.stdout, record
else:
    pattern = ('missing mode applicability rows: apply-observed-mutation.sh --batch-apply' if name == 'missing-route'
               else 'mode applicability not implemented: apply-observed-mutation.sh --batch-apply')
    assert result.returncode != 0 and pattern.encode() in result.stdout + result.stderr, record
PY_ORDERED_MODE_CHECK
  done
  tmp="$saved_tmp"
  printf 'R30_ORDERED_REPLACEMENT_MODES=PASS current/route/parser/dispatch (census-only)\n'
}

if [ "${1:-}" = --ordered-replacement-modes ]; then
  ordered_replacement_modes "${2:-}"
  exit 0
fi

positive_output="$(bash "$checker" --repo-root "$repo_root")"
grep -Eq 'HELPER_REACHABILITY=PASS population=([0-9]+) examined=\1 modes=25/25 enumeration=package-contract.artifact_payload_entries full_path_sets=equal projections=2' \
  <<<"$positive_output" || {
    printf 'helper-reachability.test: live positive census did not prove complete full-path equality\n%s\n' "$positive_output" >&2
    exit 1
}

census_output="$(bash "$checker" --census-only --repo-root "$repo_root")"
grep -Eq 'HELPER_REACHABILITY_CENSUS=PASS population=([0-9]+) examined=\1 modes=25/25 enumeration=package-contract.artifact_payload_entries full_path_sets=equal projections=2' \
  <<<"$census_output" || {
    printf 'helper-reachability.test: census-only result was not distinctly nonterminal\n%s\n' "$census_output" >&2
    exit 1
  }

for mutation in wrong-buffer missing-digest wrong-owner broken-statement; do
  shell_capture="$(make_candidate "shell-capture-$mutation")"
  python - "$shell_capture/skills/implementaudit/scripts/claim-run.sh" "$mutation" <<'PYSHELL'
from pathlib import Path
import sys
path, mutation = Path(sys.argv[1]), sys.argv[2]
text = path.read_text()
old, new = {
    "wrong-buffer": ('exec(compile(raw, str(path), "exec",', 'exec(compile(b"", str(path), "exec",'),
    "missing-digest": ('hashlib.sha256(raw).hexdigest() != expected_sha256', 'False'),
    "wrong-owner": (
        'expected_bytes = ' + str(len(path.with_name('claim-run-rotation.py').read_bytes())),
        'expected_bytes = ' + str(len(path.with_name('claim-run-rotation.py').read_bytes()) + 1)),
    "broken-statement": ('exec(compile(raw, str(path), "exec",', 'exec\n(compile(raw, str(path), "exec",'),
}[mutation]
assert text.count(old) == 1
path.write_text(text.replace(old, new))
PYSHELL
  expect_fail "shell-capture-$mutation" 'caller does not invoke claim-run-rotation.py: scripts/claim-run.sh' "$shell_capture"
done

ordered_replacement_modes

# A progressive stage owner does not replace the declared governor helper edge.
missing_run_root_edge="$(make_candidate missing-run-root-governor-edge)"
python - "$missing_run_root_edge" <<'PY'
from pathlib import Path
import sys

candidate = Path(sys.argv[1])
governor = candidate / "skills/implementaudit/SKILL.md"
owner = candidate / "skills/implementaudit/references/plan-lifecycle.md"
assert "### Stage 5 - Write" in owner.read_text(encoding="utf-8")
text = governor.read_text(encoding="utf-8")
start = text.index("When a run root is needed, claim it with")
ending = "not dispatchable.\n"
end = text.index(ending, start) + len(ending)
governor.write_text(text[:start] + text[end:], encoding="utf-8")
PY
expect_fail "missing governor run-root edge with reference retained" \
  "unanchored trigger: claim-run.sh: run-root" "$missing_run_root_edge"

# R001E must count the scarce-resource rehearsal as a distinct governed mode,
# rather than treating the authorization-record mode as its proxy.
grep -Fqx \
  'helper-mode: check-authorization-binding.sh|--phase --rehearsal --launch|<phase> <receipt> <launch>|failed-rehearsal-blocks-launch|scripts/validate-phase.sh' \
  "$repo_root/skills/implementaudit/references/repo-state-comparison.md" || {
    printf 'helper-reachability.test: R001E rehearsal mode is missing from the route population\n' >&2
    exit 1
  }
grep -Fq 'native audit object opens a scarce-resource phase' \
  "$repo_root/skills/implementaudit/references/repo-state-comparison.md" || {
    printf 'helper-reachability.test: R001E rehearsal caller/trigger is missing\n' >&2
    exit 1
  }

missing_mode="$(make_candidate missing-mode)"
sed -i '/^helper-mode: validate-run-root.sh|--graph-parent|/d' \
  "$missing_mode/skills/implementaudit/references/repo-state-comparison.md"
expect_fail R30-M1 \
  'missing mode applicability rows: validate-run-root.sh --graph-parent' \
  "$missing_mode"

unimplemented_mode="$(make_candidate unimplemented-mode)"
printf '%s\n' \
  'helper-mode: validate-run-root.sh|--graph-invented|<catalog>|invented' \
  >>"$unimplemented_mode/skills/implementaudit/references/repo-state-comparison.md"
expect_fail R30-M2 \
  'mode applicability not implemented: validate-run-root.sh --graph-invented' \
  "$unimplemented_mode"

missing_mode_dispatch="$(make_candidate missing-mode-dispatch)"
sed -i 's/--graph-scope <catalog> <repo> <path> \[path\.\.\.\]/--graph-scope is available/' \
  "$missing_mode_dispatch/skills/implementaudit/references/repo-state-comparison.md"
expect_fail R30-M3 \
  'mode arguments absent: validate-run-root.sh --graph-scope' \
  "$missing_mode_dispatch"

missing_rehearsal_mode="$(make_candidate missing-rehearsal-mode)"
sed -i '/^helper-mode: check-authorization-binding.sh|--phase --rehearsal --launch|/d' \
  "$missing_rehearsal_mode/skills/implementaudit/references/repo-state-comparison.md"
expect_fail R30-M4 \
  'missing mode applicability rows: check-authorization-binding.sh --phase --rehearsal --launch' \
  "$missing_rehearsal_mode"
grep -Fq 'One audit object; no event, no sweep.' \
  "$repo_root/skills/implementaudit/references/repo-state-comparison.md" || {
    printf 'helper-reachability.test: same-object/no-event contract is missing\n' >&2
    exit 1
  }

missing_row="$(make_candidate missing-row)"
delete_route "$missing_row" check-authorization-binding.sh
expect_fail R30-F1 'missing applicability rows: check-authorization-binding.sh' "$missing_row"

self_reference="$(make_candidate self-reference)"
mutate_route "$self_reference" check-authorization-binding.sh 3 scripts/check-authorization-binding.sh
expect_fail R30-F2 'dispatch owner cannot be the helper itself: check-authorization-binding.sh' "$self_reference"

missing_dispatch="$(make_candidate missing-dispatch)"
mutate_route "$missing_dispatch" check-authorization-binding.sh 3 references/goal-format.md
expect_fail R30-F5 'dispatch owner does not name helper check-authorization-binding.sh' "$missing_dispatch"

presence_only="$(make_candidate presence-only)"
printf '\ncheck-authorization-binding.sh exists in the package and has direct tests.\n' \
  >>"$presence_only/skills/implementaudit/references/goal-format.md"
mutate_route "$presence_only" check-authorization-binding.sh 3 references/goal-format.md
expect_fail R30-F3/F4 \
  'procedural route absent: check-authorization-binding.sh' \
  "$presence_only"

bogus_trigger="$(make_candidate bogus-trigger)"
mutate_route "$bogus_trigger" check-authorization-binding.sh 2 none
expect_fail R30-F5 \
  'unanchored trigger: check-authorization-binding.sh: none' \
  "$bogus_trigger"

decoy_trigger="$(make_candidate decoy-trigger)"
mutate_route "$decoy_trigger" check-authorization-binding.sh 2 final
expect_fail R30-F5 \
  'unanchored trigger: check-authorization-binding.sh: final' \
  "$decoy_trigger"

bogus_arguments="$(make_candidate bogus-arguments)"
mutate_route "$bogus_arguments" check-authorization-binding.sh 5 bogus-arguments
expect_fail R30-F5 \
  'unanchored arguments: check-authorization-binding.sh: bogus-arguments' \
  "$bogus_arguments"

decoy_arguments="$(make_candidate decoy-arguments)"
mutate_route "$decoy_arguments" check-authorization-binding.sh 5 'state invocation authorization'
expect_fail R30-F5 \
  'unanchored arguments: check-authorization-binding.sh: state invocation authorization' \
  "$decoy_arguments"

swapped_arguments="$(make_candidate swapped-arguments)"
mutate_route "$swapped_arguments" check-authorization-binding.sh 5 \
  '--auth <state> --invocation <auth> --state <invocation>'
expect_fail R30-F5 \
  'unanchored arguments: check-authorization-binding.sh: --auth <state> --invocation <auth> --state <invocation>' \
  "$swapped_arguments"

omitted_flag="$(make_candidate omitted-flag)"
mutate_route "$omitted_flag" check-authorization-binding.sh 5 \
  '--auth <a> <i> --state <s>'
expect_fail R30-F5 \
  'unanchored arguments: check-authorization-binding.sh: --auth <a> <i> --state <s>' \
  "$omitted_flag"

truncated_arguments="$(make_candidate truncated-arguments)"
mutate_route "$truncated_arguments" check-authorization-binding.sh 5 '--auth <a>'
expect_fail R30-F5 \
  'unanchored arguments: check-authorization-binding.sh: --auth <a>' \
  "$truncated_arguments"

argument_self_anchor="$(make_candidate argument-self-anchor)"
mutate_route "$argument_self_anchor" check-authorization-binding.sh 5 \
  '<check-authorization-binding>'
expect_fail R30-F5 \
  'unanchored arguments: check-authorization-binding.sh: <check-authorization-binding>' \
  "$argument_self_anchor"

bogus_boundary="$(make_candidate bogus-boundary)"
mutate_route "$bogus_boundary" check-authorization-binding.sh 6 none
expect_fail R30-F5 \
  'unanchored boundary: check-authorization-binding.sh: none' \
  "$bogus_boundary"

decoy_boundary="$(make_candidate decoy-boundary)"
mutate_route "$decoy_boundary" check-authorization-binding.sh 6 final
expect_fail R30-F5 \
  'unanchored boundary: check-authorization-binding.sh: final' \
  "$decoy_boundary"

bad_class="$(make_candidate bad-class)"
mutate_route "$bad_class" check-authorization-binding.sh 1 U
expect_fail R30-F1 'invalid applicability class U for check-authorization-binding.sh' "$bad_class"

missing_caller="$(make_candidate missing-caller)"
mutate_route "$missing_caller" check-respec-impact-set.sh 4 scripts/missing-caller.sh
expect_fail R30-F11 'unshipped caller: check-respec-impact-set.sh: scripts/missing-caller.sh' "$missing_caller"

repo_only_caller="$(make_candidate repo-only-caller)"
mutate_route "$repo_only_caller" check-respec-impact-set.sh 4 ../../tests/helper-reachability.test.sh
expect_fail R30-F11 \
  'invalid caller: check-respec-impact-set.sh: ../../tests/helper-reachability.test.sh' \
  "$repo_only_caller"

mention_only_caller="$(make_candidate mention-only-caller)"
mutate_route "$mention_only_caller" check-respec-impact-set.sh 4 R
expect_fail R30-F11 \
  'caller is not a shipped script: check-respec-impact-set.sh: references/repo-state-comparison.md' \
  "$mention_only_caller"

mention_only_script="$(make_candidate mention-only-script)"
printf '\n# bash scripts/check-respec-impact-set.sh\ntrue # bash scripts/check-respec-impact-set.sh\n' \
  >>"$mention_only_script/skills/implementaudit/scripts/detect-env.sh"
mutate_route "$mention_only_script" check-respec-impact-set.sh 4 scripts/detect-env.sh
expect_fail R30-F11 \
  'caller does not invoke check-respec-impact-set.sh: scripts/detect-env.sh' \
  "$mention_only_script"

echo_only_script="$(make_candidate echo-only-script)"
printf '\necho bash scripts/check-respec-impact-set.sh\n' \
  >>"$echo_only_script/skills/implementaudit/scripts/detect-env.sh"
mutate_route "$echo_only_script" check-respec-impact-set.sh 4 scripts/detect-env.sh
expect_fail R30-F11 \
  'caller does not invoke check-respec-impact-set.sh: scripts/detect-env.sh' \
  "$echo_only_script"

printf_only_script="$(make_candidate printf-only-script)"
printf "\nprintf '%%s\\n' 'bash scripts/check-respec-impact-set.sh'\n" \
  >>"$printf_only_script/skills/implementaudit/scripts/detect-env.sh"
mutate_route "$printf_only_script" check-respec-impact-set.sh 4 scripts/detect-env.sh
expect_fail R30-F11 \
  'caller does not invoke check-respec-impact-set.sh: scripts/detect-env.sh' \
  "$printf_only_script"

bash_parse_only="$(make_candidate bash-parse-only)"
printf '\nbash -n scripts/check-respec-impact-set.sh\n' \
  >>"$bash_parse_only/skills/implementaudit/scripts/detect-env.sh"
mutate_route "$bash_parse_only" check-respec-impact-set.sh 4 scripts/detect-env.sh
expect_fail R30-F11 \
  'caller does not invoke check-respec-impact-set.sh: scripts/detect-env.sh' \
  "$bash_parse_only"

exec_echo_only="$(make_candidate exec-echo-only)"
printf '\nexec echo scripts/check-respec-impact-set.sh\n' \
  >>"$exec_echo_only/skills/implementaudit/scripts/detect-env.sh"
mutate_route "$exec_echo_only" check-respec-impact-set.sh 4 scripts/detect-env.sh
expect_fail R30-F11 \
  'caller does not invoke check-respec-impact-set.sh: scripts/detect-env.sh' \
  "$exec_echo_only"

bash_command_echo="$(make_candidate bash-command-echo)"
printf "\nbash -c 'echo scripts/check-respec-impact-set.sh'\n" \
  >>"$bash_command_echo/skills/implementaudit/scripts/detect-env.sh"
mutate_route "$bash_command_echo" check-respec-impact-set.sh 4 scripts/detect-env.sh
expect_fail R30-F11 \
  'caller does not invoke check-respec-impact-set.sh: scripts/detect-env.sh' \
  "$bash_command_echo"

prefix_collision="$(make_candidate prefix-collision)"
printf '\nbash scripts/not-check-respec-impact-set.sh\n' \
  >>"$prefix_collision/skills/implementaudit/scripts/detect-env.sh"
mutate_route "$prefix_collision" check-respec-impact-set.sh 4 scripts/detect-env.sh
expect_fail R30-F11 \
  'caller does not invoke check-respec-impact-set.sh: scripts/detect-env.sh' \
  "$prefix_collision"

suffix_collision="$(make_candidate suffix-collision)"
printf '\nbash scripts/check-respec-impact-set.sh-not\n' \
  >>"$suffix_collision/skills/implementaudit/scripts/detect-env.sh"
mutate_route "$suffix_collision" check-respec-impact-set.sh 4 scripts/detect-env.sh
expect_fail R30-F11 \
  'caller does not invoke check-respec-impact-set.sh: scripts/detect-env.sh' \
  "$suffix_collision"

variable_prefix_collision="$(make_candidate variable-prefix-collision)"
printf '\nfake_checker="scripts/not-check-respec-impact-set.sh"\nbash "$fake_checker"\n' \
  >>"$variable_prefix_collision/skills/implementaudit/scripts/detect-env.sh"
mutate_route "$variable_prefix_collision" check-respec-impact-set.sh 4 scripts/detect-env.sh
expect_fail R30-F11 \
  'caller does not invoke check-respec-impact-set.sh: scripts/detect-env.sh' \
  "$variable_prefix_collision"

variable_suffix_collision="$(make_candidate variable-suffix-collision)"
printf '\nfake_checker="scripts/check-respec-impact-set.sh-not"\nbash "$fake_checker"\n' \
  >>"$variable_suffix_collision/skills/implementaudit/scripts/detect-env.sh"
mutate_route "$variable_suffix_collision" check-respec-impact-set.sh 4 scripts/detect-env.sh
expect_fail R30-F11 \
  'caller does not invoke check-respec-impact-set.sh: scripts/detect-env.sh' \
  "$variable_suffix_collision"

mandatory_advisory="$(make_candidate mandatory-advisory)"
mutate_route "$mandatory_advisory" lane-survivor-inventory.sh 6 must-block-closure
expect_fail R30-F8 'advisory/standalone row implies mandatory enforcement: lane-survivor-inventory.sh' "$mandatory_advisory"

owner_overclaim="$(make_candidate owner-overclaim)"
printf '\nlane-survivor-inventory.sh\nmust gate closure.\n' \
  >>"$owner_overclaim/skills/implementaudit/references/child-agents.md"
expect_fail R30-F8 \
  'advisory owner overclaim: lane-survivor-inventory.sh' \
  "$owner_overclaim"

future_helper="$(make_candidate future-helper)"
cp "$future_helper/skills/implementaudit/scripts/detect-stack.sh" \
  "$future_helper/skills/implementaudit/scripts/future-helper.sh"
expect_fail R30-F20 'missing applicability rows: future-helper.sh' "$future_helper"

extra_row="$(make_candidate extra-row)"
printf '%s\n' \
  'helper-route: scripts/ghost-helper.sh|S|owner-diagnosis|R|-|none|never-automatic' \
  >>"$extra_row/skills/implementaudit/references/repo-state-comparison.md"
expect_fail R30-F11 'applicability rows not in package: ghost-helper.sh' "$extra_row"

for mutation in metadata-buffer duplicate-buffer uncaptured-buffer changed-size changed-digest; do
  native_input="$(make_candidate "native-input-$mutation")"
  python - "$native_input/skills/implementaudit/scripts/rotate-canonical-state.py" "$mutation" <<'PY'
from pathlib import Path
import re
import sys

path, mutation = Path(sys.argv[1]), sys.argv[2]
text = path.read_text(encoding="utf-8")
if mutation in {"metadata-buffer", "duplicate-buffer"}:
    before = "    raw, _ = read_regular(path, path.parent, 'native input source', require_owner_write=False)"
    after = before.replace("raw, _", "_, raw" if mutation == "metadata-buffer" else "raw, raw")
elif mutation == "uncaptured-buffer":
    start = text.index("def native_inputs_module_v1():")
    end = text.index("\ndef _native_subject", start)
    before = text[start:end]
    after = before.replace("compile(raw, str(path), 'exec')", "compile(b'', str(path), 'exec')")
else:
    name = "NATIVE_INPUT_MODULE_BYTES" if mutation == "changed-size" else "NATIVE_INPUT_MODULE_SHA256"
    match = re.search(r"(?m)^" + name + r" = .+$", text)
    assert match is not None
    before = match.group()
    after = name + (" = 0" if mutation == "changed-size" else " = '" + "0" * 64 + "'")
assert before != after and text.count(before) == 1
path.write_bytes(text.replace(before, after).encode("utf-8"))
PY
  expect_fail "native-input-$mutation" \
    'caller does not capture/load canonical_rotation_inputs.py: scripts/rotate-canonical-state.py' \
    "$native_input"
done

# The TY mode must have both its actual dispatch and exact applicability row.
missing_yield_mode="$(make_candidate missing-yield-mode)"
python - "$missing_yield_mode" <<'PYMODE'
from pathlib import Path
import sys
p=Path(sys.argv[1])/"skills/implementaudit/references/repo-state-comparison.md"
p.write_text("\n".join(line for line in p.read_text().splitlines()
                        if not line.startswith("helper-mode: validate-run-root.sh|--nonterminal-yield|"))+"\n")
PYMODE
expect_fail R37-YIELD-MISSING 'missing mode applicability rows: validate-run-root.sh --nonterminal-yield' "$missing_yield_mode"

false_yield_mode="$(make_candidate false-yield-mode)"
python - "$false_yield_mode" <<'PYMODE'
from pathlib import Path
import sys
p=Path(sys.argv[1])/"skills/implementaudit/scripts/validate-run-root.sh"
s=p.read_text();needle='elif [ "${1:-}" = "--nonterminal-yield" ]; then'
assert s.count(needle)==1
p.write_text(s.replace(needle,'elif [ "${1:-}" = "--not-yield" ]; then'))
PYMODE
expect_fail R37-YIELD-FALSE 'mode applicability not implemented: validate-run-root.sh --nonterminal-yield' "$false_yield_mode"


# A new historical read mode adds one actual mode; original24 receipts remain
# historical. Neither an absent declaration nor a false dispatch may pass.
missing_history_mode="$(make_candidate missing-history-mode)"
python - "$missing_history_mode" <<'PYMODE'
from pathlib import Path
import sys
p=Path(sys.argv[1])/"skills/implementaudit/references/repo-state-comparison.md"
text=p.read_text(); prefix="helper-mode: claim-run.sh|--resolve-retained-continuity-predecessor|"
assert sum(line.startswith(prefix) for line in text.splitlines()) == 1
p.write_text("\n".join(line for line in text.splitlines() if not line.startswith(prefix))+"\n")
PYMODE
expect_fail R39-HISTORY-MISSING 'missing mode applicability rows: claim-run.sh --resolve-retained-continuity-predecessor' "$missing_history_mode"

false_history_mode="$(make_candidate false-history-mode)"
python - "$false_history_mode" <<'PYMODE'
from pathlib import Path
import sys
p=Path(sys.argv[1])/"skills/implementaudit/scripts/claim-run.sh"
text=p.read_text(); assert "--resolve-retained-continuity-predecessor" in text
p.write_text(text.replace("--resolve-retained-continuity-predecessor", "--not-retained-history"))
PYMODE
expect_fail R39-HISTORY-FALSE 'mode applicability not implemented: claim-run.sh --resolve-retained-continuity-predecessor' "$false_history_mode"

printf 'helper-reachability.test: retained controls passed (dynamic full-path census + modes 25/25 + native-input, nonterminal-yield, ordered-replacement and historical-link controls)\n'

python -I -B "$repo_root/tests/helper-reachability-successor.py" "$repo_root" "$BASH"
python -I -B "$repo_root/tests/helper-reachability-custody.py" "$repo_root" "$BASH"
