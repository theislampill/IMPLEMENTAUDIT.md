fix(eval): close static collaboration evasions

Finding: BLOCK-COLLAB-OPTIONAL-CHAIN-EXECUTION-OMISSION on 1b875d3, with the same bounded static-lexical cause covering escaped identifiers and alias-then-call forms.

Countermeasure: recognize optional static access/calls, decode valid identifier Unicode escapes, and track simple scope-aware static aliases independently in official, Matrix, and B3 scanners. Retain inert literal/search controls and V34 fail-closed evidence.

Evidence: lifecycle; native parity 251/251; host-read 130/130; hosts; Matrix/B3 rederivers; AST parity/import independence; registry 59/59; pycompile; diff check.

Boundary: no skill, product, fixture, prompt, scorer, evaluator, model, packet, campaign, acceptance, package, network, or model execution.
