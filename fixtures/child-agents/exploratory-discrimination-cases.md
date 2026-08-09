# Fixture bank: anchored fanout versus independent discrimination

These cases distinguish ordinary coverage or adversarial fanout from the
narrow exploratory-discrimination variant. They are deterministic review
fixtures, not live child-agent evidence and not a fixed lane quota.

## FD-01 — seeded conclusion creates false diversity

All five exploratory trigger conditions hold, but the dispatcher tells every
lane that hypothesis H1 is probably correct and asks for supporting evidence.
The reports paraphrase H1 without a decision-changing discriminator,
counterexample, or concrete causal mechanism.

Expected disposition: REJECT. Semantically duplicated seeded outputs are not
independent corroboration.

## FD-02 — conclusion-neutral mechanism discrimination

All five exploratory trigger conditions hold. Lanes receive the same
authoritative facts, scope, security rules, and evidence boundary, but not the
root-favoured conclusion. Each lane tests a materially different mechanism and
returns a decision-changing discriminator, counterexample, or concrete causal
mechanism before synthesis.

Expected disposition: PASS. Fresh-context serial passes are valid when the
host cannot run the lanes concurrently.

## FD-03 — defined candidate needs adversarial coverage

A candidate and its known risks are already defined. Separate reviewers test
security, correctness, and recovery coverage against those known failure
modes; discovering competing causal hypotheses is not the purpose.

Expected disposition: PASS. Share the candidate, current reconnaissance, and
known risks; withholding them would weaken ordinary coverage review.

## FD-04 — unchanged blocked family is saturated

Prior exploratory passes tested the same mechanisms and returned no new
discriminator. Evidence, state, and plausible mechanisms are unchanged.

Expected disposition: REJECT another pass. Preserve the unresolved result
instead of manufacturing apparent independence through repetition.

## FD-05 — changed evidence permits reopening

A previously saturated question receives materially changed evidence, state,
or a new plausible mechanism that can change the decision.

Expected disposition: ALLOW a bounded reopening under the five-condition
trigger; the earlier stop is not permanent when its state changes.

## FD-06 — deterministic cheap path

An authoritative live owner and deterministic check already settle a small,
reversible question. There is no unresolved multi-hypothesis uncertainty.

Expected disposition: PASS without exploratory machinery. Use the
authoritative deterministic discriminator directly.
