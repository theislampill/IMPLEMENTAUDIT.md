## Normative and acceptance amendment — host-native governed turn-exit actuation

RLGWO_AMENDMENT=YES
RLGWO_OWNER=R0037 / #211
AMENDMENT_CLASS=NORMATIVE_CONTRACT_AND_ACCEPTANCE_AMENDMENT_WITH_SUPPORTING_BINDING_DEPENDENCY

LIVE_SOURCE_ANCHOR_COMMIT=62507de00e16cc2ada0e7546273988c387a20390
LIVE_SOURCE_ANCHOR_TREE=6b24f9500ac00838c9e66389f3f4dfcbf2528be3

EXISTING_R0037_TERMINAL_CAP_COMMENT=5312883966
EXISTING_TERMINAL_CAP_ACCEPTANCE_CHANGED=NO
EXISTING_TERMINAL_CAP_ROW_SATISFIED_BY_THIS_AMENDMENT=NO
EXISTING_TERMINAL_CAP_ROW_SUPERSEDED_BY_THIS_AMENDMENT=NO

This amendment is additive to the existing R0037 terminal-cap residual.

The existing requirement that arbitrary finite retry/strike-count policies must
not stop or hand off a run remains independently open until its exact current
RED is repaired and read back.

A host-imposed forced-exit ceiling, including Claude's Stop-hook override, is an
external enforcement boundary. It must never be interpreted as satisfying,
superseding or weakening the no-arbitrary-terminal-cap invariant.

NEW_ENGINEERING_PROPERTY=NO
NEW_SEMANTIC_RXX_OWNER=NO
NEW_IMPLEMENTAUDIT_ACTUATOR_MECHANISM=YES

NEW_CHILD_SKILL=NO
NEW_CONTROL_LOOP=NO
NEW_AUTHORITY_HOLDER=NO
NEW_CLOSURE_PREDICATE=NO
NEW_NONTERMINAL_TURN_YIELD_PREDICATE=YES

IMPLEMENTATION_AUTHORITY_CREATED=NO
SOURCE_MUTATION_AUTHORISED=NO
GITHUB_MUTATION_AUTHORISED=NO

### Correction to the provisional Stop assumption

HOST_STOP_SEMANTICS=HOST_TURN_END_NOT_AUDIT_OBJECT_TERMINATION

A host Stop event means that one assistant response is ending. It may represent:

- terminal verified closure;
- audited handoff;
- a truthful nonterminal yield;
- or an invalid early exit.

The presence of an active audit object does not by itself make every host Stop
an attempted terminal audit-object transition.

The actuator must not create an agent prison by blocking a genuinely required
user clarification, owner-authority wait, bounded external wait, deliberate
pause, interruption or progress/status response.

### Semantic-centre delta

SEMANTIC_CENTRE_DELTA=
  R0037's nested control and terminal-governance contract shall distinguish
  host-turn exit from audit-object terminal state and, on an admitted host,
  may actuate the existing governor-owned closure/handoff predicates plus one
  distinct mechanically valid nonterminal-yield predicate.

CORE_INVARIANT_DELTA=
  On a supported, enabled and trusted host, a Stop actuator may govern an audit
  object only after an exact host-session-to-controller-to-current-run binding
  has been proved.

  For that bound object, Stop is allowed only when exactly one truthful
  disposition is established:

  1. terminal verified closure;
  2. valid audited handoff; or
  3. valid nonterminal yield.

  Host-turn end is not itself evidence for any of those dispositions.

  The actuator is not a child skill, lifecycle stage, control loop, closure
  predicate, currentness authority, mutation authority, release authority or
  AUDIT_COMPLETE authority.

### Current preimage

CURRENT_SOURCE_HAS_CLOSURE_VALIDATOR=YES
CURRENT_SOURCE_HAS_HANDOFF_CONTRACT=YES
CURRENT_SOURCE_HAS_NONTERMINAL_STATE_VOCABULARY=YES
CURRENT_SOURCE_HAS_SPECIFIC_MID_PHASE_PAUSE_CONTRACT=YES

