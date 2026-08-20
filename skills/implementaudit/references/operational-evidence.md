# Operational Evidence Carrier

This reference owns the strict carrier boundary for R0038. It does not collect,
query, export, publish, schedule, mutate, refresh, watch, serve a UI, call a
model, or establish authority. Native repository, Git, planning, controller,
execution, evidence, failure, package, install, host, CI, release, external and
public owners remain authoritative; this carrier validates their declared
observations only.

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
