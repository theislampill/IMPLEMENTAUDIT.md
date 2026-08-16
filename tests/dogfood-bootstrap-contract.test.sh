#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

bash scripts/check-dogfood-bootstrap-contract.sh

python - <<'PY'
import json
from pathlib import Path

schema = json.loads(
    Path("fixtures/dogfood-bootstrap/typed-event.schema.json").read_text(
        encoding="utf-8"
    )
)
actions = schema["properties"]["action"]["enum"]
if actions.count("baseline-tree") != 1:
    raise SystemExit(
        "dogfood-bootstrap-contract.test: schema must admit baseline-tree exactly once"
    )
PY

# Structural self-dogfood evidence is state-derived and runner-owned. This
# section deliberately precedes the legacy transcript pressure bank: typed
# evidence becomes the primary semantic surface without deleting or weakening
# any independent transcript fixture below.
typed_root="$tmp/typed-evidence"
runtime_root="$typed_root/temp-codex-home/skills/implementaudit"
source_root="$typed_root/source-checkout"
mkdir -p "$runtime_root/references"
cp skills/implementaudit/SKILL.md "$runtime_root/SKILL.md"
cp skills/implementaudit/references/transcript-contract.md \
  "$runtime_root/references/transcript-contract.md"
mkdir -p "$source_root/fixtures/dogfood-bootstrap" \
  "$source_root/skills/implementaudit"
cp fixtures/dogfood-bootstrap/typed-event.schema.json \
  "$source_root/fixtures/dogfood-bootstrap/typed-event.schema.json"
cp skills/implementaudit/SKILL.md "$source_root/skills/implementaudit/SKILL.md"
git -C "$source_root" init -q
git -C "$source_root" config user.name 'Dogfood Contract Test'
git -C "$source_root" config user.email 'dogfood-contract@example.invalid'
git -C "$source_root" config core.autocrlf false
git -C "$source_root" add .
git -C "$source_root" commit -q -m baseline

candidate_commit="$(git -C "$source_root" rev-parse HEAD)"
candidate_tree="$(git -C "$source_root" rev-parse 'HEAD^{tree}')"
package_sha="1111111111111111111111111111111111111111111111111111111111111111"
runtime_sha="$(python - "$runtime_root/SKILL.md" <<'PY'
import hashlib
import pathlib
import sys
print(hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest())
PY
)"

init_f01_broker() {
  local custody_root="$1"
  local checkout="$2"
  local commit="$3"
  local tree="$4"
  local session="$5"
  python scripts/dogfood-evidence-broker.py init \
    --context "$custody_root/context.json" \
    --journal "$custody_root/events.jsonl" \
    --key-file "$custody_root/event.key" \
    --session-id "$session" \
    --audit-object implementaudit-rc-self-release \
    --candidate-commit "$commit" \
    --candidate-tree "$tree" \
    --package-sha256 "$package_sha" \
    --runtime-sha256 "$runtime_sha" \
    --source-root "$checkout" \
    --runtime-root "$runtime_root"
}

f01_failures=0
clean_control="$tmp/f01-clean-control"
init_f01_broker "$clean_control" "$source_root" \
  "$candidate_commit" "$candidate_tree" S3E-F01-CLEAN
clean_status="$(python scripts/dogfood-evidence-broker.py baseline-status \
  --context "$clean_control/context.json")"
if [ -n "$clean_status" ]; then
  printf 'F-01 RED: machine-readable clean status was not empty: %s\n' \
    "$clean_status" >&2
  f01_failures=$((f01_failures + 1))
fi
python scripts/dogfood-evidence-broker.py baseline-head \
  --context "$clean_control/context.json" >/dev/null
if ! python scripts/dogfood-evidence-broker.py baseline-tree \
  --context "$clean_control/context.json" \
  >"$tmp/f01-clean-tree.out" 2>&1; then
  printf 'F-01 RED: broker did not independently derive HEAD^{tree}\n' >&2
  f01_failures=$((f01_failures + 1))
fi

for dirty_kind in tracked untracked; do
  dirty_source="$tmp/f01-dirty-$dirty_kind-source"
  git clone -q "$source_root" "$dirty_source"
  if [ "$dirty_kind" = tracked ]; then
    printf '\ntracked dirt\n' >>"$dirty_source/skills/implementaudit/SKILL.md"
  else
    printf 'untracked dirt\n' >"$dirty_source/untracked.txt"
  fi
  dirty_commit="$(git -C "$dirty_source" rev-parse HEAD)"
  dirty_tree="$(git -C "$dirty_source" rev-parse 'HEAD^{tree}')"
  dirty_control="$tmp/f01-dirty-$dirty_kind-control"
  init_f01_broker "$dirty_control" "$dirty_source" \
    "$dirty_commit" "$dirty_tree" "S3E-F01-DIRTY-${dirty_kind^^}"
  if python scripts/dogfood-evidence-broker.py baseline-status \
    --context "$dirty_control/context.json" \
    >"$tmp/f01-dirty-$dirty_kind-status.out" 2>&1; then
    printf 'F-01 RED: dirty %s checkout qualified baseline-status\n' \
      "$dirty_kind" >&2
    f01_failures=$((f01_failures + 1))
  fi
  python scripts/dogfood-evidence-broker.py baseline-head \
    --context "$dirty_control/context.json" >/dev/null
  python scripts/dogfood-evidence-broker.py baseline-tree \
    --context "$dirty_control/context.json" >/dev/null 2>&1 || true
  if python scripts/dogfood-evidence-broker.py activate \
    --context "$dirty_control/context.json" \
    --path "$runtime_root/SKILL.md" \
    >"$tmp/f01-dirty-$dirty_kind-activate.out" 2>&1; then
    printf 'F-01 RED: dirty %s checkout reached activation\n' \
      "$dirty_kind" >&2
    f01_failures=$((f01_failures + 1))
  fi
  if python scripts/dogfood-evidence-broker.py read \
    --context "$dirty_control/context.json" \
    --path "$runtime_root/references/transcript-contract.md" \
    --correlation-id "dirty-$dirty_kind-read" \
    >"$tmp/f01-dirty-$dirty_kind-read.out" 2>&1; then
    printf 'F-01 RED: dirty %s checkout reached model read\n' \
      "$dirty_kind" >&2
    f01_failures=$((f01_failures + 1))
  fi
