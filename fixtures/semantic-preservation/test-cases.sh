#!/usr/bin/env bash
set -euo pipefail

fixture_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
evaluator="$fixture_dir/evaluate.py"
cases="$fixture_dir/cases.json"
fail() { printf 'semantic-preservation-cases: %s\n' "$*" >&2; exit 1; }

[ -f "$cases" ] || fail "cases.json missing"
[ -f "$evaluator" ] || fail "evaluate.py missing"

if command -v python >/dev/null 2>&1; then
  python_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  python_cmd=(python3)
else
  fail "python or python3 is required"
fi

output="$(PYTHONDONTWRITEBYTECODE=1 "${python_cmd[@]}" "$evaluator" --cases "$cases" --check)"
printf '%s\n' "$output"

for witness in \
  'nonexistent-progressive-owner: triggered=true disposition=FAIL reason=required-owner-unshipped' \
  'moved-to-unshipped-owner: triggered=true disposition=FAIL reason=required-owner-unshipped' \
  'invented-consumer: triggered=true disposition=FAIL reason=required-consumer-unreachable' \
  'retained-literal-broken-consumer: triggered=true disposition=FAIL reason=required-consumer-unreachable' \
  'exact-owner-relabelled-semantic: triggered=true disposition=FAIL reason=exact-literal-owner-changed' \
  'safe-progressive-split: triggered=true disposition=PASS_PROGRESSIVE_SPLIT reason=progressive-consumer-chain-preserved' \
  'package-evidence: repo-only instrumentation absent (3/3)'
do
  grep -Fqx "$witness" <<<"$output" || fail "missing evidence-bound witness: $witness"
done

attack_dir="$(mktemp -d)"
trap 'rm -rf "$attack_dir"' EXIT
cp "$cases" "$attack_dir/unrelated-consumer-anchor.json"
"${python_cmd[@]}" - "$attack_dir/unrelated-consumer-anchor.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
payload["evidence_profiles"]["safe-progressive"]["consumers"][0]["route_anchor"] = "AUDIT_START"
path.write_text(json.dumps(payload), encoding="utf-8")
PY
attack_output="$(PYTHONDONTWRITEBYTECODE=1 "${python_cmd[@]}" "$evaluator" --cases "$attack_dir/unrelated-consumer-anchor.json")"
grep -Fqx \
  'safe-progressive-split: triggered=true disposition=FAIL reason=required-consumer-unreachable' \
  <<<"$attack_output" || fail "unrelated existing consumer anchor must not prove owner reachability"

cp "$cases" "$attack_dir/progressive-without-held-out.json"
"${python_cmd[@]}" - "$attack_dir/progressive-without-held-out.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
payload = json.loads(path.read_text(encoding="utf-8"))
del payload["evidence_profiles"]["safe-progressive"]["consumers"][0]["held_out"]
for case in payload["cases"]:
    if case["id"] == "safe-progressive-split":
        case["progressive_split"]["applies"] = False
        case["expected"] = {
            "triggered": True,
            "disposition": "PASS_EQUIVALENT",
            "reason_code": "predicates-and-consumers-preserved",
        }
        break
else:
    raise SystemExit("safe-progressive-split case missing")
path.write_text(json.dumps(payload), encoding="utf-8")
PY
attack_output="$(PYTHONDONTWRITEBYTECODE=1 "${python_cmd[@]}" "$evaluator" --cases "$attack_dir/progressive-without-held-out.json")"
grep -Fqx \
  'safe-progressive-split: triggered=true disposition=FAIL reason=held-out-consumer-missing' \
  <<<"$attack_output" || fail "progressive PASS must have an inspectable held-out consumer probe"
