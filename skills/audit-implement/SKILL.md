---
name: audit-implement
description: Internal maintainer-side realised-implementation qualification cognition routed by the /implementaudit governor after verified release currentness; derives an evidence-bounded implement without mutation or release authority.
metadata:
  version: "0.4.0"
---

# audit-implement

Internal maintainer-only package-relative cognition. Here `implement` is a
project-domain deverbal noun: the implementation concretely realised for the
exact candidate and claim. The productive inversion is `IMPLEMENTAUDIT:
implement -> audit`; `audit-implement: audit -> implement`.

```text
ROUTING_OWNER=/implementaudit
GOVERNOR_ROUTE_ENVELOPE=REQUIRED
TRIGGER=MAINTAINER_EXACT_CANDIDATE_AFTER_VERIFIED_RELEASE_CURRENTNESS
RELEASE_CURRENTNESS=VERIFIED_REQUIRED
RELEASE_CURRENTNESS_NOT_APPLICABLE=REJECTED
PACKAGE_GATE_SUBJECT=EXECUTING_IMPLEMENTAUDIT_PACKAGE
DIRECT_ENTRY=REFUSE_OR_RETURN_TO_GOVERNOR
CHILD_ROUTING=FORBIDDEN
RETURN_TO_GOVERNOR=REQUIRED
AUTHORITY_OWNERSHIP=NONE
CURRENTNESS_OWNERSHIP=NONE
LIFECYCLE_OWNERSHIP=NONE
STATE_MUTATION_OWNERSHIP=NONE
RELEASE_OWNERSHIP=NONE
CLOSURE_OWNERSHIP=NONE
CAN_ESTABLISH_AUDIT_COMPLETE=NO
```

Accept a route only when the governor envelope identifies this child, proves
the complete executing package and unambiguous precedence, proves maintainer
scope and mechanically verified release currentness, and binds exact source,
commit/tree, generated artifact, package, install and applicable host identity
to the claimed next boundary. `NOT_APPLICABLE`, stale, absent, mixed, or
ambiguous identity refuses and returns to `/implementaudit`.

For one exact non-release proposition, the child may return the following
closed evidential-support v2 envelope. Eight exact pre-v2 return-state tokens
are frozen as compatibility inputs; the canonical validator accepts them only
on a neutral verification-only route and does not claim a pre-v2 parser existed.

<!-- AUDIT_IMPLEMENT_EVIDENTIAL_SUPPORT_V2_SCHEMA_START -->
```json
{
  "$id": "implementaudit.audit-implement.evidential-support.v2",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "schema",
    "audit_object",
    "proposition_domain",
    "proposition",
    "evidence_id",
    "evidence_sha256",
    "evidence_kind",
    "support",
    "authority_ceiling"
  ],
  "properties": {
    "schema": {
      "const": "implementaudit.audit-implement.evidential-support.v2"
    },
    "audit_object": {
      "type": "string",
      "minLength": 1
    },
    "proposition_domain": {
      "const": "non-release"
    },
    "proposition": {
      "type": "string",
      "minLength": 1,
      "$comment": "Full NFC stability and Unicode Cc/Cf rejection are enforced by the canonical validator.",
      "pattern": "^[^\\s\\u0000-\\u001f\\u007f-\\u009f\\u00ad\\u0600-\\u0605\\u061c\\u06dd\\u070f\\u0890-\\u0891\\u08e2\\u180e\\u200b-\\u200f\\u202a-\\u202e\\u2060-\\u2064\\u2066-\\u206f\\ufeff\\ufff9-\\ufffb](?:.*[^\\s\\u0000-\\u001f\\u007f-\\u009f\\u00ad\\u0600-\\u0605\\u061c\\u06dd\\u070f\\u0890-\\u0891\\u08e2\\u180e\\u200b-\\u200f\\u202a-\\u202e\\u2060-\\u2064\\u2066-\\u206f\\ufeff\\ufff9-\\ufffb])?$"
    },
    "evidence_id": {
      "type": "string",
      "minLength": 1
    },
    "evidence_sha256": {
      "type": "string",
      "pattern": "^[0-9a-f]{64}$"
    },
    "evidence_kind": {
      "enum": [
        "absence",
        "attempt",
        "exact-observation",
        "nearby-release-claim",
        "package-membership",
        "receipt"
      ]
    },
    "support": {
      "enum": [
        "established",
        "contradicted",
        "insufficient",
        "not-applicable"
      ]
    },
    "authority_ceiling": {
      "const": "none"
    }
  },
  "allOf": [
    {
      "if": {
        "properties": {
          "support": {
            "const": "established"
          }
        },
        "required": [
          "support"
        ]
      },
      "then": {
        "properties": {
          "evidence_kind": {
            "const": "exact-observation"
          },
          "proposition_domain": {
            "const": "non-release"
          },
          "proposition": {
            "not": {
              "pattern": "^([Rr][Ee][Ll][Ee][Aa][Ss][Ee]|[Cc][Uu][Rr][Rr][Ee][Nn][Tt][Nn][Ee][Ss][Ss]|[Ll][Ii][Ff][Ee][Cc][Yy][Cc][Ll][Ee]):"
            }
          }
        }
      }
    }
  ]
}
```
<!-- AUDIT_IMPLEMENT_EVIDENTIAL_SUPPORT_V2_SCHEMA_END -->

The canonical return-envelope consumer is
`../implementaudit/scripts/validate-audit-implement-return.py`. Before a child
return is decision-usable, the governor invokes it with the exact bound audit
object, proposition domain and identity, evidence identity/digest and evidence
kind. Schema validity is structural only: the governor still adjudicates
whether an exact observation actually supports the proposition. Validator
success grants no authority and never skips fresh governor re-derivation.

`established` means only that the exact bound observation supports the exact
bound proposition. `contradicted` means that observation refutes it;
`insufficient` leaves it unverified; `not-applicable` says the evidence does not
bear on that proposition. Absence, attempt, receipt, package membership and a
nearby release claim never establish support. The envelope must match the
governor-bound audit object, explicit `non-release` proposition domain,
proposition, evidence identity, lowercase SHA-256, evidence kind and
`authority_ceiling=none`. Canonical v2 bytes are one compact UTF-8 JSON object
with schema-order keys and no structural whitespace, BOM or terminal newline.
After JSON decode, the consumer recursively rejects decoded C0, DEL and Unicode category `Cc` or `Cf`
in every string field. Its proposition lexical normal form is NFC-stable, nonempty, has no leading/trailing Unicode whitespace
and contains no `Cc`, `Cf` or hidden format prefix; validate that form before case-insensitive prohibited-domain classification.
Invalid UTF-8/JSON, noncanonical bytes, missing, unknown or duplicate fields,
an unknown discriminator/state/kind, a binding mismatch, or authority-bearing
output fails closed to the governor.

Compare without collapsing source, generated, packaged, installed, hosted,
exact-main, released and public-readback states. Return the bounded
realised implementation supported at each applicable evidence surface:
established, contradicted, insufficient, stale, identity mismatch,
qualification gap, unresolved, or boundary not supportable. Its direction is
`observed evidence -> bounded realised implement`, never intent or diagnosis ->
mutation. State what progression the evidence supports as advice to the
governor, not permission.

The shared qualification and marker owner is
`../implementaudit/references/transcript-contract.md`; package and currentness
checks remain deterministic governor/substrate work. Do not establish formal
qualification, provenance, currentness, global PASS, release or closure; do not
commit, push, merge, tag, publish, release, mutate lifecycle, close a tracker,
or own a DAG JOIN. Return to the governor for the consequential decision.
