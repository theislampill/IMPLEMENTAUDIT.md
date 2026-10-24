#!/usr/bin/env python3
"""Complete finite recursive inputs for three unchanged original commands."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import select
import shutil
import signal
import stat
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "scripts/qualify-work-graph-finite-leaf.py"
spec = importlib.util.spec_from_file_location("recursive_support", ROOT / "tests/work-graph-audit-spec-cases.py")
shared = importlib.util.module_from_spec(spec)
spec.loader.exec_module(shared)
Q, P = shared.Q, shared.P
CAPABILITY = "CONTROLLED_TASK_CAPABILITY_LEDGER_V1"
ISSUES = "CONTROLLED_TASK_ISSUES_DEFERRED_V1"
TERMINAL = "CONTROLLED_TASK_NO_TERMINAL_CAP_V1"
MAPPING = {CAPABILITY:(69,"tests/capability-ledger.test.sh"),
           ISSUES:(72,"tests/issues-deferred-gate.test.sh"),
           TERMINAL:(97,"tests/no-terminal-cap.test.sh")}


class CatalogCases(unittest.TestCase):
    def selected(self, profile):
        catalog, _ = shared.load("recursive_catalog", HELPER)
        registry = (ROOT / "scripts/verify-package.sh").read_bytes()
        try:
            graph, scope, node = catalog.select_node(Q.WG, registry, P.ENVIRONMENT, profile=profile)
        except ValueError as exc:
            self.fail("original recursive node lacks supported finite admission: " + str(exc))
        index, name = MAPPING[profile]
        self.assertEqual(len(graph["nodes"]),117)
        self.assertEqual(node,graph["nodes"][index])
        self.assertEqual(node["source"],"bash "+name+"\n")
        self.assertEqual(scope["nodes"],["COMMAND:"+name+":0"])
        self.assertEqual(len(scope["omitted_nodes"]),116)
        with self.assertRaisesRegex(ValueError,"registry"):
            catalog.select_node(Q.WG,registry+b"\n",P.ENVIRONMENT,profile=profile)

    def test_original69_selection(self): self.selected(CAPABILITY)
    def test_original72_selection(self): self.selected(ISSUES)
    def test_original97_selection(self): self.selected(TERMINAL)


class RecursiveFixture(shared.ProfileFixture):
    PROFILE = CAPABILITY

    def setUp(self):
        super().setUp()
        contract = self.A.contract_for(self.profile)["recursive"]
        for name in contract["roots"]:
            if (ROOT/name).exists():
                shutil.copytree(ROOT/name,self.source/name,dirs_exist_ok=True)
        for name in contract.get("optional_files",()):
            if (ROOT/name).exists():
                path=self.source/name;path.parent.mkdir(parents=True,exist_ok=True)
                shutil.copy2(ROOT/name,path)

    def session(self,name="evidence",**options):
        return Q.create_finite_leaf_session(self.source,self.base/name,profile=self.profile,**options)

    def new_member(self,raw=b"fresh complete recursive bytes\n",name=".new/.unlisted"):
        path=self.source/"skills"/name
        path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        return path

    def requirements(self):
        state,stamps,objects=self.snapshot()
        return state,self.A.temporary_requirements(state,profile=self.profile)


class AdmissionMixin:
    def setUp(self):
        super().setUp()
        for target,name in ((Q.VerifierTaskSession,"_execute"),(P,"acquire_runtime")):
            guard=mock.patch.object(target,name,side_effect=AssertionError("source predicate cannot acquire runtime or launch"))
            guard.start();self.addCleanup(guard.stop)

    def test_complete_recursive_bytes_dot_binary_and_empty_directory_are_captured(self):
        binary=b"\x00\xff\xfe\x80\nopaque byte input\n"
        path=self.new_member(binary)
        (path.parent/".empty").mkdir()
        state,stamps,objects=self.snapshot()
        name=path.relative_to(self.source).as_posix()
        self.assertEqual(objects[state["files"][name]["sha256"]],binary)
        self.assertIn((path.parent/".empty").relative_to(self.source).as_posix(),state["directories"])
        for tree in self.A.contract_for(self.profile)["recursive"]["roots"]:
            expected={p.relative_to(self.source).as_posix():p.read_bytes() for p in (self.source/tree).rglob("*") if p.is_file()}
            actual={name:objects[value["sha256"]] for name,value in state["files"].items() if name.startswith(tree+"/")}
            self.assertEqual(actual,expected)
        self.assertIn("recursive_inputs",stamps)

    def test_add_remove_and_same_byte_replacement_change_input_identity(self):
        first,_,_=self.snapshot()
        path=self.new_member()
        added,_,_=self.snapshot();self.assertNotEqual(first,added)
        path.unlink()
        removed,_,_=self.snapshot();self.assertNotEqual(added,removed)
        path=self.source/"skills/implementaudit/SKILL.md"
        raw=path.read_bytes();before,_,_=self.snapshot()
        path.unlink();path.write_bytes(raw);path.chmod(0o644)
        after,_,_=self.snapshot()
        self.assertEqual(before["files"][path.relative_to(self.source).as_posix()],after["files"][path.relative_to(self.source).as_posix()])
        self.assertNotEqual(before["recursive_inputs"],after["recursive_inputs"])

    def test_nonregular_alias_unreadable_and_parent_alias_refuse(self):
        path=self.new_member()
        outside=self.base/"outside";outside.write_bytes(b"outside")
        for kind in ("symlink","hardlink","fifo","mode"):
            path.unlink()
            if kind=="symlink":path.symlink_to(outside)
            elif kind=="hardlink":os.link(outside,path)
            elif kind=="fifo":os.mkfifo(path)
            else:path.write_bytes(b"hidden unreadable input");path.chmod(0)
            with self.subTest(kind=kind),self.assertRaises((ValueError,OSError)):
                self.snapshot()
            path.unlink();path.write_bytes(b"ordinary")
        (self.source/"skills").rename(self.source/"held-skills")
        (self.source/"skills").symlink_to(self.source/"held-skills",target_is_directory=True)
        with self.assertRaises((ValueError,OSError)):
            self.snapshot()

    def test_new_member_after_tree_read_refuses_complete_capture(self):
        original=P.snapshot_tree;changed=False
        def raced(root,objects,bounds,**kwargs):
            nonlocal changed
            result=original(root,objects,bounds,**kwargs)
            if Path(root)==self.source/"skills" and not changed:
                changed=True;self.new_member(b"arrived after first tree acquisition")
            return result
        with mock.patch.object(P,"snapshot_tree",side_effect=raced),self.assertRaisesRegex(ValueError,"changed"):
            self.snapshot()

    def test_source_ancestor_replacement_refuses_complete_capture(self):
        original=P.snapshot_tree;changed=False
        def raced(root,objects,bounds,**kwargs):
            nonlocal changed
            result=original(root,objects,bounds,**kwargs)
            if Path(root)==self.source/"skills" and not changed:
                changed=True
                (self.source/"skills").rename(self.source/"old-skills")
                shutil.copytree(self.source/"old-skills",self.source/"skills")
            return result
        with mock.patch.object(P,"snapshot_tree",side_effect=raced),self.assertRaisesRegex(ValueError,"changed"):
            self.snapshot()

    def test_byte_and_depth_bounds_refuse_without_partial_acceptance(self):
        bounds=self.A.contract_for(self.profile)["recursive"]["bounds"]
        path=self.new_member(b"x"*(bounds["file_bytes"]+1))
        with self.assertRaisesRegex(ValueError,"bound"):
            self.snapshot()
        path.unlink()
        path=self.source/"skills"
        for index in range(bounds["depth"]+1):path=path/("d%02d"%index)
        path.mkdir(parents=True)
        with self.assertRaisesRegex(ValueError,"bound"):
            self.snapshot()

    def test_required_literal_or_positive_operand_absence_refuses(self):
        contract=self.A.contract_for(self.profile)
        names=(*contract["data"],*contract["recursive"].get("required_members",()))
        for name in names:
            path=self.source/name;raw=path.read_bytes();mode=path.stat().st_mode&0o777
            path.unlink()
            with self.subTest(path=name),self.assertRaises((ValueError,OSError)):
                self.snapshot()
            path.write_bytes(raw);path.chmod(mode)


class CapabilityAdmission(AdmissionMixin,RecursiveFixture,unittest.TestCase):
    PROFILE=CAPABILITY


class IssuesAdmission(AdmissionMixin,RecursiveFixture,unittest.TestCase):
    PROFILE=ISSUES

    def test_report_bound_counts_every_filename_line_prefix_and_partial_line(self):
        state,_=self.requirements()
        before=state["recursive_inputs"]["resources"]["all_lines_grep_report_bytes"]
        path=self.new_member(b"x\ny",name=".prefix-bound")
        state,_=self.requirements()
        after=state["recursive_inputs"]["resources"]["all_lines_grep_report_bytes"]
        # Three actual bytes; two possible output records, each with the actual
        # 20-byte path, two colons, one line-number digit and a newline margin.
        name=path.relative_to(self.source).as_posix()
        self.assertEqual(name,"skills/.prefix-bound")
        self.assertEqual(after-before,3+2*(20+1+3))

    def test_large_prefixed_report_refuses_original_file_limit(self):
        self.new_member(b"gh issue create\n"*50000,name=("x"*180)+"/"+("y"*180))
        _,reservation=self.requirements()
        session=self.session()
        self.assertGreater(reservation["largest_file_bytes"],session.LIMITS["file_bytes"])
        with self.assertRaisesRegex(ValueError,"file/stream capacity"):
            self.A.require_resource_capacity(reservation,session.LIMITS)
        self.assertEqual(session.dispatch_count,0)


class TerminalAdmission(AdmissionMixin,RecursiveFixture,unittest.TestCase):
    PROFILE=TERMINAL

    def test_required_literal_or_positive_operand_absence_refuses(self):
        for name in self.A.contract_for(self.profile)["programs"]:
            path=self.source/name;raw=path.read_bytes();path.unlink()
            with self.subTest(path=name),self.assertRaises((ValueError,OSError)):
                self.snapshot()
            path.write_bytes(raw);path.chmod(0o644)

    def test_optional_absence_and_presence_are_explicit_not_read_failures(self):
        first,_,_=self.snapshot()
        for name in ("README.md","AGENTS.md","skills","docs/diagrams","docs/portal","fixtures"):
            path=self.source/name;held=self.base/("held-"+name.replace("/","-"));path.rename(held)
            missing,_,_=self.snapshot()
            self.assertEqual(missing["recursive_inputs"]["projection"]["probes"][name]["kind"],"MISSING")
            self.assertNotIn(name,missing["files"])
            self.assertFalse(any(key.startswith(name+"/") for key in missing["files"]))
            self.assertNotEqual(first,missing)
            held.rename(path)
        (self.source/"docs").rename(self.base/"held-docs")
        missing,_,_=self.snapshot()
        for name in ("docs/diagrams","docs/portal"):
            self.assertEqual(missing["recursive_inputs"]["projection"]["probes"][name],dict(kind="MISSING",missing_at="docs"))

    def test_literal_writes_fit_and_data_driven_diagnostics_are_bounded(self):
        state,reservation=self.requirements()
        self.assertEqual((reservation["files"],reservation["directories"]),(60,98))
        self.assertEqual(reservation["required_bytes"],14286848)
        self.A.require_resource_capacity(reservation,self.session().LIMITS)
        # Original negation exceptions do not reduce this resource-only bound.
        self.new_member(b"Do not use a failure_handoff strike ladder.\n")
        changed,_=self.requirements()
        self.assertGreater(changed["recursive_inputs"]["resources"]["terminal_possible_messages"],
                           state["recursive_inputs"]["resources"]["terminal_possible_messages"])

    def test_path_prefixed_diagnostic_overflow_refuses_before_execution(self):
        self.new_member(b"failure_handoff\n"*50000,name=("x"*180)+"/"+("y"*180))
        _,reservation=self.requirements();session=self.session()
        self.assertGreater(reservation["max_stderr_bytes"],session.LIMITS["file_bytes"])
        with self.assertRaisesRegex(ValueError,"file/stream capacity"):
            self.A.require_resource_capacity(reservation,session.LIMITS)
        self.assertEqual(session.dispatch_count,0)


class RecursiveLiveFixture(RecursiveFixture):
    @classmethod
    def setUpClass(cls):
        if os.environ.get("R0035_RECURSIVE_LIVE")!="1":
            raise unittest.SkipTest("set R0035_RECURSIVE_LIVE=1 for actual original command controls")

    def setUp(self):
        super().setUp()
        self.addCleanup(self.retain_completed_case)

    def retain_completed_case(self):
        destination=os.environ.get("R0035_RECURSIVE_EVIDENCE")
        if not destination:return
        case=Path(destination)/self.profile/"cases"/self._testMethodName
        case.parent.mkdir(parents=True,exist_ok=True)
        local=Path(os.environ["R0035_RECURSIVE_OBJECTS"])
        external=Path(os.environ["R0035_RECURSIVE_EXTERNAL_OBJECTS"]) if os.environ.get("R0035_RECURSIVE_EXTERNAL_OBJECTS") else None
        keys=[];external_keys=[];local_keys=[]
        # Only a terminal case is retained. Existing closed bytes are verified
        # and referenced read-only; no old object or receipt enters a live run.
        for path in sorted(self.base.glob("*/objects/*")):
            data=path.read_bytes();self.assertEqual(hashlib.sha256(data).hexdigest(),path.name)
            prior=external/path.name if external else None
            if prior is not None and prior.exists():
                self.assertEqual(prior.read_bytes(),data)
                external_keys.append(path.name);path.unlink()
            else:
                stored=local/path.name;stored.parent.mkdir(parents=True,exist_ok=True)
                if stored.exists():self.assertEqual(stored.read_bytes(),data);path.unlink()
                else:path.rename(stored)
                local_keys.append(stored.name)
            keys.append(path.name)
        def ignored(directory,names):
            return ["objects"] if Path(directory).parent==self.base and Path(directory).name!="source" and "objects" in names else []
        shutil.copytree(self.base,case,ignore=ignored)
        sources=("scripts/qualify-work-graph-finite-leaf.py","scripts/qualify-work-graph-prefix.py",
            "scripts/qualify-work-graph-verifier.py","scripts/run-work-graph-verifier.sh",
            "skills/implementaudit/scripts/compile-work-graph.py","tests/work-graph-audit-spec-cases.py",
            "tests/work-graph-recursive-cases.py",*self.A.contract_for(self.profile)["programs"])
        record=dict(profile=self.profile,authority="NONE",scope="ACTUAL_INDEPENDENT_ORIGINAL_NODE_NOT_CANONICAL_ACCEPTANCE",
            original_fixture_root=str(self.source),retention="TERMINAL_CASE_ONLY_NO_IMPORTED_LIVE_CUSTODY",
            input_objects=sorted(set(keys)),local_object_pool=os.path.relpath(local,case),local_objects=sorted(set(local_keys)),
            external_read_only_pool=os.path.relpath(external,case) if external else None,external_objects=sorted(set(external_keys)),
            source_sha256={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in sources})
        (case/"retention.json").write_text(json.dumps(record,sort_keys=True,indent=2)+"\n")

    def actual(self,session):
        result=session.run();directory=Path(result["evidence_directory"])
        stdout,stderr=((directory/name).read_bytes() for name in ("stdout.log","stderr.log"))
        self.assertEqual((directory/"exit-code.txt").read_bytes(),(str(result["exit"])+"\n").encode())
        receipt=json.loads((directory/"receipt.json").read_bytes());node="COMMAND:"+MAPPING[self.profile][1]+":0"
        self.assertEqual(receipt["node"],node);self.assertEqual(receipt["scope"],self.profile)
        self.assertEqual(result["group"]["nodes"],[node]);self.assertEqual(len(result["group"]["omitted_nodes"]),116)
        self.assertEqual((result["authority"],result["canonical_acceptance"]),("NONE","UNQUALIFIED"))
        return result,stdout,stderr

    def positive(self,session):
        result,stdout,stderr=self.actual(session)
        self.assertEqual((result["exit"],result["complete"]),(0,True),stderr)
        expected={CAPABILITY:b"capability-ledger.test: ok\n",ISSUES:b"issues-deferred-gate.test: ok\n",
            TERMINAL:b"check-no-terminal-cap: ok\n"*4+b"no-terminal-cap.test: ok\n"}
        self.assertEqual(stdout,expected[self.profile]);self.assertEqual(stderr,b"")
        return result,stdout,stderr


class LiveMixin:
    def test_original_positive_full_binary_input_and_unchanged_reuse_then_namespace_drift(self):
        binary=b"\x00\xff\xfeuninterpreted complete byte input\n";path=self.new_member(binary,name=".binary-input")
        session=self.session();first,_,_=self.positive(session)
        image=json.loads((Path(first["evidence_directory"])/"image.json").read_bytes())
        member=next(row for row in image["files"] if row["path"]=="/work/skills/.binary-input")
        self.assertEqual((member["bytes"],member["sha256"]),(len(binary),hashlib.sha256(binary).hexdigest()))
        second,_,_=self.positive(session)
        self.assertEqual((first["disposition"],second["disposition"]),("EXECUTED","REUSED"))
        self.assertEqual(first["receipt_digest"],second["receipt_digest"])
        self.new_member(b"new fully observed harmless member\n")
        with self.assertRaisesRegex(ValueError,"prior receipt refused"):
            session.run()
        self.assertEqual(session.dispatch_count,1)

    def test_previously_unlisted_semantic_failure_is_actual_and_not_reused(self):
        raw={CAPABILITY:b"We claim broad competence from this one run.\n",
             ISSUES:b"gh issue create immediately\n",
             TERMINAL:b"The three-strike sequence stops the run on Strike 3.\n"}[self.profile]
        marker={CAPABILITY:b"broad competence claim appears endorsed",
                ISSUES:b"issue publication appears enabled",
                TERMINAL:b"disallowed public-claim terminal-cap wording"}[self.profile]
        self.new_member(raw);session=self.session();result,_,stderr=self.actual(session)
        self.assertEqual((result["exit"],result["complete"]),(1,True),stderr)
        self.assertIn(marker,stderr);self.assertEqual(session._issued,{})
        with self.assertRaisesRegex(ValueError,"failed or interrupted"):
            session.run()
        self.assertEqual(session.dispatch_count,1)

    def test_foreign_producer_and_tampered_retained_output_refuse(self):
        session=self.session();result,stdout,_=self.positive(session)
        (self.base/"issued-stdout-before-tamper.bin").write_bytes(stdout)
        read,write=os.pipe();child=os.fork()
        if child==0:
            os.close(read)
            try:session.run();data=b"WRONGLY_ACCEPTED"
            except (ValueError,OSError) as exc:data=str(exc).encode()
            os.write(write,data[:4096]);os.close(write);os._exit(0)
        os.close(write)
        try:
            ready,_,_=select.select([read],[],[],5);self.assertTrue(ready,"foreign refusal did not return")
            message=os.read(read,4096);_,status=os.waitpid(child,0);child=None
            self.assertEqual(os.waitstatus_to_exitcode(status),0);self.assertIn(b"producer process changed",message)
            (self.base/"foreign-process-refusal.txt").write_bytes(message+b"\n")
        finally:
            os.close(read)
            if child is not None:os.kill(child,signal.SIGKILL);os.waitpid(child,0)
        path=Path(result["evidence_directory"])/"stdout.log";path.chmod(0o600);path.write_bytes(stdout+b"tampered output\n");path.chmod(0o400)
        with self.assertRaisesRegex(ValueError,"evidence refused"):
            session.run()
        self.assertEqual(session.dispatch_count,1)


class CapabilityLive(LiveMixin,RecursiveLiveFixture,unittest.TestCase):
    PROFILE=CAPABILITY


class IssuesLive(LiveMixin,RecursiveLiveFixture,unittest.TestCase):
    PROFILE=ISSUES

    def test_oversized_prefixed_report_refuses_before_original_dispatch(self):
        self.new_member(b"gh issue create\n"*50000,name=("x"*180)+"/"+("y"*180))
        session=self.session()
        with self.assertRaisesRegex(ValueError,"file/stream capacity"):
            session.run()
        self.assertEqual(session.dispatch_count,0);self.assertEqual(session._issued,{})
        self.assertEqual(list(session.output.rglob("dispatch.json")),[])


class TerminalLive(LiveMixin,RecursiveLiveFixture,unittest.TestCase):
    PROFILE=TERMINAL

    def test_original_optional_absence_is_explicit_and_runs_all_literal_controls(self):
        for name in ("README.md","AGENTS.md"):(self.source/name).unlink()
        for name in ("skills","docs/diagrams","docs/portal","fixtures"):shutil.rmtree(self.source/name)
        session=self.session();result,_,_=self.positive(session)
        image=json.loads((Path(result["evidence_directory"])/"image.json").read_bytes())
        probes=image["directory_membership"]["probes"]
        self.assertEqual(set(probes),{"skills","docs/diagrams","docs/portal","fixtures","README.md","AGENTS.md"})
        self.assertTrue(all(row["kind"]=="MISSING" for row in probes.values()))
        self.assertEqual(session.dispatch_count,1)


if __name__=="__main__":unittest.main()
