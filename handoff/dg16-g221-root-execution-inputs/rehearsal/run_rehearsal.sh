#!/bin/bash
# SIMULATED dry rehearsal of the G221 Root sequence. Authority NONE.
#   Part A reproduces G220's ACTUAL documents byte-for-byte with the packet tools (proves every encoder and schema).
#   Part B rebuilds the G221 correction universe from this repository checkout and closes its pin chain.
#   Part C runs the host-21 sequence with a throwaway TEST certificate and TEST decision bodies, in <scratch> ONLY.
# Nothing here is a recipient, a Root decision, a review, a seal, a publication or an acceptance. The TEST private key
# is written to a temporary file and deleted immediately; no TEST body is committed. Only the printed transcript is kept.
# usage: run_rehearsal.sh <repo-checkout-root> <fresh-scratch-dir> [--with-remote]
set -u
REPO=$(cd "$1" && pwd); S=$2; REMOTE=${3:-}
H=$REPO/handoff/dg16-g221-root-execution-inputs; T=$H/tools; C=$H/g220-custody; PY=${PYTHON:-python3}
[ -e "$S" ] && { echo "scratch must not exist: $S"; exit 2; }
mkdir -p "$S"; S=$(cd "$S" && pwd); FAIL=0; N=0
ASTRA=01a1cf82-cdd6-7053-b7b7-32f5c3d93d21
OLDH=pro/dg16-r5-full-g2-direct-host-20-20261114; OLDC=pro/dg16-r5-full-g2-direct-control-20-20261114
NEWH=pro/dg16-r5-full-g2-direct-host-21-20261115; NEWC=pro/dg16-r5-full-g2-direct-control-21-20261115
G220WS=/home/agent/pr255-g2-completion-20261114-10
# Optional: TEST_ISSUER=<uuid> rehearses the owner-gated issuer-thread rebind proposal (RUNBOOK section 0). Default: labels unchanged.
CI=${TEST_ISSUER:-$ASTRA}; REBIND=""; [ "$CI" = "$ASTRA" ] || REBIND="--old-issuer-thread $ASTRA --new-issuer-thread $CI"
step() { N=$((N+1)); echo; echo "### $N. $1"; }
run() { echo "\$ ${*//$REPO/<repo>}" | sed "s#$S#<scratch>#g"; "$@" 2>&1 | sed -e "s#$S#<scratch>#g" -e "s#$REPO#<repo>#g" | cut -c1-260 | tail -n ${TAIL:-12}; rc=${PIPESTATUS[0]}; [ "$rc" -eq 0 ] || { echo "   EXIT $rc"; FAIL=$((FAIL+1)); }; return 0; }
refuse() { echo "\$ ${*//$REPO/<repo>}" | sed "s#$S#<scratch>#g"; out=$("$@" 2>&1); rc=$?; echo "$out" | sed "s#$S#<scratch>#g" | tail -n 1 | cut -c1-200; if [ "$rc" -ne 0 ]; then echo "   EXPECTED REFUSAL (exit $rc)"; else echo "   UNEXPECTED PASS"; FAIL=$((FAIL+1)); fi; }
same() { if cmp -s "$1" "$2"; then echo "   BYTE-IDENTICAL  $3  sha256=$(sha256sum "$1" | cut -c1-64)"; else echo "   DIFFERENT       $3  $(sha256sum "$1" | cut -c1-16) vs $(sha256sum "$2" | cut -c1-16)"; FAIL=$((FAIL+1)); fi; }
echo "SIMULATED REHEARSAL â€” authority NONE â€” $(date -u +%Y-%m-%dT%H:%M:%SZ) â€” $($PY --version 2>&1) â€” issuer-label-in-part-C=$CI — repo HEAD $(git -C "$REPO" rev-parse HEAD 2>/dev/null)"

