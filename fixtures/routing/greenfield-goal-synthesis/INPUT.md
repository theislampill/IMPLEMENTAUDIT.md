# Greenfield Goal Synthesis Input

User request:

```text
/implementaudit create a new checker that prevents unsupported host-install
claims in README and references.
```

Repo context:

- No existing host-install claim checker is named in the request.
- The repo already has package validation and generated README diagram checks.
- The run must inspect current validators before creating a new checker.

Expected route:

- outer shell: brownfield repo inspection
- inner artifact: greenfield checker intake before implementation
