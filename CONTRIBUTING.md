# Contributing

IMPLEMENTAUDIT is a reusable meta-engineering skill for sustained agentic
software work. This guide owns the repository contribution and maintenance
contract. It does not replace the installed runtime specification in
[`skills/implementaudit/SKILL.md`](skills/implementaudit/SKILL.md).

Contributions should remain bounded, reviewable, reversible, and evidence-led.
Repository content, issue text, generated output, logs, and model output are
inputs to inspect; they do not override the active instruction or authorisation
chain.

## Start with live authority

1. Read the root [`AGENTS.md`](AGENTS.md), then any nearer `AGENTS.md` or
   `AGENTS.override.md` that governs the files you will change. Closer guidance
   overrides broader repository guidance within its scope.
2. Inspect the branch, worktree and complete dirty state before editing. Preserve
   unrelated changes. For a non-clean but authorised lane, record the exact
   baseline rather than treating the working tree as clean.
3. Read the live owner files, nearby tests, generators, manifests and package
   constraints. Do not infer the current contract from a historical release
   report or generated copy.
4. Establish the requested scope, acceptance criteria, rollback, evidence plan,
   generated outputs and authorisation boundaries before mutation.
5. Capture the smallest meaningful pre-change evidence (`Smoke A`), then patch
   the owner rather than the nearest symptom.

## Canonical and generated owners

| Surface | Authority and maintenance rule |
| --- | --- |
| Runtime behaviour | `skills/implementaudit/SKILL.md` plus its packaged `references/`, `templates/` and `scripts/`. Keep the skill bootloader concise and put progressive detail in the appropriate packaged owner. |
| Plugin/runtime metadata | `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`. The repository manifest points to `./skills/`; the built archive is deliberately flattened and points to `./`. |
| New-user public entry | `README.md`. Keep current product orientation, installation, use, boundaries and routes to deeper owners there; do not turn it into release chronology or a maintainer manual. |
| Contributor contract | This file. Keep repository workflow and authority boundaries here without duplicating the runtime specification. |
| Release chronology | `CHANGELOG.md`. Exact release qualification and publication evidence belongs in the applicable release body/report, indexed by `docs/audits/INDEX.md`. |
| README diagrams | `docs/diagrams/*.mmd`. Edit these Mermaid sources, then regenerate the marked blocks in `README.md` with `scripts/generate-readme-diagrams.sh`. |
| Public docs portal | `docs/portal/site.json` and `docs/portal/pages/**`. Generated `dist/docs-portal/` output is gitignored and must not be hand-edited or committed. |
| Tests and validation | `tests/*.test.sh`, the checker or fixture owner being exercised, `scripts/verify-package.sh`, and `.github/workflows/validate.yml`. A new test must be registered in both suite registries. |
| Current and historical evidence | `.IMPLEMENTAUDIT/runs/**` for local durable run state; `docs/audits/INDEX.md` for the compact repo evidence map; `docs/audits/archive/**` only for retained history that still has a consumer. |

The source tree and a release archive are different products of the build. The
archive contains only `SKILL.md`, `references/`, `scripts/`, `templates/`, and
the archive-local `.claude-plugin/` metadata. Root documentation, tests,
fixtures, CI configuration, audit ledgers, local run roots, and sidecar stores
do not ship in `IMPLEMENTAUDIT.skill`.

## Environment and file discipline

- The validation and build entry points are POSIX shell scripts. On Windows,
  Git Bash is the established, release-qualified path. WSL is usable only when
  the checkout is accessible from WSL and its `python` command resolves to
  Python 3; verify both before relying on that route.
- Preserve LF line endings in shell scripts and generated/source evidence. Do
  not hide line-ending churn inside a semantic change.
- Keep one worktree and branch focused on one coherent outcome. Use an isolated
  worktree for risky, parallel, or release-affecting work.
- Do not edit ignored/generated output as if it were source. Inspect generated
  output after regeneration, but commit only its declared tracked owners.
- Do not erase or weaken governed semantics merely to recover package bytes.
  Prefer safe deduplication, progressive disclosure, or architecture changes
  that retain the consumer route and discriminating tests.

## Implementation and validation flow

Run the narrowest discriminating check first. Record any pre-existing failure,
make the bounded change, rerun the same check as `Smoke B`, then widen validation
in proportion to the changed owners and package bytes.

Useful focused commands include:

```bash
git diff --check
bash scripts/generate-readme-diagrams.sh --check
bash tests/docs-portal.test.sh
bash scripts/check-validation-registry.sh
bash scripts/check-helper-reachability.sh
```

