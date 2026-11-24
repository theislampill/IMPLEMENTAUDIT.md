#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

first_line="$(sed -n '1p' skills/implementaudit/scripts/repo-state.sh)"
[ "$first_line" = '#!/usr/bin/env bash' ] || {
  printf 'repo-state.test: repo-state.sh shebang is not LF-safe\n' >&2
  exit 1
}

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

mkdir -p "$tmp/repo with spaces/skills/implementaudit/scripts"
cp skills/implementaudit/scripts/repo-state.sh "$tmp/repo with spaces/skills/implementaudit/scripts/repo-state.sh"

cd "$tmp/repo with spaces"
git init -q
git config user.email test@example.invalid
git config user.name 'ImplementAudit Test'

printf 'ignored.txt\n' >.gitignore
printf 'base\n' >tracked.txt
printf 'committed base\n' >committed-masked.txt
printf 'remove me\n' >delete-me.txt
mkdir -p 'space dir'
printf 'index base\n' >'space dir/staged masked.txt'
printf 'base space\n' >'space dir/original.txt'
git add .
git commit -q -m baseline
baseline="$(git rev-parse HEAD)"

empty_added="$(bash skills/implementaudit/scripts/repo-state.sh added-lines "$baseline")"
empty_changed="$(bash skills/implementaudit/scripts/repo-state.sh changed-files "$baseline")"
if [ -n "$empty_added$empty_changed" ]; then
  printf 'repo-state.test: clean census was not empty\n' >&2
  exit 1
fi

printf 'committed\n' >committed-after.txt
printf 'COMMITTED_MASKED_SENTINEL\n' >committed-masked.txt
git add committed-after.txt committed-masked.txt
git commit -q -m 'after baseline'

# A later layer can restore the baseline text without erasing an earlier
# index or committed copy from the required 5S review.
printf 'STAGED_MASKED_SENTINEL\n' >'space dir/staged masked.txt'
git add -- 'space dir/staged masked.txt'
git show "$baseline:space dir/staged masked.txt" >'space dir/staged masked.txt'
git show "$baseline:committed-masked.txt" >committed-masked.txt
git add -- committed-masked.txt

printf 'modified\n++count;\ncount += 1;\n' >>tracked.txt
printf 'staged\n' >staged.txt
git add staged.txt
rm delete-me.txt
printf 'untracked\nDEBUG_SENTINEL\n' >untracked.txt
printf 'first' >a-first.txt
printf 'second\n' >b-second.txt
printf 'space file\n' >'space dir/path with spaces.txt'
printf 'ignored debug\n' >ignored.txt

changed="$(bash skills/implementaudit/scripts/repo-state.sh changed-files "$baseline")"
for expected in \
  committed-after.txt \
  committed-masked.txt \
  'space dir/staged masked.txt' \
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

bash skills/implementaudit/scripts/repo-state.sh deliverable "$baseline" untracked.txt | grep -F 'present - untracked new file' >/dev/null
bash skills/implementaudit/scripts/repo-state.sh deliverable "$baseline" 'space dir/path with spaces.txt' | grep -F 'present - untracked new file' >/dev/null

if bash skills/implementaudit/scripts/repo-state.sh deliverable "$baseline" delete-me.txt >/dev/null 2>&1; then
  printf 'repo-state.test: deleted deliverable should be missing\n' >&2
  exit 1
fi

bash skills/implementaudit/scripts/repo-state.sh deliverable not-a-real-ref tracked.txt | grep -F 'baseline unavailable' >/dev/null
added="$(bash skills/implementaudit/scripts/repo-state.sh added-lines "$baseline")"
for line in DEBUG_SENTINEL STAGED_MASKED_SENTINEL COMMITTED_MASKED_SENTINEL \
  '++count;' 'count += 1;' first second
do
  if ! printf '%s\n' "$added" | grep -Fx "$line" >/dev/null; then
    printf 'repo-state.test: missing added line %s\n' "$line" >&2
    exit 1
  fi
done

if printf '%s\n' "$added" | grep -Fx '++ b/tracked.txt' >/dev/null; then
  printf 'repo-state.test: file header leaked into added lines\n' >&2
  exit 1
fi


git config --local color.ui always
colored="$(bash skills/implementaudit/scripts/repo-state.sh added-lines "$baseline")"
git config --local --unset color.ui
if [ "$colored" != "$added" ]; then
  printf 'repo-state.test: forced diff color changed the added-lines census\n' >&2
  exit 1
fi

mkdir "$tmp/git-fault"
cat >"$tmp/git-fault/git" <<'SH'
#!/usr/bin/env bash
if [ "$1" = diff ] && [ "${2:-}" = --cached ]; then
  printf 'simulated Git index census failure\n' >&2
  exit 128
