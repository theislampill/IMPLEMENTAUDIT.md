# Repository State Comparison

Use this reference when final audit, deliverable checks, release-readiness
checks, or cleanliness scans need to answer: what changed since the run
baseline?

## Rule

Compare the baseline commit to the complete working tree, not just to `HEAD`.

```text
tracked changes = git diff <baseline>
untracked files = git ls-files --others --exclude-standard
invalid baseline / no git = existence-only fallback
```

`git diff <baseline>` with one revision compares the baseline commit to the
current working tree. That includes committed-after-baseline, staged, unstaged,
and deleted tracked changes. A two-dot range such as `<baseline>..HEAD` compares
only commits and misses uncommitted work.

Untracked files are diff-invisible, so they must be listed separately.

Ignored files are intentionally not treated as untracked deliverables by
`--exclude-standard`. If ignored output matters for an audit, record an explicit
cleanliness or deliverable override in the phase/audit spec and cite the
owner/source.

## Helper

Use the native helper instead of hand-typing the git incantation:

```bash
bash "${IMPLEMENTAUDIT_SKILL_DIR:-skills}"/scripts/repo-state.sh deliverable <baseline> <path>
bash "${IMPLEMENTAUDIT_SKILL_DIR:-skills}"/scripts/repo-state.sh changed-files <baseline>
bash "${IMPLEMENTAUDIT_SKILL_DIR:-skills}"/scripts/repo-state.sh added-lines <baseline>
```

The helper is read-only. It does not mutate files, repo config, or the git
index. Paths with spaces must be quoted by the caller.

## Audit use

- `deliverable`: proves whether a path is present, missing, untracked, changed,
  unchanged, or baseline-unavailable.
- `changed-files`: feeds final audit and release-readiness review.
- `added-lines`: feeds cleanliness and overclaim scans, including untracked text
  files.

If the baseline is invalid, mark the evidence as weaker. Existence-only
fallback is useful for orientation, not full release proof.
