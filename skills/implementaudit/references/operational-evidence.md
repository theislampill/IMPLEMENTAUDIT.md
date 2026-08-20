# Operational Evidence Carrier

This reference owns the strict carrier boundary for R0038. Its C02 collector is
limited to read-only repository, Git, file, package-declaration and registry-file
facts plus positive Python-AST relations. It does not collect later-cell native
run/evidence/release owners, query, export, publish, schedule, mutate, refresh,
watch, serve a UI, call a model, or establish authority. Native repository,
Git, planning, controller, execution, evidence, failure, package, install, host,
CI, release, external and public owners remain authoritative.

## Canonical record

`operational-evidence-schema.json` defines
`implementaudit-operational-evidence-v1`. Every record preserves exactly one of
the frozen `CODE`, `OWNERSHIP`, `EXECUTION`, `EVIDENCE`, `FAILURE`, or `RELEASE`
families and binds a native owner, source identity, source layer, evidence
layer, and primary currentness state. The loader rejects a source/evidence
layer mismatch; a relation may connect entities from different native layers,
but its own evidence leg cannot silently borrow another layer's authority.

The primary fact states are `CURRENT`, `UNKNOWN`, `UNSUPPORTED`, `STALE`,
`UNVERIFIED`, `CONTRADICTORY`, `PARSER_ERROR`, and `INVALID`. A `CURRENT` record
cannot retain an invalidator. A `STALE` record must name at least one
invalidator. `COMPLETE` requires one required `CURRENT` entity in every frozen
family. Non-complete aggregates name their affected families explicitly, so
unsupported, missing, or invalid input never degrades to a silent empty result.

## Byte contracts

`canonical_json_v1` is UTF-8 without BOM, recursively sorted object keys,
declared array order, no insignificant whitespace, strict JSON scalars, and no
implicit Unicode or line-ending rewrite inside ordinary strings.

Source text payloads have one separate, explicit normalization before canonical
JSON serialization:

1. replace CRLF with LF;
2. replace remaining CR with LF;
3. remove every trailing LF;
4. perform no other whitespace or Unicode normalization;
5. encode as UTF-8 without BOM and verify `payload_sha256` over those bytes.

This is the trailing-LF-removed convention used by the R0038 live-object
re-anchor. A one-trailing-LF digest is not a competing content fact and is not
accepted as the canonical payload digest.

The packaged carrier is `scripts/operational-evidence.py`. `validate` returns a
typed validation receipt and `canonicalize` returns the canonical record bytes.
Unsupported schema versions and invalid inputs return one machine-readable
`implementaudit-operational-evidence-error-v1` object on standard error with a
stable error code; they never return an empty model. C01 does not register this
carrier as a shipped helper or public route. That later admission remains C11's
owner boundary.

## Bounded repository and static collection

`collect_repository` uses fixed, read-only local Git commands to bind the exact
commit, tree, worktree state and tracked input-file-set digest. Every call
disables system/global configuration, environment-supplied helpers, repository
fsmonitor, hooks, credential/SSH helpers, external diff and ext transports; it
never executes target-configured Git helpers. It hashes working-tree bytes
without following tracked symlinks. An exact pre/post fence compares commit,
tree, tracked-path population, status bytes, file type/length and every file or
symlink-target hash; any mid-scan change is a typed refusal and no mixed
`CURRENT` snapshot is returned. The same exact fence runs again after bounded
AST/package processing, immediately before facts can be returned, so a change
after the second file read is also refused. The complete result is sorted,
canonicalized and decoded into its return object before a third and truly final
physical fence. After that bound observation the prebuilt object is returned
directly: no later sorting, digest, parsing, filesystem, Git or callback-capable
work occurs. `CURRENT` is stable at that observation boundary; a later physical
change is an explicit invalidator, not a continuous-state guarantee. Every
readable tracked file stays an exact file fact; an unreadable or missing tracked
path produces a non-empty `STALE` observation and degrades the file capability
to `PARTIAL`.
Known package JSON contributes only present, positively declared shared roots.
The shell validation registry remains an exact file/hash fact; C02 does not
parse shell or infer registry entries.

Python collection uses the standard-library AST only. It never imports a target
module. A resolved local static import may produce a positive import and
reverse-dependent fact bound to the Python implementation/version, stdlib AST
module digest, fixed invocation/output schema, parser, input path and input
digest.
Computed imports stay `UNKNOWN`; syntax/UTF-8 failures remain non-empty
`PARSER_ERROR` observations; imports outside the declared local module map stay
typed `UNSUPPORTED` observations rather than missing edges; unsupported
languages remain file facts. Source edges and cycles never become work
dependencies, work-DAG cycles, `READY`, `JOIN`, deletion or
obligation-omission decisions.