done

wrong_tree_control="$tmp/f01-wrong-tree-control"
wrong_tree="0000000000000000000000000000000000000000"
init_f01_broker "$wrong_tree_control" "$source_root" \
  "$candidate_commit" "$wrong_tree" S3E-F01-WRONG-TREE
python scripts/dogfood-evidence-broker.py baseline-status \
  --context "$wrong_tree_control/context.json" >/dev/null
python scripts/dogfood-evidence-broker.py baseline-head \
  --context "$wrong_tree_control/context.json" >/dev/null
python scripts/dogfood-evidence-broker.py baseline-tree \
  --context "$wrong_tree_control/context.json" >/dev/null 2>&1 || true
if python scripts/dogfood-evidence-broker.py activate \
  --context "$wrong_tree_control/context.json" \
  --path "$runtime_root/SKILL.md" \
  >"$tmp/f01-wrong-tree-activate.out" 2>&1; then
  printf 'F-01 RED: caller-supplied wrong tree reached activation\n' >&2
  f01_failures=$((f01_failures + 1))
fi
if python scripts/dogfood-evidence-broker.py read \
  --context "$wrong_tree_control/context.json" \
  --path "$runtime_root/references/transcript-contract.md" \
  --correlation-id wrong-tree-read \
  >"$tmp/f01-wrong-tree-read.out" 2>&1; then
  printf 'F-01 RED: caller-supplied wrong tree reached model read\n' >&2
  f01_failures=$((f01_failures + 1))
fi

if [ "$f01_failures" -ne 0 ]; then
  printf 'F-01 RED: %s discriminating controls failed\n' "$f01_failures" >&2
  exit 1
fi

if ! python scripts/dogfood-evidence-broker.py init \
  --context "$typed_root/context.json" \
  --journal "$typed_root/events.jsonl" \
  --key-file "$typed_root/event.key" \
  --session-id S3E-SELF-DOGFOOD-TDD \
  --audit-object implementaudit-rc-self-release \
  --candidate-commit "$candidate_commit" \
  --candidate-tree "$candidate_tree" \
  --package-sha256 "$package_sha" \
  --runtime-sha256 "$runtime_sha" \
  --source-root "$source_root" \
  --runtime-root "$runtime_root"; then
  printf 'S3E DOGFOOD STRUCTURAL RED: runner-owned typed evidence interface is absent\n' >&2
  exit 1
fi

python scripts/dogfood-evidence-broker.py baseline-status --context "$typed_root/context.json"
python scripts/dogfood-evidence-broker.py baseline-head --context "$typed_root/context.json"
python scripts/dogfood-evidence-broker.py baseline-tree --context "$typed_root/context.json"
python scripts/dogfood-evidence-broker.py activate \
  --context "$typed_root/context.json" \
  --path "$runtime_root/SKILL.md"
python scripts/dogfood-evidence-broker.py read \
  --context "$typed_root/context.json" \
  --path "$runtime_root/references/transcript-contract.md" \
  --correlation-id read-contract >/dev/null
python scripts/dogfood-evidence-broker.py search \
  --context "$typed_root/context.json" \
  --path "skills/implementaudit/SKILL.md" \
  --fixed-string 'Execution Spine' \
  --correlation-id search-source >/dev/null

typed_check=(
  bash scripts/check-dogfood-bootstrap-contract.sh
  --control self-dogfood
  --event-file "$typed_root/events.jsonl"
  --event-key-file "$typed_root/event.key"
  --expected-candidate "$candidate_commit"
  --expected-tree "$candidate_tree"
  --expected-package "$package_sha"
  --expected-runtime "$runtime_sha"
)

"${typed_check[@]}" \
  --corroboration-file fixtures/dogfood-bootstrap/typed/self-dogfood-corroboration.jsonl

python - "$typed_root/events.jsonl" "$typed_root/event.key" "$tmp" <<'PY'
import hashlib
import hmac
import json
import pathlib
import sys

source = pathlib.Path(sys.argv[1])
key_path = pathlib.Path(sys.argv[2])
target = pathlib.Path(sys.argv[3])
key = bytes.fromhex(key_path.read_text(encoding="ascii").strip())
events = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines()]

