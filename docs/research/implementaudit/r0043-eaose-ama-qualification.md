# R0043 EAOSE and AMA continuation — canonically unallocated

R0043 is published, canonically unallocated. EAOSE-132 and
AMA-CONTINUATION-278/32 have separate acceptance records at issue 232. This
repository route supplies complete original and later documentary dispositions;
entitled acceptance, actual receiving and issue closure are separate evidence.
Runtime 0.4.0 and release family v0.4.0.0 are unchanged.

## Declared entry and complete content

The repository reader is `scripts/r0043-reconstruct.py`. It reuses the existing
R0044 strict JSON/hash/archive helpers (published, canonically unallocated). It is
repository-only research tooling, excluded from the runtime projections, and
does not become a runtime receiving evaluator or a controller.

`r0043-member-dispositions.json` binds seven content parts, each below 800,000
bytes, so every part is accessible through the GitHub text-content route. The
parts preserve all 278 original identities, source/guard/action distinctions,
all 32 original groups and exact older public target records. The reader checks
part identities before assembling the complete projection. Missing or changed
parts refuse loading; a digest does not substitute for their contents.

The original packet is the public immutable
`docs/research/genealogy/ama/packet/EVOLVED_AMA_FROZEN_PACKET.zip` at commit
`cacfe97da7656b472bf4f11e50c9d106a6c3f92a`. Its SHA-256 is
`1c9654ab3017ecccdd3b24810b20ac23a5b51a5c19c1a488b64a2684dade026f`.
The supplied delivery evidence preserves those bytes. Archive code is data and
is never executed by the reader. All original context text and JSON members
remain available through `context`; `member` returns the full original record,
intake, bibliography, incident typed relations, independently recorded reverses,
explicit negative pairs, bridges, groups and lineage context.

```bash
python3 scripts/r0043-reconstruct.py check
python3 scripts/r0043-reconstruct.py check --packet /path/to/EVOLVED_AMA_FROZEN_PACKET.zip
python3 scripts/r0043-reconstruct.py member --packet /path/to/EVOLVED_AMA_FROZEN_PACKET.zip --key EAOSE:EAOSE-C026 --output /path/to/c026.json
python3 scripts/r0043-reconstruct.py group --packet /path/to/EVOLVED_AMA_FROZEN_PACKET.zip --key AMA-K008 --output /path/to/k008.json
python3 scripts/r0043-reconstruct.py relation --packet /path/to/EVOLVED_AMA_FROZEN_PACKET.zip --key AMA-R02009 --output /path/to/relation.json
python3 scripts/r0043-reconstruct.py context --packet /path/to/EVOLVED_AMA_FROZEN_PACKET.zip --key EVOLVED_AMA_COMPOSITION_INDUCED_PROPERTY_LEDGER.json --output /path/to/novelty.json
```

To reproduce the projection, supply the exact older public
`docs/research/implementaudit/triad-integration/DISPOSITIONS.json`, SHA-256
`616584f2e13d41fd8afb116f2b81b035d2f4600a13814f7523ebff4010a05dab`, as
`--antecedent`, and run `build --packet ... --antecedent ... --output ...`.
The local `r0043-tc-source.json` preserves the full twelve original analytical
hypotheses and parents; no new normative property is admitted by their presence.

## Layers and limits

The original EAOSE statuses, older public target judgments, later prepared
target judgments and actual current qualification are separate. The original
132-source census is retained exactly. The older public target has 51
STRENGTHENS_EXISTING, 74 QUALIFICATION_ONLY, three DEFERRED and four
UNRESOLVED_DISCRIMINATOR records. These are not the later 34 partial, 66
conditional, 25 rejected, three deferred and four research-only assignments.

The original portable candidate could not obtain the later crosswalk, EAOSE
row 0 or AMA row 3. Its seven original parts, historical nulls and failed
`member --require-prepared` outcome remain unchanged historical evidence.

