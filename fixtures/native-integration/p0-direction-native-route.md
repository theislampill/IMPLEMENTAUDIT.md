# Native Category Route Fixture: Direction / Features / Roadmap / Next

Input shape:
The user asks "what next?" or requests features, roadmap, replacement design, or future direction.

Native route:
- Category: direction / design / next
- tdqyq-audit-object: direction row with grounded candidates, owner/source, acceptance, risk, verification, rollback, and final disposition
- ydqyq-audit-action: separate defects from direction, run DMADV, and close as spike, phase, defer, reject, or owner decision
- Owner/source: intent docs, product surface, architecture constraints, and validation path
- Route: DMADV direction/design routing
- Smoke A/B: Smoke A records current constraints and absence/gap; Smoke B verifies selected phase/spec/checker or owner deferral
- Andon: trigger on generic roadmap prose, missing owner/source, or mixing defects with future direction
- Final audit: confirms direction candidates are grounded and separated from defects
- Plan Closure: phase/spike/defer/reject with owner/source and remaining risk

Finding row:
- Finding title: Grounded "what next" candidate needs DMADV design before implementation
- Category: direction / features / roadmap / next
- Evidence: repo intent docs, unfinished surfaces, user friction, or adjacent architecture signal
- Impact: guides next work without confusing it with a defect
- Effort: variable; phase plan or spike first when risk is high
- Risk: speculative direction can waste implementation effort
- Confidence: medium unless owner acceptance and evidence are strong
- Fix sketch / implementation route: DMADV direction/design route with alternatives and acceptance criteria
- Owner/source: product intent file, public API owner, or design surface
- Acceptance criteria: selected candidate has constraints, verification, rollback, and owner/source
- Verification: phase plan, spike result, owner decision, or explicit deferral
- Rollback / Plan Closure: reject/defer candidate or remove designed artifact if verification fails
- Rejected/deferred rationale: reject generic idea-slop or candidates unsupported by repo evidence
- Remaining risk: product context may require owner decision
- Route: DMADV / mixed

Negative control:
- False parity to reject: generic roadmap prose, feature wish-list, or next-step advice not grounded in repo evidence
- Forbidden behavior: implement direction work as a loose planning lane or blend it with defect findings