for action, wrong_identity in (
    ("baseline-status", "f" * 64),
    ("baseline-head", "0" * 40),
    ("baseline-tree", "0" * 40),
):
    population = [dict(event) for event in events]
    event = next(item for item in population if item["action"] == action)
    event["target_identity"] = wrong_identity
    event["content_sha256"] = "e" * 64
    unsigned = dict(event)
    unsigned.pop("hmac_sha256")
    event["hmac_sha256"] = hmac.new(
        key,
        json.dumps(
            unsigned,
            ensure_ascii=True,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    (target / f"f01-wrong-{action}.jsonl").write_text(
        "\n".join(
            json.dumps(item, separators=(",", ":"), sort_keys=True)
            for item in population
        )
        + "\n",
        encoding="utf-8",
    )
PY

semantic_failures=0
for baseline_action in baseline-status baseline-head baseline-tree; do
  if bash scripts/check-dogfood-bootstrap-contract.sh \
    --control self-dogfood \
    --event-file "$tmp/f01-wrong-$baseline_action.jsonl" \
    --event-key-file "$typed_root/event.key" \
    --expected-candidate "$candidate_commit" \
    --expected-tree "$candidate_tree" \
    --expected-package "$package_sha" \
    --expected-runtime "$runtime_sha" \
    --corroboration-file fixtures/dogfood-bootstrap/typed/self-dogfood-corroboration.jsonl \
    >"$tmp/f01-wrong-$baseline_action.out" 2>&1; then
    printf 'F-01 RED: HMAC-valid %s semantics self-corroborated\n' \
      "$baseline_action" >&2
    semantic_failures=$((semantic_failures + 1))
  fi
done
if [ "$semantic_failures" -ne 0 ]; then
  printf 'F-01 RED: %s independent semantic controls failed\n' \
    "$semantic_failures" >&2
  exit 1
fi

bash scripts/check-dogfood-bootstrap-contract.sh \
  --control ordinary \
  --activation-file fixtures/dogfood-bootstrap/typed/ordinary-control-activation.jsonl

ordinary_runtime_activation="$tmp/ordinary-runtime-activation.jsonl"
cp fixtures/dogfood-bootstrap/typed/ordinary-control-activation.jsonl \
  "$ordinary_runtime_activation"
printf '%s\n' '{"schema":"implementaudit.activation-trace.v1","sequence":2,"actor":"host","action":"activate-runtime","target_role":"temp-installed-runtime","result":"completed"}' \
  >>"$ordinary_runtime_activation"
if bash scripts/check-dogfood-bootstrap-contract.sh \
  --control ordinary \
  --activation-file "$ordinary_runtime_activation" \
  >"$tmp/ordinary-runtime-activation.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: ordinary runtime activation unexpectedly passed\n' >&2
  exit 1
fi
python - fixtures/dogfood-bootstrap/typed/ordinary-control-activation.jsonl "$tmp" <<'PY'
import json
import pathlib
import sys
source = pathlib.Path(sys.argv[1])
target = pathlib.Path(sys.argv[2])
event = json.loads(source.read_text(encoding="utf-8"))
cases = {
    "wrong-schema": dict(event, schema="attacker.activation-trace.v9"),
    "missing-schema": {key: value for key, value in event.items() if key != "schema"},
    "extra-identity": dict(event, target_identity="wrong"),
}
for name, value in cases.items():
    (target / f"ordinary-{name}.jsonl").write_text(
        json.dumps(value, separators=(",", ":"), sort_keys=True) + "\n",
        encoding="utf-8",
    )
PY
for ordinary_case in wrong-schema missing-schema extra-identity; do
  if bash scripts/check-dogfood-bootstrap-contract.sh \
    --control ordinary \
    --activation-file "$tmp/ordinary-$ordinary_case.jsonl" \
    >"$tmp/ordinary-$ordinary_case.out" 2>&1; then
    printf 'dogfood-bootstrap-contract.test: invalid ordinary envelope unexpectedly passed: %s\n' "$ordinary_case" >&2
    exit 1
  fi
done

extra_observation="$typed_root/extra-observation.jsonl"
cp fixtures/dogfood-bootstrap/typed/self-dogfood-corroboration.jsonl \
  "$extra_observation"
printf '%s\n' '{"schema":"implementaudit.observed-action.v1","sequence":7,"correlation_id":"unbrokered-read","actor":"model","action":"read","target_role":"real-home-runtime","result":"completed"}' \
  >>"$extra_observation"
if "${typed_check[@]}" \
  --corroboration-file "$extra_observation" \
  >"$tmp/typed-extra-observation.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: untyped observed action unexpectedly passed\n' >&2
  exit 1
fi
grep -F 'Andon: typed dogfood evidence contradicts independent observation' \
  "$tmp/typed-extra-observation.out" >/dev/null || {
  printf 'dogfood-bootstrap-contract.test: expected extra-observation Andon\n' >&2
  cat "$tmp/typed-extra-observation.out" >&2
  exit 1
}

if "${typed_check[@]}" \
  --corroboration-file fixtures/dogfood-bootstrap/typed/self-dogfood-contradiction.jsonl \
  >"$tmp/typed-contradiction.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: typed/transcript contradiction unexpectedly passed\n' >&2
  exit 1
fi
grep -F 'Andon: typed dogfood evidence contradicts independent observation' \
  "$tmp/typed-contradiction.out" >/dev/null || {
  printf 'dogfood-bootstrap-contract.test: expected contradiction Andon\n' >&2
  cat "$tmp/typed-contradiction.out" >&2
  exit 1
}

renumbered_reorder="$tmp/typed-renumbered-reorder.jsonl"
python - \
  fixtures/dogfood-bootstrap/typed/self-dogfood-corroboration.jsonl \
  "$renumbered_reorder" <<'PY'
import json
import pathlib
import sys
source = pathlib.Path(sys.argv[1])
target = pathlib.Path(sys.argv[2])
events = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines()]
events[0], events[1] = events[1], events[0]
for sequence, event in enumerate(events, 1):
    event["sequence"] = sequence
target.write_text(
    "\n".join(json.dumps(event, separators=(",", ":"), sort_keys=True) for event in events) + "\n",
    encoding="utf-8",
)
PY
if "${typed_check[@]}" \
  --corroboration-file "$renumbered_reorder" \
  >"$tmp/typed-renumbered-reorder.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: renumbered corroboration reorder unexpectedly passed\n' >&2
  exit 1
fi
grep -F 'Andon: typed dogfood evidence contradicts independent observation' \
  "$tmp/typed-renumbered-reorder.out" >/dev/null || {
  printf 'dogfood-bootstrap-contract.test: expected corroboration-order Andon\n' >&2
  cat "$tmp/typed-renumbered-reorder.out" >&2
  exit 1
}

python - fixtures/dogfood-bootstrap/typed/self-dogfood-corroboration.jsonl "$tmp" <<'PY'
import json
import pathlib
import sys
source = pathlib.Path(sys.argv[1])
target = pathlib.Path(sys.argv[2])
events = [json.loads(line) for line in source.read_text(encoding="utf-8").splitlines()]

wrong_schema = [dict(event, schema="attacker.observed-action.v9") for event in events]
missing_schema = [dict(event) for event in events]
missing_schema[0].pop("schema")
extra_identity = [dict(event, target_identity="wrong") for event in events]

for name, population in (
    ("wrong-schema", wrong_schema),
    ("missing-schema", missing_schema),
    ("extra-identity", extra_identity),
):
    (target / f"typed-{name}.jsonl").write_text(
        "\n".join(json.dumps(event, separators=(",", ":"), sort_keys=True) for event in population) + "\n",
        encoding="utf-8",
    )
PY
for observation_case in wrong-schema missing-schema extra-identity; do
  if "${typed_check[@]}" \
    --corroboration-file "$tmp/typed-$observation_case.jsonl" \
    >"$tmp/typed-$observation_case.out" 2>&1; then
    printf 'dogfood-bootstrap-contract.test: invalid corroboration envelope unexpectedly passed: %s\n' "$observation_case" >&2
    exit 1
  fi
  grep -F 'Andon: typed dogfood evidence contradicts independent observation' \
    "$tmp/typed-$observation_case.out" >/dev/null || {
    printf 'dogfood-bootstrap-contract.test: expected corroboration-envelope Andon: %s\n' "$observation_case" >&2
    cat "$tmp/typed-$observation_case.out" >&2
    exit 1
  }
done

python - \
  fixtures/dogfood-bootstrap/typed/self-dogfood-corroboration.jsonl \
  fixtures/dogfood-bootstrap/typed/ordinary-control-activation.jsonl \
  "$tmp" <<'PY'
import json
import pathlib
import sys
observed_source = pathlib.Path(sys.argv[1])
ordinary_source = pathlib.Path(sys.argv[2])
target = pathlib.Path(sys.argv[3])
observed = [json.loads(line) for line in observed_source.read_text(encoding="utf-8").splitlines()]
ordinary = [json.loads(line) for line in ordinary_source.read_text(encoding="utf-8").splitlines()]
for name, invalid in (("boolean", True), ("float", 1.0), ("string", "1")):
    observed_case = [dict(event) for event in observed]
    ordinary_case = [dict(event) for event in ordinary]
    observed_case[0]["sequence"] = invalid
    ordinary_case[0]["sequence"] = invalid
    for prefix, population in (("observed", observed_case), ("ordinary", ordinary_case)):
        (target / f"{prefix}-sequence-{name}.jsonl").write_text(
            "\n".join(json.dumps(event, separators=(",", ":"), sort_keys=True) for event in population) + "\n",
            encoding="utf-8",
        )
PY
for sequence_case in boolean float string; do
  if "${typed_check[@]}" \
    --corroboration-file "$tmp/observed-sequence-$sequence_case.jsonl" \
    >"$tmp/observed-sequence-$sequence_case.out" 2>&1; then
    printf 'dogfood-bootstrap-contract.test: invalid observed sequence unexpectedly passed: %s\n' "$sequence_case" >&2
    exit 1
  fi
  if bash scripts/check-dogfood-bootstrap-contract.sh \
    --control ordinary \
    --activation-file "$tmp/ordinary-sequence-$sequence_case.jsonl" \
    >"$tmp/ordinary-sequence-$sequence_case.out" 2>&1; then
    printf 'dogfood-bootstrap-contract.test: invalid ordinary sequence unexpectedly passed: %s\n' "$sequence_case" >&2
    exit 1
  fi
done

broker_duplicate_root="$tmp/broker-duplicate-journal"
python scripts/dogfood-evidence-broker.py init \
  --context "$broker_duplicate_root/context.json" \
  --journal "$broker_duplicate_root/events.jsonl" \
  --key-file "$broker_duplicate_root/event.key" \
  --session-id S3E-BROKER-DUPLICATE-JOURNAL \
  --audit-object implementaudit-rc-self-release \
  --candidate-commit "$candidate_commit" \
  --candidate-tree "$candidate_tree" \
  --package-sha256 "$package_sha" \
  --runtime-sha256 "$runtime_sha" \
  --source-root "$source_root" \
  --runtime-root "$runtime_root"
python scripts/dogfood-evidence-broker.py baseline-status \
  --context "$broker_duplicate_root/context.json" >/dev/null
python - "$broker_duplicate_root/events.jsonl" <<'PY'
import pathlib
import re
import sys
path = pathlib.Path(sys.argv[1])
lines = path.read_text(encoding="utf-8").splitlines()
matches = list(re.finditer(r'"result":"([^"]+)"', lines[0]))
if len(matches) != 1:
    raise SystemExit("broker journal first event lacks one result field")
original = matches[0].group(0)
value = matches[0].group(1)
lines[0] = lines[0].replace(
    original, f'"result":"ambiguous","result":"{value}"', 1
)
path.write_text("\n".join(lines) + "\n", encoding="utf-8")
PY
if python scripts/dogfood-evidence-broker.py baseline-head \
  --context "$broker_duplicate_root/context.json" \
  >"$tmp/broker-duplicate-journal.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: broker duplicate-key journal unexpectedly passed\n' >&2
  exit 1
fi

broker_context_root="$tmp/broker-duplicate-context"
python scripts/dogfood-evidence-broker.py init \
  --context "$broker_context_root/context.json" \
  --journal "$broker_context_root/events.jsonl" \
  --key-file "$broker_context_root/event.key" \
  --session-id S3E-BROKER-DUPLICATE-CONTEXT \
  --audit-object implementaudit-rc-self-release \
  --candidate-commit "$candidate_commit" \
  --candidate-tree "$candidate_tree" \
  --package-sha256 "$package_sha" \
  --runtime-sha256 "$runtime_sha" \
  --source-root "$source_root" \
  --runtime-root "$runtime_root"
python - "$broker_context_root/context.json" <<'PY'
import pathlib
import sys
path = pathlib.Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
needle = '"schema":"implementaudit.dogfood-broker-context.v1"'
if text.count(needle) != 1:
    raise SystemExit("broker context lacks one schema identity")
path.write_text(text.replace(needle, '"schema":"attacker.context.v9",' + needle, 1), encoding="utf-8")
PY
if python scripts/dogfood-evidence-broker.py baseline-status \
  --context "$broker_context_root/context.json" \
  >"$tmp/broker-duplicate-context.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: broker duplicate-key context unexpectedly passed\n' >&2
  exit 1
fi

prebaseline_root="$tmp/prebaseline-evidence"
python scripts/dogfood-evidence-broker.py init \
  --context "$prebaseline_root/context.json" \
  --journal "$prebaseline_root/events.jsonl" \
  --key-file "$prebaseline_root/event.key" \
  --session-id S3E-PREBASELINE-NEGATIVE \
  --audit-object implementaudit-rc-self-release \
  --candidate-commit "$candidate_commit" \
  --candidate-tree "$candidate_tree" \
  --package-sha256 "$package_sha" \
  --runtime-sha256 "$runtime_sha" \
  --source-root "$source_root" \
  --runtime-root "$runtime_root"
if python scripts/dogfood-evidence-broker.py read \
  --context "$prebaseline_root/context.json" \
  --path "$runtime_root/references/transcript-contract.md" \
  --correlation-id prebaseline-read \
  >"$tmp/prebaseline-read.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: pre-baseline broker read unexpectedly completed\n' >&2
  exit 1
fi
python - "$prebaseline_root/events.jsonl" <<'PY'
import json
import pathlib
import sys
event = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()[-1])
if (event.get("action"), event.get("phase"), event.get("result")) != ("read", "pre-baseline", "blocked"):
    raise SystemExit("pre-baseline rejection was not emitted at the runner action boundary")
