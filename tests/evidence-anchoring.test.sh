#!/usr/bin/env bash
set -euo pipefail

# Evidence-version anchoring (#4): detect-env anchor fields, full-SHA
# anchor format enforcement, and stale-artifact substitution refusal.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

de="$repo_root/skills/implementaudit/scripts/detect-env.sh"
cea="$repo_root/skills/implementaudit/scripts/check-evidence-anchor.sh"
vrr="$repo_root/skills/implementaudit/scripts/validate-run-root.sh"

fail() { printf 'evidence-anchoring: %s\n' "$*" >&2; exit 1; }

# Package-version attribution must survive all generated layouts. The helper
# resolves generated package identity, not an archive-local host manifest.
[ "$(bash "$de" --package-version)" = "0.4.0" ] \
  || fail "source package version did not resolve to 0.4.0"

mkdir -p "$tmp/standalone" "$tmp/plugin/skills/implementaudit" \
  "$tmp/plugin/package" "$tmp/missing"
cp "$repo_root/package/implementaudit-package.json" \
  "$tmp/standalone/IMPLEMENTAUDIT_PACKAGE.json"
cp "$repo_root/package/implementaudit-package.json" \
  "$tmp/plugin/IMPLEMENTAUDIT_PACKAGE.json"
[ "$(bash "$de" --package-version "$tmp/standalone")" = "0.4.0" ] \
  || fail "standalone package version did not resolve"
[ "$(bash "$de" --package-version "$tmp/plugin/skills/implementaudit")" = "0.4.0" ] \
  || fail "canonical plugin package version did not resolve"
[ "$(bash "$de" --package-version "$tmp/missing")" = "unknown" ] \
  || fail "missing package identity must resolve to unknown"

cp "$repo_root/package/implementaudit-package.json" \
  "$tmp/plugin/package/implementaudit-package.json"
python - "$tmp/plugin/package/implementaudit-package.json" <<'PY'
import json
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
data = json.loads(path.read_text(encoding="utf-8"))
data["runtime_version"] = "9.9.9"
path.write_text(json.dumps(data) + "\n", encoding="utf-8")
PY
if bash "$de" --package-version "$tmp/plugin/skills/implementaudit" \
    >"$tmp/package-version-conflict.out" 2>&1; then
  fail "contradictory package versions unexpectedly resolved"
fi
grep -F "package version contradiction" "$tmp/package-version-conflict.out" >/dev/null \
  || fail "package version contradiction diagnostic is missing"

# --- detect-env fixture pair: WITHOUT upstream ------------------------------
mkdir "$tmp/no-upstream" && cd "$tmp/no-upstream"
git init -q . && git -c user.email=t@t -c user.name=t commit -q --allow-empty -m x
out="$(bash "$de")"
printf '%s\n' "$out" | grep -qE '^head=[0-9a-f]+ \(' || fail "no head=<sha> (<date>) field"
printf '%s\n' "$out" | grep -q '^upstream=none$' || fail "expected upstream=none"
printf '%s\n' "$out" | grep -q '^remote_freshness=not_checked$' \
  || fail "missing remote_freshness=not_checked"

# --- detect-env fixture pair: WITH upstream (behind 0 / ahead 1) ------------
cd "$tmp"
git clone -q "$tmp/no-upstream" with-upstream
cd "$tmp/with-upstream"
git -c user.email=t@t -c user.name=t commit -q --allow-empty -m y
out2="$(bash "$de")"
printf '%s\n' "$out2" | grep -qE '^upstream=origin/[^ ]+ behind_ahead=0/1$' \
  || fail "expected upstream=origin/<branch> behind_ahead=0/1, got: $(printf '%s' "$out2" | grep '^upstream=')"
printf '%s\n' "$out2" | grep -q '^remote_freshness=not_checked$' \
  || fail "missing remote_freshness with upstream"

# read-only: detect-env must not have touched the work tree
[ -z "$(git status --short)" ] || fail "detect-env mutated the repo"

cd "$repo_root"

