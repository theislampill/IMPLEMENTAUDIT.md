#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

fail() {
  printf 'operational-evidence-contract.test: %s\n' "$*" >&2
  exit 1
}

if command -v python >/dev/null 2>&1; then
  py_cmd=(python)
elif command -v python3 >/dev/null 2>&1; then
  py_cmd=(python3)
elif command -v py >/dev/null 2>&1; then
  py_cmd=(py -3)
else
  fail "python, python3, or py -3 is required"
fi

loader="skills/implementaudit/scripts/operational-evidence.py"
fixtures="fixtures/operational-evidence"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

expect_typed_failure() {
  local fixture="$1"
  local code="$2"
  local status
  set +e
  "${py_cmd[@]}" "$loader" validate "$fixtures/$fixture" \
    >"$tmp/stdout" 2>"$tmp/stderr"
  status=$?
  set -e
  [ "$status" -eq 2 ] \
    || fail "$fixture expected typed exit 2, got $status"
  "${py_cmd[@]}" - "$tmp/stderr" "$code" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as stream:
    error = json.load(stream)
if error.get("schema") != "implementaudit-operational-evidence-error-v1":
    raise SystemExit("stable typed error schema missing")
if error.get("code") != sys.argv[2]:
    raise SystemExit(
        f"expected typed failure {sys.argv[2]}, got {error.get('code')!r}")
PY
}

"${py_cmd[@]}" "$loader" validate "$fixtures/valid-minimal.json" \
  >"$tmp/valid.json"
"${py_cmd[@]}" - "$tmp/valid.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as stream:
    result = json.load(stream)
if result.get("schema") != "implementaudit-operational-evidence-validation-v1":
    raise SystemExit("validation receipt schema missing")
if result.get("aggregate") != "COMPLETE":
    raise SystemExit("valid COMPLETE fixture did not remain COMPLETE")
if result.get("families") != [
        "CODE", "OWNERSHIP", "EXECUTION", "EVIDENCE", "FAILURE", "RELEASE"]:
    raise SystemExit("six frozen families were not preserved in order")
PY

"${py_cmd[@]}" "$loader" validate "$fixtures/valid-unknown.json" \
  >"$tmp/unknown-receipt.json"
"${py_cmd[@]}" "$loader" canonicalize "$fixtures/valid-unknown.json" \
  >"$tmp/unknown-canonical.json"
"${py_cmd[@]}" - "$tmp/unknown-receipt.json" \
  "$tmp/unknown-canonical.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as stream:
    receipt = json.load(stream)
with open(sys.argv[2], encoding="utf-8") as stream:
    canonical = json.load(stream)
if receipt.get("aggregate") != "DEGRADED":
    raise SystemExit("UNKNOWN receipt must preserve DEGRADED aggregate")
if receipt.get("fact_state_census") != {"UNKNOWN": 1}:
    raise SystemExit("UNKNOWN receipt state census drift")
if canonical["aggregate"] != "DEGRADED":
    raise SystemExit("UNKNOWN canonical aggregate drift")
if canonical["affected_families"] != ["CODE"]:
    raise SystemExit("UNKNOWN affected family drift")
if canonical["entities"][0]["currentness"] != {
        "state": "UNKNOWN", "invalidators": []}:
    raise SystemExit("UNKNOWN canonical state drift")
PY

expect_typed_failure duplicate-key.json OE_JSON_DUPLICATE_KEY
expect_typed_failure nonfinite.json OE_JSON_NONFINITE
expect_typed_failure malformed-record.json OE_SCHEMA_INVALID
expect_typed_failure record-type-array.json OE_SCHEMA_INVALID
expect_typed_failure integer-digit-limit.json OE_JSON_NUMBER_LIMIT
expect_typed_failure cross-layer.json OE_CROSS_LAYER
expect_typed_failure stale-current.json OE_STALE_RECORD
expect_typed_failure unsupported-schema.json OE_SCHEMA_UNSUPPORTED
expect_typed_failure duplicate-id.json OE_SCHEMA_INVALID
expect_typed_failure payload-digest-mismatch.json OE_PAYLOAD_DIGEST

"${py_cmd[@]}" "$loader" canonicalize "$fixtures/payload-lf.json" \
  >"$tmp/payload-lf.json"
"${py_cmd[@]}" "$loader" canonicalize "$fixtures/payload-crlf.json" \
  >"$tmp/payload-crlf.json"
cmp "$tmp/payload-lf.json" "$tmp/payload-crlf.json" \
  || fail "equivalent payload newline forms did not canonicalize byte-identically"
"${py_cmd[@]}" - "$tmp/payload-lf.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as stream:
    value = json.load(stream)
payload = value["payload_records"][0]
if payload["payload"] != "line one\nline two":
    raise SystemExit("payload rule must normalize CRLF/CR to LF and strip trailing LF")
if payload["payload_sha256"] != (
        "b6858b03a6cae635deeaeab09a74e598979b72c917cbfff0bb3fe2cd05111dbc"):
    raise SystemExit("payload digest drift")
PY

printf 'operational-evidence-contract.test: ok\n'
