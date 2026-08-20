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
after the second file read is also refused. Every readable tracked file stays
an exact file fact; an unreadable or missing tracked path produces a non-empty
`STALE` observation and degrades the file capability to `PARTIAL`.
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
