#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

fail() {
  printf 'interruption-durability.test: %s\n' "$*" >&2
  exit 1
}

require() {
  local file="$1" text="$2"
  [ -f "$file" ] || fail "missing file: $file"
  grep -Fqi -e "$text" "$file" || fail "missing in $file: $text"
}

continuity="skills/implementaudit/references/continuity.md"
child_ref="skills/implementaudit/references/child-agents.md"
report_template="skills/implementaudit/templates/child-agent-report.md"
inventory="skills/implementaudit/scripts/lane-survivor-inventory.sh"
fixture="eval/fixtures/B1r-pending-terminal/fixture.json"
seed_root="eval/fixtures/B1r-pending-terminal/seed/.IMPLEMENTAUDIT/runs/pending-terminal-b1r"

for tracked_seed in "$seed_root/PENDING_TERMINAL" "$seed_root/launch-intent.md"; do
  git ls-files --error-unmatch "$tracked_seed" >/dev/null 2>&1 ||
    fail "B1r seed is present locally but not tracked: $tracked_seed"
done

# Contract carrier failures: deleting any durability mechanism must fail here.
for text in PENDING_TERMINAL "exact command and preconditions" \
  "Clear it only after success" "re-checking its preconditions" \
  "never redo a satisfied one-shot" "never lose an unsatisfied one"; do
  require "$continuity" "$text"
done
for text in interrupted-partial "not PASS" "not NO_GO" \
  "does not consume the substantive verdict" \
  "provisional until independently reproduced" "Report state: PARTIAL" \
  "synthetic-model" "zero-token" "one-turn" "is_error" \
  "before acquiring" "browser tabs" "containers" "listeners" \
  "temp roots" "worktrees"; do
  require "$child_ref" "$text"
done
require "$report_template" "Report state: PARTIAL | FINAL | interrupted-partial"
require "$report_template" "Owned resources:"

# Real script behavior: present, absent, and shape-invalid outputs are distinct;
# re-dispatch is absent union partial; the command changes no run-root bytes.
[ -x "$inventory" ] || fail "missing executable survivor inventory: $inventory"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
cp -R fixtures/interruption-durability/kill-mid-fanout "$tmp/interrupted"
before="$(find "$tmp/interrupted" -type f -printf '%P\t%s\n' | sort)"
out="$(bash "$inventory" "$tmp/interrupted" \
  --expect lane-1.json --contains misleading_shortcuts \
  --expect lane-2.json --contains misleading_shortcuts \
  --expect lane-3.json --contains misleading_shortcuts \
  --expect lane-4.json --contains misleading_shortcuts \
  --expect lane-5.json --contains misleading_shortcuts)"
after="$(find "$tmp/interrupted" -type f -printf '%P\t%s\n' | sort)"
[ "$before" = "$after" ] || fail "inventory mutated the run root"
printf '%s\n' "$out" | grep -Fqx $'present\tlane-1.json' || fail "present classification missing"
printf '%s\n' "$out" | grep -Fqx $'absent\tlane-4.json' || fail "absent classification missing"
printf '%s\n' "$out" | grep -Fqx $'re-dispatch\tlane-4.json' || fail "lane 4 missing from re-dispatch set"
printf '%s\n' "$out" | grep -Fqx $'re-dispatch\tlane-5.json' || fail "lane 5 missing from re-dispatch set"
[ "$(printf '%s\n' "$out" | grep -c $'^re-dispatch\t')" -eq 2 ] || fail "interrupted fanout re-dispatch set was not exact"
printf '%s\n' "$out" | grep -Fq $'advisory\t' || fail "advisory explanation missing"

cp -R fixtures/interruption-durability/fanout-complete "$tmp/complete"
all_present="$(bash "$inventory" "$tmp/complete" \
  --expect lane-1.json --contains misleading_shortcuts \
  --expect lane-2.json --contains misleading_shortcuts \
  --expect lane-3.json --contains misleading_shortcuts \
  --expect lane-4.json --contains misleading_shortcuts \
  --expect lane-5.json --contains misleading_shortcuts)"
if printf '%s\n' "$all_present" | grep -q $'^re-dispatch\t'; then
  fail "complete fanout emitted a non-empty re-dispatch set"
fi

cp -R fixtures/interruption-durability/partial-record "$tmp/partial"
partial="$(bash "$inventory" "$tmp/partial" \
  --expect lane.json --contains misleading_shortcuts)"
printf '%s\n' "$partial" | grep -Fqx $'partial\tlane.json' || fail "partial classification missing"
printf '%s\n' "$partial" | grep -Fqx $'re-dispatch\tlane.json' || fail "partial output missing from re-dispatch set"

if bash "$inventory" "$tmp/complete" --expect ../escape.json >/dev/null 2>&1; then
  fail "inventory accepted a path outside the run root"
fi
if bash "$inventory" "$tmp/complete" \
  --expect lane-1.json --expect lane-1.json >/dev/null 2>&1; then
  fail "inventory accepted a duplicate member in the re-dispatch set"
fi
if bash "$inventory" "$tmp/complete" --expect $'lane\t1.json' >/dev/null 2>&1; then
  fail "inventory accepted a path that corrupts its tabular output"
