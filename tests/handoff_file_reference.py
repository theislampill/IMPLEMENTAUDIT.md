#!/usr/bin/env python3
"""Actual digest-bound receiver references in a disposable native repository."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SCORER = ROOT / "skills/implementaudit/scripts/check-handoff-packet.sh"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args()
    results = []
    with tempfile.TemporaryDirectory(prefix="handoff-file-") as temporary:
        repo = Path(temporary) / "repo"
        repo.mkdir()
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        def command(argv):
            return subprocess.run(argv, cwd=repo, env=env, text=True,
                                  capture_output=True, timeout=20)
        for argv in [["git", "init", "-q"], ["git", "config", "user.name", "receiver-test"],
                     ["git", "config", "user.email", "receiver@example.invalid"]]:
            assert command(argv).returncode == 0
        (repo / "seed").write_text("disposable receiver\n", encoding="utf-8")
        assert command(["git", "add", "seed"]).returncode == 0
        assert command(["git", "commit", "-qm", "fixture"]).returncode == 0
        commit = command(["git", "rev-parse", "HEAD"]).stdout.strip()
        (repo / "state").mkdir()
        state = repo / "state/current.txt"
        original = b"current required state\n"
        state.write_bytes(original)
        wanted = hashlib.sha256(original).hexdigest()
        active_scorer = SCORER
        def invoke(name, reference, accept):
            fields = dict(packet_id="receiver-local", packet_version="1", sender_run_id="sender-local",
                handoff_state="READY", implementation_identity_present="yes", frozen_denominator_present="yes",
                acceptance_oracle_present="yes", reproduction_inputs_present="yes", evaluator_schema_semantics_present="yes",
                prior_evidence_present="yes", rejected_non_evidence_present="yes", authority_stop_boundaries_present="yes",
                exact_handoff_receipt_present="yes", current_state_ref=reference, provenance_ref="packet:receiver-local",
                pending_effects_disposition="none-observed", authority_capability_ref="owner:R001F",
                discrepancy_state="none-observed", receiver_live_verification="opaque receiver obligation",
                claimed_tree=commit, has_state_claims="no")
            body="".join(f"{k}: {v}\n" for k,v in fields.items()).encode()
            packet=repo.parent/"handoff.pkt"
            packet.write_bytes(body+b"packet_content_hash: "+hashlib.sha256(body).hexdigest().encode()+b"\n")
            outcome=command([shutil.which("bash"),active_scorer.as_posix(),packet.as_posix(),
                             "--repo-root",repo.as_posix(),"--receiver-requires-reproduction"])
            row=dict(case=name,exit=outcome.returncode,stdout=outcome.stdout,stderr=outcome.stderr)
            results.append(row)
            if args.evidence_dir:
                args.evidence_dir.mkdir(parents=True,exist_ok=True)
                (args.evidence_dir/"results.json").write_text(json.dumps(results,indent=2)+"\n",encoding="utf-8")
            if accept:
                assert outcome.returncode==0 and "RECEIVER_ACCEPTANCE_STATE=COMPLETE" in outcome.stdout,row
            else:
                assert outcome.returncode==1 and "RECEIVER_INCOMPLETE" in outcome.stderr,row
                assert "RECEIVER_ACCEPTANCE_STATE=COMPLETE" not in outcome.stdout,row
            print("handoff-file-reference",name,"PASS",flush=True)
        reference=f"file:state/current.txt#sha256={wanted}"
        invoke("current",reference,True)
        state.write_bytes(b"changed required state\n")
        invoke("stale",reference,False)
        wanted=hashlib.sha256(state.read_bytes()).hexdigest()
        invoke("rebound",f"file:state/current.txt#sha256={wanted}",True)
        state.unlink()
        invoke("missing",reference,False)
        state.mkdir()
        invoke("directory",reference,False)
        state.rmdir()
        state.write_bytes(original)
        for name,path in [("traversal","state/../state/current.txt"),
                          ("backslash","state\\current.txt"),
                          ("absolute",state.as_posix())]:
            invoke(name,f"file:{path}#sha256={hashlib.sha256(original).hexdigest()}",False)
        outside = repo.parent / "outside.txt"
        outside.write_bytes(original)
        invoke("absolute-intermediate-component",
               f"file:{str(repo.parent)}/outside.txt#sha256={hashlib.sha256(original).hexdigest()}",False)
        shadow_marker=repo.parent/"cwd-module-must-not-execute"
        shadow=repo/"pathlib.py"
        shadow.write_text(f"open({shadow_marker.as_posix()!r}, 'w').write('ran')\nraise RuntimeError('repository module shadowed standard library')\n",encoding="utf-8")
        startup_shadow=repo/"sitecustomize.py"
        startup_shadow.write_text(shadow.read_text(encoding="utf-8"),encoding="utf-8")
        invoke("cwd-module-shadow",reference,True)
        assert not shadow_marker.exists(), "repository code imported by receiver"
        shadow.unlink()
        startup_shadow.unlink()
        if os.name == "nt":
            outside=repo.parent/"outside-root"
            outside.mkdir()
            (outside/"current.txt").write_bytes(original)
            digest=hashlib.sha256(original).hexdigest()
            for name,parent in [("drive-absolute-parent",str(outside)),
                                ("rooted-backslash-parent",str(outside)[2:])]:
                invoke(name,f"file:{parent}/current.txt#sha256={digest}",False)
            copied = repo.parent / "receiver-source"
            copied.mkdir()
            active_scorer = copied / SCORER.name
            shutil.copyfile(SCORER, active_scorer)
            companion = copied / "canonical_custody.py"
            exact = SCORER.with_name(companion.name).read_bytes()
            companion.write_bytes(exact)
            invoke("exact-copied-source", reference, True)
            marker = repo.parent / "must-not-execute"
            end = exact.index(b'"""', 3) + 3
            prefix = f"open({marker.as_posix()!r}, 'w').write('ran')\n".encode()
            mutant = prefix + b"#" * (end-len(prefix)-1) + b"\n" + exact[end:]
            future = b"from __future__ import annotations"
            mutant = mutant.replace(future, b"#" * len(future), 1)
            assert len(mutant) == len(exact)
            compile(mutant, str(companion), "exec")
            companion.write_bytes(mutant)
            invoke("same-size-source-drift", reference, False)
            assert not marker.exists(), "unverified source executed"
            companion.unlink()
            invoke("missing-source", reference, False)
            sibling = copied / "source-original.py"
            sibling.write_bytes(exact)
            os.link(sibling, companion)
            invoke("hardlinked-source", reference, False)
            active_scorer = SCORER
            alias=repo/"state-alias"
            linked=command(["cmd","/c","mklink","/J",str(alias),str(state.parent)])
            assert linked.returncode==0, linked.stderr
            invoke("native-junction-reference",f"file:state-alias/current.txt#sha256={hashlib.sha256(original).hexdigest()}",False)
            alias.rmdir()
            sibling_state=state.with_name("same-state.txt")
            os.link(state,sibling_state)
            invoke("native-hardlinked-state",reference,False)
            sibling_state.unlink()
            receipt = repo.parent / "replacement-attempts.json"
            # A strip-byte-equal derived receiver schedules actual rename attempts
            # while native handles are held. Isolated Python disables env hooks.
            companion.unlink()
            companion.write_bytes(exact)
            receiver_source=SCORER.read_text(encoding="utf-8")
            anchor="        with custody.File(directory, parts[-1], maximum=sys.maxsize) as state:\n"
            injected=f'''            import json
            attempts=[]
            for attempted in (state.path,state.path.parent):
                try:
                    os.rename(attempted,str(attempted)+".replaced")
                    attempts.append({{"path":str(attempted),"denied":False}})
                except PermissionError:
                    attempts.append({{"path":str(attempted),"denied":True}})
            Path({str(receipt)!r}).write_text(json.dumps(attempts))
'''
            assert receiver_source.count(anchor)==1
            derived=receiver_source.replace(anchor,anchor+injected)
            assert derived.replace(injected,"")==receiver_source
            active_scorer=copied/"instrumented-receiver.sh"
            active_scorer.write_text(derived,encoding="utf-8",newline="\n")
            invoke("native-retained-handle-exclusion",reference,True)
            attempts=json.loads(receipt.read_text())
            assert len(attempts)==2 and all(r["denied"] for r in attempts)
            assert state.read_bytes()==original
        print(f"handoff-file-reference: {len(results)}/{len(results)} PASS")


if __name__ == "__main__":
    main()
