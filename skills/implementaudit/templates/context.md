# Context

Runtime copy target: `.IMPLEMENTAUDIT/runs/<task-slug>-<id>/context.md`

Stage 0 operating-context record. Live repo evidence wins over everything
recorded here.

| Field | Value |
|---|---|
| Repo root |  |
| Baseline ref (`git rev-parse HEAD` at run start) |  |
| Working-tree state at start | clean / dirty (summarize; never absorb pre-existing dirt into run evidence) |
| Invocation shape | embedded / direct / goal synthesis / governed casual-build intake |
| Route | greenfield / brownfield / mixed |
| Host / session constraints |  |
| Repo instructions read | AGENTS.md / CONTRIBUTING.md / CI files, with any conflicts noted |
| Prior run roots found | (read-only continuity inputs) |

Owner decisions pending at intake:
