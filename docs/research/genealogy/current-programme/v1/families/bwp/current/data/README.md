# BWP — scientific record guide

The narrative accounts explain the questions, mechanisms, guards, findings and uncertainty. These records make their detailed scientific basis inspectable. They preserve negative, unresolved and non-novel outcomes and historical corrections; they do not promote finite analytical constructions into empirical or operational evidence.

Repeated **identical scientific values** are stored once in [shared-records.json](shared-records.json). A value of the form `{"$scientific_ref": "…"}` refers to that key in its `definitions` object. Resolve such references recursively to reconstruct the full normalized record. The human-readable property readers link to the same passages. The transformation was checked by exact value reconstruction after the recorded source-safety substitutions. That mechanical check is not independent scientific acceptance.

The [record index](RECORD_INDEX.json) binds every record set to source hashes. Original source and review qualifications remain in [SOURCE_QUALIFICATION.json](../SOURCE_QUALIFICATION.json); actual reading limits are described in the [family account](../README.md). Dates, pending review strings and counters inside historical scientific layers retain their original scope and are not current publication verdicts.

## Record sets

| Scientific record set | Complete structured data |
|---|---|
| BWP-L1-records | [BWP-L1-records](BWP-L1-records.json) |
| BWP-L2-records | [BWP-L2-records](BWP-L2-records.json) |
| BWP-L3-records | [BWP-L3-records](BWP-L3-records.json) |
| BWP-S-records | [BWP-S-records](BWP-S-records.json) |

## Full BWP relationship population

The [relationship guide](../relationships/README.md) provides substantive examples, property navigation and complete human readers. Its [record index](relationships/RECORD_INDEX.json) identifies the full directed ledger, pair matrix, negative memberships and their supporting profiles, source roles and judgments. These new sets use their own [shared values](relationships/shared-records.json), with the same recursive reference convention; the four original display record sets above remain unchanged.