fi
exec "$REPO_STATE_TEST_REAL_GIT" "$@"
SH
chmod +x "$tmp/git-fault/git"
for census in added-lines changed-files; do
  fault_code=0
  REPO_STATE_TEST_REAL_GIT="$(command -v git)" PATH="$tmp/git-fault:$PATH" \
    bash skills/implementaudit/scripts/repo-state.sh "$census" "$baseline" \
    >"$tmp/git-fault.stdout" 2>"$tmp/git-fault.stderr" || fault_code=$?
  if [ "$fault_code" -ne 128 ] || [ -s "$tmp/git-fault.stdout" ] || \
     ! grep -Fq 'simulated Git index census failure' "$tmp/git-fault.stderr"; then
    printf 'repo-state.test: %s masked a failed Git acquisition\n' "$census" >&2
    exit 1
  fi
done

mkdir "$tmp/no-git"
printf 'plain\n' >"$tmp/no-git/file.txt"
(
  cd "$tmp/no-git"
  bash "$tmp/repo with spaces/skills/implementaudit/scripts/repo-state.sh" deliverable no-git file.txt | grep -F 'baseline unavailable' >/dev/null
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

  changed_out="$(bash "$tmp/repo with spaces/skills/implementaudit/scripts/repo-state.sh" changed-files "$rrbaseline" 2>"$tmp/rr-stderr.log")"
  printf '%s\n' "$changed_out" | grep -Fx new-file.txt >/dev/null
  if printf '%s\n' "$changed_out" | grep -F '.IMPLEMENTAUDIT/' >/dev/null; then
    printf 'repo-state.test: run-root path leaked into changed-files\n' >&2
    exit 1
  fi
  grep -F 'excluded 1 run-root path' "$tmp/rr-stderr.log" >/dev/null || {
    printf 'repo-state.test: run-root exclusion note missing from stderr\n' >&2
    exit 1
  }

  added_out="$(bash "$tmp/repo with spaces/skills/implementaudit/scripts/repo-state.sh" added-lines "$rrbaseline" 2>/dev/null)"
  printf '%s\n' "$added_out" | grep -F 'REAL_CHANGE_SENTINEL' >/dev/null
  if printf '%s\n' "$added_out" | grep -F 'RUNROOT_SENTINEL' >/dev/null; then
    printf 'repo-state.test: run-root content leaked into added-lines\n' >&2
    exit 1
  fi
)

# Git quoting cannot affect run-root membership, and each rename endpoint
# participates according to its own path.
mkdir "$tmp/rename-repo"
(
  cd "$tmp/rename-repo"
  git init -q
  git config --local core.quotepath true
  mkdir .IMPLEMENTAUDIT
  printf 'moved inside\n' >outside.txt
  printf 'moved outside\n' >.IMPLEMENTAUDIT/prior.txt
  git add .
  git -c user.email=t@example.invalid -c user.name=t commit -qm init
  start="$(git rev-parse HEAD)"
  git mv outside.txt '.IMPLEMENTAUDIT/renamé.txt'
  git mv .IMPLEMENTAUDIT/prior.txt visible.txt
  printf 'excluded scratchless note\n' >'.IMPLEMENTAUDIT/nôté.txt'
  printf 'untracked text\n' >visible-note.txt
  changed="$(bash "$tmp/repo with spaces/skills/implementaudit/scripts/repo-state.sh" changed-files "$start" 2>"$tmp/rename.stderr")"
  if ! printf '%s\n' "$changed" | grep -Fxq outside.txt ||
     ! printf '%s\n' "$changed" | grep -Fxq visible.txt ||
     printf '%s\n' "$changed" | grep -Fq .IMPLEMENTAUDIT/; then
    printf 'repo-state.test: incorrect rename endpoint or run-root membership\n' >&2
    exit 1
  fi
  grep -Fq 'excluded 3 run-root path(s)' "$tmp/rename.stderr"
  mkdir repo-local-tmp
  local_tmp="$(cd repo-local-tmp && pwd -P)"
  # Bound the output even if a regressed helper attempts to read its own buffer.
  added="$(
    limit=()
    if ! ulimit -f 1024 2>/dev/null; then
      limit=(timeout 10s)
    fi
    TMPDIR="$local_tmp" "${limit[@]}" bash "$tmp/repo with spaces/skills/implementaudit/scripts/repo-state.sh" added-lines "$start" 2>"$tmp/rename-added.stderr"
  )"
  if [ "$added" != "$(printf 'moved outside\nuntracked text\n')" ]; then
    printf 'repo-state.test: incorrect added-lines membership with a repo-local TMPDIR\n' >&2
    exit 1
  fi
  [ -z "$(find "$local_tmp" -mindepth 1 -print -quit)" ]
)

