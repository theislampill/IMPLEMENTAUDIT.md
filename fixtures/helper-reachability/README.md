# Helper reachability fixture map

The focused test creates disposable candidate copies from these deterministic case definitions:

| Case | Expected result |
|---|---|
| live 18-helper package manifest and closed declarations | PASS 18/18 |
| one shipped helper lacks a declaration | FAIL |
| a helper cites only itself as its owner | FAIL |
| a required-procedural owner does not contain the exact helper route | FAIL |
| a declaration uses a non-contract class such as `unit-tested` | FAIL |
| an automatic helper names a missing caller | FAIL |
| an advisory helper claims a mandatory closure effect | FAIL |
| a nineteenth packaged helper is added without a declaration | FAIL 18/19, proving a derived denominator |
| a declaration names a helper absent from the package | FAIL |

Package presence, a self-usage comment, direct unit tests, and wildcard discovery are deliberately insufficient dispatch evidence.
The live positive also requires one audit object and a cheap no-event path.