# --- anchor row format: full SHA passes, short SHA fails --------------------
full="0123456789abcdef0123456789abcdef01234567"
bash "$cea" --row "grep clean @$full" >/dev/null || fail "full-sha row rejected"
if bash "$cea" --row "grep clean @0123456f" >/dev/null 2>&1; then
  fail "short-sha anchor row was accepted"
fi
bash "$cea" --row "legacy row without anchor" >/dev/null \
  || fail "legacy unanchored row rejected (must stay valid)"

# --- artifact substitution refusal ------------------------------------------
other="fedcba9876543210fedcba9876543210fedcba98"
printf 'verdict: ok\nAnchor: %s\n' "$full" > "$tmp/verdict.md"
bash "$cea" --artifact "$tmp/verdict.md" --tree "$full" >/dev/null \
  || fail "matching-anchor artifact refused"
if bash "$cea" --artifact "$tmp/verdict.md" --tree "$other" >/dev/null 2>&1; then
  fail "artifact anchored to tree X was ACCEPTED for tree Y"
fi
printf 'verdict: ok, no anchor\n' > "$tmp/unanchored.md"
if bash "$cea" --artifact "$tmp/unanchored.md" --tree "$full" >/dev/null 2>&1; then
  fail "unanchored artifact was accepted as current-state evidence"
fi

# --- malformed anchor tokens in artifacts (Fable review of PR #23) ----------
# A 41-hex anchor must not pass by first-40-chars truncation.
printf 'verdict: ok\nAnchor: %sf\n' "$full" > "$tmp/longhex.md"
if bash "$cea" --artifact "$tmp/longhex.md" --tree "$full" >/dev/null 2>&1; then
  fail "41-hex anchor was accepted via truncation"
fi
# A short @token in an artifact violates the same format rule rows enforce.
printf 'see @0123456f\nAnchor: %s\n' "$full" > "$tmp/shorttok.md"
if bash "$cea" --artifact "$tmp/shorttok.md" --tree "$full" >/dev/null 2>&1; then
  fail "artifact with a short-sha anchor token was accepted"
fi
# Two VALID full anchors (attestation header first, body reference later)
# stay accepted: the FIRST anchor names the attested tree; later full-SHA
# tokens are legitimate commit references, not the attestation.
printf 'Anchor: %s\nfixes regression from @%s\n' "$full" "$other" \
  > "$tmp/mixed.md"
bash "$cea" --artifact "$tmp/mixed.md" --tree "$full" >/dev/null \
  || fail "artifact with a valid header anchor plus a full-SHA body reference was refused"

# #87: an optional bounded-surface manifest preserves an artifact across only
# disjoint commit changes. Without the manifest, exact whole-tree identity is
# unchanged; an intersecting or unsafe declaration stays red.
mkdir "$tmp/surface-repo"
(
  cd "$tmp/surface-repo"
  git init -q
  git config user.email test@example.invalid
  git config user.name 'ImplementAudit Test'
  mkdir -p relevant unrelated
  printf 'A\n' > relevant/a.txt
  printf 'A\n' > unrelated/a.txt
  git add . && git commit -qm anchor
  anchor="$(git rev-parse HEAD)"
  printf 'relevant/**\n' > surfaces.txt
  surfaces_sha="$(sha256sum surfaces.txt | awk '{print $1}')"
  printf 'Anchor: %s\nBound-Surfaces-SHA256: %s\n' "$anchor" "$surfaces_sha" > verdict.md
  printf '../outside\n' > unsafe-surfaces.txt
  unsafe_sha="$(sha256sum unsafe-surfaces.txt | awk '{print $1}')"
  printf 'Anchor: %s\nBound-Surfaces-SHA256: %s\n' "$anchor" "$unsafe_sha" > unsafe-verdict.md
  if bash "$cea" --artifact unsafe-verdict.md --tree "$anchor" --bound-surfaces unsafe-surfaces.txt >/dev/null 2>&1; then
    fail "unsafe bounded-surface declaration accepted at an equal anchor"
  fi
  printf 'B\n' > unrelated/a.txt
  git add unrelated/a.txt && git commit -qm unrelated
  current="$(git rev-parse HEAD)"
  bash "$cea" --artifact verdict.md --tree "$current" --bound-surfaces surfaces.txt >/dev/null \
    || fail "disjoint bounded-surface change invalidated artifact"
  printf 'other/**\n' > surfaces.txt
  if bash "$cea" --artifact verdict.md --tree "$current" --bound-surfaces surfaces.txt >/dev/null 2>&1; then
    fail "substituted bound-surfaces manifest accepted without artifact binding"
  fi
  printf 'relevant/**\n' > surfaces.txt
  if bash "$cea" --artifact verdict.md --tree "$current" >/dev/null 2>&1; then
    fail "missing bound-surfaces manifest weakened exact whole-tree refusal"
  fi
  printf 'B\n' > relevant/a.txt
  git add relevant/a.txt && git commit -qm relevant
  current="$(git rev-parse HEAD)"
  if bash "$cea" --artifact verdict.md --tree "$current" --bound-surfaces surfaces.txt >/dev/null 2>&1; then
    fail "intersecting bounded-surface change accepted"
  fi
  if bash "$cea" --artifact verdict.md --tree "$current" --bound-surfaces unsafe-surfaces.txt >/dev/null 2>&1; then
    fail "unsafe bounded-surface declaration accepted"
  fi
)