# Untracked links are path evidence, not text from their referents.
mkdir "$tmp/link-repo"
(
  cd "$tmp/link-repo"
  git init -q
  printf 'UNCHANGED_REFERENT_SENTINEL\n' >unchanged.txt
  git add unchanged.txt
  git -c user.email=t@example.invalid -c user.name=t commit -qm init
  link_base="$(git rev-parse HEAD)"
  printf 'REGULAR_UNTRACKED_SENTINEL\n' >regular.txt
  helper="$tmp/repo with spaces/skills/implementaudit/scripts/repo-state.sh"
  [ "$(bash "$helper" added-lines "$link_base")" = 'REGULAR_UNTRACKED_SENTINEL' ]
  if (export MSYS=winsymlinks:nativestrict; ln -s unchanged.txt text-link 2>/dev/null) && [ -L text-link ]; then
    bash "$helper" changed-files "$link_base" | grep -Fxq text-link
    if [ "$(bash "$helper" added-lines "$link_base")" != 'REGULAR_UNTRACKED_SENTINEL' ]; then
      printf 'repo-state.test: link referent leaked into added-lines\n' >&2
      exit 1
    fi
  else
    printf 'repo-state.test: symlink control skipped (fixture link unavailable)\n'
  fi
)

# #76 R3-F10: ignored stale output is package/release evidence only. The same
# bytes remain outside this additional gate for a source-only success surface.
mkdir -p "$tmp/artifact-repo/dist"
(
  cd "$tmp/artifact-repo"
  git init -q
  printf 'dist/\n' > .gitignore
  printf 'source\n' > source.txt
  printf 'current payload\n' > dist/pkg.skill
  current_sha="$(sha256sum dist/pkg.skill | awk '{print $1}')"
  printf '%s  dist/pkg.skill\n' "$current_sha" > published-digests.txt
  git add .gitignore source.txt published-digests.txt
  git -c user.email=t@example.invalid -c user.name=t commit -qm init
  authority_baseline="$(git rev-parse HEAD)"
  bash "$tmp/repo with spaces/skills/implementaudit/scripts/repo-state.sh" \
    ignored-artifact package dist/pkg.skill published-digests.txt "$authority_baseline" >/dev/null || {
      printf 'repo-state.test: current ignored package artifact rejected\n' >&2
      exit 1
    }
  printf 'stale payload\n' > dist/pkg.skill
  if bash "$tmp/repo with spaces/skills/implementaudit/scripts/repo-state.sh" \
      ignored-artifact package dist/pkg.skill published-digests.txt "$authority_baseline" >/dev/null 2>&1; then
    printf 'repo-state.test: stale ignored package artifact accepted\n' >&2
    exit 1
  fi
  bash "$tmp/repo with spaces/skills/implementaudit/scripts/repo-state.sh" \
    ignored-artifact source dist/pkg.skill published-digests.txt "$authority_baseline" >/dev/null || {
      printf 'repo-state.test: source-only control was subjected to package currency\n' >&2
      exit 1
    }
  stale_sha="$(sha256sum dist/pkg.skill | awk '{print $1}')"
  printf '%s  dist/pkg.skill\n' "$stale_sha" > ad-hoc.txt
  if bash "$tmp/repo with spaces/skills/implementaudit/scripts/repo-state.sh" \
      ignored-artifact release dist/pkg.skill ad-hoc.txt "$authority_baseline" >/dev/null 2>&1; then
    printf 'repo-state.test: ad-hoc untracked release digest accepted as authority\n' >&2
    exit 1
  fi
  printf '%s  dist/pkg.skill\n' "$stale_sha" > published-digests.txt
  if bash "$tmp/repo with spaces/skills/implementaudit/scripts/repo-state.sh" \
      ignored-artifact release dist/pkg.skill published-digests.txt "$authority_baseline" >/dev/null 2>&1; then
    printf 'repo-state.test: modified tracked release digest accepted as baseline authority\n' >&2
    exit 1
  fi
)

# #211: L4 remains reachable from every governing loop after a failed check.
interruption_owner="$repo_root/skills/implementaudit/scripts/repo-state.sh"
for loop in L1 L2 L3 L5; do
  test "$(bash "$interruption_owner" interrupt-after-check "$loop" 1)" = L4
  test "$(bash "$interruption_owner" interrupt-after-check "$loop" 0)" = "$loop"
done
for value in unknown -1 256 01; do
  if bash "$interruption_owner" interrupt-after-check L2 "$value" >/dev/null 2>&1; then
    printf 'repo-state.test: malformed observed exit accepted: %s\n' "$value" >&2
    exit 1
  fi
done
if bash "$interruption_owner" interrupt-after-check L4 1 >/dev/null 2>&1; then
  printf 'repo-state.test: another L4 entry falsely treated as a caller loop\n' >&2
  exit 1
fi

printf 'repo-state.test: ok\n'