echo; echo "================ PART A: reproduce G220's ACTUAL documents (historical; proves the tools) ================"
step "G220 universe from g220-custody; structural pin chain"
run $PY $T/build_universe.py g220 --repo $REPO --out $S/u0
TAIL=1 run $PY $T/check_chain.py $S/u0 G220-base $S/check-u0.json
step "candidate seal encoder == Astra's CANDIDATE_SEAL.json"
run $PY $T/draft_records.py candidate-seal --candidate $S/u0/candidate-e76-source-01 --modes-from $C/root-issuer/CANDIDATE_SEAL.json --actor /root --issuer-thread $ASTRA --out $S/a/CANDIDATE_SEAL.json
same $S/a/CANDIDATE_SEAL.json $C/root-issuer/CANDIDATE_SEAL.json CANDIDATE_SEAL.json
step "runtime encoder == Astra's PUBLIC_RUNTIME.json"
run $PY $T/draft_records.py runtime --universe $S/u0 --actor /root --issuer-thread $ASTRA --workspace-root $G220WS --receiver-output-root $G220WS/public-acquisition --maintained-source-root /home/agent/pr255-g2-completion-20261114-08/product-205aeab7 --out $S/a/PUBLIC_RUNTIME.json
same $S/a/PUBLIC_RUNTIME.json $C/root-issuer/PUBLIC_RUNTIME.json PUBLIC_RUNTIME.json
step "review / review-seal / adoption encoders == G220's four decision bodies and REVIEW_SEAL.json"
run $PY $T/draft_records.py reviews --previous-universe $S/u0 --universe $S/u0 --previous-decisions $C/root-issuer/decisions --candidate-seal $S/a/CANDIDATE_SEAL.json --reviewer /root/g220_source_review --out-dir $S/a/decisions
run $PY $T/draft_records.py review-seal --reviews $S/a/decisions --candidate-seal $S/a/CANDIDATE_SEAL.json --reviewer /root/g220_source_review --report-descriptor 3475:5bafe35d05435e0095e21b1b07e09e39c055474e4bc6079a38e7c0b36be24b2a --out $S/a/REVIEW_SEAL.json
run $PY $T/draft_records.py adoptions --previous-universe $S/u0 --universe $S/u0 --previous-decisions $C/root-issuer/decisions --reviews $S/a/decisions --review-seal $S/a/REVIEW_SEAL.json --candidate-seal $S/a/CANDIDATE_SEAL.json --author /root --out-dir $S/a/decisions
same $S/a/REVIEW_SEAL.json $C/root-issuer/REVIEW_SEAL.json REVIEW_SEAL.json
for n in INDEPENDENT_COLD_REVIEW NATIVE_INDEPENDENT_REVIEW ROOT_POLICY_ADOPTION ROOT_NATIVE_APPLICABILITY_ADOPTION; do same $S/a/decisions/$n.json $C/root-issuer/decisions/$n.json $n.json; done
step "composer stages: compose.py -> candidate-bound -> final-bound == G220's stage files"
run $PY $T/stage_composer.py --in $C/author/compose.py --out $S/a/compose-candidate-bound.py --candidate-seal $S/a/CANDIDATE_SEAL.json
same $S/a/compose-candidate-bound.py $C/author/compose-candidate-bound.py compose-candidate-bound.py
run $PY $T/stage_composer.py --in $S/a/compose-candidate-bound.py --out $S/a/compose-final-bound.py --review-seal $S/a/REVIEW_SEAL.json --runtime $S/a/PUBLIC_RUNTIME.json --witness $C/host-witness/root.json
same $S/a/compose-final-bound.py $C/author/compose-final-bound.py compose-final-bound.py
step "final-stage composition == Astra's composition (tree bbc3669b, 49 public + 5 documents)"
run $PY $S/a/compose-final-bound.py --candidate $S/u0/candidate-e76-source-01 --issuer $S/a --host-witness $C/host-witness/root.json --decisions $S/a/decisions --code-review-seal $S/a/REVIEW_SEAL.json --native-review-seal $S/a/REVIEW_SEAL.json --output $S/a/composition
if diff -r -x SEAL.json $S/a/composition $C/astra-g220-publication/composition >/dev/null; then echo "   BYTE-IDENTICAL  composition/ ($(find $S/a/composition -type f | wc -l) files) == astra-g220-publication/composition minus SEAL.json"; else echo "   DIFFERENT composition/"; FAIL=$((FAIL+1)); fi
step "composition seal, review selection, public index == Astra's records"
run $PY $T/draft_records.py composition-seal --composition $S/a/composition --actor /root --issuer-thread $ASTRA --out $S/a/COMPOSITION_SEAL.json
same $S/a/COMPOSITION_SEAL.json $C/astra-g220-publication/composition/SEAL.json composition/SEAL.json
cp $S/a/COMPOSITION_SEAL.json $S/a/composition/SEAL.json
run $PY $T/draft_records.py selection --composition $S/a/composition --composition-seal $S/a/composition/SEAL.json --candidate-seal $S/a/CANDIDATE_SEAL.json --actor /root --issuer-thread $ASTRA --author /root --reviewer /root/g220_source_review --out $S/a/FINAL_REVIEW_SELECTION.json
same $S/a/FINAL_REVIEW_SELECTION.json $C/astra-g220-publication/FINAL_REVIEW_SELECTION.json FINAL_REVIEW_SELECTION.json
run $PY $T/draft_records.py public-index --composition $S/a/composition --out $S/a/PUBLIC_INDEX.json
same $S/a/PUBLIC_INDEX.json $C/astra-g220-publication/PUBLIC_INDEX.json PUBLIC_INDEX.json
step "binder -> seven-file receiver == G220's installed receiver seal (0950cb87)"
TAIL=3 run $PY $T/bind_harness.py g220-actual $S/u0/author/bind_public_successor.py $S/u0/candidate-e76-source-01 $S/a/composition $S/a $S/a/public-receiver-bound $S/a/bind-report.json --composition-path $G220WS/composition --candidate-path $G220WS/candidate-e76-source-01
run $PY $T/draft_records.py receiver-seal --receiver $S/a/public-receiver-bound --composition $S/a/composition --actor /root --issuer-thread $ASTRA --out $S/a/PUBLIC_RECEIVER_SEAL.json
same $S/a/PUBLIC_RECEIVER_SEAL.json $C/operator-bundle-records/PUBLIC_RECEIVER_SEAL.json PUBLIC_RECEIVER_SEAL.json

