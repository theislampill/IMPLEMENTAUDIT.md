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

## Landed post-conditions (#76)

State the intended post-condition, then put the exact mutation command inside
one checker-controlled window. The checker captures the same target, executes
that command without a shell, and inspects the landed file before returning.
Tool success and a predicate that was already true are not landing evidence.
Use one exact declaration:

```text
--mutation-window <path> --expect occurrences:<n>:<literal> -- <command> [args...]
--mutation-window <path> --expect anchor:<literal> -- <command> [args...]
--mutation-window <path> --expect hunk:<one-based-line>:<literal> -- <command> [args...]
```

Counts are exact and literals are fixed strings. The command is passed as an
argument vector, not shell text. The single process rejects a nonzero command,
an absent/nonregular target, identical before/after bytes, and a condition
already true before the command. It validates the expectation grammar and
false-before precondition before launching the mutation command, so rejected
declarations cannot produce side effects. It emits canonical target, `HEAD`, command
exit, and both SHA-256 identities. Former separate capture/receipt modes are
rejected, so no stale, reusable, substituted, or recomputable authority exists.
A whole capture from #75's verification window may carry this output; a tailed
live pipe may not.

## Generated-artifact detection before edit (#76)

Before editing a suspected output, run `summarize-repo.sh --generated-owner
<path>`. Content markers (`DO NOT EDIT`, `auto-generated`, `generated by`),
generated-output path components, and target-naming regeneration gates are
reported before mutation. A generated result redirects the edit to the named
generator. Quoted JSON/YAML or unquoted `generator: hand-authored` is the
explicit negative control. A declaration combined with a generated marker or
target-naming harness gate is contradictory authority and fails.

## Declared duplication sets (#76)

Declare intentional duplicates once in `.IMPLEMENTAUDIT/duplication-sets.txt`:

```text
<set-name>: <path>::<unique-line-anchor>, <path>::<unique-line-anchor>
```

`check-duplication-parity.sh` requires at least two distinct canonical regular
files inside the repository, exactly one anchored assignment line per member,
equal right-hand-side values, and equal immediately preceding comment blocks.
Path and anchor aliases cannot count one physical file twice; symlink parents
are refused. This preserves both `WINDOW_SECONDS = 30` and the prose that
justifies it. The manifest admits intended duplication; it does not excuse
divergence.

## Pin-chain map (#76)

Run `map-pin-chain.sh <path> [--expect-hops N]` once at plan time for every
artifact the phase may edit. It performs read-only breadth-first discovery of
consumers that name the prior hop alongside `sha256`, `--check`, `manifest`,
`byte-identical`, or regeneration signals. The map is advisory discovery
evidence, not proof of completeness; committed harness/checker gates remain
authoritative and must be replayed after the edit.

## Stale ignored build artifacts (#76)

The default changed-files census still excludes ignored files. When the
success surface is `package` or `release`, add:

```text
repo-state.sh ignored-artifact <package|release> <artifact> <published-digest-record> <authority-baseline>
```

The supplied authority is a standard lowercase SHA-256 record containing
exactly one row for the ignored artifact. For package or release claims, that
record must be tracked with identical bytes at the declared full-SHA ancestor;
an untracked or locally rewritten digest is not publication authority. A digest
mismatch is stale evidence and fails until the artifact is removed, renamed,
or rebuilt to the declared identity. The same four-argument command with
surface `source` is a negative control and adds no package-only obligation.
Countermeasure non-target effects remain owned by #92; cross-reference them
rather than duplicating that rule.

## Package and publication identity (#89)

A plain package build proves local bytes only; it is not publication proof.
Before a release gate can claim a forward release or a same-version
republication, run:

```text
scripts/verify-package.sh --release-identity <forward|republish> <previous-version> <release-commit>  # source repo only
```

`forward` requires the two canonical version owners to agree and differ from
the previous published version. `republish` requires them to retain that
version; both modes require the declared commit to be an ancestor of current
`HEAD` and its tree to equal current `HEAD` tree, allowing metadata-only merge
identity without permitting unrelated same-tree authority or byte drift.
The previous version is derived from the ordered published-version headings in
`CHANGELOG.md`, not trusted from the caller. `republish` also requires that
commit's own `CHANGELOG.md` additions to contain distinct lowercase SHA-256 and
byte-count values for `IMPLEMENTAUDIT.skill` labeled `superseded` and
`superseding`. The superseding digest and byte count must equal the
deterministically built candidate asset. A pair from another commit, another
artifact, or fabricated bytes cannot discharge the gate.

The completed #96 v0.3.2.0 correction remains inspectable with
`scripts/build-release-asset.sh --check-historical-release-record`, but that
command is a pinned, nonqualifying history check. It cannot qualify a current
or prospective release and `retroactive` is not a release-identity mode.

`build-release-asset.sh --check` also inspects an existing ignored
`dist/IMPLEMENTAUDIT.skill`: if its digest is labeled `superseded` in
`CHANGELOG.md`, package proof fails until the artifact is removed, renamed, or
rebuilt. Source-only runs retain the #76 negative-control boundary and do not
gain this package/release obligation.

A publication closure claim carries both its evidence digest and a contained,
hash-bound current-digest receipt:

```text
claim: <id> | surface: publication | status: verified|unverified | evidence-surface: publication | evidence-digest: <sha256>
publication-identity: <id> | live-digest-file: <bare-file.sha256> | live-file-sha256: <sha256> | live-digest: <sha256> | disposition: verified|SUPERSEDED
```

Equal evidence/current digests use `verified`. Drift cannot remain verified;
retain it as `status: unverified` with disposition `SUPERSEDED`, reusing #87's
vocabulary rather than inventing another terminal state.

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
