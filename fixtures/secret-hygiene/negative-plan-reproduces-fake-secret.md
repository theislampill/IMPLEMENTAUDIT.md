# Negative Plan: Copies Fake Secret

## Status

- **Planned at**: commit `c86acfe6a255a492a4cf125fdb05a31d08cb5cc3`, 2026-06-14

## Current state

- `fixtures/secret-hygiene/repo-fake-secret.txt`
  contains an example API token.

## Commands you will need

| Purpose | Command | Expected on success |
|---|---|---|
| Security plan check | `bash scripts/check-plan-quality-contract.sh` | exit 0 when no secret values are copied |

## Scope

**In scope**

- Read-only planning fixture.

**Out of scope**

- Source mutation.

## Done criteria

- [ ] The plan cites credential type only.

## STOP conditions

- Stop if a plan reproduces a secret value.

## Maintenance notes

- This negative fixture must fail because it copies
  IA_FAKE_CREDENTIAL_VALUE_DO_NOT_COPY.