CURRENT_SOURCE_HAS_HOST_NATIVE_STOP_ACTUATOR=NO
CURRENT_SOURCE_USES_HOST_SESSION_ID=NO
CURRENT_SOURCE_HAS_HOST_SESSION_TO_CONTROLLER_BINDING=NO
CURRENT_SOURCE_HAS_GENERIC_STOP_TIME_YIELD_PREDICATE=NO

CURRENT_SOURCE_RUNTIME_GAP_PROVED=YES
CURRENT_SOURCE_RUNTIME_DELTA_PROVED=YES

The current machine-readable custody chain begins at the controller:

  refs/implementaudit/controllers/<controller>
  -> implementaudit.controller-current.v1
  -> claim ID + explicit run root
  -> .controller + .claimed
  -> STATE epoch
  -> applicable continuity receipt.

It does not contain the preceding host-session -> controller edge.

### Active-object binding

ACTIVE_OBJECT_BINDING_REQUIRED=YES

Required qualifying chain:

  host session ID
  -> exact controller ID + claim ID
  -> refs/implementaudit/controllers/<controller>
  -> explicit current run root
  -> validated .controller and .claimed custody
  -> applicable currentness/continuity receipt.

SESSION_ID_USED_BY_CURRENT_SOURCE=NO
SESSION_ID_USE_REQUIRED_BY_AMENDMENT=YES

CONTROLLER_SINGLETON_LOOKUP_IS_SESSION_BINDING=NO
CWD_IS_SESSION_BINDING=NO
NEWEST_RUN_DIRECTORY_IS_SESSION_BINDING=NO
MODEL_PROSE_IS_SESSION_BINDING=NO
CHILD_OUTPUT_IS_SESSION_BINDING=NO

The binding must be established during governed activation, before Stop.
Stop-time lookup must be read-only.

If governed activation cannot establish the binding, the package must surface
that host-native Stop enforcement is unavailable. It must not silently claim
enforcement and must not ask the Stop hook to guess a run root.

No active binding in a genuinely ordinary session is the immediate cheap-path
allow case.

A previously established binding whose controller, claim, run root or
currentness proof is stale, foreign, missing or ambiguous is a blocking identity
residual, not an ordinary-session allow case.

DIRECT_IN_SESSION_BOUNDARY=
  Current direct in-session governance has no equivalent durable machine
  binding. Until a minimal session-bound object record is separately proved,
  host-native Stop enforcement qualifies only for machine-bound objects.
  Direct in-session runs retain the normative closure contract and no
  host-interception claim.

### Turn-disposition classification

TURN_DISPOSITION=
  NO_ACTIVE_OBJECT |
  TERMINAL_CLOSURE |
  AUDITED_HANDOFF |
  NONTERMINAL_YIELD

The adapter must not infer terminal intent merely because Stop fired.

TERMINAL_CLOSURE_CLAIM=
  AUDIT_COMPLETE, IMPLEMENTAUDIT_RUN_COMPLETE or an equivalent authoritative
  terminal-state claim on the current response/state surface.

AUDITED_HANDOFF_CLAIM=
  AUDIT_HANDOFF or ANDON_HANDOFF under the existing handoff exclusivity and
  evidence contract.

NONTERMINAL_YIELD=
  The host turn ends while the audit object remains open and a deterministic
  validator proves durable current state sufficient for safe continuation.

### Nonterminal-yield predicate

NEW_LIFECYCLE_STATE_REQUIRED=NO
EXISTING_STATE_REUSE_REQUIRED=YES

The yield validator shall consume the existing run-root owners rather than
create a second audit object:

- controller/claim/currentness binding;
- STATE Current phase table;
- audit-object state;
- applicable Andon row;
- IMPLEMENTAUDIT_PAUSE record when its existing in-phase interruption trigger
  applies;
- current phase/specification where one exists.

A valid nonterminal yield requires:

1. the exact bound run root passes applicable structural validation;
2. STATE uses one applicable nonterminal status:
   open, READY_TO_DISPATCH, IN_PHASE, PAUSED, BLOCKED or INTERRUPTED;
3. audit-object state remains explicitly nonterminal;
4. current phase/frontier is identifiable;
5. Last check records the latest safe evidence boundary or an exact
   not-yet-run intake reason;