fi

# Envelope/content classification fixtures exercise both polarities.
python - <<'PY'
import copy
import json
from pathlib import Path

root = Path("fixtures/interruption-durability")
bad = json.loads((root / "envelope-contradiction.json").read_text(encoding="utf-8"))
good = json.loads((root / "envelope-consistent.json").read_text(encoding="utf-8"))

def contradiction(case):
    env = case["envelope"]
    meta = case["model_metadata"]
    return (
        env.get("subtype") == "success" and (
            env.get("is_error") is True or
            env.get("output_tokens") == 0 or
            env.get("num_turns") == 1 or
            (meta.get("actual_model") == "<synthetic>" and
             meta.get("requested_model") != "<synthetic>")
        )
    )

assert contradiction(bad)
assert bad["expected_classification"] == "interrupted-partial"
assert not contradiction(good)
assert good["expected_classification"] == "FINAL"

for label, mutate in (
    ("is_error", lambda case: case["envelope"].update(is_error=True)),
    ("zero-token", lambda case: case["envelope"].update(output_tokens=0)),
    ("one-turn", lambda case: case["envelope"].update(num_turns=1)),
    ("synthetic-model", lambda case: case["model_metadata"].update(actual_model="<synthetic>")),
):
    case = copy.deepcopy(good)
    mutate(case)
    assert contradiction(case), label

provisional = (root / "provisional-not-credited-FAIL.md").read_text(encoding="utf-8")
reproduced = (root / "provisional-reproduced-PASS.md").read_text(encoding="utf-8")
assert "Closure credit: denied" in provisional
assert "Independent reproduction: absent" in provisional
assert "Closure credit: allowed" in reproduced
assert "Independent reproduction: complete" in reproduced

undeclared = (root / "undeclared-resources-FAIL.md").read_text(encoding="utf-8")
declared = (root / "declared-resources-PASS.md").read_text(encoding="utf-8")
assert "Residue classification: UNVERIFIED" in undeclared
assert "Pre-declared before acquisition: no" in undeclared
assert "Residue classification: enumerable" in declared
assert "Pre-declared before acquisition: yes" in declared
PY

# B1r reuses the existing matrix instruction-contract validator without
# becoming an official scored matrix cell in this issue.
PYTHONPATH=eval python - <<'PY'
import json
from pathlib import Path
import candidate_matrix_rederive as rederive

root = Path("eval/fixtures/B1r-pending-terminal")
fixture = json.loads((root / "fixture.json").read_text(encoding="utf-8"))
rederive.FIXTURE_ORDER = tuple(rederive.FIXTURE_ORDER) + (fixture["id"],)
rederive._validate_fixture_schema(fixture, fixture["id"])

mission = fixture["mission"].casefold()
required_forbidden = {
    "pending_terminal",
    "resume at the recorded command",
    "do not replay",
}
declared_forbidden = {
    phrase.casefold()
    for row in fixture["matrix_instruction_contract"]["fields"]
    for phrase in row["forbidden_mission_phrases"]
}
assert required_forbidden <= declared_forbidden
assert all(phrase not in mission for phrase in declared_forbidden)
assert "terminal_signal" in fixture["expected_correct_behavior"]
launch_intent = (root / "seed/.IMPLEMENTAUDIT/runs/pending-terminal-b1r/launch-intent.md").read_text(encoding="utf-8")
assert "terminal_signal:" in launch_intent
assert "not defined by this fixture" in launch_intent

resume = (root / "control-resume-PASS.txt").read_text(encoding="utf-8")
restart = (root / "control-resume-restart-FAIL.txt").read_text(encoding="utf-8")
satisfied = (root / "control-satisfied-one-shot-PASS.txt").read_text(encoding="utf-8")
replayed = (root / "control-satisfied-one-shot-replay-FAIL.txt").read_text(encoding="utf-8")

assert "NEXT_ACTION: EXECUTE_RECORDED" in resume
assert "PRECONDITIONS: RECHECKED" in resume
assert "NEXT_ACTION: RESTART_PROGRAMME" in restart
assert "NEXT_ACTION: NO_ACTION" in satisfied
assert "SATISFIED_ONE_SHOT: SKIPPED" in satisfied
assert "SATISFIED_ONE_SHOT: REPLAYED" in replayed

summary = {"changed_files": [".IMPLEMENTAUDIT/runs/pending-terminal-b1r/PENDING_TERMINAL"]}

def evaluate(text):
    texts = {"assistant": text}
    return {
        prop["name"]: rederive._eval_rule(prop["rule"], texts, summary)
        for prop in fixture["properties"]
    }

resume_states = evaluate(resume)
restart_states = evaluate(restart)
satisfied_states = evaluate(satisfied)
replayed_states = evaluate(replayed)
assert all(resume_states.values()), resume_states
assert not all(restart_states.values()), restart_states
assert satisfied_states["programme_not_replayed"], satisfied_states
assert satisfied_states["pending_record_cleared"], satisfied_states
assert not replayed_states["programme_not_replayed"], replayed_states
PY

printf 'interruption-durability.test: ok\n'
