# Optional Sidecars And First-Run Tooling

Use this reference only after recording a sidecar applicability decision.
Graphify is a candidate only when all of these observable triggers hold: the
repo is unfamiliar to this run, it is majority-code by file count, the question
is terrain-shaped (components or the neighborhood of a named component), and
one `rg`, `git grep`, or `git ls-tree` query cannot answer it. ActiveGraph is a
candidate only for authorized `fork` / `diff` resume-from-checkpoint assistance.
Sidecars are progressive detail, not always-loaded ceremony.

Any reference-shaped question is an anti-trigger. Use `git grep -ln <basename>`
for data-file consumers, identifier `rg` for module-level constants or
duplicated literals, live-file reads for embedded languages, `git ls-tree` plus
`rg` for prose carriers, and native Git commands for topology. These are known
limits as tested, not universal claims about either tool.

## Graphify-Assisted Gemba

Graphify is orientation only. Live files remain proof. A Graphify path, node, or
summary may suggest where to inspect, but it does not prove correctness,
authorize mutation, replace Smoke A/B, or override `AGENTS.md`.

Before any Graphify query, execute the packaged freshness check:

```bash
bash "${IMPLEMENTAUDIT_SKILL_DIR:-skills/implementaudit}"/scripts/validate-run-root.sh \
  --graph-freshness <graph.json> <repo-root>
```

It reads `built_at_commit` from `graph.json` and compares it with
`git rev-parse HEAD`. A mismatch fires `stale-sidecar`; the terrain is unusable
for orientation. Record both full SHAs, the command, exit status, and fallback
in `sidecars.md`, then use ordinary live-file Gemba. Ambiguous or contradictory
output also falls back to live files. `graphify diagnose multigraph` may be an
advisory integrity companion after its live `--help` confirms the flags; it is
not the freshness gate.

Graphify absence does not block consumer runs. Continue with live-file Gemba,
repo-state comparison, checkers, and final audit evidence. IMPLEMENTAUDIT self-maintenance may use Graphify
terrain when the owner authorizes extraction
or indexing, but no sidecar output enters the release package. Prefer
`--code-only --no-cluster` with `--out` outside the target repo; an in-repo
output path or ignore-file edit is a separate mutation decision.

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
| ActiveGraph | yes/no/configured | command shown/skipped | no unless authorized | no unless authorized | none/owner | checkpoint or non-authoritative mirror |

Authorization gates remain separate for tool installation, Graphify indexing,
ActiveGraph store setup, ActiveGraph export, local commit, push, tag, release,
publication, issue creation, license choice, marketplace claim, and provenance.

## Privacy and spend

Graphify semantic extraction applies to documents, papers, and images. Contents
may leave the machine through Gemini or consume host-model quota; the only
sensitive-name skip is a filename heuristic, so an innocuously named secret is
not protected. Some backends report unmeasurable spend: numeric zero may be a
placeholder, not a zero-cost claim. Every authorized model pass therefore needs
an out-of-band privacy and spend bound before dispatch.

Semantic or clustering passes require an owner-named backend. Auto-detected
backends authorize nothing, including `GEMINI_API_KEY` / `GOOGLE_API_KEY`, the
host-agent fallback, or `OLLAMA_HOST`. Ollama is explicitly unauthorized. This
preserves the dated in-repo precedent from the v0.3.0.0-era run root
`v0300-improve-parity-rQsOui/tools.md:19`: "owner said Codex, not Ollama"
(owner reaffirmed 2026-08-05). `ANTHROPIC_API_KEY` and `OPENAI_API_KEY` are not
read by the tested Graphify semantic path. `--code-only --no-cluster` is the
documented zero-LLM-dispatch default.

## Qualification and retirement

The narrow capability statement is dogfood-only and qualified as tested on two
repos, one Windows 11 host, Python 3.11.9, graphifyy 0.9.33, ActiveGraph 1.10.0,
on 2026-08-05. Documented, installed-package, registered-skill, and current
package versions do not self-reconcile; confirm live `--help` before using any
flag. A version change on any axis invalidates the qualification until rechecked.
A read-only, no-model trial on an unfamiliar third-party repo, with output
outside that repo and a full no-mutation snapshot, is a precondition for
broadening the claim, not for shipping this narrowed contract.

Owner decision, 2026-08-05: the missed-use-detection goal is retired. Four of
six Graphify hypotheses and one of five ActiveGraph hypotheses were unsuitable,
and a detector would cost more than the narrow surviving uses. Reopening needs
a named owner, date, and checkable trigger; it must not silently re-defer.

## ActiveGraph checkpoint assistance

The evidenced use is authorized `fork` / `diff` resume-from-checkpoint. An
event store or `custody-append.sh` output may remain an optional
non-authoritative mirror, but the run root remains the sole authority for
lifecycle facts. `replay` does not reconstruct the tested custody use case from
custom event names. Store setup, writes, reads, exports, and helper use keep
their separate authorization boundaries; absence blocks nothing.

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
