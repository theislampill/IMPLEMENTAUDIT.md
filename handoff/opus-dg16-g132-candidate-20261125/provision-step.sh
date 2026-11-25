set -euo pipefail
test "$GITHUB_RUN_ATTEMPT" = 1
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
fetch() {
  curl --proto '=https' --tlsv1.2 --fail --silent --show-error --location --max-filesize "$3" --output "$work/$1" "$2"
  test "$(stat -c %s "$work/$1")" = "$3"
  printf '%s  %s\n' "$4" "$work/$1" | sha256sum --check --strict --quiet
}
fetch git.deb 'https://launchpad.net/~git-core/+archive/ubuntu/ppa/+files/git_2.56.0-0ppa1~ubuntu24.04.2_amd64.deb' 7773244 8681013502ef3b3ab4131c94e43ca89dd133934d0f5dc143cd456a7896b0ba81
fetch bwrap.deb 'https://snapshot.ubuntu.com/ubuntu/20260901T000000Z/pool/main/b/bubblewrap/bubblewrap_0.9.0-1ubuntu0.1_amd64.deb' 50178 1b506492bd9c7fd0cdb4f02ac822f1d3e336b0aead5113c1239baf8db5db562a
dpkg-deb --fsys-tarfile "$work/git.deb" | tar --extract --directory "$work" ./usr/bin/git
dpkg-deb --fsys-tarfile "$work/bwrap.deb" | tar --extract --directory "$work" ./usr/bin/bwrap
printf '%s  %s\n' 824d5b2fffef332ec7ba053e579659bb12f26a0b4747da6f9c6dc0e71d36f235 "$work/usr/bin/git" 52231e1caf55bcbc667b269f49c63599a6f7db4767ae6a039580d0ff853db712 "$work/usr/bin/bwrap" | sha256sum --check --strict --quiet
test "$(stat -c %s "$work/usr/bin/git")" = 4640352
test "$(stat -c %s "$work/usr/bin/bwrap")" = 72160
${DRY_RUN:+exit 0}
sudo /usr/bin/install -o root -g root -m 0755 "$work/usr/bin/git" /usr/bin/git
sudo /usr/bin/install -o root -g root -m 0755 "$work/usr/bin/bwrap" /usr/bin/bwrap
printf '%s  %s\n' 824d5b2fffef332ec7ba053e579659bb12f26a0b4747da6f9c6dc0e71d36f235 /usr/bin/git 52231e1caf55bcbc667b269f49c63599a6f7db4767ae6a039580d0ff853db712 /usr/bin/bwrap | sha256sum --check --strict
stat -c '%a %U %G %s %n' /usr/bin/git /usr/bin/bwrap
