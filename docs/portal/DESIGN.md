# IMPLEMENTAUDIT docs portal v2 design notes

This file documents the design contract for the generated v2 docs portal. It is
source-side guidance for maintainers and future tooling work. It is not generated
into the reader-facing pages, and it does not claim that any separate docs tool
or slash command already exists.

## Purpose

The v2 portal is the public front door for IMPLEMENTAUDIT. It must teach a new
developer what the skill does before it asks them to understand the method's
formal vocabulary.

The visible promise is:

1. The user gives Claude Code or Codex a repository request.
2. IMPLEMENTAUDIT creates or binds a durable work record.
3. Phased or larger runs create a run folder with state, roadmap, phase files, and evidence.
4. The run checks before and after edits.
5. The run stops visibly on abnormal evidence.
6. The run records the failure path.
7. The run finishes only with final audit completion or an honest handoff.

The formal vocabulary remains visible, but plain meaning comes first. Use
`run folder (run root)`, `before/after checks (Smoke A/B)`, `stop-the-line
failure handling (Andon)`, `final fix-and-verify loop (audit-fix)`, and similar
plain-first forms when introducing specialist terms.

## Architecture

The portal is intentionally split into an overview, onboarding pages, audience
pages, core model pages, evidence pages, closure pages, repository pages, and
reference pages.

- Overview pages carry the product thesis and first-read onboarding.
- First-run pages answer what to paste, what gets written, and what outcomes are
  possible.
- Audience pages route new users, operators, auditors, and maintainers.
- Core model pages explain gates, invocation shapes, usage examples, planning,
  routing, the nested loop model, and the operating method.
- Evidence pages explain artifacts, repo-state comparison, error handling,
  evidence boundaries, optional tooling, and child-agent review reports as
  evidence inputs.
- Closure pages explain completion semantics and continuity/resume behavior.
- Repository pages explain repo layout, package contents, and the repo record.
- Reference pages hold terminology and the final index.

There is no separate `Maintainers` sidebar group. Maintainer-facing surfaces are
cross-cutting reference material unless a future source-backed role page proves
they need a dedicated lane.

The overview must not be the whole portal. The reference material must not be
hidden in footer pills or a collapsed proof museum. The left sidebar is the
stable portal map. The right sidebar is page-local orientation only.

## Source ownership

The v2 portal is generator-owned.

- Edit source pages under `docs/portal/pages/`.
- Edit shared CSS and JS under `docs/portal/assets/`.
- Edit navigation, route, source-citation, and release metadata in
  `docs/portal/site.json`.
- Generate output with `scripts/build-docs-portal.py`.
- Validate generated output with `scripts/check-docs-portal.py` or
  `scripts/verify-docs-portal.sh`.
- Do not hand-edit `dist/docs-portal/` or `dist/docs-draft-v2/` as source.

Generated output is evidence of the current source tree. It is not a release,
publication, provenance, or GitHub Pages deployment by itself.

## Information architecture contract

The sidebar order is part of the product contract. Keep it chronological:

1. Overview.
2. First run.
3. Audience.
4. Core model.
5. Evidence.
6. Closure.
7. Repository.
8. References.

Navigation rules:

- Every page appears exactly once in the left sidebar.
- Page-local headings appear only in the right sidebar and mobile on-page table
  of contents.
- Previous and next links move by page order, not by same-page heading.
- The overview splash links into the page sequence without leaving the portal
  shell.
- The reference index is the final page in `References`, not the first item in
  its own section.
- `References` contains only `Terminology` and `Index`; it is the final lookup
  shelf, not a junk drawer for every page that sounds detailed.
- `Repository` contains `Repo layout`, `Package contents`, and `Repo record`;
  repo-shape and release-history surfaces belong together because they answer
  what is in this repository and what durable record it keeps.
- Optional tooling lives in `Evidence`, not `References`, because Graphify and
  ActiveGraph affect proof surfaces and sidecar boundaries. Pages that discuss
  sidecars, continuity, package contents, or auditor maintenance cross-link
  there instead of duplicating the same optional-tooling explanation.
- Child-agent review loops live in `Evidence`, not `References`, because their
  reports are evidence inputs rather than authority.
- Usage examples live in `Core model`, not `First run` or `References`, because
  they teach invocation shapes and governed intake behavior after the first
  command is already clear.
- `Repo record` is the consolidated home for audit trail, release-history
  status, changelog, and current-truth boundaries. Do not split that material
  back into duplicate audit-trail and audit-status pages.
- Sidebar groups can expand visually, but the active page must stay stable and
  not jump between groups during scroll.

## Readability normalization

Reader-facing content should be clear, not compressed. The user's annotation
pattern for this portal prefers:

- one idea per paragraph;
- `<br>` between short paired sentences when splitting into a second paragraph
  would be too heavy;
