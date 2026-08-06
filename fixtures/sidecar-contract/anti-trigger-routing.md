# Fixture: reference-shaped Graphify proposal must fail

Fixture kind: graphify-routing
Proposed action: Graphify query
Repository: unfamiliar
Repository shape: majority-code
Question shape: data-file-consumer
One-search answer: yes — `git grep -ln <basename>`

Expected result: reject because a reference-shaped question and a one-search
answer are anti-triggers.
