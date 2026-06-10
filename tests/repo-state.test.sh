#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

first_line="$(sed -n '1p' skills/scripts/repo-state.sh)"
[ "$first_line" = '#!/usr/bin/env bash' ] || {
  printf 'repo-state.test: repo-state.sh shebang is not LF-safe\n' >&2
  exit 1
}

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

mkdir -p "$tmp/repo with spaces/skills/scripts"
cp skills/scripts/repo-state.sh "$tmp/repo with spaces/skills/scripts/repo-state.sh"

cd "$tmp/repo with spaces"
git init -q
git config user.email test@example.invalid
git config user.name 'ImplementAudit Test'

printf 'ignored.txt\n' >.gitignore
printf 'base\n' >tracked.txt
printf 'remove me\n' >delete-me.txt
mkdir -p 'space dir'
printf 'base space\n' >'space dir/original.txt'
git add .
git commit -q -m baseline
baseline="$(git rev-parse HEAD)"

printf 'committed\n' >committed-after.txt
git add committed-after.txt
git commit -q -m 'after baseline'

printf 'modified\n' >>tracked.txt
printf 'staged\n' >staged.txt
git add staged.txt
rm delete-me.txt
printf 'untracked\nDEBUG_SENTINEL\n' >untracked.txt
printf 'space file\n' >'space dir/path with spaces.txt'
printf 'ignored debug\n' >ignored.txt

changed="$(bash skills/scripts/repo-state.sh changed-files "$baseline")"
for expected in \
  committed-after.txt \
  delete-me.txt \
  staged.txt \
  tracked.txt \
  untracked.txt \
  'space dir/path with spaces.txt'
do
  printf '%s\n' "$changed" | grep -Fx "$expected" >/dev/null || {
    printf 'repo-state.test: missing changed file %s\n%s\n' "$expected" "$changed" >&2
    exit 1
  }
done

if printf '%s\n' "$changed" | grep -Fx ignored.txt >/dev/null; then
  printf 'repo-state.test: ignored file should not appear in changed-files\n' >&2
  exit 1
fi

bash skills/scripts/repo-state.sh deliverable "$baseline" untracked.txt | grep -F 'present - untracked new file' >/dev/null
bash skills/scripts/repo-state.sh deliverable "$baseline" 'space dir/path with spaces.txt' | grep -F 'present - untracked new file' >/dev/null

if bash skills/scripts/repo-state.sh deliverable "$baseline" delete-me.txt >/dev/null 2>&1; then
  printf 'repo-state.test: deleted deliverable should be missing\n' >&2
  exit 1
fi

bash skills/scripts/repo-state.sh deliverable not-a-real-ref tracked.txt | grep -F 'baseline unavailable' >/dev/null
bash skills/scripts/repo-state.sh added-lines "$baseline" | grep -F 'DEBUG_SENTINEL' >/dev/null

mkdir "$tmp/no-git"
printf 'plain\n' >"$tmp/no-git/file.txt"
(
  cd "$tmp/no-git"
  bash "$tmp/repo with spaces/skills/scripts/repo-state.sh" deliverable no-git file.txt | grep -F 'baseline unavailable' >/dev/null
)

# Run-root artifacts under .IMPLEMENTAUDIT/ are excluded from enumeration
# evidence in target repos that do not gitignore them — visibly, never silently.
mkdir -p "$tmp/runroot-repo"
(
  cd "$tmp/runroot-repo"
  git init -q
  printf 'base\n' > base.txt
  git add base.txt
  git -c user.email=t@example.invalid -c user.name=t commit -qm init
  rrbaseline="$(git rev-parse HEAD)"
  mkdir -p .IMPLEMENTAUDIT/runs/demo-x
  printf 'RUNROOT_SENTINEL\n' > .IMPLEMENTAUDIT/runs/demo-x/STATE.md
  printf 'REAL_CHANGE_SENTINEL\n' > new-file.txt

  changed_out="$(bash "$tmp/repo with spaces/skills/scripts/repo-state.sh" changed-files "$rrbaseline" 2>"$tmp/rr-stderr.log")"
  printf '%s\n' "$changed_out" | grep -Fx new-file.txt >/dev/null
  if printf '%s\n' "$changed_out" | grep -F '.IMPLEMENTAUDIT/' >/dev/null; then
    printf 'repo-state.test: run-root path leaked into changed-files\n' >&2
    exit 1
  fi
  grep -F 'excluded 1 run-root path' "$tmp/rr-stderr.log" >/dev/null || {
    printf 'repo-state.test: run-root exclusion note missing from stderr\n' >&2
    exit 1
  }

  added_out="$(bash "$tmp/repo with spaces/skills/scripts/repo-state.sh" added-lines "$rrbaseline" 2>/dev/null)"
  printf '%s\n' "$added_out" | grep -F 'REAL_CHANGE_SENTINEL' >/dev/null
  if printf '%s\n' "$added_out" | grep -F 'RUNROOT_SENTINEL' >/dev/null; then
    printf 'repo-state.test: run-root content leaked into added-lines\n' >&2
    exit 1
  fi
)

printf 'repo-state.test: ok\n'
