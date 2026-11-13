#!/usr/bin/env bash
set -euo pipefail

# Receiving-side handoff inspection (#15): PROTOCOL contract text + the
# four acceptance fixtures (contradicted-blocks, matching-proceeds,
# owner-acceptance-carried, no-claims negative control). The matching
# fixture is generated against the LIVE repo so the recompute path is
# exercised for real.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

proto="skills/implementaudit/templates/PROTOCOL.md"
scorer="skills/implementaudit/scripts/check-handoff-packet.sh"
fx="fixtures/handoff-packet"
fail() { printf 'handoff-packet-contract: %s\n' "$*" >&2; exit 1; }

# Bind test packets independently of the checker. Mutations below are issued
# afresh unless the test specifically exercises an unchanged stale packet.
seal_packet() {
  python3 - "$1" <<'PY'
import hashlib
import pathlib
import sys

packet = pathlib.Path(sys.argv[1])
body = b"".join(line for line in packet.read_bytes().splitlines(keepends=True)
                if not line.lower().startswith(b"packet_content_hash:"))
packet.write_bytes(body + b"packet_content_hash: " +
                   hashlib.sha256(body).hexdigest().encode() + b"\n")
PY
}

flat="$(tr '\n' ' ' < "$proto")"
printf '%s' "$flat" | grep -qi 'Receiving-side handoff inspection' \
  || fail "PROTOCOL missing receiving-side handoff inspection section"
printf '%s' "$flat" | grep -qi 'Three claim classes' \
  || fail "three claim classes missing"
printf '%s' "$flat" | grep -qi 'PRESERVED verbatim' \
  || fail "Class-3 verbatim preservation missing"
printf '%s' "$flat" | grep -qi 'BLOCKS ONLY.*DEPENDENT EXECUTION' \
  || fail "block-only-dependent-execution rule missing"
printf '%s' "$flat" | grep -qi -- '--receiver-requires-reproduction' \
  || fail "receiver-required acceptance-state route missing"

# A. contradicted claim blocks + names abnormality + carries owner verbatim
out="$(bash "$scorer" "$fx/contradicted.pkt" --repo-root "$repo_root" 2>&1 || true)"
printf '%s' "$out" | grep -q 'CONTRADICTED' || fail "contradicted packet did not block"
printf '%s' "$out" | grep -q 'evidence-mismatch' || fail "no named abnormality"
printf '%s' "$out" | grep -qi 'Class-3 preserved verbatim' \
  || fail "owner acceptance not carried verbatim through a mismatch"
if bash "$scorer" "$fx/contradicted.pkt" --repo-root "$repo_root" >/dev/null 2>&1; then
  fail "contradicted packet must exit nonzero (block)"
fi

# D. no state claims -> nothing to verify, proceed
bash "$scorer" "$fx/no-claims.pkt" --repo-root "$repo_root" >/dev/null 2>&1 \
  || fail "no-claims packet must proceed"

# B. matching claims -> proceed. Generate a packet from LIVE state.
tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
live_repo="$(basename "$(git -C "$repo_root" rev-parse --show-toplevel)")"
live_branch="$(git -C "$repo_root" rev-parse --abbrev-ref HEAD)"
live_tree="$(git -C "$repo_root" rev-parse HEAD)"
if [ -z "$(git -C "$repo_root" status --porcelain)" ]; then live_clean=yes; else live_clean=no; fi
cat > "$tmp/match.pkt" <<EOF
packet_id: pkt-live
packet_version: 1
packet_content_hash: livehash
sender_run_id: run-sender-B
subject_repo: $live_repo
claimed_branch: $live_branch
claimed_tree: $live_tree
claimed_clean: $live_clean
has_state_claims: yes
owner_acceptance: none
EOF
bash "$scorer" "$tmp/match.pkt" --repo-root "$repo_root" >/dev/null 2>&1 \
  || fail "matching packet must proceed against live state"

# E. ADVERSARIAL (post-merge robustness): a packet with only the required
# identity fields + a contradicted subject_repo, and NO optional fields
# (owner_acceptance, branch, tree, clean) must STILL reach the Class-1
# contradiction logic and NAME the abnormality — not die early on an
# absent-field lookup under `set -euo pipefail`.
cat > "$tmp/min-contradicted.pkt" <<EOF
packet_id: pmin
packet_version: 1
packet_content_hash: h
sender_run_id: r
subject_repo: DEFINITELY-NOT-THIS-REPO
has_state_claims: yes
EOF
out="$(bash "$scorer" "$tmp/min-contradicted.pkt" --repo-root "$repo_root" 2>&1 || true)"
printf '%s' "$out" | grep -q 'CONTRADICTED' \
  || fail "minimal contradicted packet did not reach the contradiction logic (early-death regression)"
printf '%s' "$out" | grep -q 'evidence-mismatch' \
  || fail "minimal contradicted packet did not name the abnormality"

# --- Fable review of PR #30: adversarial regressions -----------------------
# F. A claimed_tree PREFIX (even a long one) is never confirmed identity.
cat > "$tmp/prefix.pkt" <<EOF
packet_id: pfx
packet_version: 1
packet_content_hash: h
sender_run_id: r
claimed_tree: ${live_tree:0:7}
has_state_claims: yes
EOF
if bash "$scorer" "$tmp/prefix.pkt" --repo-root "$repo_root" >/dev/null 2>&1; then
  fail "short-prefix claimed_tree was confirmed as tree identity"