The recovered exact inputs now have a separate
`r0043-prepared-dispositions.json` entry and twelve bounded content parts.
`r0043-prepared-source-lock.json` binds the actual crosswalk, distinct row 0
and row 3, all full ledgers, final-input correspondence and the 47-concern
reconciliation. All 278 prepared assignments come from their own records;
counts do not create assignments. Every inherited row-1 group field matches
the row-3-bound full group record. The additional controls preserve all 32
exact RED discriminators and positive boundaries. All 11,960 identical
accepted EMAS direction records are reused through the pinned sibling file;
only the other 8,192 directions are added. Their union remains 20,152,
without creating scheduler dependencies or new independent evidence.

The default reader discovers this later entry, validates its identity and
checks its present source owners against main
`3c41194af2db331f63706a49ef50a6e435138a4b`. Historical prepared anchors for
`composed-evidence.md` and packaged `operational-evidence.md` are absent at that
base and remain explicitly absent. Repository `docs/operational-evidence.md`
is a separate present source. No absent historical path is relabelled as
present behavior. Current-source drift refuses the stronger binding.

```bash
python3 scripts/r0043-reconstruct.py check --packet /path/to/EVOLVED_AMA_FROZEN_PACKET.zip --require-prepared
python3 scripts/r0043-reconstruct.py member --packet /path/to/EVOLVED_AMA_FROZEN_PACKET.zip --key EAOSE:EAOSE-C026 --require-prepared --output /path/to/c026.json
```

The later public projection retains member actions, guards, owner/source
routes, supported portions, reasons, residuals, first discriminators and
horizons; the immutable original packet supplies complete originals,
bibliography, independent reverses, negatives and context. The exact private
input map is retained with the commissioning owner's issue evidence, outside
Git. Aliases and hashes in the public lock are custody identifiers, not
public downloads. An authorized consumer can additionally verify all exact
input correspondence or retrieve full private content locally:

```bash
python3 scripts/r0043-reconstruct.py check --packet /path/to/EVOLVED_AMA_FROZEN_PACKET.zip --input-map /private/prepared-input-map.json --require-prepared
python3 scripts/r0043-reconstruct.py prepared-record --input-map /private/prepared-input-map.json --key PROPERTY_LEDGER.jsonl --selector EAOSE:EAOSE-C026 --output /private/full-c026.json
python3 scripts/r0043-reconstruct.py prepared-record --input-map /private/prepared-input-map.json --key prior_preparation --selector /rows/3 --output /private/ama-row3.json
```

The map explicitly names each local file for the lock's aliases; the reader
never follows embedded historical host paths. Raw private output must remain
outside Git and public delivery. Regenerate only the later projection with
`build-prepared --packet ... --input-map ... --output ...`; its independently
reviewed digest belongs in the prepared source lock. A regenerated digest is
not permission to change source judgments or acceptance.

The accepted EAA-70 contribution is bound to its certificate and exact
636,575-byte member projection. The accepted EMAS-76 contribution is bound to
its certificate, exact main commit/tree and 9,359,909-byte member blob. That
current EMAS blob is now recovered with SHA-256
`b015b4f04202059e04a2e2da5e470ff4a49e7e5a493b242ddd493f05f2889bd7`
and Git blob `86e4fa1f02a88d9759323dc018e63a25380e59bf`. The existing
`member` route consumes its exact accepted member records. The prior access
failure and older smaller projection remain historical evidence; neither is
substituted for this accepted file. Its row-1 preparation binding is distinct
from EAOSE row 0 and AMA row 3.

The shared EAA-001/EAOSE-C001 case is one accepted evidence family with two
scoped references. Both EMAS documentary alternatives completed their six units;
total comparison cost remains INCONCLUSIVE. No accepted trial is repeated.

## Qualification record

The recovered C026 exercise used an actual ordinary parent and child. The
parent received the child's bounded evidence and retained responsibility for
integration and residuals. It rejected two labelled parent-authored controls
with missing or overreaching cross-level responsibility and accepted the
adequate direct path. The immediate root consumed that result. This is bounded
documentary receiving, with same-parent control exposure, not blind trials or
native R0037 acceptance. C026 retains original `DOMAIN_SPECIFIC` and older
target `DEFERRED`; C027 and C062 do not acquire a trigger from this exercise.
No exact-current runtime false acceptance was demonstrated, so runtime
`NO_CHANGE` is retained.

