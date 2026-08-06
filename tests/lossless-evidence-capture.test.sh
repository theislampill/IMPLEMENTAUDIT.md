#!/usr/bin/env bash
set -euo pipefail

# Lossless verification-evidence capture (#74): whole capture, producer-exit
# authority, coverage declarations, truncation downgrades, and host warnings.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

phase_validator="skills/implementaudit/scripts/validate-phase.sh"
closure_validator="skills/implementaudit/scripts/check-closure-surface.sh"
detect_env="skills/implementaudit/scripts/detect-env.sh"
source_phase="fixtures/phase-validation/valid-full-spec.md"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

pass=0
fail=0

ok() { pass=$((pass + 1)); }
not_ok() {
  printf 'lossless-evidence-capture.test: %s\n' "$*" >&2
  fail=$((fail + 1))
}

make_coverage_phase() {
  local dest="$1"
  cp "$source_phase" "$dest"
  sed -i \
    's|^- npm run build —|- npm run build > evidence/build.log 2>\&1 —|; s|^- npm test -- --testPathPattern=settings —|- npm test -- --testPathPattern=settings > evidence/settings.log 2>\&1 —|; s/; expected: exit 0 with no errors/; coverage: full; capture: evidence\/build.log; expected: exit 0 with no errors/; s/; expected: exit 0 with settings tests passing/; coverage: full; capture: evidence\/settings.log; expected: exit 0 with settings tests passing/' \
    "$dest"
}

# R1-F1: a live tail pipeline cannot register as complete verification capture.
f="$tmp/F1-piped-tail.md"
make_coverage_phase "$f"
sed -i \
  's|^- npm run build > evidence/build.log 2>\&1 —|- python fail_many.py 2>\&1 \| tail -1 —|' "$f"
out="$tmp/F1.out"
if bash "$phase_validator" "$f" >"$out" 2>&1; then
  not_ok "R1-F1 live tail pipeline expected FAIL"
elif grep -Fq 'tail -1' "$out" && grep -Fqi 'whole capture' "$out"; then
  ok
else
  not_ok "R1-F1 failure did not identify the piped command and whole-capture rule"
fi

# Paired pipeline controls: a complete tee capture is allowed only when the
# producer verdict survives through pipefail or an explicit PIPESTATUS read.
f="$tmp/piped-tail-pipefail.md"
make_coverage_phase "$f"
sed -i \
  's|^- npm run build > evidence/build.log 2>\&1 —|- set -o pipefail; python fail_many.py 2>\&1 \| tee evidence/build.log \| tail -1 —|' \
  "$f"
if bash "$phase_validator" "$f" >/dev/null 2>&1; then
  ok
else
  not_ok "complete tee capture with pipefail expected PASS"
fi

f="$tmp/piped-tail-pipestatus.md"
make_coverage_phase "$f"
sed -i \
  's|^- npm run build > evidence/build.log 2>\&1 —|- python fail_many.py 2>\&1 \| tee evidence/build.log \| tail -1; status=${PIPESTATUS[0]}; exit "$status" —|' \
  "$f"
if bash "$phase_validator" "$f" >/dev/null 2>&1; then
  ok
else
  not_ok "complete tee capture with PIPESTATUS producer authority expected PASS"
fi

f="$tmp/piped-tail-no-authority.md"
make_coverage_phase "$f"
sed -i \
  's|^- npm run build > evidence/build.log 2>\&1 —|- python fail_many.py 2>\&1 \| tee evidence/build.log \| tail -1 —|' \
  "$f"
out="$tmp/piped-tail-no-authority.out"
if bash "$phase_validator" "$f" >"$out" 2>&1; then
  not_ok "tee capture without producer exit authority expected FAIL"
elif grep -Fqi 'producer exit' "$out"; then
  ok
else
  not_ok "unsafe tee pipeline failure did not name producer exit authority"
fi

# Redirection owned by the truncating stage is not a whole producer capture.
f="$tmp/piped-tail-redirect-after-window.md"
make_coverage_phase "$f"
sed -i \
  's|^- npm run build > evidence/build.log 2>\&1 —|- set -o pipefail; python fail_many.py 2>\&1 \| tail -1 > evidence/build.log —|' \
  "$f"