fi

# G. Duplicate conflicting keys are a malformed packet, not first-wins.
cat > "$tmp/dup.pkt" <<EOF
packet_id: pdup
packet_version: 1
packet_content_hash: h
sender_run_id: r
claimed_branch: $live_branch
claimed_branch: totally-other-branch
has_state_claims: yes
EOF
out="$(bash "$scorer" "$tmp/dup.pkt" --repo-root "$repo_root" 2>&1 || true)"
printf '%s' "$out" | grep -qi 'malformed packet' \
  || fail "duplicate conflicting keys were not rejected as malformed"

# H. sha256 content hash binds the packet: a correct hash passes; a
# packet altered after issue (tampered Class-3 text) fails the binding.
if command -v sha256sum >/dev/null 2>&1; then
  cat > "$tmp/bound.body" <<EOF
packet_id: pbind
packet_version: 1
sender_run_id: r
owner_acceptance: owner accepted residual risk R1 (verbatim)
has_state_claims: no
EOF
  bh="$(sha256sum "$tmp/bound.body" | cut -d' ' -f1)"
  { head -n1 "$tmp/bound.body"; printf 'packet_content_hash: %s\n' "$bh"; \
    tail -n +2 "$tmp/bound.body"; } > "$tmp/bound.pkt"
  bash "$scorer" "$tmp/bound.pkt" --repo-root "$repo_root" >/dev/null 2>&1 \
    || fail "correctly sha256-bound packet must pass"
  sed 's/residual risk R1/residual risk R1 AND R2/' "$tmp/bound.pkt" \
    > "$tmp/tampered.pkt"
  if bash "$scorer" "$tmp/tampered.pkt" --repo-root "$repo_root" >/dev/null 2>&1; then
    fail "tampered Class-3 text passed a sha256-bound packet"
  fi
fi

# I. Control: an opaque (non-sha256) hash token is still tolerated, with
# the unverifiability said out loud.
out="$(bash "$scorer" "$fx/no-claims.pkt" --repo-root "$repo_root" 2>&1)" \
  || fail "opaque-hash legacy packet must still proceed"
printf '%s' "$out" | grep -qi 'not verifiable' \
  || fail "opaque hash must be reported as not verifiable, not silently trusted"

# J. A terminal READY fold-in that requires independent receiver
# re-adjudication is receiver-incomplete without its acceptance-state bundle.
cat > "$tmp/receiver-incomplete.pkt" <<EOF
packet_id: preceiver
packet_version: 1
packet_content_hash: opaque-receiver-test
sender_run_id: sender-receiver-test
handoff_state: READY
implementation_identity_present: yes
frozen_denominator_present: no
acceptance_oracle_present: no
reproduction_inputs_present: no
evaluator_schema_semantics_present: no
prior_evidence_present: yes
rejected_non_evidence_present: no
authority_stop_boundaries_present: yes
exact_handoff_receipt_present: yes
current_state_ref: git:HEAD
provenance_ref: packet:preceiver
pending_effects_disposition: unresolved-listed-above
authority_capability_ref: owner:R001F
discrepancy_state: acceptance-state-incomplete
receiver_live_verification: command:git-rev-parse-HEAD
has_state_claims: no
EOF
if bash "$scorer" "$tmp/receiver-incomplete.pkt" --repo-root "$repo_root" \
    --receiver-requires-reproduction \
    >/dev/null 2>&1; then
  fail "receiver-incomplete READY handoff was accepted"
fi

# K. The complete reproduction bundle passes when the receiver requires it.
cat > "$tmp/receiver-complete.pkt" <<EOF
packet_id: preceiver-complete
packet_version: 1
packet_content_hash: opaque-receiver-complete-test
sender_run_id: sender-receiver-complete-test
handoff_state: READY
implementation_identity_present: yes
frozen_denominator_present: yes
acceptance_oracle_present: yes
reproduction_inputs_present: yes
evaluator_schema_semantics_present: yes
prior_evidence_present: yes
rejected_non_evidence_present: yes
authority_stop_boundaries_present: yes
exact_handoff_receipt_present: yes
current_state_ref: git:HEAD
provenance_ref: packet:preceiver-complete
pending_effects_disposition: none-observed
authority_capability_ref: owner:R001F
discrepancy_state: none-observed
receiver_live_verification: command:git-rev-parse-HEAD
claimed_tree: $live_tree
has_state_claims: no
EOF
seal_packet "$tmp/receiver-complete.pkt"
out="$(bash "$scorer" "$tmp/receiver-complete.pkt" --repo-root "$repo_root" \
  --receiver-requires-reproduction 2>&1)" \
  || fail "complete receiver-required acceptance bundle was rejected"
printf '%s' "$out" | grep -q 'RECEIVER_ACCEPTANCE_STATE=COMPLETE' \
  || fail "complete receiver-required bundle lacked terminal evidence"