The actual AMA receiver retrieved all 278 original/member records and all 32
groups, inspected the declared mechanism, trigger, cheap-path, assumption and
authority fields, and recorded action-distinguishing group decisions. It
interpreted the 22 constructed cases in
`fixtures/r0043/composition-cases.json` and two additional notification/privacy
probes. It read all 70 accepted EAA member actions. These are the receiver's
declared semantic fields and cases; full retrieval is not a claim that every
field of every original or every unchanged relation was semantically reviewed.
The final report, intermediate failures and exact input/output manifests are
retained in the delivery.

A recovery continuation verified the retained receiving manifests and read all
76 newly accessible accepted EMAS member-action mappings, including their
guards, authority, residual, first discriminator, cheap path, next action,
horizon and scope. Repeated exact prose was read once with every mapping
inspected. It also read all 32 available EMAS group discriminator/context
records. Its inspection was exposed to the earlier reports and is a scoped
access/readback completion, not another independent vote or comparison trial.
All 11,960 EMAS target directions were mechanically matched to their original
record hashes; that does not assert a new semantic adjudication of every edge.

The previously unfinished TC07 control is retained separately in
`fixtures/r0043/progress-cases.json`. A fresh documentary receiver, supplied
neutral questions and no prior receiving conclusions, rejected both proposed
overclaims. In A23 neither step is initially enabled, so completion is
unreachable and fairness cannot supply the missing prerequisite. A24 has the
reachable path A then B, a sound stipulated completion predicate and no
reachable nonterminal work deadlock. Its default scheduler permits waiting
forever. The explicitly added continuous-enabledness obligation establishes
eventual completion only within that finite model and supplies no time bound.
Actual completion acceptance still requires observing both completed flags.
All five TC07 parents remain attached; its original general discriminator
remains `UNRESOLVED_DISCRIMINATOR`.

These observations preserve the distinction between field integrity,
documentary interpretation and actual entitled receiving. No new general
superiority, progress, self-revision, host-principal or native LOAD/USE/JOIN
claim follows. The accompanying owner return binds the exact source and
receiving subjects, exposure limits, tests, review, failures and next entitled
accepting actions.

## Validation and integration

The authorized serialized integration adds the existing issue-owned
`tests/r0043-reconstruction.test.sh` to `scripts/verify-package.sh`, preserving
both registrations from accepted main. The donor's unregistered-wrapper CI
failure remains historical. Native Windows baseline also exposed POSIX versus
Windows separator inequality in the reader's sibling identity strings; the
two repository paths now use explicit POSIX serialization. No runtime source
mechanism was changed.

The ordinary reconstruction tests distinguish local projection integrity from
tests requiring the frozen packet. Supply the exact retained packet explicitly
for packet-dependent controls, and supply the private map for its integrity
control:

```bash
R0043_PACKET=/path/to/EVOLVED_AMA_FROZEN_PACKET.zip R0043_INPUT_MAP=/private/prepared-input-map.json bash tests/r0043-reconstruction.test.sh # published, canonically unallocated
```

Without those inputs four packet-dependent and one private-input test report
skips. With both, all nineteen controls execute. The immutable
packet belongs to the separate frozen corpus commit; its historic path is not
assumed present in a main checkout. The complete reconstruction engine and
original test bank are preserved. No test is hidden or renamed to evade the
reserved registration edge.

## Continuation and transfer

Neither this document nor issue hosting appoints a lifetime programme steward.
No predecessor is retired. An explicit compatible owner decision and full
content/field/relation/action readback remain necessary for any claimed transfer.
Unrelated current release work may proceed at its qualified scope while dormant
future states remain accessible; the two issue-owned acceptance undertakings
remain open until their own required evidence or authorised disposition exists.
