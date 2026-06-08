# Phase shape: UI feature

**Shape:** Feature with visible user-facing output (web UI component).
**Phases:** 4
**P4-1 hardening:** included (Phase 4)
**P4-2 visual polish:** included (Phase 3)
**P4-3 brownfield safety-net:** included if mutating existing component (Phase 1 characterization); greenfield variant skips with documentation
**P4-4 package/release split:** N/A (no release artifact — documented skip)
**P4-5 provenance boundary:** N/A (no release artifact — documented skip)

---

## Phase 1 — Implement (component + logic)

Owner/source: src/components/SettingsPanel.tsx
Work: Build component with all states (loading, error, empty, populated).
Acceptance criteria:
- `npm run build` exits 0
- Component renders in all 4 states (unit test passes)
- No TypeScript errors (tsc --noEmit exits 0)
Mandatory commands: npm run build, npm test -- --testPathPattern=SettingsPanel, npx tsc --noEmit
Rollback: git checkout HEAD -- src/components/SettingsPanel.tsx
Depends on: none

## Phase 2 — Integration validate

Owner/source: src/app.tsx (integration point)
Work: Wire component into app; run full test suite.
Acceptance criteria:
- No regression in full test suite
- Component appears in app route at /settings
Mandatory commands: npm test, npm run lint
Rollback: git checkout HEAD -- src/app.tsx
Depends on: Phase 1

## Phase 3 — Visual polish

Owner/source: src/components/SettingsPanel.tsx, src/styles/
Work: Visual QA; spacing, color, responsive behaviour at 3 breakpoints.
Acceptance criteria:
- Screenshot at 1440px shows component aligned per design spec
- Screenshot at 768px shows responsive layout without overflow
- Screenshot at 375px (mobile) shows no clipping
- Accessible: aria-label present; keyboard navigation works
Evidence required: 3 screenshots in transcript (or browser smoke output)
Mandatory commands: npm run dev (browser smoke), npx playwright test settings-panel.spec.ts (if available)
Rollback: git checkout HEAD -- src/components/SettingsPanel.tsx src/styles/
Depends on: Phase 2

## Phase 4 — Hardening

Owner/source: src/components/SettingsPanel.tsx, docs/
Work: Error boundary; loading skeleton; cleanliness; docs.
Acceptance criteria:
- Error boundary renders fallback (not blank screen) on API failure
- Loading skeleton visible (not blank) during data fetch
- check-added-lines-clean exits 0
- docs/components/SettingsPanel.md created or updated
Mandatory commands: bash scripts/verify-package.sh, npm test
Rollback: git checkout HEAD -- src/components/SettingsPanel.tsx docs/
Depends on: Phase 3

---

P4-4 skip rationale: Web component deploy is a separate infrastructure concern; no build artifact released in this plan.
P4-5 skip rationale: No provenance boundary crossing in scope.