PY

readable_source_root="$tmp/model-readable-source"
mkdir -p "$readable_source_root/fixtures/dogfood-bootstrap"
cp fixtures/dogfood-bootstrap/typed-event.schema.json \
  "$readable_source_root/fixtures/dogfood-bootstrap/typed-event.schema.json"
if python scripts/dogfood-evidence-broker.py init \
  --context "$readable_source_root/custody/context.json" \
  --journal "$readable_source_root/custody/events.jsonl" \
  --key-file "$readable_source_root/custody/event.key" \
  --session-id S3E-MODEL-READABLE-CUSTODY-NEGATIVE \
  --audit-object implementaudit-rc-self-release \
  --candidate-commit "$candidate_commit" \
  --candidate-tree "$candidate_tree" \
  --package-sha256 "$package_sha" \
  --runtime-sha256 "$runtime_sha" \
  --source-root "$readable_source_root" \
  --runtime-root "$runtime_root" \
  >"$tmp/model-readable-custody.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: model-readable runner custody unexpectedly passed\n' >&2
  exit 1
fi

# The source checkout and installed runtime are distinct evidence carriers.
# A nested "runtime" can otherwise make the tracked source SKILL self-attest as
# a successful temporary-home activation.
nested_root="$tmp/nested-runtime-negative"
if python scripts/dogfood-evidence-broker.py init \
  --context "$nested_root/context.json" \
  --journal "$nested_root/events.jsonl" \
  --key-file "$nested_root/event.key" \
  --session-id S3E-NESTED-RUNTIME-NEGATIVE \
  --audit-object implementaudit-rc-self-release \
  --candidate-commit "$candidate_commit" \
  --candidate-tree "$candidate_tree" \
  --package-sha256 "$package_sha" \
  --runtime-sha256 "$(python - <<'PY'
