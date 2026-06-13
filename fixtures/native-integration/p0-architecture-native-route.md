# Native Category Route Fixture: Tech Debt / Architecture

Input shape:
An audit finds a god module, layering violation, duplication cluster, or circularity that blocks safe change.

Native route:
- Category: architecture / tech debt
- tdqyq-audit-object: architecture row with owner/source boundary, current coupling evidence, route decision, and defer option
- ydqyq-audit-action: classify brownfield repair through DMAIC or replacement design through DMADV
- Owner/source: module boundary, dependency edge, generated/source ownership, or package interface
- Route: DMAIC for bounded repair; DMADV for replacement design
- Smoke A/B: Smoke A records current dependency/coupling behavior; Smoke B proves boundary-preserving change or plan closure
- Andon: trigger on broad rewrite pressure, owner/source ambiguity, or unrelated restructuring
- Final audit: confirms scope containment and remaining architectural risk
- Plan Closure: changed for bounded fix, deferred/spike for broad redesign, blocked for owner decision

Finding row:
- Finding title: God module mixes routing, persistence, and rendering policy
- Category: architecture / tech debt
- Evidence: live module readback, dependency edges, duplication/circularity example
- Impact: changes are risky and ownership is unclear
- Effort: medium/high depending on boundary
- Risk: refactor may alter public behavior
- Confidence: medium/high when dependency evidence is direct
- Fix sketch / implementation route: DMAIC boundary repair or DMADV replacement phase plan
- Owner/source: canonical module boundary and nearest validation surface
- Acceptance criteria: one bounded responsibility is moved or redesign handoff is explicit
- Verification: focused tests/checkers and dependency/readback proof
- Rollback / Plan Closure: revert bounded extraction or defer redesign with owner/source
- Rejected/deferred rationale: reject if coupling is intentional and documented
- Remaining risk: broader architecture may require later phased work
- Route: DMAIC / DMADV / mixed

Negative control:
- False parity to reject: labeling "tech debt" without owner/source, coupling evidence, or route decision
- Forbidden behavior: broad rewrite, new architecture lane, or replacement design without DMADV acceptance and rollback