# L. Cheap path: a READY implementation-only handoff needs no synthetic
# denominator/oracle bundle when the receiver does not require reproduction.
cat > "$tmp/receiver-cheap-path.pkt" <<EOF
packet_id: preceiver-cheap
packet_version: 1
packet_content_hash: opaque-receiver-cheap-test
sender_run_id: sender-receiver-cheap-test
handoff_state: READY
implementation_identity_present: yes
has_state_claims: no
EOF
bash "$scorer" "$tmp/receiver-cheap-path.pkt" --repo-root "$repo_root" \
  >/dev/null 2>&1 || fail "implementation-only READY cheap path was rejected"

# M. A reproduction-required continuation also needs the current decision state
# it will act from.  An acceptance bundle without current state, provenance,
# pending-effect disposition, authority/capability, discrepancy state, and the
# receiver's live-verification obligation is receiver-incomplete.
cat > "$tmp/receiver-stale-state.pkt" <<EOF
packet_id: preceiver-stale-state
packet_version: 1
packet_content_hash: opaque-receiver-stale-state-test
sender_run_id: sender-receiver-stale-state-test
handoff_state: READY
implementation_identity_present: yes
frozen_denominator_present: yes
acceptance_oracle_present: yes
reproduction_inputs_present: yes
evaluator_schema_semantics_present: yes
prior_evidence_present: yes
rejected_non_evidence_present: yes
authority_stop_boundaries_present: yes
exact_handoff_receipt_present: yes
has_state_claims: no
EOF
if bash "$scorer" "$tmp/receiver-stale-state.pkt" --repo-root "$repo_root" \
    --receiver-requires-reproduction >/dev/null 2>&1; then
  fail "S3E-W01 RED: receiver-current decision state was not required"
fi

# N. Presence-shaped values are not state evidence.
cat >> "$tmp/receiver-stale-state.pkt" <<EOF
current_state_present: yes
provenance_present: yes
pending_effects_disposition_present: yes
authority_capability_present: yes
discrepancy_state_present: yes
receiver_live_verification_present: yes
EOF
if bash "$scorer" "$tmp/receiver-stale-state.pkt" --repo-root "$repo_root" \
    --receiver-requires-reproduction >/dev/null 2>&1; then
  fail "S3E-W01 RED: presence markers false-greened without concrete state values"
fi

# O. Horizontal whitespace cannot turn presence tokens into concrete values.
for variant in trailing-space trailing-spaces trailing-tab leading-tab space-before-cr; do
  grep -vE '^(current_state_ref|provenance_ref|pending_effects_disposition|authority_capability_ref|discrepancy_state|receiver_live_verification):' \
    "$tmp/receiver-complete.pkt" > "$tmp/receiver-placeholder-$variant.pkt"
  prefix="" suffix="" cr=""
  case "$variant" in
    trailing-space) suffix=" " ;;
    trailing-spaces) suffix="   " ;;
    trailing-tab) suffix=$'\t' ;;
    leading-tab) prefix=$'\t' ;;
    space-before-cr) suffix=" "; cr=$'\r' ;;
  esac
  printf 'current_state_ref: %syes%s%s\nprovenance_ref: %spresent%s%s\npending_effects_disposition: %sunknown%s%s\nauthority_capability_ref: %strue%s%s\ndiscrepancy_state: %sno%s%s\nreceiver_live_verification: %sfalse%s%s\n' \
    "$prefix" "$suffix" "$cr" "$prefix" "$suffix" "$cr" \
    "$prefix" "$suffix" "$cr" "$prefix" "$suffix" "$cr" \
    "$prefix" "$suffix" "$cr" "$prefix" "$suffix" "$cr" \
    >> "$tmp/receiver-placeholder-$variant.pkt"
  seal_packet "$tmp/receiver-placeholder-$variant.pkt"
  if bash "$scorer" "$tmp/receiver-placeholder-$variant.pkt" --repo-root "$repo_root" \
      --receiver-requires-reproduction >/dev/null 2>&1; then
    fail "S3E-W01 RED: $variant presence placeholders false-greened"
  fi
done

# P. Real receiver state must resolve. Deleting only the target while retaining
# the exact packet must block; a nonempty string is not reproduction evidence.
python3 "$repo_root/tests/handoff_file_reference.py"
state_dir="$(mktemp -d "$repo_root/fixtures/handoff-packet/receiver-state.XXXXXX")"
trap 'rm -rf "$tmp" "$state_dir"' EXIT
reference_failures=0
set_receiver_field() {
  python3 - "$tmp/receiver-complete.pkt" "$tmp/receiver-case.pkt" "$1" "$2" <<'PY'
import pathlib
import sys

source, target, key, value = sys.argv[1:]
lines = pathlib.Path(source).read_text().splitlines()
pathlib.Path(target).write_text("\n".join(
    key + ": " + value if line.startswith(key + ":") else line
    for line in lines) + "\n")
PY
  seal_packet "$tmp/receiver-case.pkt"
}
expect_receiver_reject() {
  local name="$1" packet="$2" receiver_root="${3:-$repo_root}" out rc
  if out="$(bash "$scorer" "$packet" --repo-root "$receiver_root" \
      --receiver-requires-reproduction 2>&1)"; then
    printf 'R002D receiver-reference RED: %s was accepted\n%s\n' "$name" "$out" >&2
    reference_failures=$((reference_failures + 1))
  else
    rc=$?
    if [ "$rc" -ne 1 ] || ! printf '%s' "$out" | grep -qE 'RECEIVER_INCOMPLETE|CONTRADICTED'; then
      fail "$name failed unexpectedly: $out"
    fi
    if printf '%s' "$out" | grep -q 'RECEIVER_ACCEPTANCE_STATE=COMPLETE'; then
      printf 'R002D receiver-reference RED: %s printed COMPLETE before refusing\n' "$name" >&2
      reference_failures=$((reference_failures + 1))
    fi
  fi
}
printf 'receiver state version 1\n' > "$state_dir/state.txt"
state_path="${state_dir#"$repo_root"/}/state.txt"
state_hash="$(python3 -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest())' "$state_dir/state.txt")"
sed "s|^current_state_ref:.*|current_state_ref: file:$state_path#sha256=$state_hash|" \
  "$tmp/receiver-complete.pkt" > "$tmp/receiver-file.pkt"