6. Next action is concrete, nonempty and not `none` or `pending`;
7. owner/source and authorization state are current where relevant;
8. any blocker, external dependency or owner decision is durably identified;
9. the re-entry condition or next probe is explicit;
10. no completion marker is present;
11. no handoff marker is present unless the handoff predicate, rather than the
    yield predicate, is being evaluated.

State-specific requirements:

- IN_PHASE:
  current checkpoint, last completed safe step and next action are present.

- PAUSED:
  pause reason and resume point are present. When the pause follows a user
  interruption during an active phase, the existing IMPLEMENTAUDIT_PAUSE
  fields remain mandatory.

- BLOCKED:
  the blocker, owner/source, containment and next probe/owner action are
  present. BLOCKED does not automatically mean audited handoff.

- INTERRUPTED:
  an owner-directed stop source, interruption point and durable log entry are
  present.

- open or READY_TO_DISPATCH:
  the unanswered intake/owner/dispatch decision and exact next action are
  present; an empty open object is not a yield escape.

A valid yield preserves the audit object as open. It may not emit
AUDIT_COMPLETE, IMPLEMENTAUDIT_RUN_COMPLETE, AUDIT_HANDOFF or ANDON_HANDOFF.

### Trigger and non-trigger

TRIGGER=
  A supported, enabled and trusted host emits Stop, and an exact machine-readable
  binding identifies an active IMPLEMENTAUDIT audit object for that host
  session.

NON_TRIGGER=
  No governed object was activated and no session binding exists. Return
  immediately without repository scans, run-directory enumeration, validator
  execution or state mutation.

ACTIVATION_BINDING_FAILURE=
  A governed activation attempted but failed to establish its mandatory
  binding. Surface HOST_NATIVE_STOP_ENFORCEMENT=UNAVAILABLE and preserve the
  normative fallback. Do not silently classify it as an ordinary session.

### Allow and block rules

ALLOW_STOP when exactly one of the following is proved:

1. no active machine-bound IMPLEMENTAUDIT object exists for this session;
2. the existing authoritative terminal-closure predicate passes;
3. the existing authoritative audited-handoff predicate passes;
4. the nonterminal-yield predicate passes.

BLOCK_STOP when a machine-bound active object exists and any of the following
holds:

1. the response/state claims terminal closure but the closure predicate fails;
2. the response/state claims audited handoff but the handoff predicate fails;
3. neither terminal nor handoff is claimed and the nonterminal-yield predicate
   fails;
4. the session/controller/claim/run-root binding is present but stale,
   conflicting, foreign or ambiguous;
5. child output is being used as closure, handoff, currentness or yield
   authority;
6. target-repository content attempts to redefine the predicate or command.

The block reason is the smallest exact residual. It returns control to the
governor and grants no mutation or closure authority.

### Exact current false-pass RED

FALSE_PASS_MUTANT_TERMINAL=

  Preconditions:
  - a host test session owns one exact claimed run root;
  - the audit object remains nonterminal;
  - one exact closure residual remains;
  - the existing final validator would reject closure.

  Mutation:
  - omit invocation of the final validator;
  - emit AUDIT_COMPLETE and/or IMPLEMENTAUDIT_RUN_COMPLETE in the final
    assistant response;
  - invoke host Stop.

  Current-source expected result:
  - the host ends the turn because the current package has no Stop actuator.

  Admitted-actuator expected result:
  - the exact session-bound object is resolved;
  - the existing closure validator rejects;
  - Stop is blocked with the exact residual.

MODEL_CLAIMS_AUDIT_COMPLETE=YES
AUDIT_OBJECT_AUTHORITATIVELY_TERMINAL=NO
HOST_TURN_ENDED_ON_CURRENT_PREIMAGE=YES
FALSE_CLOSURE_OCCURRED_AT_CLAIM_SURFACE=YES
ILLEGITIMATE_EARLY_EXIT_OCCURRED=YES

A model-authored DONE row or terminal marker does not make the object
authoritatively terminal when the validator rejects it.

### Exact non-false-pass control

