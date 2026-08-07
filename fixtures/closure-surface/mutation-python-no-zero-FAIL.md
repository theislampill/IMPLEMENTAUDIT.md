claim: python-close | surface: api | property: behavioral | status: verified | evidence-surface: api | external-kind: mutation | external-mutation-record: python-close
external-mutation-record: python-close | runner: python | target-kind: issue | target-id: 207 | mutation-command: subprocess.run(["gh","issue","close","207"], capture_output=True) | mutation-evidence: python-mut | readback-command: subprocess.run(["gh","issue","view","207","--json","state"], capture_output=True) | readback-exit: 0 | readback-file: external-close-readback-PASS.json | readback-sha256: 2a25ed590f602f5941d5ccea2ed27345c83de9184757a91b4b1b93fb635370dc | readback-field: state | expected-value: CLOSED | observed-value: CLOSED | readback-evidence: python-read

```python
result = subprocess.run(["gh", "issue", "close", "207"], capture_output=True)
if result.returncode:
    raise RuntimeError("mutation failed")
```
