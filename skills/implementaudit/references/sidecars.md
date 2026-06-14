# Optional Sidecars And First-Run Tooling

Use this reference when optional Graphify or ActiveGraph tooling might help
orientation, custody, first-run onboarding, or IMPLEMENTAUDIT self-maintenance.
Sidecars are progressive detail, not always-loaded ceremony.

## Graphify-Assisted Gemba

Graphify is orientation only. Live files remain proof. A Graphify path, node, or
summary may suggest where to inspect, but it does not prove correctness,
authorize mutation, replace Smoke A/B, or override `AGENTS.md`.

If Graphify output is stale, ambiguous, or contradictory, stale output triggers Andon or fallback
to ordinary live-file Gemba. Record the stale-output
Andon/fallback in the run ledger or `sidecars.md`, then inspect live source,
fixtures, scripts, manifests, and generated artifacts before acting.

Graphify absence does not block consumer runs. Continue with live-file Gemba,
repo-state comparison, checkers, and final audit evidence. IMPLEMENTAUDIT self-maintenance may use Graphify
terrain when the owner authorizes extraction
or indexing, but no sidecar output enters the release package.

## First-Run Tooling Onboarding

First-run onboarding distinguishes four separate actions:

- detect optional tools and existing sidecar outputs;
- document install or usage commands for the owner;
- install or configure tools only after explicit authorization;
- index/export/write sidecar outputs only after separate explicit
  authorization.

Rule phrase: index/export/write sidecar outputs only after separate explicit authorization.

No silent install. No silent indexing. No silent export. Tool availability is
tooling evidence only, not audit correctness proof.

Record first-run status with this shape:

| Tool | Detected | Documented | Installed | Indexed/exported | Authorization | Evidence boundary |
|---|---|---|---|---|---|---|
| Graphify | yes/no/stale | command shown/skipped | no unless authorized | no unless authorized | none/owner | orientation only |
| ActiveGraph | yes/no/configured | command shown/skipped | no unless authorized | no unless authorized | none/owner | custody only |

Authorization gates remain separate for tool installation, Graphify indexing,
ActiveGraph store setup, ActiveGraph export, local commit, push, tag, release,
publication, issue creation, license choice, marketplace claim, and provenance.

## Package Boundary

Sidecar outputs stay outside the runtime package:

- no `graphify-out/`;
- no `.graphify/`;
- no `.activegraph/`;
- no `.IMPLEMENTAUDIT/`;
- no `custody.db`;
- no `.jsonl` diagnostics.

Package proof uses archive listing, manifest equality, checksums, install-copy
smoke, and installed file existence. It does not use model-visible full
sidecar or full installed-payload readback as proof.