seal_packet "$tmp/receiver-file.pkt"
bash "$scorer" "$tmp/receiver-file.pkt" --repo-root "$repo_root" \
  --receiver-requires-reproduction >/dev/null 2>&1 \
  || fail "current digest-bound receiver file was rejected"
rm "$state_dir/state.txt"
expect_receiver_reject 'missing current-state file' "$tmp/receiver-file.pkt"

# Q. Same-path changed bytes invalidate the unchanged packet. A newly issued
# digest-bound packet re-establishes identity without interpreting state JSON.
printf 'receiver state version 2\n' > "$state_dir/state.txt"
expect_receiver_reject 'changed current-state bytes' "$tmp/receiver-file.pkt"
state_hash="$(python3 -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest())' "$state_dir/state.txt")"
set_receiver_field current_state_ref "file:$state_path#sha256=$state_hash"
bash "$scorer" "$tmp/receiver-case.pkt" --repo-root "$repo_root" \
  --receiver-requires-reproduction >/dev/null 2>&1 \
  || fail "reissued current-state file identity was rejected"
cp "$tmp/receiver-case.pkt" "$tmp/receiver-rebound.pkt"

# An unavailable secure-open primitive is a normal refusal, not a traceback
# or a fallback to following paths. Simulate the platform boundary in the real
# Python resolver; the exact Git route must remain usable under the same host.
# These faults target POSIX descriptor APIs. Native NTFS uses retained handles;
# its actual source, alias and replacement controls run in the family above.
if [ "$(python3 -c 'import os; print(os.name)')" != nt ]; then
mkdir "$tmp/unsupported-host"
python3 - "$tmp/unsupported-host/python3" <<'PY'
import pathlib
import sys

shim = pathlib.Path(sys.argv[1])
shim.write_text("#!" + sys.executable + "\n" + '''
import os
import sys
source = sys.stdin.read()
sys.argv = [argument for argument in sys.argv[1:] if argument != "-I"]
if os.environ.get("HANDOFF_TEST_OPEN_UNAVAILABLE") == "flag":
    del os.O_NOFOLLOW
else:
    def unavailable(*args, **kwargs):
        raise NotImplementedError("host does not implement secure dir_fd open")
    os.open = unavailable
    os.supports_dir_fd.add(unavailable)
exec(compile(source, "<handoff-reference-resolver>", "exec"))
''')
shim.chmod(0o755)
PY
for unavailable in flag operation; do
  if out="$(PATH="$tmp/unsupported-host:$PATH" HANDOFF_TEST_OPEN_UNAVAILABLE="$unavailable" \
      bash "$scorer" "$tmp/receiver-rebound.pkt" --repo-root "$repo_root" \
      --receiver-requires-reproduction 2>&1)"; then
    fail "unavailable secure-open $unavailable was accepted"
  fi
  printf '%s' "$out" | grep -q 'RECEIVER_INCOMPLETE' \
    || fail "unavailable secure-open $unavailable lacked a receiver refusal: $out"
  if printf '%s' "$out" | grep -q 'Traceback'; then
    fail "unavailable secure-open $unavailable escaped as a traceback: $out"
  fi
  PATH="$tmp/unsupported-host:$PATH" HANDOFF_TEST_OPEN_UNAVAILABLE="$unavailable" \
    bash "$scorer" "$tmp/receiver-complete.pkt" --repo-root "$repo_root" \
    --receiver-requires-reproduction >/dev/null 2>&1 \
    || fail "unavailable secure-open $unavailable disabled exact Git references"
done

# A captured state descriptor must still be the file named by the receiver's
# live root/parent entries. Swap immediately after the real open returns, before
# either fstat/hash; a stale descriptor alone must not complete the handoff.
mkdir "$tmp/state-swap-tools"
python3 - "$tmp/state-swap-tools/python3" <<'PY'
import pathlib
import sys