# --- run-root validation: short-sha anchor in STATE.md fails ----------------
seed="$tmp/run-root"
mkdir -p "$seed/phases"
for f in ROADMAP.md THINKING.md PROTOCOL.md context.md tools.md sidecars.md; do
  printf 'x\n' > "$seed/$f"
done
cp "$repo_root/skills/implementaudit/templates/STATE.md" "$seed/STATE.md"
if bash "$vrr" "$seed" >/dev/null 2>&1; then
  base_ok=1
else
  base_ok=0  # template may fail other structural checks; we only need the delta
fi
printf '| 1 | f | 1 | a | open | grep @%s | - | - |\n' "$full" >> "$seed/STATE.md"
out3="$(bash "$vrr" "$seed" 2>&1 || true)"
printf '%s' "$out3" | grep -q 'anchor' && fail "full-sha anchor flagged by validator"
printf '| 2 | f | 1 | a | open | grep @0123456f | - | - |\n' >> "$seed/STATE.md"
out4="$(bash "$vrr" "$seed" 2>&1 || true)"
printf '%s' "$out4" | grep -q 'anchor' \
  || fail "short-sha anchor NOT flagged by validator"

# #76 R3-F1/F2: capture, intended command, and landed verification share one
# process, so no stale, forged, substituted, or reusable receipt exists.
mkdir "$tmp/mutation-repo"
(
  cd "$tmp/mutation-repo"
  git init -q
  git config user.email test@example.invalid
  git config user.name 'ImplementAudit Test'
  printf 'ANCHOR\n' > occurrences.txt
  printf 'before\n' > anchor.txt
  printf 'one\nOLD\n' > hunk.txt
  printf 'ALREADY\nALREADY\n' > noop.txt
  printf 'BASE\n' > dirty-noop.txt
  printf 'BASE\n' > invalid-spec.txt
  git add .
  git commit -qm baseline
  if bash "$cea" --mutation-window occurrences.txt --expect 'occurrences:4:ANCHOR' \
      -- python -c 'pass' >/dev/null 2>&1; then
    fail "missing landed occurrences accepted"
  fi
  bash "$cea" --mutation-window occurrences.txt --expect 'occurrences:4:ANCHOR' -- \
    python -c 'from pathlib import Path; Path("occurrences.txt").write_text("ANCHOR\nANCHOR\nANCHOR\nANCHOR\n", encoding="utf-8")' \
    >/dev/null \
    || fail "exact landed occurrence transition rejected"
  bash "$cea" --mutation-window anchor.txt --expect 'anchor:ANCHOR' -- \
    python -c 'from pathlib import Path; Path("anchor.txt").write_text("before\nANCHOR\n", encoding="utf-8")' \
    >/dev/null || fail "landed anchor transition rejected"
  if bash "$cea" --mutation-window hunk.txt --expect 'hunk:2:MISSING' -- \
      python -c 'from pathlib import Path; Path("hunk.txt").write_text("one\nWRONG\n", encoding="utf-8")' \
      >/dev/null 2>&1; then
    fail "missing landed hunk accepted"
  fi
  printf 'one\nOLD\n' > hunk.txt
  bash "$cea" --mutation-window hunk.txt --expect 'hunk:2:NEW' -- \
    python -c 'from pathlib import Path; Path("hunk.txt").write_text("one\nNEW\n", encoding="utf-8")' \
    >/dev/null || fail "landed hunk transition rejected"
  for expectation in 'occurrences:2:ALREADY' 'anchor:ALREADY' 'hunk:1:ALREADY'; do
    if bash "$cea" --mutation-window noop.txt --expect "$expectation" -- \
        python -c 'from pathlib import Path; Path("noop.txt").write_text("COMMAND-RAN\n", encoding="utf-8")' \
        >/dev/null 2>&1; then
      fail "pre-existing no-op mutation expectation accepted: $expectation"
    fi
    [ "$(cat noop.txt)" = $'ALREADY\nALREADY' ] \
      || fail "pre-existing expectation executed mutation command: $expectation"
  done
  if bash "$cea" --mutation-window invalid-spec.txt --expect 'invalid-spec' -- \
      python -c 'from pathlib import Path; Path("invalid-spec.txt").write_text("MUTATED\n", encoding="utf-8")' \
      >/dev/null 2>&1; then
    fail "malformed mutation expectation accepted"
  fi
  grep -Fxq 'BASE' invalid-spec.txt \
    || fail "malformed mutation expectation executed mutation command"
  printf 'BASE\nALREADY\n' > dirty-noop.txt
  if bash "$cea" --mutation-window dirty-noop.txt --expect 'anchor:ALREADY' -- \
      python -c 'pass' >/dev/null 2>&1; then
    fail "pre-existing dirty expected state accepted after intended no-op"
  fi
  if bash "$cea" --mutation-window dirty-noop.txt --expect 'anchor:NEW' -- \
      python -c 'raise SystemExit(7)' >/dev/null 2>&1; then
    fail "nonzero mutation command accepted"
  fi
  if bash "$cea" --capture-mutation-before dirty-noop.txt >/dev/null 2>&1; then
    fail "retired capture receipt mode remained available"
  fi
  if bash "$cea" --mutation-landed dirty-noop.txt --before-receipt missing.json \
      --expect 'anchor:ALREADY' >/dev/null 2>&1; then
    fail "retired receipt verification mode remained available"
  fi
)

