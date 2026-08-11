#!/usr/bin/env bash
set -euo pipefail

# Final-audit success-surface indexing (#14): the PROTOCOL clause + scorer
# fixtures. A closure claim closes only with evidence from the surface that
# establishes it; lower-layer evidence is never promoted.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

proto="skills/implementaudit/templates/PROTOCOL.md"
state_template="skills/implementaudit/templates/STATE.md"
scorer="skills/implementaudit/scripts/check-closure-surface.sh"
fx="fixtures/closure-surface"
fail() { printf 'closure-surface-contract: %s\n' "$*" >&2; exit 1; }

publication_identity_controls() {
  local work="$1" evidence_digest live_digest stable_file_hash drift_file_hash
  evidence_digest='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
  live_digest='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
  printf '%s\n' "$evidence_digest" > "$work/publication-stable.sha256"
  stable_file_hash="$(sha256sum "$work/publication-stable.sha256" | awk '{print $1}')"
  cat > "$work/publication-stable.md" <<EOF
claim: pub-stable | surface: publication | status: verified | evidence-surface: publication | evidence-digest: $evidence_digest
publication-identity: pub-stable | live-digest-file: publication-stable.sha256 | live-file-sha256: $stable_file_hash | live-digest: $evidence_digest | disposition: verified
EOF
  bash "$scorer" "$work/publication-stable.md" >/dev/null \
    || fail 'stable publication digest identity was rejected'

  printf '%s\n' "$live_digest" > "$work/publication-drift.sha256"
  drift_file_hash="$(sha256sum "$work/publication-drift.sha256" | awk '{print $1}')"
  cat > "$work/publication-drift-verified.md" <<EOF
claim: pub-drift | surface: publication | status: verified | evidence-surface: publication | evidence-digest: $evidence_digest
publication-identity: pub-drift | live-digest-file: publication-drift.sha256 | live-file-sha256: $drift_file_hash | live-digest: $live_digest | disposition: verified
EOF
  if bash "$scorer" "$work/publication-drift-verified.md" >/dev/null 2>&1; then
    fail 'publication digest drift remained verified instead of SUPERSEDED'
  fi

  grep -v '^publication-identity:' "$work/publication-stable.md" \
    > "$work/publication-missing-identity.md"
  if bash "$scorer" "$work/publication-missing-identity.md" >/dev/null 2>&1; then
    fail 'verified publication claim without a current-digest identity row was accepted'
  fi

  sed -e 's/status: verified/status: unverified/' \
      -e 's/disposition: verified/disposition: SUPERSEDED/' \
      "$work/publication-drift-verified.md" > "$work/publication-drift-superseded.md"
  bash "$scorer" "$work/publication-drift-superseded.md" >/dev/null \
    || fail 'publication digest drift with explicit SUPERSEDED disposition was rejected'

  sed "s/live-file-sha256: $drift_file_hash/live-file-sha256: $evidence_digest/" \
    "$work/publication-drift-superseded.md" > "$work/publication-drift-unbound.md"
  if bash "$scorer" "$work/publication-drift-unbound.md" >/dev/null 2>&1; then
    fail 'caller-supplied live digest was accepted without binding the live digest file'
  fi

  sed "s/live-digest: $live_digest/live-digest: $evidence_digest/" \
    "$work/publication-drift-superseded.md" > "$work/publication-live-field-mismatch.md"
  if bash "$scorer" "$work/publication-live-field-mismatch.md" >/dev/null 2>&1; then
    fail 'live digest field was accepted when it contradicted the bound file'
  fi
}

