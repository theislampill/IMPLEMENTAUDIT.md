# Valid Mixed Audit Spec

Classification: mixed

Owner/source: `skills/references/example.md`

Scope:
- Add one governed reference and one fixture.

Non-scope:
- No release publication.

Constraints / invariants:
- Patch owner/source before derived docs.
- Keep optional sidecars absent-safe.

Acceptance criteria:
- Valid fixture passes.
- Invalid fixture fails.

Rollback/removal path:
- Remove the new reference, fixture, and validation wiring.

Evidence plan:
- Run the structural validator and package verification.

Generated artifact plan:
- No generated artifact is edited directly.

Graphify sidecar status:
- Optional terrain only; absent is acceptable.

ActiveGraph sidecar status:
- Optional custody only; absent is acceptable.

Release/provenance gate status:
- Blocked unless separately authorized and evidenced.
