# Tools

Runtime copy target: `.IMPLEMENTAUDIT/runs/<task-slug>-<id>/tools.md`

Stage 0 detection record. Mirror `detect-env.sh` output here; do not claim a
tool available without a detection result.

| Field | Value |
|---|---|
| IMPLEMENTAUDIT_SKILL_DIR | (resolved path, or `skills` default in the source repo) |
| Helper layer (bash) | available / unavailable — if unavailable, name the weaker-evidence fallback in use |
| IMPLEMENTAUDIT_BASE (run-root base) |  |
| Language runtimes / package managers |  |
| Web / current-doc lookup | available + authorized? |
| Graphify | absent / present (version); authorization |
| ActiveGraph | absent / present (version); authorization |
| Version skew (dogfood only) | installed payload vs repo manifest, when applicable |

Orientation Andons (e.g., version skew, helper layer unavailable) are recorded
here and classed per the transcript contract.