- lists when a sentence contains a long sequence of named requirements;
- `<code>` wrappers for filenames, markers, commands, and exact tokens;
- tables when the table is genuinely comparative and readable;
- targeted table column widths for narrow numeric columns;
- no broad table-to-card conversion just because a table exists.

Tables are not the enemy. Bad line breaks, orphaned labels, over-wide numeric
columns, and long unwrapped inline tokens are the enemy.

## Evidence and overclaim boundaries

The docs must preserve IMPLEMENTAUDIT's proof boundaries:

- A run folder is evidence of run state, not proof of product delivery.
- Before/after checks prove observed evidence, not publication or provenance.
- Graphify is orientation evidence, not correctness proof.
- ActiveGraph custody is event evidence, not correctness proof.
- A checksum manifest verifies artifact integrity; it can support a separately
  authorized release provenance gate, but it is not a signature, SBOM,
  install check, or host-load proof.
- Install extraction is not host-load proof unless that host path was actually
  tested.
- Commit, push, tag, release, publication, provenance, host installation,
  sidecar setup, and plugin-state mutation remain separate owner-authorized
  gates.

## Optional tooling boundary

Graphify and ActiveGraph are optional for consuming repos. The method may use
them during IMPLEMENTAUDIT self-maintenance when they are present and authorized,
but the docs must not turn that dogfood expectation into a requirement for users.

When optional tooling is described, include the fallback:

- live files remain the first source of truth;
- Markdown run folders remain valid;
- sidecars can support owner/source, terrain, custody, and review context;
- sidecars cannot replace before/after evidence or final audit closure.

## Generator design

The generator is deliberately small and dependency-free. It should remain easy to
audit because the docs themselves are part of the evidence trail.

Generator responsibilities:

- load `site.json` with duplicate-key rejection;
- reject unsafe or ambiguous route paths;
- reject page sources outside `docs/portal/pages/`;
- reject orphan page sources not listed in navigation;
- generate stable page shells, sidebars, breadcrumbs, page-local TOCs, previous
  and next links, footer links, metadata, and copied assets;
- add mobile table data labels from table headers;
- record source files and hashes in `docs-metadata.json`.

The generator should not:

- infer product claims not present in source pages or cited repo sources;
- deploy, publish, tag, release, or claim provenance;
- require external libraries, assets, CDNs, or frameworks;
- silently accept duplicate routes or stale orphan sources.

## Checker design

The checker exists to keep the generated portal non-stale and non-overclaiming.

Checker responsibilities:

- validate required metadata fields;
- validate page count, navigation groups, routes, local links, anchors, and
  duplicate IDs;
- validate that sidebar links and footer links resolve;
- validate that source files and source hashes match the current source tree;
- reject stale legacy portal text and unsupported marketplace/provenance claims;
- ensure required concepts remain visible in the generated portal;
- ensure generated tables keep mobile labels;
- ensure page-local `h2[id]` anchors are present in both desktop and mobile TOCs;
- ensure CSS/JS contains the classes used by the source pages.

The checker is not a runtime validator. It protects the docs portal's source and
generated output contract.

## Future docs-system counterfactual

These notes may later inform a separate docs-system project, possibly named
`/implementdocs`, but that project does not exist in this repository today.
Do not mention it in reader-facing IMPLEMENTAUDIT pages as a current feature.

The useful counterfactual is:

> If a future docs-system skill had existed before this v2 portal, and it was
> pointed at the old IMPLEMENTAUDIT repository, it should have produced a portal
> that is contract-equivalent to this one.

Contract-equivalent means:

- same clarity of onboarding;
- same overview plus reference architecture;
- same source-backed evidence trail;
- same generator-owned output discipline;
- same CI freshness requirements;
- same non-overclaim boundaries;
- same product-surface smell;
- not pixel-identical, not a generic docs template, and not a claim that the
  future system is already implemented.

The lesson for that future project is not "make generic docs." The lesson is:

Given a repository, infer its product surface, owner/source contracts, evidence
trail, generated artifacts, onboarding problem, and CI freshness requirements;
then produce a tasteful static docs portal that stays non-stale on every push.

## Maintenance checklist

Before claiming the portal is ready:

1. Read the relevant source docs and repo constraints.
2. Edit `docs/portal/` source, not generated output.
3. Regenerate the portal.
4. Run `scripts/check-docs-portal.py` against the generated output.
5. Run `tests/docs-portal.test.sh`.
6. Run `scripts/verify-docs-portal.sh`.
7. Browser-check desktop and mobile for horizontal overflow, readable sidebars,
   active right-side TOC, and code/table wrapping.
8. Keep release/publication/provenance claims separate unless those gates were
   actually authorized and verified.
