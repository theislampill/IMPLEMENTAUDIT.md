claim: close-207 | surface: api | property: behavioral | status: verified | evidence-surface: api | external-kind: mutation | external-mutation-record: close-207
external-mutation-record: close-207 | runner: bash | target-kind: issue | target-id: 207 | mutation-command: gh issue close 207 | mutation-exit: 0 | mutation-evidence: mut-207 | readback-command: gh issue view 207 --json state | readback-exit: 0 | readback-file: external-close-readback-PASS.json | readback-sha256: 2a25ed590f602f5941d5ccea2ed27345c83de9184757a91b4b1b93fb635370dc | readback-field: state | expected-value: CLOSED | observed-value: CLOSED | readback-evidence: read-207

## Suggested Commit Message When No Commit Authorized

```text
fix: issue 207 closure verified

Evidence anchor: claim:close-207
```