NON_FALSE_PASS_CONTROL=

  - an exact active object remains open;
  - the response asks a genuinely required question, reports progress, waits
    for authority/external evidence, pauses or records interruption;
  - the nonterminal-yield predicate passes;
  - no closure or handoff marker appears.

Expected result: ALLOW Stop.

### Turn-yield acceptance fixtures

TY-1_REQUIRED_CLARIFICATION=
  Positive fixture. PAUSED/open nonterminal state, exact question and re-entry
  action; Stop allowed.

TY-2_OWNER_AUTHORITY_WAIT=
  Positive fixture. Missing mutation/publication/commit/release authority is
  explicit, no effect occurs, next owner action is exact; Stop allowed.

TY-3_EXTERNAL_DEPENDENCY_WAIT=
  Positive fixture. BLOCKED or PAUSED, dependency identity, last evidence,
  containment and next probe recorded, no handoff claim; Stop allowed.

TY-4_PAUSED_OR_INTERRUPTED=
  Positive fixture. Existing PAUSED/INTERRUPTED state and applicable pause/log
  evidence pass; Stop allowed.

TY-5_PROGRESS_STATUS=
  Positive fixture. IN_PHASE/open/READY current checkpoint and concrete next
  action, no terminal claim; Stop allowed.

TY-6_BARE_ABANDONMENT=
  Negative fixture. Active bound object, no valid closure, no handoff and no
  valid nonterminal-yield state; Stop blocked.

TY-6 does not become a false-closure claim merely because the host turn would
otherwise end. Its failure class is illegitimate early exit or missing durable
yield state.

### Binding acceptance fixtures

BINDING_POSITIVE=
  Exact host session resolves one controller, claim and current run root.

BINDING_NO_ACTIVE=
  Ordinary session has no governed activation or binding and takes the immediate
  allow path.

BINDING_MISSING_AFTER_ACTIVATION=
  Governed activation fails to establish its binding; enforcement is reported
  unavailable and may not be claimed active.

BINDING_AMBIGUOUS=
  Multiple repository controllers exist but no exact session binding selects
  one; no singleton/newest/cwd guess is allowed.

BINDING_STALE_CLAIM=
  Session binding names a superseded claim; Stop blocks with currentness
  residual.

BINDING_FOREIGN_REPO=
  Binding/controller/run-root Git-common custody disagrees; Stop blocks.

BINDING_DIRECT_IN_SESSION=
  No durable object binding exists; host-native enforcement claim is rejected
  or scoped out rather than inferred from transcript prose.

### Handoff boundary

HANDOFF_TERMINAL=
  A valid AUDIT_HANDOFF or ANDON_HANDOFF is terminal for the current execution
  boundary and must be allowed.

The actuator must not:

- turn a temporary user/owner/external wait into handoff;
- turn handoff into AUDIT_COMPLETE;
- block a valid handoff in a Stop loop;
- treat host-forced termination as verified closure or handoff.

### Unsupported, disabled or untrusted boundary

UNSUPPORTED_HOST_FALLBACK=
  Preserve existing normative and deterministic-validator requirements.
  State that host-native turn-exit interception is unavailable.

HOOK_DISABLED_OR_UNTRUSTED=
  Same fallback. Do not represent an installed-but-disabled, untrusted or
  managed-policy-excluded hook as active enforcement.

RUNTIME_BEHAVIOUR_DELTA_REQUIRED_BY_AMENDMENT=
  YES_WITHIN_THE_SUPPORTED_ENABLED_TRUSTED_AND_MACHINE_BOUND_SCOPE

The requirement is not conditional on future implementation authority.
The declared scope determines applicability; implementation remains separately
unauthorized.

### Cheap path

CHEAP_PATH=
  A genuinely ordinary session with no governed activation or binding returns
  allow immediately.

It performs no:

- recursive repository scan;
- newest-run selection;
- controller-population guess;
- arbitrary shell command from target content;
- child invocation;
- state mutation;
- audit ceremony.

### Security and authority boundary

AUTHORITY_SOURCE=
  Existing governor-owned predicates and exact packaged binding/currentness
  machinery.