shim = pathlib.Path(sys.argv[1])
shim.write_text("#!" + sys.executable + "\n" + '''
import os
import pathlib
import sys
source = sys.stdin.read()
sys.argv = [argument for argument in sys.argv[1:] if argument != "-I"]
real_open = os.open
swapped = False
def opening(path, *args, **kwargs):
    global swapped
    fd = real_open(path, *args, **kwargs)
    if path == "state.txt" and not swapped:
        swapped = True
        target = pathlib.Path(os.environ["HANDOFF_STATE_SWAP_TARGET"])
        mode = os.environ["HANDOFF_STATE_SWAP_MODE"]
        target.rename(str(target) + ".captured")
        if mode == "file":
            target.write_bytes(b"changed state after open\\n")
        else:
            target.mkdir()
            (target / "state.txt").write_bytes(b"changed state after open\\n")
            if mode == "root":
                (target / ".git").write_bytes((pathlib.Path(str(target) + ".captured") / ".git").read_bytes())
        pathlib.Path(os.environ["HANDOFF_STATE_SWAP_RECEIPT"]).write_text("swapped")
    return fd
os.open = opening
os.supports_dir_fd.add(opening)
exec(compile(source, "<handoff-state-resolver>", "exec"))
''')
shim.chmod(0o755)
PY
trap 'rm -rf "$tmp" "$state_dir" "$state_dir.captured"' EXIT
for mode in parent file; do
  target="$state_dir"
  [ "$mode" != file ] || target="$state_dir/state.txt"
  PATH="$tmp/state-swap-tools:$PATH" HANDOFF_STATE_SWAP_MODE="$mode" \
    HANDOFF_STATE_SWAP_TARGET="$target" HANDOFF_STATE_SWAP_RECEIPT="$tmp/state-$mode.receipt" \
    expect_receiver_reject "replaced state $mode after open" "$tmp/receiver-rebound.pkt"
  [ -f "$tmp/state-$mode.receipt" ] || fail "state $mode replacement did not reach the open boundary"
  rm -rf "$target"
  mv "$target.captured" "$target"
done
mkdir "$tmp/receiver-root"
printf 'gitdir: %s\n' "$(git rev-parse --absolute-git-dir)" > "$tmp/receiver-root/.git"
cp "$state_dir/state.txt" "$tmp/receiver-root/state.txt"
set_receiver_field current_state_ref "file:state.txt#sha256=$state_hash"
PATH="$tmp/state-swap-tools:$PATH" HANDOFF_STATE_SWAP_MODE=root \
  HANDOFF_STATE_SWAP_TARGET="$tmp/receiver-root" HANDOFF_STATE_SWAP_RECEIPT="$tmp/state-root.receipt" \
  expect_receiver_reject 'replaced receiver root after open' "$tmp/receiver-case.pkt" "$tmp/receiver-root"
[ -f "$tmp/state-root.receipt" ] || fail "root replacement did not reach the open boundary"

# R. Resolution stays inside the receiver root and never follows aliases or
# opens non-regular evidence. Every negative uses an otherwise valid packet.
mv "$state_dir/state.txt" "$tmp/state.txt"
ln -s "$tmp/state.txt" "$state_dir/state.txt"
expect_receiver_reject 'symlink current-state file' "$tmp/receiver-rebound.pkt"
rm "$state_dir/state.txt"
mv "$tmp/state.txt" "$state_dir/state.txt"
ln -s "$state_dir" "$state_dir/alias"
set_receiver_field current_state_ref "file:${state_path%/*}/alias/state.txt#sha256=$state_hash"
expect_receiver_reject 'symlink current-state directory' "$tmp/receiver-case.pkt"
set_receiver_field current_state_ref "file:${state_path%/*}/../$(basename "$state_dir")/state.txt#sha256=$state_hash"
expect_receiver_reject 'parent traversal current-state path' "$tmp/receiver-case.pkt"
set_receiver_field current_state_ref "file:$state_dir/state.txt#sha256=$state_hash"
expect_receiver_reject 'absolute current-state path' "$tmp/receiver-case.pkt"
set_receiver_field current_state_ref "file:${state_path%/*}#sha256=$state_hash"
expect_receiver_reject 'directory instead of state file' "$tmp/receiver-case.pkt"
else
  printf 'handoff-packet-contract: POSIX descriptor faults not applicable to native NTFS; native handle controls executed\n'
fi
set_receiver_field current_state_ref "file:$state_path#sha256=${state_hash:0:12}"
expect_receiver_reject 'short current-state digest' "$tmp/receiver-case.pkt"
set_receiver_field current_state_ref "file:$state_path"
expect_receiver_reject 'unbound current-state file' "$tmp/receiver-case.pkt"

# S. HEAD aliases need the existing immutable commit binding even when the
# sender says no Class-1 claims. Exact commit references work; names/prefixes do
# not. A contradictory Class-1 fact must never have an earlier COMPLETE marker.
set_receiver_field current_state_ref "git:${live_tree^^}"
bash "$scorer" "$tmp/receiver-case.pkt" --repo-root "$repo_root" \
  --receiver-requires-reproduction >/dev/null 2>&1 \
  || fail "exact case-insensitive Git identity was rejected"
