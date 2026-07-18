IMPLEMENTAUDIT_PHASE_START
Phase: 1 of 3 — Add user settings endpoint
Task: Implement GET /api/settings with auth check and tests
Type: brownfield / greenfield-endpoint
Run root: .IMPLEMENTAUDIT/runs/add-settings-Xy9Zq1
Baseline ref: abc123def456
Owner/source: src/routes/settings.ts
Mandatory commands: npm run build, npm test
Acceptance criteria: 3
Evidence required: build exit 0, test output, file listing
Depends on phases: none

## Why

The audit found no settings endpoint; users cannot retrieve their preferences.

## Current state excerpts

- `src/app.ts` has no registered `/api/settings` route at baseline `abc123def456`.
- `src/middleware/auth.ts` provides the existing auth middleware to reuse.

## Work

- Create src/routes/settings.ts with GET handler and auth middleware
- Add tests/settings.test.ts with happy path and 401 cases
- Register route in src/app.ts

## Implementation steps (ordered)

- Step 1: Create the settings route — target: src/routes/settings.ts (registerSettingsRoutes); change: add GET /api/settings handler behind requireAuth from src/middleware/auth.ts; verify: npm run build; expected: exit 0 with no errors
- Step 2: Add settings tests — target: tests/settings.test.ts; change: happy-path 200 and unauthenticated 401 cases modeled on the existing route tests; verify: npm test -- --testPathPattern=settings; expected: exit 0, all settings tests pass
- Step 3: Register the route — target: src/app.ts (registerRoutes); change: mount the settings router under /api after auth wiring; verify: npm test -- --testPathPattern=settings; expected: exit 0 including the 200/401 cases

## Scope boundaries

In scope: src/routes/settings.ts, tests/settings.test.ts, src/app.ts
Out of scope: src/middleware/auth.ts — reused, not modified; any response-shape change to existing endpoints — clients depend on current contracts.

## STOP conditions (plan-specific)

- Stop if `src/middleware/auth.ts` exports differ from the current-state excerpt above — the baseline has drifted; re-anchor before mutating.
- Stop if registering the route requires touching files outside the in-scope list.

## Acceptance criteria (all must pass — verify each in transcript)

- `npm run build` exits 0 with no errors
- `npm test -- --testPathPattern=settings` exits 0, all tests pass
- GET /api/settings returns 200 for authenticated user and 401 for unauthenticated

## Mandatory commands (run each; surface last ~10 lines + exit code in transcript)

- npm run build — property: behavioral; scope: the app compiles from current sources; expected: exit 0 with no errors
- npm test -- --testPathPattern=settings — property: behavioral; scope: settings behavior under the test suite, not full-app correctness; expected: exit 0 with settings tests passing

## Evidence required in transcript

- Build command output (last 10 lines + exit code)
- Test output with pass count and exit code
- ls -la src/routes/settings.ts tests/settings.test.ts

## Rollback / defer path

Revert: git checkout HEAD -- src/routes/settings.ts tests/settings.test.ts src/app.ts
Re-run npm run build to confirm clean state.

## Graphify / ActiveGraph / Markdown fallback status

Graphify: absent
ActiveGraph: absent
Markdown fallback: yes

## Cleanliness override, if any

## Maintenance notes

- Keep the route aligned with existing auth middleware imports and update tests if the middleware path changes.

## Notes

Auth middleware is already wired in src/middleware/auth.ts; import from there.

---

IMPLEMENTAUDIT_PHASE_VERIFY

Phase 1 acceptance criteria:
- [pass] npm run build exits 0: Build successful, 0 errors
- [pass] npm test settings exits 0: 4 passed, 0 failed
- [pass] GET /api/settings returns correct status codes: curl output verified

Mandatory commands:
- npm run build exit 0: Build successful in 2.1s
- npm test exit 0: Test suite passed

Cleanliness (.IMPLEMENTAUDIT/runs/.../repo-state.sh added-lines abc123def456):
- Debug prints added: 0
- Session debug-markers added (todo/fixme/xxx): 0
- Dead imports added: 0

Sidecar: Graphify skipped; ActiveGraph skipped; Markdown fallback yes
Remaining risk: none
Trust-prior count: 0
Re-verified count: 3

AGENTS_UPDATE_DECISION

Decision: not warranted
Reason: No new durable repo-local rule emerged from this phase.
Scope: N/A
Evidence location: N/A
Conflict or owner-decision note: none

CONTINUITY_DECISION

Decision: none
Reason: No non-obvious learning worth persisting.
Evidence boundary: N/A

IMPLEMENTAUDIT_PHASE_DONE

Status: done
Evidence: build pass, test pass, file listing confirmed
Follow-up: none