import hashlib
from pathlib import Path
print(hashlib.sha256(Path('skills/implementaudit/SKILL.md').read_bytes()).hexdigest())
PY
)" \
  --source-root "$repo_root" \
  --runtime-root "$repo_root/skills/implementaudit" \
  >"$tmp/nested-runtime.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: nested source/runtime roots unexpectedly passed\n' >&2
  exit 1
fi

carrier_root="$tmp/carrier-binding-negative"
cp "$runtime_root/SKILL.md" "$runtime_root/alternate-runtime.md"
python scripts/dogfood-evidence-broker.py init \
  --context "$carrier_root/context.json" \
  --journal "$carrier_root/events.jsonl" \
  --key-file "$carrier_root/event.key" \
  --session-id S3E-CARRIER-BINDING-NEGATIVE \
  --audit-object implementaudit-rc-self-release \
  --candidate-commit "$candidate_commit" \
  --candidate-tree "$candidate_tree" \
  --package-sha256 "$package_sha" \
  --runtime-sha256 "$runtime_sha" \
  --source-root "$source_root" \
  --runtime-root "$runtime_root"
python scripts/dogfood-evidence-broker.py baseline-status --context "$carrier_root/context.json" >/dev/null
python scripts/dogfood-evidence-broker.py baseline-head --context "$carrier_root/context.json" >/dev/null
python scripts/dogfood-evidence-broker.py baseline-tree --context "$carrier_root/context.json" >/dev/null
if python scripts/dogfood-evidence-broker.py activate \
  --context "$carrier_root/context.json" \
  --path "$runtime_root/alternate-runtime.md" \
  >"$tmp/carrier-binding.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: non-carrier runtime activation unexpectedly passed\n' >&2
  exit 1
fi

declared_real_home="$tmp/declared-user/.codex/skills/implementaudit"
mkdir -p "$declared_real_home/references"
cp skills/implementaudit/SKILL.md "$declared_real_home/SKILL.md"
cp skills/implementaudit/references/transcript-contract.md \
  "$declared_real_home/references/transcript-contract.md"
if python scripts/dogfood-evidence-broker.py init \
  --context "$tmp/declared-real-home/context.json" \
  --journal "$tmp/declared-real-home/events.jsonl" \
  --key-file "$tmp/declared-real-home/event.key" \
  --session-id S3E-DECLARED-REAL-HOME-NEGATIVE \
  --audit-object implementaudit-rc-self-release \
  --candidate-commit "$candidate_commit" \
  --candidate-tree "$candidate_tree" \
  --package-sha256 "$package_sha" \
  --runtime-sha256 "$runtime_sha" \
  --source-root "$source_root" \
  --runtime-root "$declared_real_home" \
  >"$tmp/declared-real-home.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: declared real-home runtime unexpectedly passed\n' >&2
  exit 1
fi

real_home_root="$tmp/real-home-evidence"
python scripts/dogfood-evidence-broker.py init \
  --context "$real_home_root/context.json" \
  --journal "$real_home_root/events.jsonl" \
  --key-file "$real_home_root/event.key" \
  --session-id S3E-REAL-HOME-NEGATIVE \
  --audit-object implementaudit-rc-self-release \
  --candidate-commit "$candidate_commit" \
  --candidate-tree "$candidate_tree" \
  --package-sha256 "$package_sha" \
  --runtime-sha256 "$runtime_sha" \
  --source-root "$source_root" \
  --runtime-root "$runtime_root"