set_receiver_field current_state_ref "git:${live_tree:0:12}"
expect_receiver_reject 'short Git current-state identity' "$tmp/receiver-case.pkt"
set_receiver_field current_state_ref 'git:0000000000000000000000000000000000000000'
expect_receiver_reject 'foreign Git current-state identity' "$tmp/receiver-case.pkt"
set_receiver_field current_state_ref 'git:main'
expect_receiver_reject 'ambiguous Git current-state alias' "$tmp/receiver-case.pkt"
set_receiver_field claimed_tree '0000000000000000000000000000000000000000'
expect_receiver_reject 'stale claimed commit with no-state-claims bypass' "$tmp/receiver-case.pkt"
grep -v '^claimed_tree:' "$tmp/receiver-complete.pkt" > "$tmp/receiver-case.pkt"
seal_packet "$tmp/receiver-case.pkt"
expect_receiver_reject 'unbound HEAD alias' "$tmp/receiver-case.pkt"
set_receiver_field packet_content_hash opaque-reproduction-binding
# This case deliberately retains the opaque token rather than sealing it.
sed 's/^packet_content_hash:.*/packet_content_hash: opaque-reproduction-binding/' \
  "$tmp/receiver-case.pkt" > "$tmp/receiver-opaque.pkt"
expect_receiver_reject 'opaque reproduction packet hash' "$tmp/receiver-opaque.pkt"
set_receiver_field provenance_ref packet:foreign-packet
expect_receiver_reject 'foreign packet provenance identity' "$tmp/receiver-case.pkt"
sed 's/^has_state_claims: no/has_state_claims: yes/' "$tmp/receiver-complete.pkt" \
  > "$tmp/receiver-case.pkt"
printf 'claimed_branch: definitely-not-this-branch\n' >> "$tmp/receiver-case.pkt"
seal_packet "$tmp/receiver-case.pkt"
expect_receiver_reject 'contradicted Class-1 branch' "$tmp/receiver-case.pkt"

# T. Packet commands are data: neither a reference-shaped command nor the
# receiver's live-verification instruction may run. Cheap handoffs keep their
# existing opaque/reference-free path and do not acquire this resolver.
set_receiver_field current_state_ref "command:touch $tmp/reference-command-ran"
expect_receiver_reject 'executable current-state reference' "$tmp/receiver-case.pkt"
[ ! -e "$tmp/reference-command-ran" ] || fail "current_state_ref executed a command"
set_receiver_field receiver_live_verification "command:touch $tmp/verification-command-ran"
bash "$scorer" "$tmp/receiver-case.pkt" --repo-root "$repo_root" \
  --receiver-requires-reproduction >/dev/null 2>&1 \
  || fail "opaque receiver verification obligation was executed or rejected"
[ ! -e "$tmp/verification-command-ran" ] || fail "receiver verification text executed a command"
rm "$state_dir/state.txt"
bash "$scorer" "$tmp/receiver-rebound.pkt" --repo-root "$repo_root" \
  >/dev/null 2>&1 || fail "ordinary handoff acquired reproduction-only resolution"
[ "$reference_failures" -eq 0 ] || fail "$reference_failures receiving-reference controls failed"

# U. Packet hash and subsequent fields must come from one captured byte
# sequence. This copied hash utility consumes the real hash input, then swaps
# only the disposable packet before returning; production source is unchanged.
if command -v sha256sum >/dev/null 2>&1; then
  mkdir "$tmp/packet-swap-tools"
  cp "$(command -v sha256sum)" "$tmp/packet-swap-tools/real-sha256sum"
  cat > "$tmp/packet-swap-tools/sha256sum" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
"$HANDOFF_REAL_HASHER" "$@"
mv "$HANDOFF_PACKET_SUCCESSOR" "$HANDOFF_PACKET_TARGET"
printf 'swapped\n' > "$HANDOFF_SWAP_RECEIPT"
SH
  chmod +x "$tmp/packet-swap-tools/sha256sum"
  set_receiver_field claimed_tree '0000000000000000000000000000000000000000'
  printf 'owner_acceptance: ORIGINAL-HASHED-OWNER-TEXT\n' >> "$tmp/receiver-case.pkt"
  seal_packet "$tmp/receiver-case.pkt"
  cp "$tmp/receiver-case.pkt" "$tmp/packet-race.pkt"
  sed -e "s/^claimed_tree:.*/claimed_tree: $live_tree/" \
    -e 's/ORIGINAL-HASHED-OWNER-TEXT/CHANGED-UNHASHED-OWNER-TEXT/' \
    "$tmp/receiver-case.pkt" > "$tmp/packet-successor.pkt"
  rc=0
  out="$(PATH="$tmp/packet-swap-tools:$PATH" \
    HANDOFF_REAL_HASHER="$tmp/packet-swap-tools/real-sha256sum" \
    HANDOFF_PACKET_TARGET="$tmp/packet-race.pkt" \
    HANDOFF_PACKET_SUCCESSOR="$tmp/packet-successor.pkt" \
    HANDOFF_SWAP_RECEIPT="$tmp/packet-swap.receipt" \
    bash "$scorer" "$tmp/packet-race.pkt" --repo-root "$repo_root" \
    --receiver-requires-reproduction 2>&1)" || rc=$?
  [ -f "$tmp/packet-swap.receipt" ] || fail "packet swap did not reach the real hash boundary"
  [ "$rc" -eq 1 ] || fail "packet custody RED: unhashed replacement was accepted: $out"
  printf '%s' "$out" | grep -q 'ORIGINAL-HASHED-OWNER-TEXT' \
    || fail "packet custody did not retain the captured owner text"
  if printf '%s' "$out" | grep -qE 'CHANGED-UNHASHED-OWNER-TEXT|RECEIVER_ACCEPTANCE_STATE=COMPLETE'; then
    fail "packet custody consumed or completed replacement fields: $out"
  fi
