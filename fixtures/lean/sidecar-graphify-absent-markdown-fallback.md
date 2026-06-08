# Fixture: Graphify absent — Markdown/Gemba fallback remains valid

Route: DMAIC (brownfield — sidecar absent scenario)

## Scenario

Graphify is absent (not installed, not indexed, or unauthorized).
IMPLEMENTAUDIT proceeds with live-file Gemba and repo-state.sh as the
sole terrain source.

## Expected runtime behavior

1. **Graphify status**: absent (logged in THINKING.md and sidecars.md)
2. **Seiri / Sort**: performed via `git ls-files`, `verify-package.sh require_file` list,
   and direct file inspection — not Graphify. All artifact classes are classified against
   live files only.
3. **Seiton / Set in order**: owner/source mapping performed via live file reads,
   AGENTS.md, verify-package.sh, and repo-state.sh — not Graphify degree queries.
4. **Seiso / Shine**: cleanliness check via `check-added-lines-clean.sh` and
   `repo-state.sh added-lines <baseline>` — not Graphify stale-node queries.
5. **DMAIC Measure/Analyze**: defect surface identified by reading live owner/source files,
   Smoke A command output, and git diff — not Graphify queries.
6. **AUDIT_COMPLETE is valid** when all Smoke A/B, criteria, and final audit checks pass,
   even when Graphify is absent.

## What must NOT happen

- IMPLEMENTAUDIT must not claim Graphify was used when it was absent.
- IMPLEMENTAUDIT must not block execution waiting for Graphify installation.
- IMPLEMENTAUDIT must not downgrade the audit verdict solely because Graphify is absent.
- The `.skill` package must not include Graphify outputs, graph.json, or graphify-out/.

## PHASE_VERIFY stub

IMPLEMENTAUDIT_PHASE_VERIFY
- [pass] Graphify absent logged: yes — THINKING.md Optional sidecars: absent
- [pass] Live-file Gemba substituted: yes — direct file reads used throughout
- [pass] Smoke A/B run without Graphify: yes — check-lean-discipline.sh and verify-package.sh used
- [pass] AUDIT_COMPLETE valid: yes — sidecar absence does not block completion
Sidecar: Graphify absent; ActiveGraph skipped; Markdown fallback yes
Remaining risk: none — absence is the defined non-blocking path
