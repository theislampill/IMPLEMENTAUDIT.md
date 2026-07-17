# Fable design review of issue #35 — Context-epoch continuity

## Provenance statement

This design review was produced end to end by **Claude Fable 5** (model id
`claude-fable-5`) on 2026-07-17 (session 15/16). The harness reported
Fable 5 at session start and no substitution was observed. The issue and
its first fixture were filed during the owner-observed substituted turn;
every design claim below was independently re-verified against the live
issue body, the merged B3 fixture (`82297b0`), and the six composing
issues (#2, #4, #7, #12, #13, #15) whose bodies this program has already
reviewed in sessions 04, 03, 08, 12, 09, and 10 respectively.

## Live state

- Issue #35: **OPEN**, milestone **v0.3.2.0**, zero comments at review
  time. It remains open pending B3 pre-change evidence, implementation,
  and post-change comparison — per its own sequencing note. Correct.
- PR #36 (B3 supplementary fixture) is merged at `82297b0` and receives
  its own review in session 16; this review touches it only at the
  design/contract level.

## Design adjudication (packet-required points)

1. **Core invariant** — present and correctly scoped: the seven-step
   pre-mutation reconciliation (unique active run root + repository
   identity; reread durable state; classify instructions; compare
   reconstructed vs live; refuse satisfied-one-shot replay; restore next
   authorized action; hand off over speculation). The framing sentence —
   “the compacted summary is an observation of history, not
   current-state authority” — is exactly the packet’s invariant.
   **CONFIRMED.**
2. **Instruction lifecycle** — all five kinds byte-for-byte
   (`one-shot-action`, `standing-constraint`, `standing-authorization`,
   `persistent-objective`, `query-or-information-request`); “only a
   one-shot action is normally `satisfied`”; all six statuses
   (`active / satisfied / superseded / revoked / expired / ambiguous`);
   the applicability record binds id, source reference, hash, kind,
   authority, subject identity/version, epoch, preconditions, terminal
   predicate, status + evidence, supersession links, expiry.
   **CONFIRMED.**
3. **Repeated owner message** — fresh authority event; already-satisfied
   target answered with evidence and no duplicate action; reactivation
   requires explicit reopen, changed target, or evidence invalidating
   the terminal predicate. Exactly the packet rule. **CONFIRMED.**
4. **Continuity provenance** — all five sources; “do not fabricate a
   compaction the host did not expose” is verbatim in a heading.
   **CONFIRMED.**
5. **Generated capsule** — derived from canonical sources, explicitly
   “not a competing source of truth; do not hand-maintain a NorthStar
   file”. All packet bindings present after one amendment (below):
   run **and repository** identity, goal/terminal condition,
   phase/status, HEAD/tree/dirty, latest completed action, latest
   terminal + current open Andon, next authorized action, open owner
   decisions, active/satisfied continuity-critical instructions,
   in-flight command/provider state, source hashes.
   **CONFIRMED WITH ONE AMENDMENT.**
6. **Handoff conditions** — all five packet conditions plus three
   sound extras (invalid/stale ROADMAP/STATE; repeated reconciliation
   failures put the governing rule on trial per #7; no-run-root →
   truthful intake). **CONFIRMED.**
7. **Privacy and authority** — no raw conversation text in committed
   artifacts; hash/reference + bounded normalized fields under the
   existing custody boundary; standing constraints and authorizations
   survive compaction (negative controls 4–5); epoch claiming bounds
   concurrent resumes to one writer (control 8, composing with the
   #20/#21 claim semantics). **CONFIRMED.**
8. **Baseline integrity** — primary 14-fixture campaign (84 missions)
   explicitly unchanged mid-campaign; B3 strictly supplementary:
   pre-change `1 × 2 × 3 = 6` against immutable v0.3.1.0; post-change
   six interleaved contemporaneous control/candidate missions; B3
   reported separately from the primary aggregate. Byte-matches the
   packet. **CONFIRMED.**
9. **Composition** — #4 (occurrence/version identity), #12
   (parameter-bound authority), #15 (re-entry as implicit
   receiving-side handoff), #2 (unknown terminal state), #7/#13
   (governing-rule review + lesson lift) each named with the correct
   role; “do not hide it entirely inside #15” explicit. This program’s
   own reviews of those six contracts (sessions 03–12) found nothing
   that conflicts with this composition. **CONFIRMED — distinct,
   PR-sized invariant.**
10. **Evidence framing** — “This issue does NOT claim a proven
    production duplicate-mutation incident”; the release case is stated
    exactly as the packet requires (frequent real trigger — 41
    host-reported compactions in the Branch-11 record — + direct
    contract gap + deterministic synthetic reproducer). The filing
    footer repeats the non-claim. **CONFIRMED; no overclaim present.**

## Issue-body disposition

**One minimal amendment applied** (2026-07-17, this session; GitHub
preserves the edit history): the capsule binding list opened with
“run id” but never explicitly bound the **repository identity** the
capsule’s HEAD/tree belong to — the packet requires “run and repository
identity”, and invariant step 1 already treats repository identity as
first-class. Amended phrase:

> Generate from canonical sources: run id **and repository identity
> (the subject repository the HEAD/tree below belong to)**; goal and
> terminal condition; …

Everything else was left byte-identical. No other required point was
missing or contradicted.

## B3 fixture contract (input to session 16)

The merged fixture encodes the core reproducer faithfully: five required
properties (honest boundary provenance; live-state-read-before-mutation;
stale steer classified satisfied; continuation from ANDON 251; no
duplicate mutation of 150), matching the issue’s seed and FAIL list.

**One design-level observation for session 16:** the issue’s B3 PASS
text also names “generated capsule bound to current state” and
“ambiguity routes to audited handoff”, which the fixture does not score
(5 properties, no artifact/host rules). For the PRE-change baseline this
is defensible — v0.3.1.0 has no capsule to generate, and adding
required properties that must fail pre-change would blur the
comparison. Recommended resolution, safe before the pre-change campaign
(which has not run): EITHER record in the fixture that capsule-binding
and ambiguity-routing PASS aspects are covered by the deterministic
contract tests of the acceptance criteria (not the B3 missions), OR add
them as `required: false` scored-separately properties so the
post-change comparison can observe them without changing the six
required-property baseline semantics. Session 16 should adjudicate and,
if warranted, apply this to PR #36’s fixture contract.

## Exact implementation sequence (as the issue orders it; confirmed)

1. **Now (done):** B3 fixture exists as fixture-only supplementary
   baseline (PR #36, merged); primary campaign definition untouched.
2. **Before any behavior change:** run the six B3 pre-change missions
   (2 configurations × 3 repetitions) against immutable v0.3.1.0 —
   owner-gated model-in-the-loop work, NOT performable in a review
   session (no metered calls).
3. **Then implement** the product behavior on the issue’s owner
   surfaces (PROTOCOL, STATE, continuity reference, transcript
   contract, run-root validator, registries; prefer no new marker),
   with the deterministic contract tests + negative controls of the
   acceptance criteria.
4. **Then** run the six interleaved contemporaneous control/candidate
   post-change missions; report B3 separately from the primary
   aggregate.
5. **Close #35** only after pre-change evidence, implementation, and
   post-change comparison are all recorded — the issue stays open
   until then.

## Residual risks and nonclaims

- No behavioral feature is implemented by this review, per the packet’s
  explicit prohibition before the six pre-change B3 missions exist.
- The 41-compaction trigger count is the owner’s Branch-11 record,
  taken as filed; this review verifies the claim’s framing (trigger
  frequency, not incident), not the private record itself.
- Whether the feature reduces stale-steer replay is exactly what the
  B3 pre/post comparison exists to measure; nothing here presumes the
  result.

## Verdict

**CONFIRMED_WITH_FIXES** (one minimal issue-body amendment; no product
bytes changed).

The issue is a complete, honestly-framed, correctly-sequenced,
PR-sized design that satisfies every packet-required point — lifecycle
vocabulary, provenance honesty, derived capsule, handoff-over-
speculation, privacy bounds, strict baseline separation, and clean
composition with the six neighboring contracts this program has already
reviewed. The single gap (explicit repository identity in the capsule)
is amended in place with history preserved.

Integrator notes: this branch adds only this report; the issue-body
amendment lives on GitHub with edit history. Session 16 owns the PR #36
fixture adjudication, carrying the capsule/ambiguity observation above.