# #76 R3-F6/F7/F8: declared duplicates include the immediately adjacent
# comment block, so equal values with stale explanatory prose are still red.
dup="$repo_root/skills/implementaudit/scripts/check-duplication-parity.sh"
mkdir -p "$tmp/dup"
for n in a b c; do
  printf '# window is ceil(9.242) == 10\nWINDOW_SECONDS = 10\n' > "$tmp/dup/$n.py"
done
printf 'window: a.py::WINDOW_SECONDS, b.py::WINDOW_SECONDS, c.py::WINDOW_SECONDS\n' \
  > "$tmp/dup/manifest.txt"
(cd "$tmp/dup" && bash "$dup" manifest.txt >/dev/null) \
  || fail "matching declared duplication set rejected"
printf '# window is ceil(9.242) == 30\nWINDOW_SECONDS = 30\n' > "$tmp/dup/a.py"
if (cd "$tmp/dup" && bash "$dup" manifest.txt >/dev/null 2>&1); then
  fail "divergent duplicate value accepted"
fi
for n in a b c; do printf '# window is ceil(9.242) == 30\nWINDOW_SECONDS = 30\n' > "$tmp/dup/$n.py"; done
printf '# window is ceil(9.242) == 10\nWINDOW_SECONDS = 30\n' > "$tmp/dup/c.py"
if (cd "$tmp/dup" && bash "$dup" manifest.txt >/dev/null 2>&1); then
  fail "divergent adjacent duplicate prose accepted"
fi
printf 'escape: ../outside.py::WINDOW_SECONDS, a.py::WINDOW_SECONDS\n' \
  > "$tmp/dup/escape-manifest.txt"
if (cd "$tmp/dup" && bash "$dup" escape-manifest.txt >/dev/null 2>&1); then
  fail "duplication manifest traversal member accepted"