python scripts/dogfood-evidence-broker.py baseline-status --context "$real_home_root/context.json" >/dev/null
python scripts/dogfood-evidence-broker.py baseline-head --context "$real_home_root/context.json" >/dev/null
python scripts/dogfood-evidence-broker.py baseline-tree --context "$real_home_root/context.json" >/dev/null
python scripts/dogfood-evidence-broker.py activate \
  --context "$real_home_root/context.json" \
  --path "$runtime_root/SKILL.md"
fake_real_home="$tmp/fake-user/.codex/skills/implementaudit"
mkdir -p "$fake_real_home/references"
cp skills/implementaudit/SKILL.md "$fake_real_home/SKILL.md"
cp skills/implementaudit/references/transcript-contract.md \
  "$fake_real_home/references/transcript-contract.md"
if python scripts/dogfood-evidence-broker.py read \
  --context "$real_home_root/context.json" \
  --path "$fake_real_home/SKILL.md" \
  --correlation-id real-home-read \
  >"$tmp/real-home-read.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: real-home broker read unexpectedly completed\n' >&2
  exit 1
fi
python - "$real_home_root/events.jsonl" <<'PY'
import json
import pathlib
import sys
event = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()[-1])
if (event.get("action"), event.get("target_role"), event.get("result")) != ("read", "real-home-runtime", "blocked"):
    raise SystemExit("real-home rejection was not emitted at the runner action boundary")
PY

if python scripts/dogfood-evidence-broker.py read \
  --context "$real_home_root/context.json" \
  --path "$fake_real_home/references/transcript-contract.md" \
  --correlation-id real-home-reference-read \
  >"$tmp/real-home-reference-read.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: real-home reference read unexpectedly completed\n' >&2
  exit 1
