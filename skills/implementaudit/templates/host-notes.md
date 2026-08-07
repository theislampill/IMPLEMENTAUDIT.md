# IMPLEMENTAUDIT Host Notes

Machine-local, append-only observations live here. The owner is the
repository-family root (the parent of Git's common directory), so linked
sibling worktrees share one file. Do not copy host-specific facts into the
portable skill payload or replace a prior row in place.

One data row per normalized signature:

```text
<ISO8601> | <signature> | <workaround> | first-seen-run: <run-id>
```

Normalize a signature by lowercasing it; removing absolute paths, process identifiers, long hexadecimal identifiers, line and column numbers, and timestamps; then retaining the first error or exception class token plus the next six words. Record the second distinct linked occurrence. A repeated signature with a reasoned `Not memoized:` disposition needs no row.