fi
printf 'alias: a.py::WINDOW_SECONDS, a.py:: WINDOW_SECONDS\n' \
  > "$tmp/dup/alias-manifest.txt"
if (cd "$tmp/dup" && bash "$dup" alias-manifest.txt >/dev/null 2>&1); then
  fail "same physical duplicate accepted twice through an anchor alias"
fi
printf 'separator: a.py::WINDOW_SECONDS, ./a.py::WINDOW_SECONDS\n' \
  > "$tmp/dup/separator-manifest.txt"
if (cd "$tmp/dup" && bash "$dup" separator-manifest.txt >/dev/null 2>&1); then
  fail "same physical duplicate accepted twice through a separator alias"
fi
if [ -f "$tmp/dup/A.py" ]; then
  printf 'case: a.py::WINDOW_SECONDS, A.py::WINDOW_SECONDS\n' \
    > "$tmp/dup/case-manifest.txt"
  if (cd "$tmp/dup" && bash "$dup" case-manifest.txt >/dev/null 2>&1); then
    fail "same physical duplicate accepted twice through a case alias"
  fi
fi
mkdir -p "$tmp/symlink-repo/real"
printf '# same rationale\nVALUE = 1\n' > "$tmp/symlink-repo/real/a.py"
printf '# same rationale\nVALUE = 1\n' > "$tmp/symlink-repo/b.py"
linked=0
if ln -s real "$tmp/symlink-repo/alias" 2>/dev/null \
    && [ -L "$tmp/symlink-repo/alias" ]; then
  linked=1
elif command -v cmd.exe >/dev/null 2>&1 && command -v cygpath >/dev/null 2>&1; then
  rm -rf "$tmp/symlink-repo/alias"
  if cmd.exe //c mklink //J "$(cygpath -w "$tmp/symlink-repo/alias")" \
      "$(cygpath -w "$tmp/symlink-repo/real")" >/dev/null 2>&1; then
    linked=1
  fi
fi
if [ "$linked" -eq 1 ]; then
  printf 'symlink: alias/a.py::VALUE, b.py::VALUE\n' > "$tmp/symlink-repo/manifest.txt"
  if (cd "$tmp/symlink-repo" && bash "$dup" manifest.txt >/dev/null 2>&1); then
    fail "symlink-parent duplicate member accepted"
  fi
fi

# #76 R3-F9: map the four-hop pin chain before mutation; the independent
# harness remains the authority that turns an unreplayed target edit red.
mapper="$repo_root/skills/implementaudit/scripts/map-pin-chain.sh"
mkdir -p "$tmp/pins/src" "$tmp/pins/tools" "$tmp/pins/tests"
printf 'original\n' > "$tmp/pins/src/source.txt"
source_sha="$(sha256sum "$tmp/pins/src/source.txt" | awk '{print $1}')"
printf 'source=src/source.txt sha256=%s\n' "$source_sha" > "$tmp/pins/tools/builder.py"
printf 'manifest tools/builder.py sha256\n' > "$tmp/pins/artifact.manifest"
printf 'manifest artifact.manifest byte-identical\n' > "$tmp/pins/release.manifest"
printf '%s\n' '#!/usr/bin/env bash' \
  "target=src/source'.txt'; printf '%s  %s\\n' '$source_sha' \"\$target\" | sha256sum --check -" \
  '# release.manifest --check' > "$tmp/pins/tests/check.sh"
pin_out="$(cd "$tmp/pins" && bash "$mapper" src/source.txt --expect-hops 4)" \
  || fail "four-hop pin chain was not mapped"
[ "$(printf '%s\n' "$pin_out" | grep -c '^hop:')" = 4 ] \
  || fail "pin mapper did not emit exactly four hops"
if (cd "$tmp/pins" && bash "$mapper" ../outside --expect-hops 0 >/dev/null 2>&1); then
  fail "pin mapper accepted traversal target"
fi
printf 'changed\n' > "$tmp/pins/src/source.txt"
if (cd "$tmp/pins" && bash tests/check.sh >/dev/null 2>&1); then
  fail "unreplayed pin chain harness stayed green"
fi

printf 'evidence-anchoring: ok\n'