fi

# V. Capturing a text packet must preserve its exact hash input, including an
# unterminated final line and CRLF. NUL/empty/oversized inputs refuse explicitly.
python3 - "$tmp" <<'PY'
import hashlib
import pathlib
import sys

root = pathlib.Path(sys.argv[1])
body = b"packet_id: byte-control\npacket_version: 1\nsender_run_id: bytes\nhas_state_claims: no\nowner_acceptance: literal $() `text`\n"
for name, payload, ending in (
    ("lf", body, b"\n"),
    ("crlf", body.replace(b"\n", b"\r\n"), b"\r\n"),
    ("no-final-lf", body[:-1], b"\n"),
    ("trailing-blank-lines", body + b"\n\n", b"\n"),
):
    header = b"packet_content_hash: " + hashlib.sha256(payload).hexdigest().encode() + ending
    (root / ("bytes-" + name + ".pkt")).write_bytes(header + payload)
opaque = body + b"packet_content_hash: opaque\n"
(root / "bytes-empty.pkt").write_bytes(b"")
(root / "bytes-nul.pkt").write_bytes(opaque + b"\0")
(root / "bytes-oversized.pkt").write_bytes(opaque + b"#" + b"x" * (1024 * 1024))
PY
for form in lf crlf no-final-lf trailing-blank-lines; do
  bash "$scorer" "$tmp/bytes-$form.pkt" --repo-root "$repo_root" >/dev/null 2>&1 \
    || fail "exact captured $form bytes failed their SHA-256 binding"
done
for form in empty nul oversized; do
  if bash "$scorer" "$tmp/bytes-$form.pkt" --repo-root "$repo_root" >/dev/null 2>&1; then
    fail "$form packet was accepted after byte capture"
  fi
done

# P. A sender denial cannot suppress any populated Class-1 claim. Removing
# any recognized field from the no-claims guard must fail its actual comparison.
# Receiver-reference fixtures above change the worktree after match.pkt was
# issued. Bind these new packets to a fresh observation, preserving that earlier
# packet and its already-tested source state.
denial_status="$(git -C "$repo_root" status --porcelain)" \
  || fail 'claim-flag fixture could not observe current cleanliness'
if [ -z "$denial_status" ]; then denial_clean=yes; else denial_clean=no; fi
for claim in subject_repo claimed_branch claimed_tree claimed_clean; do
  case "$claim" in
    subject_repo) false_value=R37-DEFINITELY-NOT-THIS-REPO ;;
    claimed_branch) false_value="$live_branch-r37-other" ;;
    claimed_tree) false_value=0000000000000000000000000000000000000000 ;;
    claimed_clean)
      if [ "$denial_clean" = yes ]; then false_value=no; else false_value=yes; fi
      ;;
  esac
  cat > "$tmp/denied-$claim.pkt" <<EOF
packet_id: r37-denied-$claim
packet_version: 1
packet_content_hash: r37-claim-flag-regression
sender_run_id: r37-constructed-regression
$claim: $false_value
has_state_claims: no
owner_acceptance: retained R0037 test judgment
EOF
  code=0
  out="$(bash "$scorer" "$tmp/denied-$claim.pkt" --repo-root "$repo_root" 2>&1)" || code=$?
  [ "$code" -eq 1 ] || fail "denied $claim escaped its actual comparison (exit $code)"
  printf '%s' "$out" | grep -q 'CONTRADICTED' \
    || fail "denied $claim did not retain the Class-1 contradiction"
  printf '%s' "$out" | grep -q 'evidence-mismatch' \
    || fail "denied $claim did not name the existing abnormality"
  printf '%s' "$out" | grep -Fq 'Class-3 preserved verbatim: retained R0037 test judgment' \
    || fail "denied $claim dropped the owner's verbatim judgment"
done

# A denial also cannot manufacture a contradiction: true populated claims
# still take the existing comparison path and pass. D/I/L retain no-claims use.
sed -e 's/^has_state_claims: yes$/has_state_claims: no/' \
  -e "s/^claimed_clean:.*/claimed_clean: $denial_clean/" "$tmp/match.pkt" \
  > "$tmp/denied-matching.pkt"
seal_packet "$tmp/denied-matching.pkt"
out="$(bash "$scorer" "$tmp/denied-matching.pkt" --repo-root "$repo_root" 2>&1)" \
  || fail "matching populated claims were rejected because of the sender denial"
printf '%s' "$out" | grep -q 'verified.*Class-1 claims confirmed' \
  || fail "matching populated claims bypassed receiver verification"
printf 'handoff-packet-contract: claim-flag controls ok (four contradictory fields + matching claims)\n'

# Q. R0037: failed Git observation is unavailable evidence, never a value
# confirming a populated claim. Real Git failures are used; no wrapper is mocked.
observation_repo="$tmp/observation-repo"
git -c init.defaultBranch=r0037-observation init -q --template= "$observation_repo"
printf 'R0037 observation seed\n' > "$observation_repo/seed.txt"
git -C "$observation_repo" add seed.txt
git -C "$observation_repo" -c user.name=handoff-observation-test \
  -c user.email=handoff-observation@example.invalid -c commit.gpgSign=false \
  commit -qm 'R0037 observation fixture'