external_composition_controls() {
  local root="$1" work="$1/records" operator="$1/operator" output failures=0
  local grant_sha wrong_grant_sha digest_file_sha public_sha qualification_sha
  local qualified_commit qualified_tree asset_size asset_digest fake_commit fake_tree
  local release_url asset_url download_url case_sha trusted_path

  mkdir -p "$work" "$operator/bin" "$operator/source"

  expect_composed_fail() {
    local file="$1" expected="$2" false_green="$3"
    if output="$(bash "$scorer" "$file" 2>&1)"; then
      printf 'closure-surface-contract: %s\n' "$false_green" >&2
      failures=$((failures + 1))
    elif ! printf '%s\n' "$output" | grep -Fxq "$expected"; then
      printf 'closure-surface-contract: %s wrong diagnostic; expected %s; got %s\n' \
        "$(basename "$file")" "$expected" "${output//$'\n'/ }" >&2
      failures=$((failures + 1))
    fi
  }

  cp "$fx/external-close-readback-PASS.json" "$work/external-close-readback-PASS.json"
  cp "$fx/external-close-authorization.txt" "$work/external-close-authorization.txt"
  sed "s/mutation-command: gh issue close 207/mutation-command: gh issue close 208 --comment 'issue 207'/" \
    "$fx/external-close-readback-PASS.md" > "$work/misleading-comment-target.md"
  expect_composed_fail "$work/misleading-comment-target.md" \
    "check-closure-surface: external mutation close-207: mutation-command effective target issue '208' does not match declared issue '207'" \
    'misleading comment token satisfied the declared mutation target'

  sed \
    -e '1 s/ | external-authorization-grant: grant-close-207//' \
    -e '/^external-authorization-grant:/d' \
    "$fx/external-close-readback-PASS.md" > "$work/missing-authorization.md"
  expect_composed_fail "$work/missing-authorization.md" \
    'check-closure-surface: claim close-207: external mutation requires external-authorization-grant' \
    'verified external mutation passed without a bound authorization grant'

  grant_sha="$(sha256sum "$work/external-close-authorization.txt" | awk '{print $1}')"
  cp "$fx/external-close-readback-PASS.md" "$work/composed-close-PASS.md"
  if ! output="$(bash "$scorer" "$work/composed-close-PASS.md" 2>&1)"; then
    printf 'closure-surface-contract: composed external mutation expected PASS; got %s\n' \
      "${output//$'\n'/ }" >&2
    failures=$((failures + 1))
  fi

  sed 's/target_id: 207/target_id: 208/' \
    "$work/external-close-authorization.txt" > "$work/wrong-target-authorization.txt"
  wrong_grant_sha="$(sha256sum "$work/wrong-target-authorization.txt" | awk '{print $1}')"
  sed \
    -e 's/grant-close-207/grant-wrong-target/g' \
    -e 's/external-close-authorization.txt/wrong-target-authorization.txt/' \
    -e "s/$grant_sha/$wrong_grant_sha/" \
    "$work/composed-close-PASS.md" > "$work/wrong-grant-target.md"
  expect_composed_fail "$work/wrong-grant-target.md" \
    "check-closure-surface: authorization grant grant-wrong-target: target_id '208' does not bind mutation target '207'" \
    'authorization for a different target satisfied the external mutation'

  printf '%s\n' 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
    > "$work/hosted-local-only.sha256"
  digest_file_sha="$(sha256sum "$work/hosted-local-only.sha256" | awk '{print $1}')"
  cat > "$work/hosted-local-only.md" <<EOF
claim: hosted-local-only | surface: publication | publication-kind: hosted-release-asset | status: verified | evidence-surface: publication | evidence-digest: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
publication-identity: hosted-local-only | live-digest-file: hosted-local-only.sha256 | live-file-sha256: $digest_file_sha | live-digest: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa | disposition: verified
EOF
  expect_composed_fail "$work/hosted-local-only.md" \
    'check-closure-surface: claim hosted-local-only: hosted release asset requires release/tag/asset/qualification/public-readback identity' \
    'hosted release asset passed on a local digest file alone'

  mkdir "$work/qualified-repository"
  git -C "$work/qualified-repository" init -q
  printf '%s\n' 'qualified source tree' > "$work/qualified-repository/source.txt"
  git -C "$work/qualified-repository" add source.txt
  git -C "$work/qualified-repository" -c user.name=Fixture \
    -c user.email=fixture@example.invalid commit -q -m fixture
  qualified_commit="$(git -C "$work/qualified-repository" rev-parse HEAD)"
  qualified_tree="$(git -C "$work/qualified-repository" rev-parse 'HEAD^{tree}')"
  printf '%s' 'qualified release asset bytes' > "$work/qualified-package.skill"
  asset_size="$(wc -c < "$work/qualified-package.skill" | tr -d ' ')"
  asset_digest="$(sha256sum "$work/qualified-package.skill" | awk '{print $1}')"
  release_url='https://api.github.com/repos/acme/example/releases/R_test'
  asset_url='https://api.github.com/repos/acme/example/releases/assets/A_test'
  download_url='https://github.com/acme/example/releases/download/v9.9.9/IMPLEMENTAUDIT.skill'
  printf '%s\n' \
    "{\"release_id\":\"R_test\",\"tag\":\"v9.9.9\",\"asset_id\":\"A_test\",\"asset_name\":\"IMPLEMENTAUDIT.skill\",\"asset_size\":$asset_size,\"asset_digest\":\"$asset_digest\",\"qualified_commit\":\"$qualified_commit\",\"qualified_tree\":\"$qualified_tree\",\"release_url\":\"$release_url\",\"asset_url\":\"$asset_url\",\"download_url\":\"$download_url\"}" \
    > "$operator/source/release.json"
  printf '%s' 'qualified release asset bytes' > "$operator/source/asset.skill"
  public_sha="$(sha256sum "$operator/source/release.json" | awk '{print $1}')"

  # The authority-controlled transport lives outside the evaluated record
  # tree. The checker selects it once, resolves it, and invokes fixed argv.
  cat > "$operator/bin/curl" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
url="${*: -1}"
printf '%s\n' "$url" >> "$CAPTURE_LOG"
if [[ "$url" == https://api.github.com/repos/acme/example/releases/* ]]; then
  cat "$CAPTURE_RELEASE_SOURCE"
elif [[ "$url" == https://github.com/acme/example/releases/download/*/IMPLEMENTAUDIT.skill ]]; then
  case "${CAPTURE_ASSET_MODE:-good}" in
    good) cat "$CAPTURE_ASSET_SOURCE" ;;
    wrong) printf '%s' 'unrelated copied bytes' ;;
    missing) exit 22 ;;
  esac
else
  exit 22
fi
EOF
  chmod +x "$operator/bin/curl"
  export PATH="$operator/bin:$PATH"
  trusted_path="$PATH"
  export CAPTURE_LOG="$operator/capture.log"
  export CAPTURE_RELEASE_SOURCE="$operator/source/release.json"
  export CAPTURE_ASSET_SOURCE="$operator/source/asset.skill"

  printf '%s\n' \
    "{\"qualified_commit\":\"$qualified_commit\",\"qualified_tree\":\"$qualified_tree\",\"package_name\":\"IMPLEMENTAUDIT.skill\",\"package_size\":$asset_size,\"package_digest\":\"$asset_digest\"}" \
    > "$work/qualification.json"
  qualification_sha="$(sha256sum "$work/qualification.json" | awk '{print $1}')"

  # This is the former false pass: caller-authored JSON plus copied local
  # bytes, even with real Git objects, must not satisfy public capture.
  cp "$operator/source/release.json" "$work/preauthored-readback.json"
  cp "$work/qualified-package.skill" "$work/copied-asset.skill"
  cat > "$work/preauthored-copied.md" <<EOF
claim: hosted-release | surface: publication | publication-kind: hosted-release-asset | status: verified | evidence-surface: publication | evidence-digest: $asset_digest
publication-identity: hosted-release | publication-kind: hosted-release-asset | release-id: R_test | tag: v9.9.9 | asset-id: A_test | asset-name: IMPLEMENTAUDIT.skill | asset-size: $asset_size | asset-digest: $asset_digest | qualified-repository: qualified-repository | qualified-commit: $qualified_commit | qualified-tree: $qualified_tree | qualified-package-file: qualified-package.skill | release-url: $release_url | asset-url: $asset_url | download-url: $download_url | public-readback-file: preauthored-readback.json | public-readback-sha256: $public_sha | downloaded-asset-file: copied-asset.skill | disposition: verified
EOF
  expect_composed_fail "$work/preauthored-copied.md" \
    'check-closure-surface: claim hosted-release: hosted release asset requires checker-captured public evidence and a qualification record' \
    'pre-authored JSON and copied local bytes satisfied public evidence'

  cat > "$work/hosted-release-PASS.md" <<EOF
claim: hosted-release | surface: publication | publication-kind: hosted-release-asset | status: verified | evidence-surface: publication | evidence-digest: $asset_digest
publication-identity: hosted-release | publication-kind: hosted-release-asset | release-id: R_test | tag: v9.9.9 | asset-id: A_test | asset-name: IMPLEMENTAUDIT.skill | asset-size: $asset_size | asset-digest: $asset_digest | qualified-repository: qualified-repository | qualified-commit: $qualified_commit | qualified-tree: $qualified_tree | qualified-package-file: qualified-package.skill | qualification-record-file: qualification.json | qualification-record-sha256: $qualification_sha | release-url: $release_url | asset-url: $asset_url | download-url: $download_url | public-readback-sha256: $public_sha | disposition: verified
EOF
  if ! output="$(bash "$scorer" "$work/hosted-release-PASS.md" 2>&1)"; then
    printf 'closure-surface-contract: hosted release identity expected PASS; got %s\n' \
      "${output//$'\n'/ }" >&2
    failures=$((failures + 1))
  fi

  mkdir "$work/candidate-bin"
  cp "$operator/bin/curl" "$work/candidate-bin/curl"
  chmod +x "$work/candidate-bin/curl"
  PATH="$work/candidate-bin:$trusted_path"
  expect_composed_fail "$work/hosted-release-PASS.md" \
    'check-closure-surface: claim hosted-release: public capture transport must be outside the evaluated record tree' \
    'candidate-controlled PATH transport satisfied public capture'
  PATH="$trusted_path"

  sed 's/{"release_id":"R_test"/{"release_id":"R_other","release_id":"R_test"/' \
    "$operator/source/release.json" > "$operator/source/duplicate-release.json"
  case_sha="$(sha256sum "$operator/source/duplicate-release.json" | awk '{print $1}')"
  sed "s/public-readback-sha256: $public_sha/public-readback-sha256: $case_sha/" \
    "$work/hosted-release-PASS.md" > "$work/hosted-duplicate-readback.md"
  CAPTURE_RELEASE_SOURCE="$operator/source/duplicate-release.json"
  expect_composed_fail "$work/hosted-duplicate-readback.md" \
    'check-closure-surface: claim hosted-release: public readback is not valid unique-key UTF-8 JSON' \
    'duplicate-key public JSON satisfied captured readback'
  CAPTURE_RELEASE_SOURCE="$operator/source/release.json"

  sed -e 's/asset-id: A_test/asset-id: A_other/' \
    -e 's|/assets/A_test|/assets/A_other|' \
    "$work/hosted-release-PASS.md" > "$work/hosted-asset-id-mismatch.md"
  expect_composed_fail "$work/hosted-asset-id-mismatch.md" \
    "check-closure-surface: claim hosted-release: public readback asset_id 'A_test' does not match identity 'A_other'" \
    'hosted release identity accepted a different public asset ID'

  fake_commit='1111111111111111111111111111111111111111'
  sed "s/qualified-commit: $qualified_commit/qualified-commit: $fake_commit/" \
    "$work/hosted-release-PASS.md" > "$work/hosted-missing-commit.md"
  expect_composed_fail "$work/hosted-missing-commit.md" \
    "check-closure-surface: claim hosted-release: qualified commit '$fake_commit' does not resolve in qualified repository" \
    'nonexistent qualified commit was accepted'

  fake_tree='2222222222222222222222222222222222222222'
  sed "s/qualified-tree: $qualified_tree/qualified-tree: $fake_tree/" \
    "$work/hosted-release-PASS.md" > "$work/hosted-wrong-tree.md"
  expect_composed_fail "$work/hosted-wrong-tree.md" \
    "check-closure-surface: claim hosted-release: qualified tree '$fake_tree' does not match commit tree '$qualified_tree'" \
    'wrong qualified tree was accepted'

  cp "$work/hosted-release-PASS.md" "$work/hosted-missing-download.md"
  export CAPTURE_ASSET_MODE=missing
  expect_composed_fail "$work/hosted-missing-download.md" \
    'check-closure-surface: claim hosted-release: public asset capture failed' \
    'hosted release passed without a downloaded asset'
  unset CAPTURE_ASSET_MODE

  cp "$work/hosted-release-PASS.md" "$work/hosted-wrong-bytes.md"
  export CAPTURE_ASSET_MODE=wrong
  expect_composed_fail "$work/hosted-wrong-bytes.md" \
    'check-closure-surface: claim hosted-release: captured public asset bytes do not match qualified package' \
    'wrong downloaded asset bytes were accepted'
  unset CAPTURE_ASSET_MODE

  sed "s/asset-size: $asset_size/asset-size: 999/" \
    "$work/hosted-release-PASS.md" > "$work/hosted-wrong-size.md"
  expect_composed_fail "$work/hosted-wrong-size.md" \
    "check-closure-surface: claim hosted-release: asset-size '999' does not match measured size '$asset_size'" \
    'wrong hosted asset size was accepted'

  sed "s/asset-digest: $asset_digest/asset-digest: aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa/g" \
    "$work/hosted-release-PASS.md" > "$work/hosted-wrong-digest.md"
  expect_composed_fail "$work/hosted-wrong-digest.md" \
    "check-closure-surface: claim hosted-release: asset-digest does not match measured digest '$asset_digest'" \
    'wrong hosted asset digest was accepted'

  sed -e "s|release-url: $release_url|release-url: https://example.invalid/releases/R_test|" \
    "$work/hosted-release-PASS.md" > "$work/hosted-wrong-url.md"
  expect_composed_fail "$work/hosted-wrong-url.md" \
    'check-closure-surface: claim hosted-release: release-url does not bind repository and release-id' \
    'wrong hosted release URL was accepted'

  sed -e 's/release-id: R_test/release-id: R_other/' \
    -e 's|/releases/R_test|/releases/R_other|' \
    "$work/hosted-release-PASS.md" > "$work/hosted-release-id-mismatch.md"
  expect_composed_fail "$work/hosted-release-id-mismatch.md" \
    "check-closure-surface: claim hosted-release: public readback release_id 'R_test' does not match identity 'R_other'" \
    'wrong hosted release ID was accepted'

  sed -e 's/tag: v9.9.9/tag: v9.9.8/' \
    -e 's|/download/v9.9.9/|/download/v9.9.8/|' \
    "$work/hosted-release-PASS.md" > "$work/hosted-tag-mismatch.md"
  expect_composed_fail "$work/hosted-tag-mismatch.md" \
    "check-closure-surface: claim hosted-release: public readback tag 'v9.9.9' does not match identity 'v9.9.8'" \
    'wrong hosted tag was accepted'

  sed "s/\"package_digest\":\"$asset_digest\"/\"package_digest\":\"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa\"/" \
    "$work/qualification.json" > "$work/unbound-qualification.json"
  case_sha="$(sha256sum "$work/unbound-qualification.json" | awk '{print $1}')"
  sed -e 's/qualification-record-file: qualification.json/qualification-record-file: unbound-qualification.json/' \
    -e "s/qualification-record-sha256: $qualification_sha/qualification-record-sha256: $case_sha/" \
    "$work/hosted-release-PASS.md" > "$work/hosted-unbound-qualification.md"
  expect_composed_fail "$work/hosted-unbound-qualification.md" \
    'check-closure-surface: claim hosted-release: qualification record does not bind commit/tree/package identity' \
    'unbound qualification record satisfied hosted publication'

  [ "$failures" -eq 0 ] || fail "$failures external composition control(s) failed"
}

if [ "${1:-}" = "--publication-identity-only" ]; then
  focused_tmp="$(mktemp -d)"
  trap 'rm -rf "$focused_tmp"' EXIT
  publication_identity_controls "$focused_tmp"
  printf 'closure-surface-contract: publication-identity-only ok\n'
  exit 0
fi

if [ "${1:-}" = "--external-composition-only" ]; then
  focused_tmp="$(mktemp -d)"
  trap 'rm -rf "$focused_tmp"' EXIT
  external_composition_controls "$focused_tmp"
  publication_identity_controls "$focused_tmp"
  printf 'closure-surface-contract: external-composition-only ok\n'
  exit 0
fi

flat="$(tr '\n' ' ' < "$proto" | tr -s ' ')"
state_flat="$(tr '\n' ' ' < "$state_template" | tr -s ' ')"
repo_state_flat="$(tr '\n' ' ' < skills/implementaudit/references/repo-state-comparison.md | tr -s ' ')"
printf '%s' "$flat" | grep -qi 'Closure-claims table' \
  || fail "PROTOCOL missing closure-claims table"
printf '%s' "$flat" | grep -qi 'never promoted into a higher-surface claim' \
  || fail "layer-promotion prohibition missing"
printf '%s' "$flat" | grep -qi 'NEVER trigger an unauthorized network or deployment check' \
  || fail "unauthorized-inspection prohibition missing"
printf '%s' "$flat" | grep -qi 'closure gate .*not defect prevention' \
  || fail "honest-framing (closure gate not prevention) missing"

# Cross-run residual routing (#140). First occurrence remains cheap; a second
# independent ledger occurrence needs a durable tracker or owner refusal.
printf '%s' "$flat" | grep -qi 'second independent run' \
  || fail "PROTOCOL missing cross-run residual routing rule"
printf '%s' "$state_flat" | grep -qi 'durable tracker' \
  || fail "STATE missing cross-run residual owner guidance"
bash "$scorer" --residual-routing "$fx/residual-first.md" >/dev/null 2>&1 \
  || fail "first residual occurrence must remain legal without tracker ceremony"
if bash "$scorer" --residual-routing "$fx/residual-repeat-a.md" \
    "$fx/residual-repeat-b.md" >/dev/null 2>&1; then
  fail "repeated repo residual without durable owner was accepted"
fi
bash "$scorer" --residual-routing "$fx/residual-repeat-a.md" \
  "$fx/residual-routed-b.md" >/dev/null 2>&1 \
  || fail "repeated residual with issue tracker was rejected"
bash "$scorer" --residual-routing "$fx/residual-repeat-a.md" \
  "$fx/residual-refused-b.md" >/dev/null 2>&1 \
  || fail "repeated residual with explicit owner refusal was rejected"

# #138 automatic-effect closure. A push with no matching workflow pays only
# the trigger read; a matching Pages workflow binds direct effects and
# pushed-SHA readbacks before a no-deployment claim can survive.
effect_fx="fixtures/effect-closure"
bash "$scorer" --automatic-effects "$effect_fx/no-match" push main \
  "$effect_fx/no-match/plan.md" >/dev/null 2>&1 \
  || fail "push with no matching workflow gained extra ceremony"
if effect_error="$(bash "$scorer" --automatic-effects "$effect_fx/pages" \
    push main "$effect_fx/pages/plan-missing.md" 2>&1)"; then
  fail "push-triggered Pages effect without enumeration/readback was accepted"
fi
printf '%s\n' "$effect_error" | grep -Fq \
  'automatic-effect-preflight record missing for matching workflow effects' \
  || fail "missing Pages effect failed on the wrong predicate"
bash "$scorer" --automatic-effects "$effect_fx/pages" push main \
  "$effect_fx/pages/plan-covered.md" >/dev/null 2>&1 \
  || fail "enumerated Pages workflow/deployment effects were rejected"
effect_tmp="$(mktemp -d)"
sed 's/deployments@pushed-sha,//' "$effect_fx/pages/plan-covered.md" \
  > "$effect_tmp/readback-missing.md"
if effect_error="$(bash "$scorer" --automatic-effects "$effect_fx/pages" \
    push main "$effect_tmp/readback-missing.md" 2>&1)"; then
  fail "Pages effect without deployment readback was accepted"
fi
printf '%s\n' "$effect_error" | grep -Fq \
  'automatic-effect-preflight readback mismatch' \
  || fail "missing deployment readback failed on the wrong predicate"
sed 's/excluded-outcomes: none/excluded-outcomes: no deployment/' \
  "$effect_fx/pages/plan-covered.md" > "$effect_tmp/deployment-excluded.md"
if effect_error="$(bash "$scorer" --automatic-effects "$effect_fx/pages" \
    push main "$effect_tmp/deployment-excluded.md" 2>&1)"; then
  fail "configured Pages effect was accepted as an excluded outcome"
fi
printf '%s\n' "$effect_error" | grep -Fq \
  'automatic-effect-preflight excludes a configured deployment effect' \
  || fail "configured deployment exclusion failed on the wrong predicate"

mkdir -p "$effect_tmp/quoted/.github/workflows"
cat > "$effect_tmp/quoted/.github/workflows/quoted.yml" <<'EOF'
"on":
  "push":
    "branches": [main]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - run: echo check
EOF
printf '%s\n' \
  'automatic-effect-preflight: event: push | ref: main | workflows: .github/workflows/quoted.yml | effects: workflow-run:.github/workflows/quoted.yml | post-state-readback: workflow-runs@pushed-sha | excluded-outcomes: none' \
  > "$effect_tmp/quoted/plan.md"
bash "$scorer" --automatic-effects "$effect_tmp/quoted" push main \
  "$effect_tmp/quoted/plan.md" >/dev/null 2>&1 \
  || fail "quoted push/branches keys were not parsed structurally"

for scalar_case in alias tag folded; do
  mkdir -p "$effect_tmp/branch-$scalar_case/.github/workflows"
  cp "$effect_fx/no-match/plan.md" "$effect_tmp/branch-$scalar_case/plan.md"
done
cat > "$effect_tmp/branch-alias/.github/workflows/alias.yml" <<'EOF'
x-target: &target main
on:
  push:
    branches: [*target]
jobs:
  check:
    runs-on: ubuntu-latest
EOF
cat > "$effect_tmp/branch-tag/.github/workflows/tag.yml" <<'EOF'
on:
  push:
    branches:
      - !!str main
jobs:
  check:
    runs-on: ubuntu-latest
EOF
cat > "$effect_tmp/branch-folded/.github/workflows/folded.yml" <<'EOF'
on:
  push:
    branches:
      - >
        main
jobs:
  check:
    runs-on: ubuntu-latest
EOF
for scalar_case in alias tag folded; do
  if effect_error="$(bash "$scorer" --automatic-effects \
      "$effect_tmp/branch-$scalar_case" push main \
      "$effect_tmp/branch-$scalar_case/plan.md" 2>&1)"; then
    fail "unsupported $scalar_case branch-filter scalar was treated as no matching workflow"
  fi
  printf '%s\n' "$effect_error" | grep -Fq \
    'unsupported aliased/tagged/block branch-filter scalar' \
    || fail "unsupported $scalar_case branch-filter scalar failed on the wrong predicate"
done

mkdir -p "$effect_tmp/malformed/.github/workflows"
cat > "$effect_tmp/malformed/.github/workflows/malformed.yml" <<'EOF'
on:
  push
jobs:
  check:
    runs-on: ubuntu-latest
EOF
cp "$effect_fx/no-match/plan.md" "$effect_tmp/malformed/plan.md"
if bash "$scorer" --automatic-effects "$effect_tmp/malformed" push main \
    "$effect_tmp/malformed/plan.md" >/dev/null 2>&1; then
  fail "malformed push trigger was treated as no matching workflow"
fi

mkdir -p "$effect_tmp/nested/.github/workflows"
cat > "$effect_tmp/nested/.github/workflows/nested.yml" <<'EOF'
on:
  workflow_call:
    inputs:
      push:
        type: string
jobs:
  check:
    runs-on: ubuntu-latest
EOF
cp "$effect_fx/no-match/plan.md" "$effect_tmp/nested/plan.md"
bash "$scorer" --automatic-effects "$effect_tmp/nested" push main \
  "$effect_tmp/nested/plan.md" >/dev/null 2>&1 \
  || fail "nested workflow_call input was mistaken for top-level push"

mkdir -p "$effect_tmp/tags/.github/workflows"
cat > "$effect_tmp/tags/.github/workflows/tags.yml" <<'EOF'
on:
  push:
    tags:
      - 'v*'
jobs:
  check:
    runs-on: ubuntu-latest
EOF
cp "$effect_fx/no-match/plan.md" "$effect_tmp/tags/plan.md"
bash "$scorer" --automatic-effects "$effect_tmp/tags" push main \
  "$effect_tmp/tags/plan.md" >/dev/null 2>&1 \
  || fail "tag-only workflow was mistaken for a branch push match"

mkdir -p "$effect_tmp/quoted-uses/.github/workflows"
cat > "$effect_tmp/quoted-uses/.github/workflows/pages.yml" <<'EOF'
on: push
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - "uses": "actions/deploy-pages@v4"
EOF
printf '%s\n' \
  'automatic-effect-preflight: event: push | ref: main | workflows: .github/workflows/pages.yml | effects: deployment:github-pages,workflow-run:.github/workflows/pages.yml | post-state-readback: deployments@pushed-sha,workflow-runs@pushed-sha | excluded-outcomes: none' \
  > "$effect_tmp/quoted-uses/plan.md"
bash "$scorer" --automatic-effects "$effect_tmp/quoted-uses" push main \
  "$effect_tmp/quoted-uses/plan.md" >/dev/null 2>&1 \
  || fail "quoted structural uses key missed Pages deployment"

mkdir -p "$effect_tmp/run-text/.github/workflows"
cat > "$effect_tmp/run-text/.github/workflows/run-text.yml" <<'EOF'
on: push
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - run: 'echo "uses: actions/deploy-pages@v4"'
EOF
printf '%s\n' \
  'automatic-effect-preflight: event: push | ref: main | workflows: .github/workflows/run-text.yml | effects: workflow-run:.github/workflows/run-text.yml | post-state-readback: workflow-runs@pushed-sha | excluded-outcomes: none' \
  > "$effect_tmp/run-text/plan.md"
bash "$scorer" --automatic-effects "$effect_tmp/run-text" push main \
  "$effect_tmp/run-text/plan.md" >/dev/null 2>&1 \
  || fail "run text was mistaken for structural deploy-pages uses"

mkdir -p "$effect_tmp/alias-uses/.github/workflows"
cat > "$effect_tmp/alias-uses/.github/workflows/alias.yml" <<'EOF'
on: push
x-deploy: &deploy actions/deploy-pages@v4
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: *deploy
EOF
printf '%s\n' \
  'automatic-effect-preflight: event: push | ref: main | workflows: .github/workflows/alias.yml | effects: workflow-run:.github/workflows/alias.yml | post-state-readback: workflow-runs@pushed-sha | excluded-outcomes: none' \
  > "$effect_tmp/alias-uses/plan.md"
if effect_error="$(bash "$scorer" --automatic-effects "$effect_tmp/alias-uses" \
    push main "$effect_tmp/alias-uses/plan.md" 2>&1)"; then
  fail "aliased deploy-pages uses bypassed deployment/readback closure"
fi
printf '%s\n' "$effect_error" | grep -Fq \
  'unsupported aliased/tagged/block uses scalar' \
  || fail "aliased uses failed on the wrong predicate"

sed 's/excluded-outcomes: none/excluded-outcomes: no workflow run/' \
  "$effect_fx/pages/plan-covered.md" > "$effect_tmp/workflow-run-excluded.md"
if bash "$scorer" --automatic-effects "$effect_fx/pages" push main \
    "$effect_tmp/workflow-run-excluded.md" >/dev/null 2>&1; then
  fail "configured workflow run was accepted as an excluded outcome"
fi
sed 's/excluded-outcomes: none/excluded-outcomes:/' \
  "$effect_fx/pages/plan-covered.md" > "$effect_tmp/excluded-empty.md"
if bash "$scorer" --automatic-effects "$effect_fx/pages" push main \
    "$effect_tmp/excluded-empty.md" >/dev/null 2>&1; then
  fail "empty excluded-outcomes value was accepted"
fi

mkdir -p "$effect_tmp/dangling/.github/workflows"
cp "$effect_fx/no-match/plan.md" "$effect_tmp/dangling/plan.md"
if ln -s "$effect_tmp/missing-workflow.yml" \
    "$effect_tmp/dangling/.github/workflows/dangling.yml" 2>/dev/null; then
  if bash "$scorer" --automatic-effects "$effect_tmp/dangling" push main \
      "$effect_tmp/dangling/plan.md" >/dev/null 2>&1; then
    fail "dangling workflow symlink was silently skipped"
  fi
fi

mkdir -p "$effect_tmp/symlink-root/.github" "$effect_tmp/outside-workflows"
cp "$effect_fx/pages/.github/workflows/pages.yml" \
  "$effect_tmp/outside-workflows/pages.yml"
cp "$effect_fx/no-match/plan.md" "$effect_tmp/symlink-root/plan.md"
if ln -s "$effect_tmp/outside-workflows" \
    "$effect_tmp/symlink-root/.github/workflows" 2>/dev/null; then
  if bash "$scorer" --automatic-effects "$effect_tmp/symlink-root" push main \
      "$effect_tmp/symlink-root/plan.md" >/dev/null 2>&1; then
    fail "symlinked workflows directory escaped the repository"
  fi
fi
rm -rf "$effect_tmp"
printf '%s' "$flat" | grep -Fq 'automatic-effect-preflight:' \
  || fail "PROTOCOL missing automatic-effect mutation-plan carrier"
printf '%s' "$flat" | grep -Fq 'adds no further ceremony' \
  || fail "PROTOCOL missing no-workflow cheap path"
printf '%s' "$repo_state_flat" | grep -Fq 'workflow-runs@pushed-sha' \
  || fail "repo-state owner missing workflow-run readback"
printf '%s' "$repo_state_flat" | grep -Fq 'coverage, not a second grant of authority' \
  || fail "repo-state owner incorrectly requires second authorization"

# The owner surfaces carry one vocabulary; the fixtures below then exercise
# that vocabulary through the checker instead of treating prose presence as
# sufficient evidence.
schema_owners=(
  skills/implementaudit/references/repo-state-comparison.md
  skills/implementaudit/templates/final-report.md
  skills/implementaudit/templates/STATE.md
  skills/implementaudit/templates/PROTOCOL.md
  skills/implementaudit/templates/phase-goal.txt
)
for owner in "${schema_owners[@]}"; do
  for token in external-kind external-mutation-record artifact-identity collision-receipt external-evidence; do
    grep -Fq "$token" "$owner" || fail "$owner missing canonical #88 token: $token"
  done
done
for owner in \
  skills/implementaudit/references/repo-state-comparison.md \
  skills/implementaudit/templates/final-report.md \
  skills/implementaudit/templates/PROTOCOL.md \
  skills/implementaudit/templates/phase-goal.txt; do
  for token in readback-sha256 readback-field expected-value observed-value; do
    grep -Fq "$token" "$owner" || fail "$owner missing canonical mutation field: $token"
  done
done
for owner in \
  skills/implementaudit/references/repo-state-comparison.md \
  skills/implementaudit/templates/final-report.md \
  skills/implementaudit/templates/STATE.md \
  skills/implementaudit/templates/PROTOCOL.md; do
  grep -Fq 'closure-mtime' "$owner" || fail "$owner missing canonical liveness field: closure-mtime"
done
for owner in \
  skills/implementaudit/references/repo-state-comparison.md \
  skills/implementaudit/templates/final-report.md \
  skills/implementaudit/templates/PROTOCOL.md; do
  grep -Fq 'Evidence anchor: claim:<Claim-ID>' "$owner" \
    || fail "$owner missing canonical proposed-message claim anchor"
done

pass_case() { bash "$scorer" "$fx/$1" >/dev/null 2>&1 || fail "$1 expected PASS"; }
fail_case() { if bash "$scorer" "$fx/$1" >/dev/null 2>&1; then fail "$1 expected FAIL"; fi; }

expect_pass() {
  local file="$1" output
  if ! output="$(bash "$scorer" "$file" 2>&1)"; then
    fail "$(basename "$file") expected PASS; got: ${output//$'\n'/ }"
  fi
}

expect_fail_diag() {
  local file="$1" expected="$2" false_green="$3" output
  if output="$(bash "$scorer" "$file" 2>&1)"; then
    fail "$(basename "$file") expected FAIL: $false_green"
  fi
  printf '%s\n' "$output" | grep -Fxq "$expected" \
    || fail "$(basename "$file") wrong diagnostic; expected '$expected'; got '${output//$'\n'/ }'"
}

write_external_grant() {
  local file="$1" action="$2" target_kind="$3" target_id="$4"
  cat > "$file" <<EOF
source: owner-message:test-$action-$target_kind-$target_id
issued_at: 2026-08-11
grant_quote: Authorize $action on $target_kind $target_id with independent readback.
scope: $target_kind-$target_id
lifecycle: standing-authorization
action: $action
binds: target_kind,target_id
target_kind: $target_kind
target_id: $target_id
EOF
  sha256sum "$file" | awk '{print $1}'
}

fail_case layer-promotion-FAIL.md
fail_case verified-no-evidence-FAIL.md
pass_case uninspectable-unverified-PASS.md
pass_case source-only-PASS.md
pass_case installed-verified-PASS.md
fail_case quota-reported-reset-only-FAIL.md
fail_case quota-advisory-blocked-FAIL.md
pass_case quota-advisory-resume-PASS.md
pass_case quota-genuine-blocked-PASS.md

# #88 external-state identity and freshness. These records exercise the real
# checker with static witnesses. Diagnostics are contractual so a malformed
# row cannot be mistaken for a different rejection path.
required_fixtures=(
  external-close-unverified-FAIL.md
  external-close-readback-PASS.md
  external-close-wrong-state-FAIL.md
  external-close-readback-PASS.json
  external-close-wrong-state-FAIL.json
  external-close-authorization.txt
  mutation-python-no-zero-FAIL.md
  mutation-python-zero-PASS.md
  mutation-bash-unrelated-status-FAIL.md
  mutation-bash-zero-PASS.md
  mutation-powershell-unrelated-status-FAIL.md
  mutation-powershell-zero-PASS.md
  mutation-record-near-miss-FAIL.md
  mutation-record-duplicate-id-FAIL.md
  name-collision-ledger-FAIL.md
  name-collision-exact-receipt-PASS.md
  name-collision-extra-hash-FAIL.md
  name-collision-missing-hash-FAIL.md
  external-evidence-invalid-mtime-FAIL.md
  stale-snapshot-terminal-FAIL.md
  snapshot-orientation-only-PASS.md
  terminal-restat-matches-PASS.md
)
for fixture in "${required_fixtures[@]}"; do
  [ -f "$fx/$fixture" ] || fail "required #88 fixture missing: $fixture"
done
for fixture in \
  negative-commit-message-unanchored-count.md \
  commit-message-descriptive-PASS.md \
  negative-proposed-block-omitted-anchor.md; do
  [ -f "fixtures/claim-boundaries/$fixture" ] \
    || fail "required #88 fixture missing: claim-boundaries/$fixture"
done

expect_fail_diag "$fx/external-close-unverified-FAIL.md" \
  'check-closure-surface: external mutation close-207: missing readback-command' \
  'verified external mutation accepted without a readback witness'
expect_pass "$fx/external-close-readback-PASS.md"
expect_fail_diag "$fx/external-close-wrong-state-FAIL.md" \
  "check-closure-surface: external mutation close-207: parsed readback field 'state' value 'OPEN' does not match observed 'CLOSED'" \
  'successful query accepted with the wrong observed postcondition'

expect_fail_diag "$fx/mutation-python-no-zero-FAIL.md" \
  'check-closure-surface: external mutation python-close: missing mutation-exit' \
  'Python illustrative returncode check satisfied the machine record'
expect_pass "$fx/mutation-python-zero-PASS.md"
expect_fail_diag "$fx/mutation-bash-unrelated-status-FAIL.md" \
  'check-closure-surface: external mutation bash-close: missing mutation-exit' \
  'unrelated Bash status satisfied the machine record'
expect_pass "$fx/mutation-bash-zero-PASS.md"
expect_fail_diag "$fx/mutation-powershell-unrelated-status-FAIL.md" \
  'check-closure-surface: external mutation powershell-close: missing mutation-exit' \
  'unrelated PowerShell status satisfied the machine record'
expect_pass "$fx/mutation-powershell-zero-PASS.md"
expect_fail_diag "$fx/mutation-record-near-miss-FAIL.md" \
  "check-closure-surface: malformed external-mutation-record row (key must be exactly lowercase 'external-mutation-record:')" \
  'near-miss mutation-record casing was silently skipped'
expect_fail_diag "$fx/mutation-record-duplicate-id-FAIL.md" \
  "check-closure-surface: duplicate external-mutation-record ID 'duplicate-close'" \
  'duplicate mutation-record identity was accepted'

expect_fail_diag "$fx/name-collision-ledger-FAIL.md" \
  "check-closure-surface: artifact identity 'ar8r-recursive-synthesis-continuation.zip' has 2 distinct hashes but no collision receipt" \
  'same-name distinct artifacts were accepted without a collision receipt'
expect_pass "$fx/name-collision-exact-receipt-PASS.md"
expect_fail_diag "$fx/name-collision-extra-hash-FAIL.md" \
  "check-closure-surface: collision receipt 'ar8r-recursive-synthesis-continuation.zip' hash set does not exactly match observed hashes" \
  'collision receipt accepted an unobserved hash'
expect_fail_diag "$fx/name-collision-missing-hash-FAIL.md" \
  "check-closure-surface: collision receipt 'ar8r-recursive-synthesis-continuation.zip' hash set does not exactly match observed hashes" \
  'collision receipt omitted an observed hash'

expect_fail_diag "$fx/external-evidence-invalid-mtime-FAIL.md" \
  "check-closure-surface: external evidence transcript-a: invalid mtime '2026-08-05T12:00:00+00:00' (expected RFC3339 UTC whole-second timestamp)" \
  'noncanonical external-evidence timestamp was accepted'
expect_fail_diag "$fx/stale-snapshot-terminal-FAIL.md" \
  'check-closure-surface: external evidence transcript-a: still-producing snapshot cannot support terminal use' \
  'still-producing snapshot was accepted for terminal closure'
expect_pass "$fx/snapshot-orientation-only-PASS.md"
expect_pass "$fx/terminal-restat-matches-PASS.md"

expect_fail_diag 'fixtures/claim-boundaries/negative-commit-message-unanchored-count.md' \
  'check-closure-surface: proposed commit message: digit or verdict claim requires exactly one Evidence anchor: claim:<Claim-ID>' \
  'numeric and verdict claims in the proposed commit block were accepted unanchored'
expect_pass 'fixtures/claim-boundaries/commit-message-descriptive-PASS.md'
expect_fail_diag 'fixtures/claim-boundaries/negative-proposed-block-omitted-anchor.md' \
  'check-closure-surface: proposed commit message: digit or verdict claim requires exactly one Evidence anchor: claim:<Claim-ID>' \
  'an anchor outside the proposed commit block was accepted'

# --- Fable review of PR #31: adversarial regressions -----------------------
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT

# Derive one-field mutations from the positive witness so target binding,
# zero-exit postconditions, digest identity, and path containment each have an
# independent behavioral check without network, model, or clock input.
cp "$fx/external-close-readback-PASS.json" "$tmp/external-close-readback-PASS.json"
cp "$fx/external-close-authorization.txt" "$tmp/external-close-authorization.txt"
sed 's/ | external-kind: mutation//' \
  "$fx/external-close-readback-PASS.md" > "$tmp/external-kind-missing.md"
expect_fail_diag "$tmp/external-kind-missing.md" \
  'check-closure-surface: claim close-207: verified external surface requires external-kind observation or mutation' \
  'verified external claim without external-kind was accepted'

sed 's/external-kind: mutation/External-kind: mutation/' \
  "$fx/external-close-readback-PASS.md" > "$tmp/external-kind-casing.md"
expect_fail_diag "$tmp/external-kind-casing.md" \
  "check-closure-surface: claim close-207: malformed external field 'External-kind'" \
  'near-miss external-kind casing was accepted'

printf '%s\n' \
  'claim: api-observation | surface: api | property: behavioral | status: verified | evidence-surface: api | external-kind: observation' \
  > "$tmp/external-observation.md"
expect_pass "$tmp/external-observation.md"

printf '%s\n' \
  'claim: legacy-source-api-evidence | surface: source | property: structural | status: verified | evidence-surface: api' \
  > "$tmp/legacy-source-api-evidence.md"
expect_pass "$tmp/legacy-source-api-evidence.md"

printf '%s\n%s\n%s\n%s\n%s\n' \
  'claim: descriptive-anchor | surface: source | property: structural | status: verified | evidence-surface: source' \
  '## Suggested Commit Message When No Commit Authorized' \
  '```text' \
  'docs: move dated lane reports' \
  'Evidence anchor:' \
  > "$tmp/proposed-descriptive-empty-anchor.md"
printf '%s\n' '```' >> "$tmp/proposed-descriptive-empty-anchor.md"
expect_fail_diag "$tmp/proposed-descriptive-empty-anchor.md" \
  'check-closure-surface: proposed commit message: exactly one well-formed Evidence anchor is allowed' \
  'malformed empty anchor in a descriptive proposed block was accepted'

printf '%s\n' \
  'claim: legacy-api | surface: api | property: behavioral | status: verified | evidence-surface: api' \
  > "$tmp/legacy-api.md"
expect_pass "$tmp/legacy-api.md"

printf '%s\n' '{"name":"triage"}' > "$tmp/readback-label.json"
label_sha="$(sha256sum "$tmp/readback-label.json" | awk '{print $1}')"
label_grant_sha="$(write_external_grant "$tmp/label-create-authorization.txt" create label triage)"
printf '%s\n%s\n%s\n' \
  'claim: label-create | surface: api | property: behavioral | status: verified | evidence-surface: api | external-kind: mutation | external-mutation-record: label-create | external-authorization-grant: grant-label-create' \
  "external-mutation-record: label-create | runner: bash | target-kind: label | target-id: triage | mutation-command: gh label create triage | mutation-exit: 0 | mutation-evidence: label-mut | readback-command: gh label list --search triage --json name --jq 'map(select(.name == \"triage\"))[0]' | readback-exit: 0 | readback-file: readback-label.json | readback-sha256: $label_sha | readback-field: name | expected-value: triage | observed-value: triage | readback-evidence: label-read" \
  "external-authorization-grant: grant-label-create | record-file: label-create-authorization.txt | record-sha256: $label_grant_sha" \
  > "$tmp/label-target-noun.md"
expect_pass "$tmp/label-target-noun.md"

sed 's/--search triage --json name/--search triage --search other --json name/' \
  "$tmp/label-target-noun.md" > "$tmp/readback-label-duplicate-search.md"
expect_fail_diag "$tmp/readback-label-duplicate-search.md" \
  'check-closure-surface: external mutation label-create: readback-command is not an approved read-only label query' \
  'duplicate label search with a different effective last value was accepted'

sed 's/mutation-command: gh issue close 207/mutation-command: gh issue close 208/' \
  "$fx/external-close-readback-PASS.md" > "$tmp/mutation-target-mismatch.md"
expect_fail_diag "$tmp/mutation-target-mismatch.md" \
  "check-closure-surface: external mutation close-207: mutation-command effective target issue '208' does not match declared issue '207'" \
  'mutation command target mismatch was accepted'

sed 's/readback-command: gh issue view 207/readback-command: gh issue view 208/' \
  "$fx/external-close-readback-PASS.md" > "$tmp/readback-target-mismatch.md"
expect_fail_diag "$tmp/readback-target-mismatch.md" \
  'check-closure-surface: external mutation close-207: readback-command is not an approved read-only issue query' \
  'readback command target mismatch was accepted'

sed 's/readback-command: gh issue view 207 --json state/readback-command: gh issue view 207 --json state (gh issue close 207)/' \
  "$fx/mutation-bash-zero-PASS.md" > "$tmp/readback-bash-parenthesized-expression.md"
expect_fail_diag "$tmp/readback-bash-parenthesized-expression.md" \
  'check-closure-surface: external mutation bash-close: readback-command is not an approved read-only issue query' \
  'Bash parenthesized expression was accepted as read-back evidence'

sed 's/readback-command: gh issue view 207 --json state/readback-command: gh issue view 207 --json state @(gh issue close 207)/' \
  "$fx/mutation-bash-zero-PASS.md" > "$tmp/readback-bash-array-expression.md"
expect_fail_diag "$tmp/readback-bash-array-expression.md" \
  'check-closure-surface: external mutation bash-close: readback-command is not an approved read-only issue query' \
  'Bash at-parenthesized expression was accepted as read-back evidence'

sed 's/readback-command: & gh issue view 207 --json state/readback-command: \& gh issue view 207 --json state @(gh issue close 207)/' \
  "$fx/mutation-powershell-zero-PASS.md" > "$tmp/readback-powershell-array-subexpression.md"
expect_fail_diag "$tmp/readback-powershell-array-subexpression.md" \
  'check-closure-surface: external mutation powershell-close: readback-command is not an approved read-only issue query' \
  'PowerShell array-subexpression was accepted as read-back evidence'

sed 's/readback-command: & gh issue view 207 --json state/readback-command: \& gh issue view 207 --json state (gh issue close 207)/' \
  "$fx/mutation-powershell-zero-PASS.md" > "$tmp/readback-powershell-subexpression.md"
expect_fail_diag "$tmp/readback-powershell-subexpression.md" \
  'check-closure-surface: external mutation powershell-close: readback-command is not an approved read-only issue query' \
  'PowerShell parenthesized expression was accepted as read-back evidence'

sed 's/readback-command: gh issue view 207 --json state/readback-command: gh issue reopen 207/' \
  "$fx/external-close-readback-PASS.md" > "$tmp/readback-issue-reopen.md"
expect_fail_diag "$tmp/readback-issue-reopen.md" \
  'check-closure-surface: external mutation close-207: readback-command is not an approved read-only issue query' \
  'issue reopen was accepted as read-back evidence'

pr_grant_sha="$(write_external_grant "$tmp/pr-merge-authorization.txt" merge pr 207)"
sed \
  -e 's/target-kind: issue/target-kind: pr/' \
  -e 's/mutation-command: gh issue close 207/mutation-command: gh pr merge 207/' \
  -e 's/readback-command: gh issue view 207 --json state/readback-command: gh pr review 207 --approve/' \
  -e 's/grant-close-207/grant-pr-merge/g' \
  -e 's/external-close-authorization.txt/pr-merge-authorization.txt/' \
  -e "s/9e4eb798de33536b66b3d84d0672838e7d18d678a23b4608f84faf8df8cc5c7f/$pr_grant_sha/" \
  "$fx/external-close-readback-PASS.md" > "$tmp/readback-pr-approve.md"
expect_fail_diag "$tmp/readback-pr-approve.md" \
  'check-closure-surface: external mutation close-207: readback-command is not an approved read-only pr query' \
  'PR approval was accepted as read-back evidence'

sed \
  -e 's/target-kind: issue/target-kind: pr/' \
  -e 's/mutation-command: gh issue close 207/mutation-command: gh pr merge 207/' \
  -e 's/readback-command: gh issue view 207 --json state/readback-command: gh pr view 207 --json state/' \
  -e 's/grant-close-207/grant-pr-merge/g' \
  -e 's/external-close-authorization.txt/pr-merge-authorization.txt/' \
  -e "s/9e4eb798de33536b66b3d84d0672838e7d18d678a23b4608f84faf8df8cc5c7f/$pr_grant_sha/" \
  "$fx/external-close-readback-PASS.md" > "$tmp/readback-pr-view.md"
expect_pass "$tmp/readback-pr-view.md"

printf '%s\n' '{"tagName":"v1.2.3"}' > "$tmp/readback-release.json"
release_sha="$(sha256sum "$tmp/readback-release.json" | awk '{print $1}')"
release_grant_sha="$(write_external_grant "$tmp/release-edit-authorization.txt" edit release v1.2.3)"
printf '%s\n%s\n%s\n' \
  'claim: release-view | surface: api | property: behavioral | status: verified | evidence-surface: api | external-kind: mutation | external-mutation-record: release-view | external-authorization-grant: grant-release-edit' \
  "external-mutation-record: release-view | runner: bash | target-kind: release | target-id: v1.2.3 | mutation-command: gh release edit v1.2.3 | mutation-exit: 0 | mutation-evidence: release-mut | readback-command: gh release view v1.2.3 --json tagName | readback-exit: 0 | readback-file: readback-release.json | readback-sha256: $release_sha | readback-field: tagName | expected-value: v1.2.3 | observed-value: v1.2.3 | readback-evidence: release-read" \
  "external-authorization-grant: grant-release-edit | record-file: release-edit-authorization.txt | record-sha256: $release_grant_sha" \
  > "$tmp/readback-release-view.md"
expect_pass "$tmp/readback-release-view.md"

sed 's/readback-command: gh issue view 207 --json state/readback-command: gh api repos\/example\/project\/issues\/207 --jq .state/' \
  "$fx/external-close-readback-PASS.md" > "$tmp/readback-api-get.md"
expect_pass "$tmp/readback-api-get.md"

sed 's/readback-command: gh issue view 207 --json state/readback-command: gh issue view 207 --json state; gh issue close 207/' \
  "$fx/external-close-readback-PASS.md" > "$tmp/readback-shell-chain.md"
expect_fail_diag "$tmp/readback-shell-chain.md" \
  'check-closure-surface: external mutation close-207: readback-command is not an approved read-only issue query' \
  'shell-chained mutation was accepted as read-back evidence'

sed 's/readback-command: gh issue view 207 --json state/readback-command: gh api repos\/example\/project\/issues\/207 --method POST/' \
  "$fx/external-close-readback-PASS.md" > "$tmp/readback-api-write.md"
expect_fail_diag "$tmp/readback-api-write.md" \
  'check-closure-surface: external mutation close-207: readback-command is not an approved read-only issue query' \
  'write-form gh api command was accepted as read-back evidence'

sed 's/mutation-exit: 0/mutation-exit: 9/' \
  "$fx/external-close-readback-PASS.md" > "$tmp/mutation-nonzero.md"
expect_fail_diag "$tmp/mutation-nonzero.md" \
  "check-closure-surface: external mutation close-207: mutation-exit must be 0, got '9'" \
  'nonzero mutation exit was accepted'

sed 's/readback-exit: 0/readback-exit: 4/' \
  "$fx/external-close-readback-PASS.md" > "$tmp/readback-nonzero.md"
expect_fail_diag "$tmp/readback-nonzero.md" \
  "check-closure-surface: external mutation close-207: readback-exit must be 0, got '4'" \
  'nonzero readback exit was accepted'

sed 's/2a25ed590f602f5941d5ccea2ed27345c83de9184757a91b4b1b93fb635370dc/0000000000000000000000000000000000000000000000000000000000000000/' \
  "$fx/external-close-readback-PASS.md" > "$tmp/readback-digest-mismatch.md"
expect_fail_diag "$tmp/readback-digest-mismatch.md" \
  'check-closure-surface: external mutation close-207: readback SHA-256 does not match external-close-readback-PASS.json' \
  'readback digest mismatch was accepted'

printf '%s\n' '{"state":"OPEN","state":"CLOSED"}' > "$tmp/readback-duplicate-key.json"
duplicate_key_sha="$(sha256sum "$tmp/readback-duplicate-key.json" | awk '{print $1}')"
sed \
  -e 's/readback-file: external-close-readback-PASS.json/readback-file: readback-duplicate-key.json/' \
  -e "s/2a25ed590f602f5941d5ccea2ed27345c83de9184757a91b4b1b93fb635370dc/$duplicate_key_sha/" \
  "$fx/external-close-readback-PASS.md" > "$tmp/readback-duplicate-key.md"
expect_fail_diag "$tmp/readback-duplicate-key.md" \
  "check-closure-surface: external mutation close-207: readback JSON contains duplicate object key 'state'" \
  'duplicate JSON key was accepted with last-key-wins semantics'

printf '%s\n' '{"state":NaN}' > "$tmp/readback-nan.json"
nan_sha="$(sha256sum "$tmp/readback-nan.json" | awk '{print $1}')"
sed \
  -e 's/readback-file: external-close-readback-PASS.json/readback-file: readback-nan.json/' \
  -e "s/2a25ed590f602f5941d5ccea2ed27345c83de9184757a91b4b1b93fb635370dc/$nan_sha/" \
  -e 's/expected-value: CLOSED | observed-value: CLOSED/expected-value: nan | observed-value: nan/' \
  "$fx/external-close-readback-PASS.md" > "$tmp/readback-nan.md"
expect_fail_diag "$tmp/readback-nan.md" \
  "check-closure-surface: external mutation close-207: readback JSON contains non-standard constant 'NaN'" \
  'JSON NaN constant was accepted'

printf '%s\n' '{"state":Infinity}' > "$tmp/readback-infinity.json"
infinity_sha="$(sha256sum "$tmp/readback-infinity.json" | awk '{print $1}')"
sed \
  -e 's/readback-file: external-close-readback-PASS.json/readback-file: readback-infinity.json/' \
  -e "s/2a25ed590f602f5941d5ccea2ed27345c83de9184757a91b4b1b93fb635370dc/$infinity_sha/" \
  -e 's/expected-value: CLOSED | observed-value: CLOSED/expected-value: inf | observed-value: inf/' \
  "$fx/external-close-readback-PASS.md" > "$tmp/readback-infinity.md"
expect_fail_diag "$tmp/readback-infinity.md" \
  "check-closure-surface: external mutation close-207: readback JSON contains non-standard constant 'Infinity'" \
  'JSON Infinity constant was accepted'

printf '%s\n' '{"state":-Infinity}' > "$tmp/readback-negative-infinity.json"
negative_infinity_sha="$(sha256sum "$tmp/readback-negative-infinity.json" | awk '{print $1}')"
sed \
  -e 's/readback-file: external-close-readback-PASS.json/readback-file: readback-negative-infinity.json/' \
  -e "s/2a25ed590f602f5941d5ccea2ed27345c83de9184757a91b4b1b93fb635370dc/$negative_infinity_sha/" \
  -e 's/expected-value: CLOSED | observed-value: CLOSED/expected-value: -inf | observed-value: -inf/' \
  "$fx/external-close-readback-PASS.md" > "$tmp/readback-negative-infinity.md"
expect_fail_diag "$tmp/readback-negative-infinity.md" \
  "check-closure-surface: external mutation close-207: readback JSON contains non-standard constant '-Infinity'" \
  'JSON negative Infinity constant was accepted'

sed 's/readback-file: external-close-readback-PASS.json/readback-file: ..\/external-close-readback-PASS.json/' \
  "$fx/external-close-readback-PASS.md" > "$tmp/readback-traversal.md"
expect_fail_diag "$tmp/readback-traversal.md" \
  "check-closure-surface: external mutation close-207: readback-file must be a bare relative JSON basename, got '../external-close-readback-PASS.json'" \
  'readback path traversal was accepted'

mkdir "$tmp/witness.json"
sed 's/readback-file: external-close-readback-PASS.json/readback-file: witness.json/' \
  "$fx/external-close-readback-PASS.md" > "$tmp/readback-nonregular.md"
expect_fail_diag "$tmp/readback-nonregular.md" \
  "check-closure-surface: external mutation close-207: readback-file 'witness.json' is not a regular file" \
  'non-regular readback witness was accepted'

sed 's/Evidence anchor: claim:close-207/Evidence anchor: claim:missing-claim/' \
  "$fx/external-close-readback-PASS.md" > "$tmp/proposed-anchor-unresolved.md"
expect_fail_diag "$tmp/proposed-anchor-unresolved.md" \
  "check-closure-surface: proposed commit message: Evidence anchor claim 'missing-claim' is unresolved" \
  'unresolved proposed-message anchor was accepted'

sed 's/status: verified/status: unverified/' \
  "$fx/external-close-readback-PASS.md" > "$tmp/proposed-anchor-unverified.md"
expect_fail_diag "$tmp/proposed-anchor-unverified.md" \
  "check-closure-surface: proposed commit message: Evidence anchor claim 'close-207' is not verified" \
  'unverified proposed-message anchor was accepted'

printf '%s\n%s\n%s\n' \
  'claim: missing-fence | surface: source | property: behavioral | status: verified | evidence-surface: source' \
  '## Suggested Commit Message When No Commit Authorized' \
  'test: verified closure' \
  > "$tmp/proposed-block-missing-fence.md"
expect_fail_diag "$tmp/proposed-block-missing-fence.md" \
  'check-closure-surface: proposed commit message: missing fenced block boundaries' \
  'claim-bearing proposed message without fenced boundaries was accepted'

sed 's/closure-bytes: 2478/closure-bytes: 2479/' \
  "$fx/terminal-restat-matches-PASS.md" > "$tmp/terminal-restat-mismatch.md"
expect_fail_diag "$tmp/terminal-restat-mismatch.md" \
  'check-closure-surface: external evidence transcript-a: closure re-stat does not match original bytes and mtime' \
  'mismatched terminal closure re-stat was accepted'

# Duplicate Claim-ID with conflicting surfaces is ambiguous, never valid.
printf '%s\n%s\n' \
  'claim: X | surface: source | property: structural | status: verified | evidence-surface: source' \
  'claim: X | surface: deployed-service | property: behavioral | status: unverified | residual: r1' \
  > "$tmp/dup.md"
if bash "$scorer" "$tmp/dup.md" >/dev/null 2>&1; then
  fail "duplicate Claim-ID accepted"
fi

# A near-miss row (capitalized key) must fail loudly, never be silently
# skipped — otherwise a layer-promotion row hides by casing its key.
printf '%s\n%s\n' \
  'claim: ok | surface: source | property: structural | status: verified | evidence-surface: source' \
  'Claim: bad | surface: deployed-service | property: behavioral | status: verified | evidence-surface: source' \
  > "$tmp/caps.md"
if bash "$scorer" "$tmp/caps.md" >/dev/null 2>&1; then
  fail "capitalized near-miss claim row silently skipped"
fi

# Control: two DISTINCT claims at different surfaces remain valid.
printf '%s\n%s\n' \
  'claim: a | surface: source | property: structural | status: verified | evidence-surface: source' \
  'claim: b | surface: deployed-service | property: behavioral | status: unverified | residual: r2' \
  > "$tmp/two.md"
bash "$scorer" "$tmp/two.md" >/dev/null 2>&1 \
  || fail "two distinct claims at different surfaces must pass"

# Kill authority is identity-ledger only. Broad image-name termination fails;
# a PID-targeted closure record remains within this checker's scope and the
# run-root validator performs the process-started.json identity match.
printf '%s\n%s\n' \
  'claim: kill | surface: source | property: structural | status: verified | evidence-surface: source' \
  "kill-command: Get-CimInstance Win32_Process -Filter \"Name='claude.exe'\" | Stop-Process" \
  > "$tmp/kill-broad.md"
if bash "$scorer" "$tmp/kill-broad.md" >/dev/null 2>&1; then
  fail "image-name kill authority accepted"
fi
printf '%s\n%s\n' \
  'claim: kill | surface: source | property: structural | status: verified | evidence-surface: source' \
  'kill: pid=123 | host_boot_id=boot-1 | process_creation_time=2026-08-06T01:02:03Z | authority=process-started.json' \
  > "$tmp/kill-owned.md"
bash "$scorer" "$tmp/kill-owned.md" >/dev/null 2>&1 \
  || fail "PID-targeted kill closure record must pass this grep-level gate"

# #77 R4-F9: pending markers are rejected only on an explicitly supplied
# closure-evidence file; no #78 ledger/plan/steer inference is introduced.
printf 'Status: IN PROGRESS\n' > "$tmp/pending-evidence.md"
if bash "$scorer" "$tmp/two.md" --closure-evidence "$tmp/pending-evidence.md" >/dev/null 2>&1; then
  fail "explicit pending closure evidence accepted"
fi
printf 'Status: COMPLETE\n' > "$tmp/complete-evidence.md"
bash "$scorer" "$tmp/two.md" --closure-evidence "$tmp/complete-evidence.md" >/dev/null 2>&1 \
  || fail "explicit complete closure evidence rejected"

# #78 R5-F2/F3/F6: a sibling decision ledger is absent-tolerant, but any
# pending or unresolved decision must block closure. A terminal disposition
# remains owner/policy assigned and carries its authority in the row.
printf '%s\n' \
  '{"ts":"2026-08-06T20:00:00Z","phase":"3","what":"item-a","why":"outside current scope","owner":"owner","unblock":"policy: owner-policy-17","disposition":"pending"}' \
  > "$tmp/deferrals.jsonl"
if bash "$scorer" "$tmp/two.md" >/dev/null 2>&1; then
  fail "pending deferral accepted"
fi
printf '%s\n' \
  '{"ts":"2026-08-06T20:00:00Z","phase":"3","what":"item-a","why":"outside current scope","owner":"owner","unblock":"policy: owner-policy-17","disposition":"risk-accepted"}' \
  > "$tmp/deferrals.jsonl"
bash "$scorer" "$tmp/two.md" >/dev/null 2>&1 \
  || fail "owner/policy-assigned terminal deferral rejected"
printf '%s\n' \
  '{"ts":"2026-08-06T20:00:00Z","phase":"three","what":"item-a","why":"outside current scope","owner":"owner","unblock":"policy: owner-policy-17","disposition":"risk-accepted"}' \
  > "$tmp/deferrals.jsonl"
if bash "$scorer" "$tmp/two.md" >/dev/null 2>&1; then
  fail "nonnumeric deferral phase accepted"
fi
printf '%s\n' \
  '{"ts":"2026-08-06T20:00:00Z","phase":"3","what":"item-a","why":"outside current scope","owner":"owner","unblock":"later","disposition":"risk-accepted"}' \
  > "$tmp/deferrals.jsonl"
if bash "$scorer" "$tmp/two.md" >/dev/null 2>&1; then
  fail "risk-accepted deferral without policy reference accepted"
fi
rm "$tmp/deferrals.jsonl"
bash "$scorer" "$tmp/two.md" >/dev/null 2>&1 \
  || fail "absent zero-deferral ledger must pass without ceremony"

# #78 R5-F8/F9/F10 plus runtime non-verdict carry-forward. Generic blocker
# rows are prospective; legacy closure records without them remain valid.
printf '%s\n%s\n' \
  'claim: blocker | surface: source | property: structural | status: verified | evidence-surface: source' \
  'blocker: b1 | blocked_scope: luna-cli-quota' \
  > "$tmp/blocker-missing-work.md"
if bash "$scorer" "$tmp/blocker-missing-work.md" >/dev/null 2>&1; then
  fail "blocker without unblocked_work accepted"
fi
printf '%s\n%s\n' \
  'claim: blocker | surface: source | property: structural | status: verified | evidence-surface: source' \
  'blocker: b1 | blocked_scope: luna-cli-quota | unblocked_work: none' \
  > "$tmp/blocker-none-unjustified.md"
if bash "$scorer" "$tmp/blocker-none-unjustified.md" >/dev/null 2>&1; then
  fail "unblocked_work none without justification accepted"
fi
printf '%s\n%s\n' \
  'claim: blocker | surface: source | property: structural | status: verified | evidence-surface: source' \
  'blocker: b1 | blocked_scope: lane-1 | unblocked_work: docs | unblocked_work: none | justification: misleading duplicate' \
  > "$tmp/blocker-duplicate-field.md"
if bash "$scorer" "$tmp/blocker-duplicate-field.md" >/dev/null 2>&1; then
  fail "duplicate blocker field accepted"
fi
printf '%s\n%s\n' \
  'claim: blocker | surface: source | property: structural | status: verified | evidence-surface: source' \
  'Blocker: b1 | blocked_scope: all | unblocked_work: none | justification: case spoof' \
  > "$tmp/blocker-case-spoof.md"
if bash "$scorer" "$tmp/blocker-case-spoof.md" >/dev/null 2>&1; then
  fail "case-insensitive blocker near-miss accepted"
fi
printf '%s\n%s\n' \
  'claim: blocker | surface: source | property: structural | status: verified | evidence-surface: source' \
  'blocker: b1 | blocked_scope: luna-cli-quota | unblocked_work: docs | negative-capability: true | probe_methods: Get-Command,Get-Command,Get-Command | falsification_attempted: none' \
  > "$tmp/blocker-repeated-probe.md"
if bash "$scorer" "$tmp/blocker-repeated-probe.md" >/dev/null 2>&1; then
  fail "repeated negative-capability probe accepted"
fi
printf '%s\n%s\n' \
  'claim: blocker | surface: source | property: structural | status: verified | evidence-surface: source' \
  'blocker: b1 | blocked_scope: luna-cli-quota | unblocked_work: docs | negative-capability: true | probe_methods: Get-Command,get-command | probe_evidence: Get-Command::command-discovery=>Get-Command luna exit=1;get-command::command-discovery=>get-command luna exit=1 | falsification_attempted: searched installed plugin manifests' \
  > "$tmp/blocker-casefold-probe.md"
if bash "$scorer" "$tmp/blocker-casefold-probe.md" >/dev/null 2>&1; then
  fail "case-only duplicate negative-capability methods accepted"
fi
printf '%s\n%s\n' \
  'claim: blocker | surface: source | property: structural | status: verified | evidence-surface: source' \
  'blocker: b1 | blocked_scope: luna-cli-quota | unblocked_work: docs | negative-capability: true | probe_methods: Get-Command,plugin-manifest | falsification_attempted: searched installed plugin manifests' \
  > "$tmp/blocker-unbound-probe.md"
if bash "$scorer" "$tmp/blocker-unbound-probe.md" >/dev/null 2>&1; then
  fail "negative-capability methods without structured evidence accepted"
fi
printf '%s\n%s\n' \
  'claim: blocker | surface: source | property: structural | status: verified | evidence-surface: source' \
  'blocker: b1 | blocked_scope: luna-cli-quota | unblocked_work: docs | negative-capability: true | probe_methods: Get-Command,plugin-manifest | probe_evidence: Get-Command::command-discovery=>Get-Command luna exit=1;plugin-manifest::manifest-enumeration=>installed plugin manifest count=0 | falsification_attempted: searched installed plugin manifests | terminal: blocked-non-verdict | next_probe_or_abandon: retry after capacity signal' \
  > "$tmp/blocker-good.md"
bash "$scorer" "$tmp/blocker-good.md" >/dev/null 2>&1 \
  || fail "distinct evidenced negative-capability blocker rejected"
printf '%s\n%s\n' \
  'claim: blocker | surface: source | property: structural | status: verified | evidence-surface: source' \
  'blocker: b1 | blocked_scope: lane-1 | unblocked_work: lane-2 | terminal: blocked-non-verdict' \
  > "$tmp/nonverdict-missing-next.md"
if bash "$scorer" "$tmp/nonverdict-missing-next.md" >/dev/null 2>&1; then
  fail "blocked non-verdict without next_probe_or_abandon accepted"
fi

# #78 R5-F5/F7/F11: an explicitly declared superseded plan needs a header and
# reconciliation on every unchecked item; undeclared steer precedence warns.
printf '%s\n' '# Plan A' '- [ ] unfinished task' > "$tmp/plan-a.md"
if bash "$scorer" "$tmp/two.md" --superseded-plan "$tmp/plan-a.md" >/dev/null 2>&1; then
  fail "superseded plan without header accepted"
fi
printf '%s\n' 'SUPERSEDED_BY: plan-b.md — authority narrowed' '# Plan A' \
  '- [ ] unfinished task | RECONCILIATION: TODO' > "$tmp/plan-a.md"
bash "$scorer" "$tmp/two.md" --superseded-plan "$tmp/plan-a.md" >/dev/null 2>&1 \
  || fail "properly reconciled superseded plan rejected"
mkdir "$tmp/steers"
for n in 1 2 3; do printf '# round %s\n' "$n" > "$tmp/steers/ROUND-$n-STEER.md"; done
if ! bash "$scorer" "$tmp/two.md" --steer-dir "$tmp/steers" >"$tmp/steer.out" 2>"$tmp/steer.err"; then
  fail "undeclared steer precedence must warn, not fail"
fi
grep -Fq 'warning: 3 steer/advisory artifacts lack declared precedence' "$tmp/steer.err" \
  || fail "undeclared steer precedence warning missing"

# #78 R5-F7: no implicit cycle cap exists. A plan with no bound may consume
# nine cycles, while exceeding a declared bound requires an explicit owner
# decision before the plan can support closure.
printf '%s\n%s\n' 'CYCLE_BOUND: none' 'CYCLES_CONSUMED: 9' > "$tmp/no-bound-plan.md"
bash "$scorer" "$tmp/two.md" --plan-cycle-record "$tmp/no-bound-plan.md" >/dev/null 2>&1 \
  || fail "no-bound plan rejected after nine cycles"
printf '%s\n%s\n' 'CYCLE_BOUND: 3' 'CYCLES_CONSUMED: 4' > "$tmp/overrun-plan.md"
if bash "$scorer" "$tmp/two.md" --plan-cycle-record "$tmp/overrun-plan.md" >/dev/null 2>&1; then
  fail "declared cycle-bound overrun accepted without owner decision"
fi
printf '%s\n%s\n%s\n' 'CYCLE_BOUND: 3' 'CYCLES_CONSUMED: 4' \
  'BOUND_OVERRUN: OWNER_DECISION' > "$tmp/overrun-plan.md"
bash "$scorer" "$tmp/two.md" --plan-cycle-record "$tmp/overrun-plan.md" >/dev/null 2>&1 \
  || fail "owner-decided cycle-bound overrun rejected"

grep -Fq -- '--superseded-plan <each-replaced-plan>' \
  "$repo_root/skills/implementaudit/templates/PROTOCOL.md" \
  || fail "shipped final-audit invocation omits superseded-plan inputs"
grep -Fq -- '--steer-dir <run-root>' \
  "$repo_root/skills/implementaudit/templates/PROTOCOL.md" \
  || fail "shipped final-audit invocation omits steer-dir input"
grep -Fq -- '--plan-cycle-record <each-cycle-accounted-plan>' \
  "$repo_root/skills/implementaudit/templates/PROTOCOL.md" \
  || fail "shipped final-audit invocation omits plan cycle inputs"

# #87: closure re-captures its start/verify anchors. Drift needs a hash-bound,
# per-finding re-anchor or consequential supersession record. A stochasticity
# budget counts only when its declaration is tracked at the start anchor.
base_claim='claim: identity | surface: source | property: structural | status: verified | evidence-surface: source'
reanchor_repo="$tmp/reanchor-repo"
mkdir "$reanchor_repo"
git -C "$reanchor_repo" init -q
git -C "$reanchor_repo" config user.email test@example.invalid
git -C "$reanchor_repo" config user.name 'Closure Contract Test'
printf 'start\n' > "$reanchor_repo/anchor.txt"
git -C "$reanchor_repo" add anchor.txt
git -C "$reanchor_repo" commit -qm 'start anchor'
start_sha="$(git -C "$reanchor_repo" rev-parse HEAD)"
printf 'verify\n' > "$reanchor_repo/anchor.txt"
git -C "$reanchor_repo" add anchor.txt
git -C "$reanchor_repo" commit -qm 'verification anchor'
verify_sha="$(git -C "$reanchor_repo" rev-parse HEAD)"
reanchor_check() {
  (cd "$reanchor_repo" && bash "$repo_root/$scorer" "$@")
}
printf '%s\nAUDIT_START_ANCHOR: %s\nAUDIT_VERIFY_ANCHOR: %s\n%s\n%s\n%s\n%s\n' "$base_claim" \
  "$start_sha" "$verify_sha" \
  'REANCHOR_DISPOSITION: unchanged' 'REANCHOR_EVIDENCE: none' \
  'equivalent_config_attempts: 1/1' 'terminal_qualification: QUALIFIED' \
  > "$tmp/reanchor-unreconciled.md"
if reanchor_check "$tmp/reanchor-unreconciled.md" >/dev/null 2>&1; then
  fail "moved closure anchor accepted without re-anchor or supersession"
fi
zero_hash='0000000000000000000000000000000000000000000000000000000000000000'
sed -e 's/REANCHOR_DISPOSITION: unchanged/REANCHOR_DISPOSITION: per-finding/' \
    -e 's/REANCHOR_EVIDENCE: none/REANCHOR_EVIDENCE: structured-rows/' \
    "$tmp/reanchor-unreconciled.md" > "$tmp/reanchor-dangling.md"
printf 'residual: identity | consequential: yes | disposition: SUPERSEDED_BY_CONCURRENT_MUTATION | evidence-file: missing.md | evidence-sha256: %s\n' \
  "$zero_hash" >> "$tmp/reanchor-dangling.md"
if reanchor_check "$tmp/reanchor-dangling.md" >/dev/null 2>&1; then
  fail "dangling global supersession evidence accepted"
fi

cat > "$tmp/finding-r7.md" <<EOF
Anchor: $verify_sha
Finding: identity
Disposition: SUPERSEDED_BY_CONCURRENT_MUTATION
EOF
finding_hash="$(sha256sum "$tmp/finding-r7.md" | awk '{print $1}')"
sed -e 's/REANCHOR_DISPOSITION: unchanged/REANCHOR_DISPOSITION: per-finding/' \
    -e 's/REANCHOR_EVIDENCE: none/REANCHOR_EVIDENCE: structured-rows/' \
    "$tmp/reanchor-unreconciled.md" > "$tmp/reanchor-superseded.md"
printf 'residual: identity | consequential: yes | disposition: SUPERSEDED_BY_CONCURRENT_MUTATION | evidence-file: finding-r7.md | evidence-sha256: %s\n' \
  "$finding_hash" >> "$tmp/reanchor-superseded.md"
reanchor_output=""
if ! reanchor_output="$(reanchor_check "$tmp/reanchor-superseded.md" 2>&1)"; then
  fail "hash-bound per-finding concurrent-mutation supersession rejected: ${reanchor_output:-no scorer diagnostic}"
fi
sed '/^residual: identity /d' "$tmp/reanchor-superseded.md" > "$tmp/reanchor-missing-finding.md"
if reanchor_check "$tmp/reanchor-missing-finding.md" >/dev/null 2>&1; then
  fail "moved closure anchor accepted without one structured row per claim"
fi
sed -e 's/equivalent_config_attempts: 1\/1/equivalent_config_attempts: 3\/1/' \
    "$tmp/reanchor-superseded.md" > "$tmp/repeated-qualified.md"
if reanchor_check "$tmp/repeated-qualified.md" >/dev/null 2>&1; then
  fail "3/1 equivalent draws without budget accepted as QUALIFIED"
fi
sed 's/terminal_qualification: QUALIFIED/terminal_qualification: PROVISIONAL/' \
  "$tmp/repeated-qualified.md" > "$tmp/repeated-provisional.md"
reanchor_check "$tmp/repeated-provisional.md" >/dev/null 2>&1 \
  || fail "truthful 3/1 PROVISIONAL terminal rejected"
printf 'stochasticity_budget: 3\nstochasticity_budget_anchor: %s\nstochasticity_budget_path: posthoc-budget.md\n' \
  "$start_sha" >> "$tmp/repeated-qualified.md"
if reanchor_check "$tmp/repeated-qualified.md" >/dev/null 2>&1; then
  fail "post-hoc stochasticity budget accepted as predeclared"
fi

mkdir "$tmp/budget-repo"
(
  cd "$tmp/budget-repo"
  git init -q
  git config user.email test@example.invalid
  git config user.name 'Closure Contract Test'
  printf 'stochasticity_budget: 3\n' > budget.md
  git add budget.md
  git commit -qm 'declare budget'
  budget_start="$(git rev-parse HEAD)"
  printf 'verify\n' > marker.txt
  git add marker.txt
  git commit -qm 'verification anchor'
  budget_verify="$(git rev-parse HEAD)"
  cat > finding-r7.md <<EOF
Anchor: $budget_verify
Finding: identity
Disposition: reanchored
EOF
  budget_evidence_hash="$(sha256sum finding-r7.md | awk '{print $1}')"
  printf '%s\nAUDIT_START_ANCHOR: %s\nAUDIT_VERIFY_ANCHOR: %s\n%s\n%s\n' \
    "$base_claim" "$budget_start" "$budget_verify" \
    'REANCHOR_DISPOSITION: per-finding' 'REANCHOR_EVIDENCE: structured-rows' \
    > closure.md
  printf 'reanchor-finding: identity | disposition: reanchored | evidence-file: finding-r7.md | evidence-sha256: %s\n' \
    "$budget_evidence_hash" >> closure.md
  printf '%s\n%s\n%s\n%s\n%s\n' \
    'equivalent_config_attempts: 3/1' 'terminal_qualification: QUALIFIED' \
    'stochasticity_budget: 3' "stochasticity_budget_anchor: $budget_start" \
    'stochasticity_budget_path: budget.md' >> closure.md
  bash "$repo_root/$scorer" closure.md >/dev/null 2>&1
) || fail "start-anchor-tracked stochasticity budget rejected"
sed -e "s/AUDIT_VERIFY_ANCHOR: $verify_sha/AUDIT_VERIFY_ANCHOR: invalid/" \
    -e 's/equivalent_config_attempts: 3\/1/equivalent_config_attempts: 1\/0/' \
    "$tmp/reanchor-superseded.md" > "$tmp/invalid-second-anchor.md"
if reanchor_check "$tmp/invalid-second-anchor.md" >/dev/null 2>&1; then
  fail "invalid VERIFY anchor accepted because START anchor matched first"
fi
printf '%s\nAUDIT_START_ANCHOR: %s\nAUDIT_VERIFY_ANCHOR: %s\n%s\n%s\n%s\n%s\n' "$base_claim" \
  "$start_sha" "$start_sha" \
  'REANCHOR_DISPOSITION: unchanged' 'REANCHOR_EVIDENCE: none' \
  'equivalent_config_attempts: 1/0' 'terminal_qualification: QUALIFIED' \
  > "$tmp/zero-pass-qualified.md"
if reanchor_check "$tmp/zero-pass-qualified.md" >/dev/null 2>&1; then
  fail "zero-pass terminal accepted as QUALIFIED"
fi

# #89 R16: publication verification is digest identity, not label identity.
publication_identity_controls "$tmp"

printf 'closure-surface-contract: ok (contract + quota, kill-authority, #88 external-state, #78 deferral, and #138 automatic-effect controls)\n'