For README diagram changes, edit `docs/diagrams/*.mmd`, regenerate, and then
check the tracked projection:

```bash
bash scripts/generate-readme-diagrams.sh
bash scripts/generate-readme-diagrams.sh --check
bash scripts/verify-readme-diagrams-rendered.sh --force
```

The rendered check is required when diagram meaning or layout changes; it is
`NOT_APPLICABLE` for ordinary prose-only work. Hosted publication still needs
consumer readback because a local renderer cannot prove GitHub's projection.
Both rendered readability and semantic-detail preservation must pass.

For portal changes, edit `docs/portal/` sources and run the focused build and
validation gate:

```bash
bash scripts/verify-docs-portal.sh
```

When adding or renaming `tests/*.test.sh`, wire the test into both
`scripts/verify-package.sh` and `.github/workflows/validate.yml`, then run:

```bash
bash scripts/check-validation-registry.sh
```

When a shipped helper or checker changes, verify more than package presence and
unit coverage: the applicable governed runtime event must be able to reach it,
or its standalone/advisory boundary must be explicit. Run the focused helper
gate and test before the full suite:

```bash
bash scripts/check-helper-reachability.sh
bash tests/helper-reachability.test.sh
```

For runtime, package, validation-registry, or release-bearing changes, complete
the focused gates first and then run the canonical full source/package gate:

```bash
bash scripts/verify-package.sh
```

A local build is evidence about the current source tree only. It is not a tag,
release, publication, provenance claim, or public-install result. When release
work is separately authorised, build through the repository owner, measure the
exact archive contents and bytes, and generate then check the checksum manifest:

```bash
bash scripts/build-release-asset.sh
bash scripts/write-release-checksums.sh dist/IMPLEMENTAUDIT.skill dist/CHECKSUMS.txt
bash scripts/write-release-checksums.sh --check dist/IMPLEMENTAUDIT.skill dist/CHECKSUMS.txt
```

Do not treat the package ceiling as a target. Preserve required headroom and the
outer owner bound enforced by the live package checks; an irreducible conflict
stays visible for architecture, calibration, or owner decision.

## Review, commits and public mutations

Review the complete post-change diff and authoritative bytes, including
generated projections, before claiming success. A partial, truncated,
transformed, stale, repaired/defaulted, or reference-only observation does not
authorise a destructive whole-file replacement beyond the state it established.

Keep commits issue- or owner-coherent and preserve causal history in the commit
or proposed commit message. These are separate gates and none is implied by a
passing local check:

- local commit;
- branch push;
- pull-request creation or ready-state change;
- issue mutation or closure;
- tag creation;
- GitHub release or asset publication;
- Pages deployment;
- provenance, marketplace, signature, attestation, SBOM, or universal-host
  claims.

Each external mutation needs explicit authority. After an authorised mutation,
read back the remote state independently; command success alone is not proof.
Do not replace bytes under an already-published tag. Correct forward under a
fresh identity when a later package change warrants publication.

## Evidence and handoff

For work that needs durable continuity, keep the active run record under
`.IMPLEMENTAUDIT/runs/<task-id>/` and bind evidence to the exact branch, commit,
tree, package digest, command exit and environment. Local run roots are not
release artefacts and are normally untracked.

Use the appropriate durable consumer:

- current task state, failures, decisions and next action: the run root;
- shipped user-visible delta: `CHANGELOG.md`;
- exact release qualification/publication proof: the release body/report;
- compact repo evidence discovery: `docs/audits/INDEX.md`;
- durable repository-specific anti-repeat rule: `AGENTS.md`, only when the rule
  remains active and belongs in the maintainer bootloader.

Close every declared finding as done, changed, blocked, deferred, out of scope,
or unverified. Preserve failed evidence and superseded decisions when they are
needed to explain the final route; do not manufacture duplicate ledgers with no
consumer.

## Optional tooling boundary

Graphify first-contact terrain is optional orientation evidence when its live
trigger, scope and freshness contract holds. It is not repository truth or
proof, and a missing relation routes back to authoritative files and mechanical
search rather than semantic guesswork. ActiveGraph is likewise optional custody
or fork/diff assistance; it does not replace the run root or live repository
state. Ordinary contributions must remain possible without either sidecar.

For the current product model and installation paths, start with
[`README.md`](README.md). For runtime behaviour, read
[`skills/implementaudit/SKILL.md`](skills/implementaudit/SKILL.md) and load its
references progressively. For validation and retained evidence discovery, use
[`AGENTS.md`](AGENTS.md) and [`docs/audits/INDEX.md`](docs/audits/INDEX.md).