fi
python - "$real_home_root/events.jsonl" <<'PY'
import json
import pathlib
import sys
event = json.loads(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8").splitlines()[-1])
if (event.get("action"), event.get("target_role"), event.get("result")) != ("read", "real-home-runtime", "blocked"):
    raise SystemExit("real-home descendant was not classified at the runner action boundary")
PY

cp "$typed_root/events.jsonl" "$typed_root/duplicate.jsonl"
tail -n 1 "$typed_root/events.jsonl" >>"$typed_root/duplicate.jsonl"
if bash scripts/check-dogfood-bootstrap-contract.sh \
  --control self-dogfood \
  --event-file "$typed_root/duplicate.jsonl" \
  --event-key-file "$typed_root/event.key" \
  --expected-candidate "$candidate_commit" \
  --expected-tree "$candidate_tree" \
  --expected-package "$package_sha" \
  --expected-runtime "$runtime_sha" \
  --corroboration-file fixtures/dogfood-bootstrap/typed/self-dogfood-corroboration.jsonl \
  >"$tmp/typed-duplicate.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: duplicate typed event unexpectedly passed\n' >&2
  exit 1
fi

python - \
  "$typed_root/events.jsonl" \
  "$typed_root/reordered.jsonl" \
  "$typed_root/forged.jsonl" \
  "$typed_root/missing.jsonl" \
  "$typed_root/ambiguous.jsonl" \
  "$typed_root/invalid-schema.jsonl" \
  "$typed_root/duplicate-key.jsonl" \
  "$typed_root/event.key" <<'PY'
import hashlib
import hmac
import json
import pathlib
import sys

source, reordered, forged, missing, ambiguous, invalid_schema, duplicate_key, key_path = map(pathlib.Path, sys.argv[1:])
lines = source.read_text(encoding="utf-8").splitlines()
swapped = lines[:]
swapped[-2], swapped[-1] = swapped[-1], swapped[-2]
reordered.write_text("\n".join(swapped) + "\n", encoding="utf-8")
events = [json.loads(line) for line in lines]
events[-1]["target_role"] = "real-home-runtime"
forged.write_text("\n".join(json.dumps(event, separators=(",", ":"), sort_keys=True) for event in events) + "\n", encoding="utf-8")
missing.write_text("\n".join(lines[:2] + lines[3:]) + "\n", encoding="utf-8")
duplicate_lines = lines[:]
needle = '"result":"completed"'
if duplicate_lines[0].count(needle) != 1:
    raise SystemExit("typed journal first event lacks one completed result")
duplicate_lines[0] = duplicate_lines[0].replace(
    needle, '"result":"blocked","result":"completed"', 1
)
duplicate_key.write_text("\n".join(duplicate_lines) + "\n", encoding="utf-8")

key = bytes.fromhex(key_path.read_text(encoding="ascii").strip())
ambiguous_events = [json.loads(line) for line in lines]
ambiguous_events[-1]["result"] = "ambiguous"
unsigned = dict(ambiguous_events[-1])
unsigned.pop("hmac_sha256")
ambiguous_events[-1]["hmac_sha256"] = hmac.new(
    key,
    json.dumps(unsigned, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("utf-8"),
    hashlib.sha256,
).hexdigest()
ambiguous.write_text(
    "\n".join(json.dumps(event, separators=(",", ":"), sort_keys=True) for event in ambiguous_events) + "\n",
    encoding="utf-8",
)

invalid_events = [json.loads(line) for line in lines]
invalid_events[2]["actor"] = "intruder"
unsigned = dict(invalid_events[2])
unsigned.pop("hmac_sha256")
invalid_events[2]["hmac_sha256"] = hmac.new(
    key,
    json.dumps(unsigned, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("utf-8"),
    hashlib.sha256,
).hexdigest()
invalid_schema.write_text(
    "\n".join(json.dumps(event, separators=(",", ":"), sort_keys=True) for event in invalid_events) + "\n",
    encoding="utf-8",
)
PY

for broken in reordered forged missing ambiguous invalid-schema duplicate-key; do
  if bash scripts/check-dogfood-bootstrap-contract.sh \
    --control self-dogfood \
    --event-file "$typed_root/$broken.jsonl" \
    --event-key-file "$typed_root/event.key" \
    --expected-candidate "$candidate_commit" \
    --expected-tree "$candidate_tree" \
    --expected-package "$package_sha" \
    --expected-runtime "$runtime_sha" \
    --corroboration-file fixtures/dogfood-bootstrap/typed/self-dogfood-corroboration.jsonl \
    >"$tmp/typed-$broken.out" 2>&1; then
    printf 'dogfood-bootstrap-contract.test: %s typed evidence unexpectedly passed\n' "$broken" >&2
    exit 1
  fi
done

if bash scripts/check-dogfood-bootstrap-contract.sh \
  --control self-dogfood \
  --event-file "$typed_root/events.jsonl" \
  --event-key-file "$typed_root/event.key" \
  --expected-candidate "$candidate_commit" \
  --expected-tree "$candidate_tree" \
  --expected-package "2222222222222222222222222222222222222222222222222222222222222222" \
  --expected-runtime "$runtime_sha" \
  --corroboration-file fixtures/dogfood-bootstrap/typed/self-dogfood-corroboration.jsonl \
  >"$tmp/typed-identity.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: identity-mismatched typed evidence unexpectedly passed\n' >&2
  exit 1
fi

if ! bash scripts/check-dogfood-bootstrap-contract.sh \
  --transcript-file fixtures/dogfood-bootstrap/positive/host-activation-before-baseline-transcript.jsonl \
  >/tmp/dogfood-bootstrap-host-activation.out 2>&1; then
  printf 'dogfood-bootstrap-contract.test: qualified host activation before runner baseline was rejected\n' >&2
  cat /tmp/dogfood-bootstrap-host-activation.out >&2
  exit 1
fi

if ! bash scripts/check-dogfood-bootstrap-contract.sh \
  --transcript-file fixtures/dogfood-bootstrap/positive/similarly-named-path-before-baseline-transcript.jsonl \
  >"$tmp/similar-path.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: similarly named non-root path was treated as installed payload\n' >&2
  cat "$tmp/similar-path.out" >&2
  exit 1
fi

if ! bash scripts/check-dogfood-bootstrap-contract.sh \
  --transcript-file fixtures/dogfood-bootstrap/positive/echo-installed-path-before-baseline-transcript.jsonl \
  >"$tmp/echo-path.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: harmless path echo was treated as installed payload readback\n' >&2
  cat "$tmp/echo-path.out" >&2
  exit 1
fi

if ! bash scripts/check-dogfood-bootstrap-contract.sh \
  --transcript-file fixtures/dogfood-bootstrap/positive/rg-pattern-installed-path-before-baseline-transcript.jsonl \
  >"$tmp/rg-pattern.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: rg search pattern was treated as a filesystem read target\n' >&2
  cat "$tmp/rg-pattern.out" >&2
  exit 1
fi

for baseline_case in \
  status-only-before-readback-transcript.jsonl \
  failed-baseline-before-readback-transcript.jsonl
do
  if bash scripts/check-dogfood-bootstrap-contract.sh \
    --transcript-file "fixtures/dogfood-bootstrap/negative/$baseline_case" \
    >"$tmp/$baseline_case.out" 2>&1; then
    printf 'dogfood-bootstrap-contract.test: incomplete or failed baseline unexpectedly passed: %s\n' "$baseline_case" >&2
    exit 1
  fi

  grep -F "missing successful baseline command completion" "$tmp/$baseline_case.out" >/dev/null || {
    printf 'dogfood-bootstrap-contract.test: expected successful-baseline diagnostic: %s\n' "$baseline_case" >&2
    cat "$tmp/$baseline_case.out" >&2
    exit 1
  }
done

if bash scripts/check-dogfood-bootstrap-contract.sh \
  --transcript-file fixtures/dogfood-bootstrap/negative/narrated-temp-home-before-real-home-activation-transcript.jsonl \
  >"$tmp/narrated-temp-home.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: narrated temp-home token laundered real-home activation\n' >&2
  exit 1
fi

grep -F "real-home skill readback occurred before structured temp-home installation or activation evidence" "$tmp/narrated-temp-home.out" >/dev/null || {
  printf 'dogfood-bootstrap-contract.test: expected structured temp-home evidence diagnostic\n' >&2
  cat "$tmp/narrated-temp-home.out" >&2
  exit 1
}

if bash scripts/check-dogfood-bootstrap-contract.sh \
  --transcript-file fixtures/dogfood-bootstrap/negative/uppercase-windows-readback-before-baseline-transcript.jsonl \
  >"$tmp/uppercase-readback.out" 2>&1; then
  printf 'dogfood-bootstrap-contract.test: uppercase Windows readback bypassed baseline order\n' >&2
  exit 1
fi

grep -F "installed skill readback occurred before baseline" "$tmp/uppercase-readback.out" >/dev/null || {
  printf 'dogfood-bootstrap-contract.test: expected casefolded readback diagnostic\n' >&2
  cat "$tmp/uppercase-readback.out" >&2
  exit 1
}

for payload_case in \
  bash-lc-installed-readback-before-baseline-transcript.jsonl \
  tight-pwsh-scriptblock-installed-readback-before-baseline-transcript.jsonl \
  env-prefixed-installed-readback-before-baseline-transcript.jsonl \
  rg-attached-pattern-installed-target-before-baseline-transcript.jsonl \
  rg-files-installed-root-before-baseline-transcript.jsonl \
  grep-recursive-installed-target-before-baseline-transcript.jsonl \
  select-string-explicit-pattern-installed-target-before-baseline-transcript.jsonl \
  installed-reference-before-baseline-transcript.jsonl \
  powershell-wrapped-installed-readback-before-baseline-transcript.jsonl \
  powershell-scriptblock-installed-readback-before-baseline-transcript.jsonl \
  compound-installed-readback-before-baseline-transcript.jsonl \
  posix-absolute-installed-readback-before-baseline-transcript.jsonl \
  rg-text-mode-installed-target-before-baseline-transcript.jsonl \
  mixed-separator-readback-before-baseline-transcript.jsonl \
  dot-segment-installed-readback-before-baseline-transcript.jsonl \
  dotdot-segment-installed-readback-before-baseline-transcript.jsonl \
  installed-root-listing-before-baseline-transcript.jsonl
do
  if bash scripts/check-dogfood-bootstrap-contract.sh \
    --transcript-file "fixtures/dogfood-bootstrap/negative/$payload_case" \
    >"$tmp/$payload_case.out" 2>&1; then
    printf 'dogfood-bootstrap-contract.test: installed payload path unexpectedly passed: %s\n' "$payload_case" >&2
    exit 1
  fi

  grep -F "installed skill readback occurred before baseline" "$tmp/$payload_case.out" >/dev/null || {
    printf 'dogfood-bootstrap-contract.test: expected installed-root readback diagnostic: %s\n' "$payload_case" >&2
    cat "$tmp/$payload_case.out" >&2
    exit 1
  }
done

for real_home_case in \
  host-purpose-temp-launders-real-home-transcript.jsonl \
  spaced-profile-real-home-activation-transcript.jsonl
do
  if bash scripts/check-dogfood-bootstrap-contract.sh \
    --transcript-file "fixtures/dogfood-bootstrap/negative/$real_home_case" \
    >"$tmp/$real_home_case.out" 2>&1; then
    printf 'dogfood-bootstrap-contract.test: real-home field/path held-out unexpectedly passed: %s\n' "$real_home_case" >&2
    exit 1
  fi

  grep -F "real-home skill readback occurred before structured temp-home installation or activation evidence" "$tmp/$real_home_case.out" >/dev/null || {
    printf 'dogfood-bootstrap-contract.test: expected field-scoped real-home diagnostic: %s\n' "$real_home_case" >&2
    cat "$tmp/$real_home_case.out" >&2
    exit 1
  }
done

cat >"$tmp/skill-missing-bootstrap.md" <<'BAD'
# /implementaudit

This synthetic skill fixture intentionally omits the dogfood bootstrap section.
BAD

if bash scripts/check-dogfood-bootstrap-contract.sh \
  --skill-file "$tmp/skill-missing-bootstrap.md" \
  >/tmp/dogfood-bootstrap.out 2>&1; then
  printf 'dogfood-bootstrap-contract.test: missing bootstrap unexpectedly passed\n' >&2
  exit 1
fi

grep -F "missing ## State-derived RC self-dogfood route" /tmp/dogfood-bootstrap.out >/dev/null || {
  printf 'dogfood-bootstrap-contract.test: expected missing-bootstrap diagnostic\n' >&2
  cat /tmp/dogfood-bootstrap.out >&2
  exit 1
}

if bash scripts/check-dogfood-bootstrap-contract.sh \
  --transcript-file fixtures/dogfood-bootstrap/negative/installed-readback-before-baseline-transcript.jsonl \
  >/tmp/dogfood-bootstrap-transcript.out 2>&1; then
  printf 'dogfood-bootstrap-contract.test: readback-before-baseline transcript unexpectedly passed\n' >&2
  exit 1
fi

grep -F "installed skill readback occurred before baseline" /tmp/dogfood-bootstrap-transcript.out >/dev/null || {
  printf 'dogfood-bootstrap-contract.test: expected transcript-order diagnostic\n' >&2
  cat /tmp/dogfood-bootstrap-transcript.out >&2
  exit 1
}

if bash scripts/check-dogfood-bootstrap-contract.sh \
  --transcript-file fixtures/dogfood-bootstrap/negative/chunking-readback-before-baseline-transcript.jsonl \
  >/tmp/dogfood-bootstrap-chunking.out 2>&1; then
  printf 'dogfood-bootstrap-contract.test: chunking-readback transcript unexpectedly passed\n' >&2
  exit 1
fi

grep -F "installed skill readback occurred before baseline" /tmp/dogfood-bootstrap-chunking.out >/dev/null || {
  printf 'dogfood-bootstrap-contract.test: expected chunking-readback diagnostic\n' >&2
  cat /tmp/dogfood-bootstrap-chunking.out >&2
  exit 1
}

if bash scripts/check-dogfood-bootstrap-contract.sh \
  --transcript-file fixtures/dogfood-bootstrap/negative/real-home-readback-before-temp-home-transcript.jsonl \
  >/tmp/dogfood-bootstrap-real-home.out 2>&1; then
  printf 'dogfood-bootstrap-contract.test: real-home-readback transcript unexpectedly passed\n' >&2
  exit 1
fi

grep -F "real-home skill readback occurred before structured temp-home installation or activation evidence" /tmp/dogfood-bootstrap-real-home.out >/dev/null || {
  printf 'dogfood-bootstrap-contract.test: expected real-home contamination diagnostic\n' >&2
  cat /tmp/dogfood-bootstrap-real-home.out >&2
  exit 1
}

if bash scripts/check-dogfood-bootstrap-contract.sh \
  --transcript-file fixtures/dogfood-bootstrap/negative/real-home-readback-generic-user-before-temp-home-transcript.jsonl \
  >/tmp/dogfood-bootstrap-real-home-generic.out 2>&1; then
  printf 'dogfood-bootstrap-contract.test: generic-user real-home transcript unexpectedly passed\n' >&2
  exit 1
fi

grep -F "real-home skill readback occurred before structured temp-home installation or activation evidence" /tmp/dogfood-bootstrap-real-home-generic.out >/dev/null || {
  printf 'dogfood-bootstrap-contract.test: expected generic-user real-home contamination diagnostic\n' >&2
  cat /tmp/dogfood-bootstrap-real-home-generic.out >&2
  exit 1
}

if bash scripts/check-dogfood-bootstrap-contract.sh \
  --transcript-file fixtures/dogfood-bootstrap/negative/real-home-host-activation-generic-user-transcript.jsonl \
  >/tmp/dogfood-bootstrap-real-home-host.out 2>&1; then
  printf 'dogfood-bootstrap-contract.test: generic-user real-home host activation unexpectedly passed\n' >&2
  exit 1
fi

grep -F "real-home skill readback occurred before structured temp-home installation or activation evidence" /tmp/dogfood-bootstrap-real-home-host.out >/dev/null || {
  printf 'dogfood-bootstrap-contract.test: expected real-home host-activation diagnostic\n' >&2
  cat /tmp/dogfood-bootstrap-real-home-host.out >&2
  exit 1
}

printf 'dogfood-bootstrap-contract.test: ok\n'
