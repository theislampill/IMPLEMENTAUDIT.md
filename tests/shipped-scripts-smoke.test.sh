#!/usr/bin/env bash
set -euo pipefail

# Class-killing smoke: every shipped recon/read-only helper must exit 0 in a
# minimal target repo that has none of the IMPLEMENTAUDIT source repo's
# structure. Two helpers (summarize-repo, detect-stack) shipped with
# compound-condition tails that exited non-zero exactly there; this test
# prevents that class from returning in any shipped script.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

mkdir -p "$tmp/target"
(
  cd "$tmp/target"
  git init -q
  printf 'minimal\n' > file.txt
  git add file.txt
  git -c user.email=t@example.invalid -c user.name=t commit -qm init
)

# Read-only recon helpers: must succeed in any repo, however bare.
for helper in detect-env.sh detect-stack.sh summarize-repo.sh; do
  (
    cd "$tmp/target"
    bash "$repo_root/skills/scripts/$helper" >/dev/null 2>&1
  ) || {
    printf 'shipped-scripts-smoke.test: %s exited non-zero in a bare target repo\n' "$helper" >&2
    exit 1
  }
done

# repo-state.sh enumeration in the same bare repo.
(
  cd "$tmp/target"
  baseline="$(git rev-parse HEAD)"
  bash "$repo_root/skills/scripts/repo-state.sh" changed-files "$baseline" >/dev/null 2>&1
  bash "$repo_root/skills/scripts/repo-state.sh" added-lines "$baseline" >/dev/null 2>&1
) || {
  printf 'shipped-scripts-smoke.test: repo-state.sh failed in a bare target repo\n' >&2
  exit 1
}

# claim-run.sh claims a run root and keeps stdout parseable (path only).
(
  cd "$tmp/target"
  out="$(bash "$repo_root/skills/scripts/claim-run.sh" "smoke probe" 2>/dev/null)"
  [ -d "$out" ]
) || {
  printf 'shipped-scripts-smoke.test: claim-run.sh failed or stdout is not the run-root path\n' >&2
  exit 1
}

# Round-9+ helpers: bare-repo-safe behaviors hold.
if bash skills/scripts/validate-run-root.sh "$tmp/target" >/dev/null 2>&1; then
  printf 'shipped-scripts-smoke.test: validate-run-root accepted a non-run-root dir\n' >&2
  exit 1
fi
if bash skills/scripts/custody-append.sh only two >/dev/null 2>&1; then
  printf 'shipped-scripts-smoke.test: custody-append accepted wrong arity\n' >&2
  exit 1
fi
bash skills/scripts/custody-append.sh "$tmp/x.db" r e1 t.event '{"custody_mode":"live_test"}' >/dev/null || {
  printf 'shipped-scripts-smoke.test: custody-append failed its exit-0 contract\n' >&2
  exit 1
}
detect_out="$(cd "$tmp/target" && bash "$repo_root/skills/scripts/detect-env.sh" 2>/dev/null)"
printf '%s' "$detect_out" | grep -q "implementaudit_skill_dir=" || {
  printf 'shipped-scripts-smoke.test: detect-env missing skill-dir report\n' >&2
  exit 1
}

# Validators must still reject malformed input with a non-zero exit.
printf 'not a spec\n' > "$tmp/bad-spec.md"
if bash skills/scripts/validate-phase.sh "$tmp/bad-spec.md" >/dev/null 2>&1; then
  printf 'shipped-scripts-smoke.test: validate-phase.sh accepted a malformed spec\n' >&2
  exit 1
fi
if bash skills/scripts/validate-audit-spec.sh "$tmp/bad-spec.md" >/dev/null 2>&1; then
  printf 'shipped-scripts-smoke.test: validate-audit-spec.sh accepted a malformed spec\n' >&2
  exit 1
fi

printf 'shipped-scripts-smoke.test: ok\n'