out="$tmp/piped-tail-redirect-after-window.out"
if bash "$phase_validator" "$f" >"$out" 2>&1; then
  not_ok "tail-owned redirect presented as whole capture expected FAIL"
elif grep -Fqi 'before the truncating stage' "$out"; then
  ok
else
  not_ok "tail-owned redirect failure did not name capture ordering"
fi

# Enabling pipefail after the pipeline cannot restore the producer verdict.
f="$tmp/piped-tail-late-pipefail.md"
make_coverage_phase "$f"
sed -i \
  's|^- npm run build > evidence/build.log 2>\&1 —|- python fail_many.py 2>\&1 \| tee evidence/build.log \| tail -1; set -o pipefail —|' \
  "$f"
out="$tmp/piped-tail-late-pipefail.out"
if bash "$phase_validator" "$f" >"$out" 2>&1; then
  not_ok "pipefail enabled after pipeline expected FAIL"
elif grep -Fqi 'before the first pipe' "$out"; then
  ok
else
  not_ok "late-pipefail failure did not name producer-authority ordering"
fi

# R1-F2: whole-file redirection with coverage: full remains valid.
f="$tmp/F2-whole-capture.md"
make_coverage_phase "$f"
sed -i \
  's|^- npm run build > evidence/build.log 2>\&1 —|- python fail_many.py > evidence/build.log 2>\&1 —|' "$f"
if bash "$phase_validator" "$f" >/dev/null 2>&1; then
  ok
else
  not_ok "R1-F2 redirected whole capture expected PASS"
fi

# Indented Markdown continuations remain part of the mandatory-command row.
f="$tmp/wrapped-partial-coverage.md"
make_coverage_phase "$f"
sed -i -E \
  's/; coverage: full; capture: ([^;]+); expected: ([^;]+)/; expected: \2;\n  coverage: full; capture: \1/g' \
  "$f"
sed -i \
  's|^  coverage: full; capture: evidence/build.log|  coverage: partial; range: first line; omission: remaining lines; capture: evidence/build.log|' \
  "$f"
out="$tmp/wrapped-partial-coverage.out"
if bash "$phase_validator" "$f" >"$out" 2>&1; then
  not_ok "wrapped partial coverage expected FAIL"
elif grep -Fqi 'partial capture is diagnostic only' "$out"; then
  ok
else
  not_ok "wrapped coverage failure did not prove continuation parsing"
fi

# A stdout-only redirect or tee is not lossless when stderr carries failures.
f="$tmp/stdout-only-redirect.md"
make_coverage_phase "$f"
sed -i '0,/ 2>\&1 —/{s/ 2>\&1 —/ —/}' "$f"
out="$tmp/stdout-only-redirect.out"
if bash "$phase_validator" "$f" >"$out" 2>&1; then
  not_ok "stdout-only redirect presented as whole capture expected FAIL"
elif grep -Fqi 'stdout and stderr' "$out"; then
  ok
else
  not_ok "stdout-only redirect failure did not name both streams"
fi

f="$tmp/stdout-only-tee.md"
make_coverage_phase "$f"
sed -i \
  's|^- npm run build > evidence/build.log 2>\&1 —|- set -o pipefail; npm run build \| tee evidence/build.log —|' \
  "$f"
out="$tmp/stdout-only-tee.out"
if bash "$phase_validator" "$f" >"$out" 2>&1; then
  not_ok "stdout-only tee presented as whole capture expected FAIL"
elif grep -Fqi 'stdout and stderr' "$out"; then
  ok
else
  not_ok "stdout-only tee failure did not name both streams"
fi

# PowerShell-only `*>` cannot prove a cross-shell phase row is lossless.
f="$tmp/ambiguous-powershell-all-stream.md"
make_coverage_phase "$f"
sed -i \
  's|^- npm run build > evidence/build.log 2>\&1 —|- npm run build *> evidence/build.log —|' \
  "$f"