echo; echo "================ PART B: G221 correction universe from this checkout (host-20 base) ================"
step "build from repository files + prospective-custody; pin chain closes"
TAIL=4 run $PY $T/build_universe.py g221 --repo $REPO --out $S/u1
TAIL=1 run $PY $T/check_chain.py $S/u1 G221-host20-base $S/check-u1.json
echo "   candidate SEAL.json sha256=$(sha256sum $S/u1/candidate-e76-source-01/SEAL.json | cut -c1-64) (READ_FIRST: 1d2ef960â€¦)"

echo; echo "================ PART C: host-21 sequence, SIMULATED with TEST inputs in scratch only ================"
R=$S/c; mkdir -p $R/issuer
step "TEST certificate (NOT a recipient; throwaway key deleted at once)"
K=$(mktemp); openssl req -x509 -newkey rsa:3072 -nodes -keyout $K -out $R/TEST_ONLY_NOT_A_RECIPIENT.pem -days 2 -subj "/CN=SIMULATED-TEST-ONLY-NOT-A-RECIPIENT" >/dev/null 2>&1; rm -f $K
echo "   TEST cert sha256=$(sha256sum $R/TEST_ONLY_NOT_A_RECIPIENT.pem | cut -c1-64) bytes=$(wc -c < $R/TEST_ONLY_NOT_A_RECIPIENT.pem); private key file removed: $([ -e $K ] && echo NO || echo yes)"
step "propagate host-21 / control-21 / certificate digest; pin chain closes"
TAIL=24 run $PY $T/propagate_successor.py $S/u1 $S/u21 $R/propagate-report.json --old-host-branch $OLDH --new-host-branch $NEWH --old-control-branch $OLDC --new-control-branch $NEWC --recipient-cert $R/TEST_ONLY_NOT_A_RECIPIENT.pem $REBIND
TAIL=20 run $PY $T/check_chain.py $S/u21 SIMULATED-host21 $S/check-u21.json
echo "   residual host-20/control-20 names in u21: $(grep -rl -e "-host-20-" -e "-control-20-" $S/u21 | wc -l) files"
grep -n -A1 "branches:" $S/u21/candidate-e76-source-01/candidate/public/.github/workflows/dg16-r5-full-g2.yml | sed 's/^/   workflow: /'
grep -n -e "^BRANCH = " -e "^CONTROL_BRANCH = " $S/u21/candidate-e76-source-01/candidate/public/qualification/dg16-r5-full-g2/{run,protected_bridge,live_control}.py $S/u21/candidate-e76-source-01/receiver/root_common.py | sed "s#$S#<scratch>#;s/^/   /"
refuse $PY $T/propagate_successor.py $S/u1 $S/u21-bad $R/bad.json --old-host-branch $OLDH --new-host-branch $NEWH --old-control-branch $OLDC --new-control-branch $NEWC --recipient-cert <(cat $R/TEST_ONLY_NOT_A_RECIPIENT.pem; echo "-----BEGIN PRIV""ATE KEY-----")
step "TEST runtime, candidate seal (labels as the unchanged code requires: actor /root, issuer $CI)"
WS=/simulated/g221-workspace
run $PY $T/draft_records.py runtime --universe $S/u21 --actor /root --issuer-thread $CI --workspace-root $WS --receiver-output-root $WS/public-acquisition --maintained-source-root /simulated/product-205aeab7 --out $R/issuer/PUBLIC_RUNTIME.json
run $PY $T/draft_records.py candidate-seal --candidate $S/u21/candidate-e76-source-01 --modes-from $S/u1/candidate-e76-source-01/SEAL.json --actor /root --issuer-thread $CI --out $R/issuer/CANDIDATE_SEAL.json
same $R/issuer/CANDIDATE_SEAL.json $S/u21/candidate-e76-source-01/SEAL.json "issued-form seal == propagated SEAL.json proposal"
step "TEST decision bodies and TEST review seal (reviewer label /root/simulated_rehearsal_only)"
printf 'SIMULATED TEST REPORT - not a review\n' > $R/REPORT.md
run $PY $T/draft_records.py reviews --previous-universe $S/u0 --universe $S/u21 --previous-decisions $C/root-issuer/decisions --candidate-seal $R/issuer/CANDIDATE_SEAL.json --reviewer /root/simulated_rehearsal_only --out-dir $R/decisions
run $PY $T/draft_records.py review-seal --reviews $R/decisions --report $R/REPORT.md --candidate-seal $R/issuer/CANDIDATE_SEAL.json --reviewer /root/simulated_rehearsal_only --out $R/issuer/REVIEW_SEAL.json
run $PY $T/draft_records.py adoptions --previous-universe $S/u0 --universe $S/u21 --previous-decisions $C/root-issuer/decisions --reviews $R/decisions --review-seal $R/issuer/REVIEW_SEAL.json --candidate-seal $R/issuer/CANDIDATE_SEAL.json --author /root --out-dir $R/decisions
step "final composer stage for host-21, then composition through the ORIGINAL validators"
run $PY $T/stage_composer.py --in $S/u21/author/compose-candidate-bound.py --out $R/compose-final-bound.py --candidate-seal $R/issuer/CANDIDATE_SEAL.json --runtime $R/issuer/PUBLIC_RUNTIME.json --witness $C/host-witness/root.json --review-seal $R/issuer/REVIEW_SEAL.json
COMPOSE="$PY $R/compose-final-bound.py --candidate $S/u21/candidate-e76-source-01 --issuer $R/issuer --host-witness $C/host-witness/root.json --code-review-seal $R/issuer/REVIEW_SEAL.json --native-review-seal $R/issuer/REVIEW_SEAL.json"
run $COMPOSE --decisions $R/decisions --output $R/composition
echo "   COMPOSITION branch=$($PY -c "import json;c=json.load(open('$R/composition/COMPOSITION.json'));print(c['branch'],c['control_branch'],'final_tree='+c['final_tree'])")"
refuse $COMPOSE --decisions $C/root-issuer/decisions --output $R/composition-stale-g220-decisions
step "TEST composition seal, TEST review selection, binder, seven-file receiver, receiver seal, public index"
run $PY $T/draft_records.py composition-seal --composition $R/composition --actor /root --issuer-thread $CI --out $R/composition/SEAL.json
run $PY $T/draft_records.py selection --composition $R/composition --composition-seal $R/composition/SEAL.json --candidate-seal $R/issuer/CANDIDATE_SEAL.json --actor /root --issuer-thread $CI --author /root --reviewer /root/simulated_rehearsal_only --out $R/issuer/FINAL_REVIEW_SELECTION.json
TAIL=3 run $PY $T/bind_harness.py g220-actual $S/u21/author/bind_public_successor.py $S/u21/candidate-e76-source-01 $R/composition $R/issuer $R/public-receiver-bound $R/bind-report.json --composition-path $WS/composition --candidate-path $WS/candidate-e76-source-01
echo "   bind_public=$($PY -c "import json;r=json.load(open('$R/bind-report.json'));print(r['bind_public'], sorted(r.get('outputs',{})))")"
run $PY $T/draft_records.py receiver-seal --receiver $R/public-receiver-bound --composition $R/composition --actor /root --issuer-thread $CI --out $R/issuer/PUBLIC_RECEIVER_SEAL.json
run $PY $T/draft_records.py public-index --composition $R/composition --out $R/issuer/PUBLIC_INDEX.json
step "operator static source regenerated for host-21 (workflow commit = fail-closed placeholder)"
TAIL=40 run $PY $T/regen_operator_static.py $C/operator-static-source $S/u21/candidate-e76-source-01 $R/operator-static --old-branch $OLDH --new-branch $NEWH --old-commit ce144b1d06f81bda3225b48d3bab32374515cff5 --workflow-commit 0000000000000000000000000000000000000000 --old-install-root $G220WS/operator-installed-r1 --install-root $WS/operator-installed
step "pre-launch gates against the TEST certificate"
if [ "$REMOTE" = "--with-remote" ]; then run $PY $T/prelaunch_gates.py --host-branch $NEWH --control-branch $NEWC --recipient-cert $R/TEST_ONLY_NOT_A_RECIPIENT.pem --out $R/gates.json
else run $PY $T/prelaunch_gates.py --host-branch $NEWH --control-branch $NEWC --recipient-cert $R/TEST_ONLY_NOT_A_RECIPIENT.pem --skip-remote --out $R/gates.json; fi
echo "   expired-window control:"; refuse $PY $T/prelaunch_gates.py --host-branch $NEWH --control-branch $NEWC --recipient-cert $C/candidate-e76-source-01/candidate/public/qualification/dg16-r5-full-g2/PROTECTED_RECIPIENT.pem --skip-remote --now 2026-11-15T10:20:00Z
step "live-window bodies checked by the packet's own live_control.validate (synthetic TEST request; no run exists)"
LC=$S/u21/candidate-e76-source-01/candidate/public/qualification/dg16-r5-full-g2/live_control.py; D=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa
$PY -c "import json,time;print(json.dumps(dict(TEST_ONLY_SYNTHETIC_REQUEST=True,run_id='1',workflow_commit='0'*40,repository='theislampill/IMPLEMENTAUDIT.md',control_branch='$NEWC',control_path='qualification/dg16-full-g2-control/1-1',hold_seconds=300,expires_utc_epoch=time.time()+300,proof=dict(sha256='$D'),private_observations=dict(sha256='$D'),source_commit='205aeab7c93299b0666b261485ab5658d8e183de',source_tree='9ffbaf95080092bf4a45b8772a97ed16068544a7',policy_sha256='$D',policy_adoption_sha256='$D')))" > $R/TEST_REQUEST.json
run $PY $T/live_control_payload.py review --request $R/TEST_REQUEST.json --reviewer /root/simulated_rehearsal_only --out $R/live/INDEPENDENT_REVIEW.json
run $PY $T/live_control_payload.py consume --request $R/TEST_REQUEST.json --review $R/live/INDEPENDENT_REVIEW.json --live-control $LC --author /root --publisher /root --out-dir $R/live
run $PY $T/live_control_payload.py stop --request $R/TEST_REQUEST.json --live-control $LC --publisher /root --out-dir $R/live-stop
echo "   controls: reviewer that is a current author; a non-/root consumption author; an expired window"
$PY $T/live_control_payload.py review --request $R/TEST_REQUEST.json --reviewer /root/source_package --out $R/live-bad/INDEPENDENT_REVIEW.json >/dev/null
refuse $PY $T/live_control_payload.py consume --request $R/TEST_REQUEST.json --review $R/live-bad/INDEPENDENT_REVIEW.json --live-control $LC --author /root --publisher /root --out-dir $R/live-bad1
refuse $PY $T/live_control_payload.py consume --request $R/TEST_REQUEST.json --review $R/live/INDEPENDENT_REVIEW.json --live-control $LC --author /root/successor --publisher /root --out-dir $R/live-bad2
refuse $PY $T/live_control_payload.py consume --request $R/TEST_REQUEST.json --review $R/live/INDEPENDENT_REVIEW.json --live-control $LC --author /root --publisher /root --out-dir $R/live-bad3 --now 99999999999
echo; echo "================ SUMMARY: steps=$N unexpected_failures=$FAIL (SIMULATED; nothing issued, nothing published) ================"
exit $FAIL