observation_packet() {
  local name="$1" field="$2" value="$3" flag="$4"
  cat > "$tmp/observation-$name.pkt" <<EOF
packet_id: r0037-observation-$name
packet_version: 1
packet_content_hash: r0037-observation-contract
sender_run_id: r0037-observation-regression
has_state_claims: $flag
owner_acceptance: retained R0037 observation test judgment
EOF
  if [ -n "$field" ]; then printf '%s: %s\n' "$field" "$value" >> "$tmp/observation-$name.pkt"; fi
  seal_packet "$tmp/observation-$name.pkt"
}

observation_case() {
  local name="$1" kind="$2" root="$3" field="$4" code=0
  bash "$scorer" "$tmp/observation-$name.pkt" --repo-root "$root" \
    > "$tmp/observation-$name-$kind.stdout" 2> "$tmp/observation-$name-$kind.stderr" || code=$?
  grep -Fq 'Class-3 preserved verbatim: retained R0037 observation test judgment' \
    "$tmp/observation-$name-$kind.stdout" || fail "$name lost the Class-3 judgment"
  case "$kind" in
    verified)
      [ "$code" -eq 0 ] || fail "$name rejected a successful real observation"
      grep -q 'verified.*Class-1 claims confirmed' "$tmp/observation-$name-$kind.stdout" \
        || fail "$name did not confirm its successful observation"
      ;;
    empty)
      [ "$code" -eq 0 ] || fail "$name rejected the genuine empty-claim path"
      grep -q 'nothing mechanical to verify' "$tmp/observation-$name-$kind.stdout" \
        || fail "$name did not preserve the empty-claim path"
      ;;
    unverifiable)
      [ "$code" -eq 1 ] || fail "$name accepted a failed observation (exit $code)"
      grep -Fq "UNVERIFIABLE Class-1 claim: $field" "$tmp/observation-$name-$kind.stderr" \
        || fail "$name did not identify the unavailable claim"
      grep -q 'evidence-mismatch.*dependent execution BLOCKS' "$tmp/observation-$name-$kind.stderr" \
        || fail "$name did not retain the named blocking boundary"
      if grep -q 'verified.*Class-1 claims confirmed' "$tmp/observation-$name-$kind.stdout"; then
        fail "$name falsely confirmed a failed observation"
      fi
      ;;
    *) fail "unknown observation test kind: $kind" ;;
  esac
}

# Establish a valid clean fixture before replacing only its index.
git -C "$observation_repo" status --porcelain > "$tmp/observation-valid.status" \
  2> "$tmp/observation-valid.stderr" || fail 'ordinary observation fixture status failed'
[ ! -s "$tmp/observation-valid.status" ] || fail 'ordinary observation fixture is dirty'
observation_packet clean claimed_clean yes yes
observation_case clean verified "$observation_repo" claimed_clean
cp "$observation_repo/.git/index" "$tmp/observation-original-index"
printf 'R0037-BAD-INDEX\n' > "$observation_repo/.git/index"
status_code=0
git -C "$observation_repo" status --porcelain > "$tmp/observation-failed.status" \
  2> "$tmp/observation-failed.stderr" || status_code=$?
[ "$status_code" -ne 0 ] && [ ! -s "$tmp/observation-failed.status" ] \
  && [ -s "$tmp/observation-failed.stderr" ] || fail 'real empty-output status failure was not established'
observation_case clean unverifiable "$observation_repo" claimed_clean
observation_packet empty '' '' no
observation_case empty empty "$observation_repo" ''

# A missing owned fixture path makes actual Git acquisition fail, without
# depending on ancestor discovery, an artificial sentinel, or a fake Git tool.
unavailable_repo="$tmp/unavailable-observation-repo"
[ ! -e "$unavailable_repo" ] || fail 'unavailable fixture path unexpectedly exists'
for field in subject_repo claimed_branch claimed_tree; do
  case "$field" in
    subject_repo) value=unavailable-observation-repo; git_args=(rev-parse --show-toplevel) ;;
    claimed_branch) value=unknown; git_args=(rev-parse --abbrev-ref HEAD) ;;
    claimed_tree) value=0000000000000000000000000000000000000000; git_args=(rev-parse HEAD) ;;
  esac
  observation_code=0
  git -C "$unavailable_repo" "${git_args[@]}" > "$tmp/observation-$field.git-stdout" \
    2> "$tmp/observation-$field.git-stderr" || observation_code=$?
  [ "$observation_code" -ne 0 ] && [ ! -s "$tmp/observation-$field.git-stdout" ] \
    && [ -s "$tmp/observation-$field.git-stderr" ] || fail "$field real acquisition failure was not established"
  observation_packet "$field" "$field" "$value" yes
  observation_case "$field" unverifiable "$unavailable_repo" "$field"
done
printf 'handoff-packet-contract: observation controls ok (valid clean + failed clean + empty + repository/branch/tree unavailable)\n'

printf 'handoff-packet-contract: ok (contract + digest-bound receiver references/currentness + receiver-current/complete/incomplete/cheap-path + contradicted/matching/owner/no-claims + minimal-fields + 4 Fable adversarial)\n'
