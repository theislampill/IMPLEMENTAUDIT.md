set -euo pipefail
umask 022
# Exact git 2.56.0 program tree (usr/bin/git and the whole usr/lib/git-core) from one digest-bound package.
# bwrap is deliberately NOT provisioned here: the core's qualified --provision-hosted-launcher owns that path.
URL='https://snapshot.ppa.launchpadcontent.net/git-core/ppa/ubuntu/20261101T000000Z/pool/main/g/git/git_2.56.0-0ppa1~ubuntu24.04.2_amd64.deb'
PKG_BYTES=7773244
PKG_SHA256=8681013502ef3b3ab4131c94e43ca89dd133934d0f5dc143cd456a7896b0ba81
GIT_BYTES=4640352
GIT_SHA256=824d5b2fffef332ec7ba053e579659bb12f26a0b4747da6f9c6dc0e71d36f235
TREE_SHA256=fa83107dc7b2465aed4fef67808b0cb70ed2c09c74148cdd78c9ba1838965db3
# One line per path: "<path> <sha256> <octal st_mode>"; sha256 of the content (regular file), of the link
# target text (symlink) or of the empty string (directory); LC_ALL=C sorted; digest = sha256 of all lines.
manifest() {
  (cd "$1" && /usr/bin/find usr/bin/git usr/lib/git-core -print0 | LC_ALL=C /usr/bin/sort -z |
    while IFS= read -r -d '' p; do
      if [ -L "$p" ]; then h="$(/usr/bin/readlink -n -- "$p" | /usr/bin/sha256sum)"
      elif [ -f "$p" ]; then h="$(/usr/bin/sha256sum < "$p")"
      elif [ -d "$p" ]; then h="$(printf '' | /usr/bin/sha256sum)"
      else printf 'UNEXPECTED_TREE_MEMBER %s\n' "$p" >&2; exit 1
      fi
      printf '%s %s %o\n' "$p" "${h%% *}" "0x$(/usr/bin/stat -c %f -- "$p")"
    done)
}
digest() { printf '%s\n' "$1" | /usr/bin/sha256sum | /usr/bin/cut -c1-64; }
#DRY_RUN_BEGIN
if [ -z "${DRY_RUN:-}" ]; then
#DRY_RUN_END
test "$(/usr/bin/id -u)" = 0
#DRY_RUN_BEGIN
fi
#DRY_RUN_END
work="$(/usr/bin/mktemp -d)"
trap '/usr/bin/rm -rf -- "$work"' EXIT
test "$(/usr/bin/stat -c '%u %a' -- "$work")" = "$(/usr/bin/id -u) 700"
pkg="$work/git.deb"
#DRY_RUN_BEGIN
if [ -n "${DRY_RUN:-}" ]; then /usr/bin/cp -- "$DRY_RUN_PACKAGE" "$pkg"; else
#DRY_RUN_END
/usr/bin/curl --proto '=https' --proto-redir '=https' --tlsv1.2 --fail --silent --show-error --location --max-redirs 5 \
  --max-filesize "$PKG_BYTES" --connect-timeout 20 --max-time 300 --retry 4 --retry-all-errors --retry-delay 3 \
  --output "$pkg" "$URL"
#DRY_RUN_BEGIN
fi
#DRY_RUN_END
test "$(/usr/bin/stat -c %s -- "$pkg")" = "$PKG_BYTES"
printf '%s  %s\n' "$PKG_SHA256" "$pkg" | /usr/bin/sha256sum --check --strict --quiet
test "$(/usr/bin/dpkg-deb --field "$pkg" Package Version Architecture)" = "$(printf 'Package: git\nVersion: 1:2.56.0-0ppa1~ubuntu24.04.2\nArchitecture: amd64')"
stage="$work/stage"
/usr/bin/mkdir -m 0755 -- "$stage"
/usr/bin/dpkg-deb --fsys-tarfile "$pkg" | /usr/bin/tar --extract --preserve-permissions --directory "$stage" ./usr/bin/git ./usr/lib/git-core
test "$(/usr/bin/stat -c %s -- "$stage/usr/bin/git")" = "$GIT_BYTES"
printf '%s  %s\n' "$GIT_SHA256" "$stage/usr/bin/git" | /usr/bin/sha256sum --check --strict --quiet
staged="$(manifest "$stage")"
printf 'staged git tree %s (%s entries)\n' "$(digest "$staged")" "$(printf '%s\n' "$staged" | /usr/bin/wc -l)"
test "$(digest "$staged")" = "$TREE_SHA256"
#DRY_RUN_BEGIN
if [ -n "${DRY_RUN:-}" ]; then printf 'DRY_RUN_STOP_BEFORE_INSTALL\n'; exit 0; fi
#DRY_RUN_END
test -z "$(/usr/bin/find "$stage/usr" \( ! -user 0 -o ! -group 0 \) -print)"
test -z "$(/usr/bin/find "$stage/usr/bin/git" "$stage/usr/lib/git-core" ! -type l -perm /6022 -print)"
printf 'image git tree before provisioning %s\n' "$(digest "$(manifest /)")"
/usr/bin/cp -a -- "$stage/usr/lib/git-core" /usr/lib/git-core.dg16-new
/usr/bin/install -o root -g root -m 0755 -- "$stage/usr/bin/git" /usr/bin/git.dg16-new
/usr/bin/mv -T -- /usr/lib/git-core "$work/image-git-core"
/usr/bin/mv -T -- /usr/lib/git-core.dg16-new /usr/lib/git-core
/usr/bin/mv -f -T -- /usr/bin/git.dg16-new /usr/bin/git
live="$(manifest /)"
test "$live" = "$staged"
test "$(digest "$live")" = "$TREE_SHA256"
test -z "$(/usr/bin/find /usr/bin/git /usr/lib/git-core \( ! -user 0 -o ! -group 0 \) -print)"
test -z "$(/usr/bin/find /usr/bin/git /usr/lib/git-core ! -type l -perm /6022 -print)"
printf '%s  %s\n' "$GIT_SHA256" /usr/bin/git | /usr/bin/sha256sum --check --strict
/usr/bin/stat -c '%a %U %G %s %h %n' /usr/bin/git /usr/lib/git-core /usr/lib/git-core/git
printf 'provisioned git tree %s\n' "$TREE_SHA256"
