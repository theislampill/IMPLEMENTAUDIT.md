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

Smoke/final: use the read-only helper:

```bash
bash "${IMPLEMENTAUDIT_SKILL_DIR:-skills/implementaudit}"/scripts/repo-state.sh deliverable <baseline> <path>
bash "${IMPLEMENTAUDIT_SKILL_DIR:-skills/implementaudit}"/scripts/repo-state.sh changed-files <baseline>
bash "${IMPLEMENTAUDIT_SKILL_DIR:-skills/implementaudit}"/scripts/repo-state.sh added-lines <baseline>
```

The helper is read-only. It does not mutate files, repo config, or the git
index. Paths with spaces must be quoted by the caller.

## Stacked integration merge safety

For each link in a cumulative or otherwise dependent PR stack, preserve one
five-link receipt before advancing:

1. **Successor retarget.** After its predecessor lands, retarget the successor
   to the declared next base and read back the PR base.
2. **Unchanged head.** Read back the successor head SHA and require the exact
   pre-retarget head; a rewritten head invalidates earlier qualification.
3. **Main ancestry.** Require authoritative main to contain the predecessor's
   landed commit/tree before treating it as the successor base.
4. **Logical patch identity.** Compare the successor's issue-owned patch before
   and after retarget (stable patch ID or byte-identical logical diff) and stop
   on mismatch.
5. **Resulting-tree equality or exact-tree requalification.** Compare the
   synthetic/landed resulting tree with the qualified expected tree. If tree
   equality is unavailable, qualify that exact resulting tree before the next
   merge instead of carrying forward metadata-only checks.

A retarget command, merge command, or green check alone proves none of the
other links. Record all five, or stop the stack at the first missing receipt.

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

Before an authorized push or merge, bind its configured automatic effects to
the same plan/readback boundary. Run the closure checker with
`--automatic-effects <repo-root> <event> <ref> <mutation-plan>` and record:

```text
automatic-effect-preflight: event: push | ref: <branch> | workflows: <sorted-paths|none> | effects: <sorted-direct-effects|none> | post-state-readback: <sorted-readbacks|trigger-read-only> | excluded-outcomes: <truthful-list|none>
```

The checker reads `.github/workflows/*` before mutation. A matching workflow
requires `workflow-runs@pushed-sha`; a directly identifiable Pages deployment
also requires `deployments@pushed-sha`. The post-state probe is performed only
when already authorized. No match stops after the trigger read. A configured
effect cannot be called excluded or impossible, and the mutator's output never
substitutes for the pushed-SHA readback. Listing an effect already entailed by
the authorized trigger is coverage, not a second grant of authority. Quoted
keys are normalized inside the strict structural subset; malformed or
unsupported triggers, aliased/tagged/block branch-filter scalars, arbitrary
text masquerading as `steps[*].uses`, and symlinked/escaping workflow paths
fail closed.

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

When `.IMPLEMENTAUDIT/duplication-sets.txt` exists, dispatch
`check-duplication-parity.sh <manifest>`; divergence blocks its phase. No set means no
whole-repo sweep.

## Helper dispatch (#157)

Gate derives source repo `scripts/*.sh`; presence/tests/self-use/wildcards are
not dispatch. Fields `H|C|T|O|K|A|N` mean helper/class/trigger/owner/caller/
args/no-event. Classes `A/R/O/S/I`: automatic/required/optional/standalone/
internal; owners `P/R/C/S/V`: PROTOCOL/this/child-agents/SKILL/validator.
R runs `bash <skill-dir>/scripts/<H> <A>` and blocks T; A/I need K; O/S never gate.
One audit object; no event, no sweep. Phased Stage 0 runs `detect-env.sh`; run
`validate-audit-spec.sh <spec>` for a spec and `detect-stack.sh` only for standalone diagnosis.

Graphify modes: `bash <skill-dir>/scripts/validate-run-root.sh --graph-freshness
<graph.json> <repo-root>` blocks stale; `bash <skill-dir>/scripts/validate-run-root.sh
--graph-scope <catalog> <repo> <path> [path...]` selects smallest fresh; `bash
<skill-dir>/scripts/validate-run-root.sh --graph-parent <catalog> <repo> <scope>
<reason>` revalidates then broadens/falls back.

When the native audit object opens a scarce-resource phase, `validate-phase.sh` consumes its receipt, launch, stub, hash, environment-key names, and terminal then invokes `check-authorization-binding.sh --phase <phase> --rehearsal <receipt> --launch <launch>`. The wrapper crosses a checker-owned mediator to the bounded producer; its zero exit precedes checker terminal publication. A failed rehearsal blocks launch; repair/re-run stays manual.