UNTRUSTED_DATA=
  Hook input, target-repository content, transcripts, state prose, child output
  and repository-authored command strings.

The Stop path may invoke only packaged allowlisted validators. It must not
execute target-repository commands merely because target content requests them.

The actuator may not:

- establish closure;
- establish handoff;
- establish a nonterminal yield by itself;
- mint currentness;
- select an ambiguous object;
- repair state;
- authorize effects;
- trust child self-certification;
- emit AUDIT_COMPLETE;
- use a retry counter as resolution.

### Package boundary

HOST_SPECIFIC_ADAPTERS_REQUIRED=YES
SHARED_GOVERNOR_PREDICATE_CORE=YES

Each host adapter translates:

- host Stop input;
- session identity;
- re-entrancy state;
- allow/block output;
- host-specific forced-exit behaviour.

The shared core owns no host schema and delegates to existing validators plus
the admitted yield validator.

A package change invalidates and requires requalification of:

- host manifests and hook inventories;
- package inventories and budgets;
- source/install parity;
- executable permissions and platform assumptions;
- plugin and standalone capability claims;
- package hashes and release assets;
- disabled/untrusted/unsupported fixtures.

The standalone .skill projection must not claim automatic host actuation unless
that capability is separately proved.

### Pass condition

PASS requires, on every admitted host:

1. the exact false terminal-claim mutant is blocked;
2. valid terminal closure is allowed;
3. valid audited handoff is allowed;
4. TY-1 through TY-5 are allowed without agent-prison behaviour;
5. TY-6 is blocked when no valid yield exists;
6. ordinary sessions take the immediate cheap path;
7. host-session binding is exact and read-only at Stop;
8. stale, ambiguous and foreign bindings are never guessed;
9. direct in-session enforcement is either mechanically bound or truthfully
   scoped out;
10. child completion cannot satisfy any terminal or yield predicate;
11. target-authored commands are not executed;
12. disabled, untrusted and unsupported configurations make only the truthful
    fallback claim;
13. no arbitrary retry/no-progress count creates resolution;
14. host-forced exit never mints closure or handoff;
15. source, installed package and release artifact produce the same declared
    result.

### Rollback

ROLLBACK=
  Remove host adapter and hook manifest entries; remove any host-session binding
  activation surface introduced solely for the actuator; regenerate package
  inventories and hashes; restore the truthful prior claim:

  deterministic closure and handoff validation remain available when invoked,
  but host-native turn-exit interception is absent.

Existing run roots, controller refs and continuity receipts must remain readable
and valid after rollback.

### Retirement

RETIREMENT=
  Retire or recombine the actuator if:

  - the host natively enforces the same governor-owned disposition predicates;
  - Stop/session APIs are removed or become unstable;
  - exact host-session binding cannot be maintained;
  - truthful nonterminal yield cannot be distinguished without agent prison;
  - the ordinary-session cheap path becomes materially expensive;
  - cross-platform/trust boundaries cannot be stated truthfully; or
  - evidence shows the actuator does not change a protected decision.

### Recombination

R0037 remains the semantic owner.

Supporting recombination includes:

- durable run-root/controller/continuity ownership for the missing
  host-session binding edge;
- currentness and state-legibility owners;
- predicate/checker-trust ownership;
- atomic dual-host package and inventory ownership;
- security/trust-boundary ownership;
- engineering-value, cheap-path and retirement ownership;
- execution-conformance reasoning where policy and machinery exist but the
  required route is omitted.

No supporting owner gains closure, lifecycle, handoff, currentness or
AUDIT_COMPLETE authority.

NORMATIVE_CONTRACT_DELTA=YES
NORMATIVE_ACCEPTANCE_DELTA=YES
CURRENT_SOURCE_RUNTIME_GAP_PROVED=YES
CURRENT_SOURCE_RUNTIME_DELTA_PROVED=YES

NEW_RXX=NO
IMPLEMENTATION_AUTHORISED=NO
IMPLEMENTATION_AUTHORITY_CREATED=NO
GITHUB_MUTATION_AUTHORISED=NO
SOURCE_MUTATION_AUTHORISED=NO