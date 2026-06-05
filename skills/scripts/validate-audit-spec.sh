#!/usr/bin/env bash
set -euo pipefail

fail() {
  printf 'validate-audit-spec: %s\n' "$*" >&2
  exit 1
}

spec_file="${1:-}"
[ -n "$spec_file" ] || fail "usage: validate-audit-spec.sh <spec-file>"
[ -f "$spec_file" ] || fail "spec file not found: $spec_file"

lower="$(mktemp)"
trap 'rm -f "$lower"' EXIT
tr '[:upper:]' '[:lower:]' <"$spec_file" >"$lower"

require_any() {
  local label="$1"
  shift
  local pattern
  for pattern in "$@"; do
    if grep -Eq "$pattern" "$lower"; then
      return 0
    fi
  done
  fail "$spec_file: missing $label"
}

require_any "classification" "classification:[[:space:]]*(greenfield|brownfield|mixed)" "task classification"
require_any "owner/source" "owner/source" "owner source"
require_any "scope" "scope"
require_any "non-scope" "non-scope" "out of scope"
require_any "constraints/invariants" "constraints" "invariants"
require_any "acceptance criteria" "acceptance criteria"
require_any "rollback/removal path" "rollback" "removal path"
require_any "evidence plan" "evidence plan"
require_any "generated artifact plan" "generated artifact" "generated-surface" "generated surface"
require_any "Graphify sidecar status" "graphify"
require_any "ActiveGraph sidecar status" "activegraph"
require_any "release/provenance gate status" "release/provenance" "release gate" "provenance gate"

bad_a="generic autonomous"
bad_b="build runner"
bad_c="one paste"
bad_d="and done"
bad_e="plan and"
bad_f="ship anything"
if grep -Eq "${bad_a}[[:space:]]+${bad_b}|${bad_c}[[:space:]]+${bad_d}|${bad_e}[[:space:]]+${bad_f}" "$lower"; then
  fail "$spec_file: contains generic-runner framing"
fi

printf 'validate-audit-spec: ok %s\n' "$spec_file"
