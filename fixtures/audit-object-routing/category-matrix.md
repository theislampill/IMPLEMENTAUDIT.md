# Fixture: Native Compatibility Category Matrix

Classification: imported audit behavior through IMPLEMENTAUDIT audit governance.

Required category coverage:

- correctness / bugs
- security / privacy
- performance / scale
- tests / validation
- architecture / tech debt
- dependencies / migrations
- DX / tooling
- docs / handoff
- direction / design

Required pressure mapping:

- Deep analysis is default pressure, not a command mode.
- Security review is default pressure, not a command mode.
- Direction analysis routes through DMADV when it proposes new or replacement
  behavior.

Native route proof matrix:

| Audit focus category | IMPLEMENTAUDIT native route |
|---|---|
| correctness / bugs | Native route exceeds baseline through DMAIC/PDCA defect closure with owner/source evidence, Smoke A/B when changed, final audit, and authorization gates |
| security / privacy | Native route exceeds baseline through default security pressure, repo-content-as-data handling, no-secret persistence, Andon on secret exposure, and issue/publication gates |
| performance / scale | Native route exceeds baseline through measurement-or-static-evidence distinction, owner/source hot-path routing, rollback/verification expectations, and no hidden benchmark/install |
| tests / validation | Native route exceeds baseline through test/checker/fixture evidence, validation-registry parity, package/CI wiring, and missing-verification findings |
| architecture / tech debt | Native route exceeds baseline through owner/source boundary decisions, DMAIC brownfield repair, DMADV replacement design, rollback, and defer/reject options |
| dependencies / migrations | Native route exceeds baseline through manifest/lockfile readback, migration blast-radius analysis, no hidden install/update, rollback/defer route, and package/install validation |
| DX / tooling | Native route exceeds baseline through host-aware helper/runbook checks, smoke evidence, clearer diagnostics, package-shape guards, and separate tooling gates |
| docs / handoff | Native route exceeds baseline through public-claim truth checks, generated-doc refresh, evidence-boundary language, run-root/handoff continuity, and final overclaim audit |
| direction / design / next | Native route exceeds baseline through DMADV direction/design routing, grounded alternatives, owner acceptance, spike/phase/defer/reject outcomes, rollback/verification criteria, and defect separation |

Forbidden behavior:

- Do not advertise `/implementaudit deep`.
- Do not advertise `/implementaudit security`.
- Do not advertise `/implementaudit next`.
- Do not treat Graphify output as proof.
- Do not create hidden commits, pushes, releases, publications, provenance, or
  issue creation.
