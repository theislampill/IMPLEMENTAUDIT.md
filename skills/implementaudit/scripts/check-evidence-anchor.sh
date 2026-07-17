#!/usr/bin/env bash
set -euo pipefail

# Evidence-version anchoring consumer check (#4). Read-only.
#
#   check-evidence-anchor.sh --row "<evidence cell text>"
#       exit 0 when every `@<hex>` anchor token is a full 40-hex SHA
#       (legacy rows without anchors also pass); exit 1 otherwise.
#
#   check-evidence-anchor.sh --artifact <file> --tree <full-40-hex-sha>
#       the artifact must name the exact state it attests via an
#       `Anchor: <full-sha>` line (or `@<full-sha>` token). Exit 1 when
#       the artifact is unanchored or anchored to a DIFFERENT state —
#       a stale artifact is never accepted as current-state evidence.

fail() { printf 'check-evidence-anchor: %s\n' "$*" >&2; exit 1; }

mode="${1:-}"
case "$mode" in
  --row)
    row="${2:-}"
    bad="$(printf '%s' "$row" | grep -oE '@[0-9a-f]{7,}' \
      | grep -vE '^@[0-9a-f]{40}$' || true)"
    [ -z "$bad" ] || fail "anchor(s) not full 40-hex SHAs: $bad"
    printf 'check-evidence-anchor: row ok\n'
    ;;
  --artifact)
    artifact="${2:-}"
    [ "${3:-}" = "--tree" ] || fail "usage: --artifact <file> --tree <sha>"
    tree="${4:-}"
    printf '%s' "$tree" | grep -qE '^[0-9a-f]{40}$' \
      || fail "--tree must be a full 40-hex SHA"
    [ -f "$artifact" ] || fail "artifact not found: $artifact"
    # Every anchor-shaped token must be EXACTLY 40 hex — the same format
    # rule --row enforces. Without this, `Anchor: <sha><extra-hex>` was
    # accepted via first-40-chars truncation while the identical token in
    # a row was flagged (Fable review of PR #23).
    malformed="$(grep -oE '(Anchor: *|@)[0-9a-f]{7,}' "$artifact" \
      | sed -E 's/^(Anchor: *|@)//' | grep -vE '^[0-9a-f]{40}$' || true)"
    [ -z "$malformed" ] || fail \
      "artifact $artifact carries anchor token(s) that are not full 40-hex SHAs: $(printf '%s' "$malformed" | tr '\n' ' ')"
    anchor="$(grep -oE '(Anchor: *|@)[0-9a-f]{40}' "$artifact" \
      | grep -oE '[0-9a-f]{40}' | head -n 1 || true)"
    [ -n "$anchor" ] || fail \
      "artifact $artifact names no full-SHA anchor — unanchored artifacts are not current-state evidence"
    if [ "$anchor" != "$tree" ]; then
      fail "REFUSED: artifact is anchored to $anchor but offered for $tree — re-gather evidence on the current state"
    fi
    printf 'check-evidence-anchor: artifact anchored to the offered tree\n'
    ;;
  *)
    fail "usage: --row \"<text>\" | --artifact <file> --tree <sha>"
    ;;
esac