`normalize_static_receipt` accepts only the versioned, data-only, offline
`implementaudit-static-receipt-v1` envelope. It binds collector/version/package,
invocation/output schema, parser/config/trust, target commit/tree/worktree,
input-set, scope completeness, diagnostics, polarity and currentness into every
normalized fact together with the native repository owner and a fixed
read-only structural-fact authority ceiling. Target-code execution,
auto-install and network modes are refused. Absence facts require a complete
supported scope; physical changes or named invalidators invalidate `CURRENT`,
and `STALE` must name its invalidator. Unsupported, missing-tool, crash/timeout
and parser-error outcomes synthesize typed non-empty observations.
C02 has no independent/native qualification owner or trust anchor. Therefore an
external receipt can never obtain `CURRENT` from a caller-issued qualification,
even when its caller-generated digest and positive/negative/unsupported/
parser-error/repeatability results are internally consistent. Every requested
external `CURRENT` is refused as `OE_STATIC_QUALIFICATION_REQUIRED` until a
separately governed later owner exists. Non-current external receipts require
qualification absence; a caller-supplied qualification is untrusted data, not
authority, and cannot be promoted by C02. A non-current envelope also demotes
any caller-declared `CURRENT` fact to the envelope's non-current state.
`normalize_static_receipts` requires one exact target snapshot, retains
overlapping provenance separately and marks opposing edge/absence claims
`CONTRADICTORY` instead of merging them.

C02 refuses every caller-supplied work-node mapping and never creates one.
Governed mapping envelopes and their native-owner joins belong to their later
owner; no current C02 output may be consumed directly by R0035. The normalizer
never invokes R0035. The APIs are C02 substrate, not CLI commands, default
preflight, helper registration, package admission, or a public route; those
remain in their assigned downstream cells.

## Canonical evidence and failure collection

`collect_evidence_failure` is the C04 read-only boundary. It accepts one fixed,
regular, bounded canonical run artifact named `operational-evidence.json`; it
does not scan or interpret STATE, ROADMAP, transcripts, reports, logs or nearby
prose. The strict `implementaudit-run-evidence-v1` input binds the run/artifact
identity and exact artifact SHA-256, then retains separate Claim, Criterion,
Evidence, Check and Review records across `ATTEMPT`, `RECEIPT`, `EFFECT`,
`RECOVERY` and `CLOSURE` legs. Receipt is distinct from attempt; either may be a
proxy, but neither can become effect, recovery or closure. Producer/check
success, a green proxy and a nonverdict review remain observations in their
declared legs; none establishes effect, recovery, PASS or closure.

The same canonical artifact retains Andon, Residual, Containment,
Countermeasure, Rerun and Recovery records as immutable FAILURE lineage. When a
non-proxy RED exists, the collector validates and preserves the earliest RED
and a declared non-proxy RED weakest leg. A population with no RED uses JSON
`null` for `first_red_id` and returns `first_red_state: NOT_APPLICABLE`; it does
not fabricate a RED and may retain a non-proxy green weakest observation.
Contrary evidence, open residual identities, cause confidence and direct
recovery evidence remain exact. Any FAILURE row that declares
`recovery_state: OBSERVED`, regardless of its record type, requires current,
non-proxy GREEN `RECOVERY` evidence. Recovery does not erase the Andon, first
RED, contrary evidence or residual. An unknown cause remains `UNKNOWN`; C04
does not guess it or create finite retry, strike-count or stopping semantics.

Every collected row has the `READ_ONLY_NATIVE_ARTIFACT_FACT` authority ceiling,
and the collection's `establishes` population is always empty. The collector
never edits evidence, infers closure, invokes a model, executes target content,
uses network or reads a noncanonical fallback. It builds canonical output before
checking the final path type and performing a byte-for-byte source reread as the
last target-sensitive operation. It directly returns the prebuilt object when
the bytes remain exact; a changed artifact is refused rather than returned as
mixed evidence. Later snapshot compilation/query/publication and native closure
decisions remain in their assigned downstream owners.

## Local and frozen external RELEASE collection

`collect_release` is the C05 read-only RELEASE boundary. It reuses the hardened
local repository collector for exact commit, tree and worktree observations,
then reads only two fixed tracked owner artifacts: `release-local.json` and
`external-capture.json`. The local manifest binds generated artifact, package,
install and host records to exact working-tree paths and SHA-256 bytes. The
frozen capture retains separate PullRequest, Check, Merge, Tag, Release, Asset
and PublicSurface records with stable IDs, commit identity, update time, ETag,
payload digest, native owner and currentness. Every emitted node remains a
`READ_ONLY_NATIVE_OBSERVATION`; the collection's `establishes` population is
empty.

Authentication absence, rate exhaustion, incomplete pagination, object drift
and capture expiry remain explicit invalidators. They conservatively demote the
external population to `UNVERIFIED`, `UNKNOWN` or `STALE`; they never become an
empty or successful external layer. A public predecessor whose commit differs
from local HEAD keeps the candidate `UNVERIFIED`. Even an exact match requires
later native candidate qualification and cannot establish merge, release,
publication, PASS or closure in C05. Local/frozen artifacts are fingerprinted
through the repository collector before and after compilation; changed local
bytes or a mixed scan are refused rather than normalized away.

`run_external_readonly` is the explicit refresh boundary, not a frozen query.
It accepts one exact data-only request with no method field, maps a small fixed
operation/path allowlist to one GitHub API `GET`, supplies fixed accept/version
headers and calls an explicit transport once. It exposes no POST, PUT, PATCH,
DELETE, GraphQL, shell, credential, pagination loop, retry or file-write verb.
The returned in-memory capture records status, ETag, response digest, rate,
pagination, auth declaration, drift, expiry and semantic digest under the
`READ_ONLY_EXTERNAL_CAPTURE` ceiling and an empty `establishes` population.
The frozen collector never invokes this runner, a model or network. Refresh
scheduling, cache publication, query, package admission, registry/helper
routing and public release actions remain with C06-C14 owners.
