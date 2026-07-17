#!/usr/bin/env bash
# payload-path-hygiene.test.sh - the layout contract must reject user-home
# absolute paths planted in the payload (Windows, macOS, Linux forms) and
# accept the clean payload.
set -euo pipefail

fail() {
  printf 'payload-path-hygiene.test: %s\n' "$*" >&2
  exit 1
}

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

copy="$work/repo"
mkdir -p "$copy"
(cd "$repo_root" && git ls-files -z | tar --null -T - -cf - ) | (cd "$copy" && tar -xf -)

bash "$copy/scripts/check-skill-layout-contract.sh" --repo-root "$copy" >/dev/null \
  || fail "clean payload unexpectedly rejected"

for planted in 'C:\Users\someone\.codex\skills\implementaudit\SKILL.md' \
               'C:\\Users\\someone\\.codex\\SKILL.md' \
               'C:/Users/someone/.codex/SKILL.md' \
               'c:\users\someone\.codex\SKILL.md' \
               '/Users/someone/skills/implementaudit/' \
               '/home/someone/skills/implementaudit/'; do
  printf 'leaked path: %s\n' "$planted" > "$copy/skills/implementaudit/references/__planted__.md"
  if bash "$copy/scripts/check-skill-layout-contract.sh" --repo-root "$copy" >/dev/null 2>&1; then
    fail "planted path was not rejected: $planted"
  fi
  rm -f "$copy/skills/implementaudit/references/__planted__.md"
done

# False-positive guard: placeholder and env-var forms must NOT be rejected.
{
  printf 'placeholder: %s\n' 'C:\Users\<name>\.codex\skills\implementaudit'
  printf 'env form: %s\n' '$CODEX_HOME/skills/implementaudit'
  printf 'winenv form: %s\n' '%USERPROFILE%\.codex\skills\implementaudit'
  printf 'url form: %s\n' 'https://api.github.com/users/someone/repos'
  printf 'tilde form: %s\n' '~/.codex/skills/implementaudit'
  printf 'env posix: %s\n' '/home/$USER/skills/'
} > "$copy/skills/implementaudit/references/__placeholders__.md"
bash "$copy/scripts/check-skill-layout-contract.sh" --repo-root "$copy" >/dev/null \
  || fail "placeholder/env-var forms were wrongly rejected"
rm -f "$copy/skills/implementaudit/references/__placeholders__.md"

# Scope guard: a personal path OUTSIDE the shipped payload must not trip the
# payload guard (it is a payload contract, not a repo-wide lint).
printf 'note: C:\\Users\\someone\\scratch\n' > "$copy/docs/__outside__.md"
bash "$copy/scripts/check-skill-layout-contract.sh" --repo-root "$copy" >/dev/null \
  || fail "out-of-payload path wrongly tripped the payload guard"
rm -f "$copy/docs/__outside__.md"

# Staged-payload guard: the BUILT release archive must also be free of
# user-home absolute paths, not only the source payload directory.
built="$work/built"
mkdir -p "$built"
(cd "$copy" && bash scripts/build-release-asset.sh "$built" >/dev/null)
python_bin="python"
command -v python >/dev/null 2>&1 || python_bin="python3"
"$python_bin" - "$built/IMPLEMENTAUDIT.skill" <<'PY' \
  || fail "built release archive contains user-home paths"
import re
import sys
import zipfile

backslash = chr(92)
sep = "[" + re.escape(backslash) + "/]+"
pattern = re.compile(
    "(?i:[A-Za-z]:" + sep + "Users" + sep + "[A-Za-z0-9_.-]+)"
    "|/(?:Users|home)/[A-Za-z0-9_.-]+/"
)
bad = []
with zipfile.ZipFile(sys.argv[1]) as zf:
    for name in zf.namelist():
        try:
            text = zf.read(name).decode("utf-8")
        except UnicodeDecodeError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            m = pattern.search(line)
            if m:
                bad.append(f"{name}:{lineno}: {m.group(0)}")
if bad:
    print("built release payload contains user-home path(s):")
    for item in bad:
        print(f"  {item}")
    raise SystemExit(1)
PY

bash "$copy/scripts/check-skill-layout-contract.sh" --repo-root "$copy" >/dev/null \
  || fail "payload rejected after removing planted files"

printf 'payload-path-hygiene.test: ok\n'