out="$tmp/ambiguous-powershell-all-stream.out"
if bash "$phase_validator" "$f" >"$out" 2>&1; then
  not_ok "shell-ambiguous PowerShell all-stream redirect expected FAIL"
elif grep -Fqi 'explicit shell context' "$out"; then
  ok
else
  not_ok "PowerShell all-stream failure did not name shell context"
fi

# A later command cannot replace the captured producer's exit verdict.
f="$tmp/chained-verdict-laundering.md"
make_coverage_phase "$f"
sed -i \
  's|^- npm run build > evidence/build.log 2>\&1 —|- false > evidence/build.log 2>\&1; true —|' \
  "$f"
out="$tmp/chained-verdict-laundering.out"
if bash "$phase_validator" "$f" >"$out" 2>&1; then
  not_ok "post-producer command laundering expected FAIL"
elif grep -Fqi 'one verification producer' "$out"; then
  ok
else
  not_ok "post-producer laundering failure did not name one-producer rule"
fi

# A decoy command cannot own the capture while the real producer is truncated.
f="$tmp/decoy-capture-owner.md"
make_coverage_phase "$f"
sed -i \
  's|^- npm run build > evidence/build.log 2>\&1 —|- set -o pipefail; true > evidence/build.log 2>\&1; python fail_many.py 2>\&1 \| tail -1 —|' \
  "$f"
out="$tmp/decoy-capture-owner.out"
if bash "$phase_validator" "$f" >"$out" 2>&1; then
  not_ok "decoy capture owner expected FAIL"
elif grep -Fqi 'one verification producer' "$out"; then
  ok
else
  not_ok "decoy-capture failure did not name one-producer rule"
fi

# Background separators cannot detach the captured producer from its verdict.
f="$tmp/background-verdict-laundering.md"
make_coverage_phase "$f"
sed -i \
  's|^- npm run build > evidence/build.log 2>\&1 —|- false > evidence/build.log 2>\&1 \& true —|' \
  "$f"
out="$tmp/background-verdict-laundering.out"
if bash "$phase_validator" "$f" >"$out" 2>&1; then
  not_ok "background producer laundering expected FAIL"
elif grep -Fqi 'one verification producer' "$out"; then
  ok
else
  not_ok "background laundering failure did not name one-producer rule"
fi

f="$tmp/background-decoy-capture.md"
make_coverage_phase "$f"
sed -i \
  's|^- npm run build > evidence/build.log 2>\&1 —|- set -o pipefail; true > evidence/build.log 2>\&1 \& python fail_many.py 2>\&1 \| tail -1 —|' \
  "$f"
out="$tmp/background-decoy-capture.out"
if bash "$phase_validator" "$f" >"$out" 2>&1; then
  not_ok "background decoy capture expected FAIL"
elif grep -Fqi 'one verification producer' "$out"; then
  ok
else
  not_ok "background decoy failure did not name one-producer rule"
fi

# A capture label without a whole-output transport is not complete evidence.
f="$tmp/full-label-without-redirect.md"
make_coverage_phase "$f"
sed -i '0,/ > evidence\/build.log 2>\&1/{s/ > evidence\/build.log 2>\&1//}' "$f"
out="$tmp/full-label-without-redirect.out"
if bash "$phase_validator" "$f" >"$out" 2>&1; then
  not_ok "coverage full without whole-output redirection expected FAIL"
elif grep -Fqi 'whole-output capture' "$out"; then
  ok
else
  not_ok "missing-redirection failure did not name whole-output capture"
fi

# R1-F3: lock the pipeline-laundering mechanism and the pipefail countermeasure.
without_pipefail="$(bash -c 'set +o pipefail; false | tail -1; printf "%s" "$?"')"
with_pipefail="$(bash -c 'set -o pipefail; false | tail -1; printf "%s" "$?"')"
if [ "$without_pipefail" = 0 ] && [ "$with_pipefail" = 1 ]; then
  ok
else
  not_ok "R1-F3 expected pipeline statuses 0 then 1, got $without_pipefail then $with_pipefail"
fi

