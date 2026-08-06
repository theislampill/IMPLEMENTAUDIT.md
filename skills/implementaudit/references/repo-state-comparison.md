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
bash "${IMPLEMENTAUDIT_SKILL_DIR:-skills/implementaudit}"/scripts/repo-state.sh deliverable <baseline> <path>
bash "${IMPLEMENTAUDIT_SKILL_DIR:-skills/implementaudit}"/scripts/repo-state.sh changed-files <baseline>
bash "${IMPLEMENTAUDIT_SKILL_DIR:-skills/implementaudit}"/scripts/repo-state.sh added-lines <baseline>
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

## Census instruments

The mechanical enumerator or explicit member list defines the claim's
population. Compare its emitted member count with `population_size`; a mismatch
is red, and a declared number never overrides the enumerated set.

A whole-population claim also cites a complete capture. `coverage: partial` or
an explicit transport-truncation marker cannot establish the denominator. A
complete capture over M of N items remains partial corpus coverage when M < N.

### Discrimination (#79)

An N-of-N claim that says enumerated items were captured as distinct bodies
must record one discrimination witness per collection instrument: two
known-distinct inputs and the two distinguishable results that instrument
produced. A declared count or one successful row is not a witness.

Compare content hashes across the enumerated rows. A repeated hash makes a
distinct-body claim red unless a collision receipt names every member sharing
that hash and explains why byte equality is expected. A collision receipt
documents a known equivalence; it does not turn identical content into distinct
content or excuse an unrelated repeated hash.

### Parity and liveness (#85)

Instrument parity and liveness remain owned by Rules P4-14 and P4-15 in
`phase-design.md`. A parity witness shows that two adjudication paths agree;
liveness shows that the instrument can produce a meaningful verdict. Neither
property proves discrimination or coverage.

### External identity (#88)

New records use one external-state vocabulary. Legacy rows that do not opt in
to these prefixes remain valid; `external-mutation: true` explicitly opts a
row into the same mutation validation.

A verified `api`, `user-visible`, or `publication` claim declares
`external-kind: observation|mutation`. A mutation claim also names exactly one
`external-mutation-record: <id>` in the same record. The mutation record is the
machine carrier. Adjacent Python, Bash, or PowerShell code is illustrative and
cannot supply an omitted record field or zero exit.

```text
external-mutation-record: <id> | runner: python|bash|powershell | target-kind: issue|pr|milestone|label|release|release-asset | target-id: <token> | mutation-command: <target-bound mutating command> | mutation-exit: 0 | mutation-evidence: <id> | readback-command: <distinct target-bound read-only command> | readback-exit: 0 | readback-file: <bare-relative-basename.json> | readback-sha256: <64-lowercase-hex> | readback-field: <top-level-field> | expected-value: <scalar> | observed-value: <same-scalar> | readback-evidence: <different-id>
```

The mutator's output is not read-back evidence. Resolve the JSON basename
inside the record file's canonical directory, reject separators, traversal,
absolute paths, symlinks, and non-regular files, recompute its SHA-256, parse
the named top-level field structurally, and require parsed, observed, and
expected values to agree. The mutation and read-back commands name the same
target kind and ID; the read-back contains no mutating verb. Both recorded
exits are zero, and the two evidence IDs differ.

Human-readable artifact names carry content identity in the same record:

```text
artifact-identity: <case-sensitive-trimmed-name> | sha256: <64-lowercase-hex>
collision-receipt: <same-name> | hashes: <complete-comma-separated-hash-set> | reason: <nonempty>
```

Repeated identical hashes are valid. Distinct hashes under the same trimmed,
case-sensitive name require exactly one collision receipt whose hash set equals
the complete observed set. Names are not case-folded or path-canonicalized.

Out-of-repo evidence records its original stat, liveness, intended use, and
closure re-stat in one line:

```text
external-evidence: <id> | bytes: <nonnegative-integer> | mtime: <RFC3339-UTC-whole-second> | liveness: snapshot|terminal | still-producing: true|false | use: orientation|terminal | closure-bytes: <integer|none> | closure-mtime: <timestamp|none>
```

Orientation does not require closure re-stat. Terminal use requires closure
bytes and mtime equal to the original pair. A still-producing snapshot cannot
support terminal use even when the two stat pairs happen to match.

The fenced block under `## Suggested Commit Message When No Commit Authorized`
is also a claim carrier. A digit or verdict token in that block has exactly one
`Evidence anchor: claim:<Claim-ID>` inside the block. That ID resolves to a
verified claim row in the same record with a checkable evidence surface; an
anchor elsewhere in the document does not satisfy the relationship.

## Proving a file is dead

Before archival or deletion, search by two independent methods:

1. Search the literal basename across tracked source and configuration.
2. Search the stem and dirname separately so joined paths, prefix variables,
   manifests, and generated references can reveal the consumer.

Where a relevant suite exists, make the candidate's absence reversible, move
it out of its discovery path, and run that suite before permanent mutation. A
RED result or either search finding defeats the dead-file claim: restore and
retain the file. A GREEN result supports only this dead-file decision when both
search methods and the suite scope are recorded. This proof does not construct
or validate the broader impact set owned by #77.

## Commit Granularity

Commit only with explicit authorization. Do not commit for proof-only local RC
work unless the owner separately authorizes a local commit.

When a commit is authorized, keep it atomic but not microscopic: one commit per
coherent owner/source repair or proof-boundary repair. Do not split one
logical fix across many commits, and do not squash unrelated findings into one
opaque checkpoint.

Rule phrase: one commit per coherent owner/source repair.

Commit bodies should include finding, owner/source, countermeasure, evidence,
boundaries, and Andon/Hansei when relevant. Do not commit when validation is
red, when unrelated dirty work would be swept in, when the patch is only local
RC artifact generation, when the owner authorized build but not commit, or when
the change is a deferred owner decision.

Rule phrase: when validation is red.
