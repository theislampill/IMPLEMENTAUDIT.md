# Audit Dogfood History

This index records repo-local evidence that ImplementAudit changes are being
dogfooded through audit closure. It is not a release log, provenance manifest,
or raw smoke-output dump.

| Evidence | What it proves | What remains unverified |
|---|---|---|
| Commit `9acc1b9` (`docs: harden v0.2.1.0 package governance`) | Prior package hardening used verbose local trace, Smoke A/B language, generated README diagram checks, marker-order checks, host-claim checks, and release asset validation. | The original external audit file for that run is not tracked in this repo. |
| `CHANGELOG.md` v0.2.1.0 entry | Causal history is recorded for transcript contract, marker-order, fixture, generated diagram, host-claim, and checksum-boundary hardening. | Changelog is summary evidence, not a raw transcript. |
| `fixtures/simple-audit/EXPECTED-TRANSCRIPT-SKELETON.md` | Final audit markers require `AUDIT_COMPLETE` before `IMPLEMENTAUDIT_RUN_COMPLETE`. | It is a fixture, not a full historical run transcript. |

The v0.2.2.0 lane carried the same convention forward: read-only Gemba first,
owner/source patching, fixtures/checkers for behavioral claims, Smoke A/B before
closure, and explicit release/provenance boundaries.

The v0.2.3.0 lane adds a native harness adaptation matrix plus executable
helpers/checkers for complete repo-state comparison, audit-spec validation, and
added-line cleanliness/overclaim scans. The detailed matrix lives in
`docs/audits/v0.2.3.0-harness-adaptation-matrix.md`.