# R1-F4: orientation tails outside Mandatory commands remain legal.
f="$tmp/F4-orientation-tail.md"
make_coverage_phase "$f"
sed -i '/^## Work/i - `tail -20 README.md` was used for orientation only.' "$f"
if bash "$phase_validator" "$f" >/dev/null 2>&1; then
  ok
else
  not_ok "R1-F4 orientation-only tail expected PASS"
fi

# R1-F5: fully coverage-untagged historical rows remain readable with warning.
f="$tmp/F5-legacy-coverage.md"
cp "$source_phase" "$f"
out="$tmp/F5.out"
if bash "$phase_validator" "$f" >"$out" 2>&1 \
    && grep -Fqi 'WARNING legacy coverage' "$out"; then
  ok
else
  not_ok "R1-F5 legacy phase expected PASS with coverage warning"
fi

# Newly authored coverage rows cannot omit the shared field or claim partial
# coverage without declaring both the observed range and the omission.
f="$tmp/new-mixed-coverage.md"
make_coverage_phase "$f"
sed -i '0,/; coverage: full; capture: evidence\/settings.log;/{s/; coverage: full; capture: evidence\/settings.log;//}' "$f"
if bash "$phase_validator" "$f" >/dev/null 2>&1; then
  not_ok "mixed coverage declarations expected FAIL"
else
  ok
fi

f="$tmp/partial-no-bounds.md"
make_coverage_phase "$f"
sed -i \
  's/; coverage: full; capture: evidence\/build.log;/; coverage: partial; capture: evidence\/build.log;/' \
  "$f"
if bash "$phase_validator" "$f" >/dev/null 2>&1; then
  not_ok "partial coverage without range and omission expected FAIL"
else
  ok
fi

# R1-F6: partial evidence cannot verify a closure claim. A disclosed partial
# diagnostic remains legal when the claim is explicitly unverified.
cat >"$tmp/F6-partial-verified.md" <<'EOF'
claim: complete-suite | surface: source | property: behavioral | status: verified | evidence-surface: source | coverage: partial | range: lines 90-100 | omission: lines 1-89
EOF
if bash "$closure_validator" "$tmp/F6-partial-verified.md" >/dev/null 2>&1; then
  not_ok "R1-F6 verified partial closure expected FAIL"
else
  ok
fi

cat >"$tmp/F6-partial-unverified.md" <<'EOF'
claim: diagnostic-window | surface: source | property: behavioral | status: unverified | coverage: partial | range: lines 90-100 | omission: lines 1-89 | residual: full verdict unavailable
EOF
if bash "$closure_validator" "$tmp/F6-partial-unverified.md" >/dev/null 2>&1; then
  ok
else
  not_ok "disclosed partial diagnostic expected PASS"
fi

# R1-F7: a transport truncation marker contradicts coverage: full.
cat >"$tmp/F7-truncated-full.md" <<'EOF'
claim: full-census | surface: source | property: structural | status: verified | evidence-surface: source | coverage: full | evidence: Warning: truncated output (original token count: 10024)
EOF
if bash "$closure_validator" "$tmp/F7-truncated-full.md" >/dev/null 2>&1; then
  not_ok "R1-F7 truncated result marked full expected FAIL"
else
  ok
fi

# Stream-reencoding hosts must disclose structured producer metadata and keep
# CLIXML text diagnostic-only.
detect_out="$(OS=Windows_NT SHELL=pwsh bash "$detect_env" 2>/dev/null)"
if grep -Fq 'warn=stream_reencoding_host' <<<"$detect_out" \
    && grep -Fq '{command, exit_code, started, finished}' <<<"$detect_out" \
    && grep -Fq 'CLIXML=diagnostics-only' <<<"$detect_out"; then
  ok
else
  not_ok "stream-reencoding host warning lacks structured producer metadata or CLIXML boundary"
fi

total=$((pass + fail))
if [ "$fail" -gt 0 ]; then
  printf 'lossless-evidence-capture.test: FAIL (%d/%d failed)\n' "$fail" "$total" >&2
  exit 1
fi

printf 'lossless-evidence-capture.test: ok (%d/%d)\n' "$pass" "$total"
