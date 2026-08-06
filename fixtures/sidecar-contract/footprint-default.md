# Fixture: in-repo Graphify footprint must fail

Fixture kind: graphify-footprint
Proposed action: Graphify extraction
Mode: --code-only --no-cluster
Output: inside-target-repo
Tracked ignore edit: yes

Expected result: reject. The documented default is `--out outside the target
repo`; an in-repo output or ignore-file edit requires a separate mutation
decision. `git status` alone cannot prove no mutation when output is ignored.