helper-mode: validate-run-root.sh|--graph-freshness|<graph.json> <repo-root>|stale
helper-mode: validate-run-root.sh|--graph-scope|<catalog> <repo> <path> [path...]|smallest
helper-mode: validate-run-root.sh|--graph-parent|<catalog> <repo> <scope> <reason>|fallback
helper-mode: check-authorization-binding.sh|--phase --rehearsal --launch|<phase> <receipt> <launch>|failed-rehearsal-blocks-launch|scripts/validate-phase.sh

helper-route: check-authorization-binding.sh|R|auth|P|-|--auth <a> --invocation <i> --state <s>|no-param
helper-route: check-closure-surface.sh|R|final|P|-|<closure-record> --superseded-plan <each-replaced-plan> --steer-dir <run-root> --plan-cycle-record <each-cycle-accounted-plan>|inputs
helper-route: check-duplication-parity.sh|R|duplication-set|R|-|<manifest>|no-set
helper-route: check-evidence-anchor.sh|R|scope|P|-|--artifact ... --tree ...|disjoint
helper-route: check-handoff-packet.sh|R|handoff-packet|P|-|<p> --repo-root <r>|same-session
helper-route: check-lesson-lift.sh|R|final-record|P|-|<c> --repo-root <r>|closure
helper-route: check-respec-impact-set.sh|A|impact-set|V|V|impact-set|no-impact
helper-route: claim-run.sh|R|run-root|S|-|<task>|initialize
helper-route: custody-append.sh|O|authorised-mirror|P|-|<store> <run> <event> <type> <json>|absent
helper-route: detect-env.sh|R|Stage-0|R|-|none|phased
helper-route: detect-stack.sh|S|stack-diagnosis|R|-|none|not-auto
helper-route: lane-survivor-inventory.sh|O|interrupted-lane|C|-|<root> --expect <path>|unrelated
helper-route: map-pin-chain.sh|R|artefact-edit|R|-|<path> [--expect-hops N]|no-completeness
helper-route: repo-state.sh|R|Smoke/final|R|-|changed-files <baseline>|read-only
helper-route: summarize-repo.sh|S|repo/owner-diagnosis|R|-|[--generated-owner <path>]|targeted-default
helper-route: validate-audit-spec.sh|R|audit-spec|R|-|<spec>|no-spec
helper-route: validate-phase.sh|R|phase|P|-|<phase>|exit-code
helper-route: validate-run-root.sh|R|run-root|S|-|<root>|invalid

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

Class B messages require a body. A message is Class B when its conventional
type is `feat`, `fix`, `perf`, or `revert`; its subject carries `!`; its body
carries `BREAKING CHANGE`; its subject has no parseable conventional type; or
the authoritative run ledger links it to a finding, Andon, gate, or decision.
For the last case, invoke the checker with `--ledger-linked`; do not infer
decisions from verbs in message prose. Ledger linkage cannot demote a message.

Otherwise the message is Class M and its body is optional. This includes
honestly typed regeneration, formatting, typo, pure-move, dependency/lockfile,
and comment-only work. Mislabeling behavior as mechanical is a false claim
owned by the closure truthfulness check, not a second semantic classifier here.

A Class B body names what changed, why, an evidence anchor, and finding/issue
linkage when the commit affects a finding or gate. The closed anchor grammar is
an abbreviated or full commit SHA, `path:line`, a check or command name with its
exit status, a fixture or test path, or a landed post-condition token such as
`occurrences: N`, `anchor: <value>`, or `hunk: <spec>`. A bare tally such as
`18/18` is not an anchor. Existing evidence-anchor rules independently govern
whether a present token is adequate for the claim.

Use the read-only structure checker before committing or proposing Class B
text:

```bash
bash "${IMPLEMENTAUDIT_SKILL_DIR:-skills/implementaudit}"/scripts/repo-state.sh \
  commit-message <message-file> [--ledger-linked]
```

The checker derives the declared class and enforces body, anchor, and, when
requested, linkage presence. It does not scan history or score what/why prose.
Concrete-object quality and first-use expansion of codenames or internal labels
remain reviewer judgments; each message must stand alone for a fresh reader.

Commit bodies should also retain owner/source, countermeasure, boundaries, and
Andon/Hansei when relevant. Do not commit when validation is red, when
unrelated dirty work would be swept in, when the patch is only local RC artifact
generation, when the owner authorized build but not commit, or when the change
is a deferred owner decision.

Rule phrase: when validation is red.
