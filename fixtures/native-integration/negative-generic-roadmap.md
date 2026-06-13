# Negative fixture: generic roadmap prose is not a native direction route

Input:

```text
What roadmap should this repo pursue next?
```

Reject this response shape:

- generic roadmap prose detached from repo evidence
- feature wish-list without owner/source
- mixed defect and direction advice without separation
- separated from defects is mandatory before any direction candidate can pass
- no DMADV direction/design framing
- no acceptance criteria, verification, rollback, or defer/reject outcome

Required native route:

- classify the request as DMADV direction/design unless brownfield defects are
  found first, in which case separate DMAIC repair objects from direction
  candidates;
- ground each candidate in repo evidence and owner/source;
- separate direction from defects;
- require acceptance criteria, risk, verification, rollback, and Plan Closure;
- reject or defer candidates that lack evidence.

Evidence required:

- source citation or explicit absent-source note;
- DMADV direction/design row;
- owner/source;
- acceptance criteria;
- verification;
- rollback;
- final audit classification.
