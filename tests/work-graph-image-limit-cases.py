#!/usr/bin/env python3
"""Finite image resource-phase regression controls; no campaign authority.

Default controls exercise the actual kernel limit and fixed bootstrap locally.
--native additionally exercises the real maintained Bubblewrap executor using
the current complete runtime on a qualified Linux/Python3.12 host.
"""
import argparse
import errno
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import shlex
import signal
import subprocess
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("finite_image_qualifier", REPO / "scripts/qualify-work-graph-verifier.py")
Q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Q)
S = Q.VerifierTaskSession
PAYLOAD = 8 * 1024 * 1024
LARGE = 9 * 1024 * 1024

PROBE = r'''
import errno,json,os,resource,signal,sys
signal.signal(signal.SIGXFSZ,signal.SIG_IGN)
limits=resource.getrlimit(resource.RLIMIT_FSIZE)
raised=False
try:
    resource.setrlimit(resource.RLIMIT_FSIZE,(9*1024*1024,9*1024*1024))
    raised=True
except (ValueError,OSError):
    pass
fd=os.open(sys.argv[1],os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
try:
    os.lseek(fd,8*1024*1024,os.SEEK_SET)
    try:
        os.write(fd,b'x')
        write_error=None
    except OSError as error:
        write_error=error.errno
    size=os.fstat(fd).st_size
finally:
    os.close(fd)
print(json.dumps(dict(limits=limits,raised=raised,write_error=write_error,size=size)))
'''


def phase_process(command, setup_limit):
    def limits():
        resource.setrlimit(resource.RLIMIT_FSIZE, (setup_limit, setup_limit))
    return subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          preexec_fn=limits, timeout=15,
                          env=dict(PATH="/usr/bin:/bin", LANG="C", LC_ALL="C"))


class PhaseControls(unittest.TestCase):
    def session(self):
        return object.__new__(S)

    def test_small_images_keep_the_existing_launch_path(self):
        self.assertIsNone(self.session()._image_file_policy_v1({"/small": (b"x", 0o444)}))

    def test_large_input_selects_finite_setup_without_changing_payload(self):
        policy = self.session()._image_file_policy_v1({"/input": (b"x" * LARGE, 0o444)})
        self.assertEqual(policy["materialization_file_bytes"], 9437184)
        self.assertEqual(policy["payload_file_bytes"], 8388608)
        self.assertEqual(policy["maximum_materialization_file_bytes"], 33554432)
        self.assertEqual(S.LIMITS["file_bytes"], 8388608)

    def test_input_above_materialization_ceiling_refuses(self):
        with self.assertRaisesRegex(Q.WG.WorkGraphError, "materialization"):
            self.session()._image_file_policy_v1({"/input": (b"x" * (32*1024*1024+1), 0o444)})

    def test_other_scope_does_not_gain_a_new_phase(self):
        s = self.session()
        s.SCOPE = "CONTROLLED_TASK_REGISTRY_V1"
        self.assertIsNone(s._image_file_policy_v1({"/input": (b"x" * LARGE, 0o444)}))

    def test_changed_materialization_policy_refuses_before_dispatch(self):
        with tempfile.TemporaryDirectory(prefix="dg16-image-drift-") as td:
            s = self.session()
            files = {"/input": (b"x" * LARGE, 0o444)}
            policy = s._image_file_policy_v1(files)
            policy["payload_file_bytes"] = LARGE
            target = Path(td)/"must-not-start"
            acquired = {"images": {"node": (files, {"file_limit_phases": policy})}}
            with self.assertRaisesRegex(Q.WG.WorkGraphError, "materialization policy differs"):
                s._execute(acquired, {"id": "node"}, {}, target)
            self.assertFalse(target.exists())

    def test_payload_cannot_raise_hard_limit_or_write_beyond_original_limit(self):
        with tempfile.TemporaryDirectory(prefix="dg16-file-limit-") as td:
            result = phase_process([sys.executable, "-I", "-S", "-B", "-c", S.FILE_LIMIT_BOOTSTRAP,
                                    str(PAYLOAD), sys.executable, "-I", "-S", "-B", "-c", PROBE,
                                    str(Path(td)/"payload")], LARGE)
            self.assertEqual(result.returncode, 0, result.stderr)
            row = json.loads(result.stdout)
            self.assertEqual(row["limits"], [8388608, 8388608])
            self.assertFalse(row["raised"])
            self.assertEqual(row["write_error"], errno.EFBIG)
            self.assertLessEqual(row["size"], 8388608)

    def test_failed_reset_never_executes_payload(self):
        with tempfile.TemporaryDirectory(prefix="dg16-file-reset-") as td:
            marker = Path(td)/"executed"
            result = phase_process([sys.executable, "-I", "-S", "-B", "-c", S.FILE_LIMIT_BOOTSTRAP,
                                    str(PAYLOAD), sys.executable, "-I", "-S", "-B", "-c",
                                    "from pathlib import Path;import sys;Path(sys.argv[1]).write_text('executed')",
                                    str(marker)], 1024*1024)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(marker.exists())

    def test_large_input_materializes_before_original_payload_limits(self):
        with tempfile.TemporaryDirectory(prefix="dg16-file-phase-") as td:
            s = self.session()
            policy = s._image_file_policy_v1({"/input": (b"x" * LARGE, 0o444)})
            image = Path(td)/"image"
            # Real kernel copy-before-exec control. Bubblewrap integration is
            # separately required by --native; this does not emulate its result.
            copy_then_exec = "import os,sys; p=sys.argv[1]; f=open(p,'xb'); f.write(b'x'*9437184); f.close(); os.execv(sys.argv[2],sys.argv[2:])"
            result = phase_process([sys.executable, "-I", "-S", "-B", "-c", copy_then_exec, str(image),
                                    sys.executable, "-I", "-S", "-B", "-c", S.FILE_LIMIT_BOOTSTRAP,
                                    str(PAYLOAD), sys.executable, "-I", "-S", "-B", "-c", PROBE,
                                    str(Path(td)/"payload")], policy["materialization_file_bytes"])
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(image.stat().st_size, 9437184)
            row = json.loads(result.stdout)
            self.assertEqual(row["limits"], [8388608, 8388608])
            self.assertFalse(row["raised"])
            self.assertEqual(row["write_error"], errno.EFBIG)


def native_control(destination):
    destination.mkdir(parents=True, exist_ok=False)
    before_descriptors = resource.getrlimit(resource.RLIMIT_NOFILE)
    soft, hard = before_descriptors
    if hard != resource.RLIM_INFINITY and hard < 4096:
        raise ValueError("native file-limit discriminator requires inherited hard NOFILE >=4096")
    if soft != resource.RLIM_INFINITY and soft < 4096:
        resource.setrlimit(resource.RLIMIT_NOFILE, (4096, hard))
    after_descriptors = resource.getrlimit(resource.RLIMIT_NOFILE)
    assert after_descriptors[1] == before_descriptors[1]
    s = object.__new__(S)
    s.environment = dict(S.ENVIRONMENT)
    s.runtime_root = Path("/")
    s.output = destination
    s.dispatch_count = 0
    s.producer = "constructed-file-limit-discriminator"
    files = s._runtime()
    files["/work/large-input"] = (b"x" * LARGE, 0o444)
    files["/work/scripts/run-work-graph-verifier.sh"] = ((REPO/"scripts/run-work-graph-verifier.sh").read_bytes(), 0o555)
    source = "python -c " + shlex.quote(PROBE) + " /tmp/payload-limit-probe"
    source += "\npython -c " + shlex.quote("from pathlib import Path; import hashlib,json,os; b=Path('/work/large-input').read_bytes()\ntry:\n os.open('/work/large-input',os.O_WRONLY); denied=None\nexcept OSError as error:\n denied=error.errno\nprint(json.dumps({'large_bytes':len(b),'large_sha256':hashlib.sha256(b).hexdigest(),'readonly_error':denied}))")
    node = dict(id="FINITE_IMAGE_LIMIT_DISCRIMINATOR", source=source,
                source_sha256=hashlib.sha256(source.encode()).hexdigest())
    manifest, image_digest = s._image(files, {})
    acquired = dict(images={node["id"]: (files,manifest)},
                    state=dict(scope="CONSTRUCTED_EXECUTOR_RESOURCE_PROBE_NO_CAMPAIGN"),
                    acquired=dict(scope=S.SCOPE,inputs={node["id"]:dict(image_digest=image_digest)}))
    result, _retained = s._execute(acquired,node,dict(key="f"*64),destination/"execution")
    raw = (destination/"execution/stdout.log").read_bytes()
    rows = [json.loads(line) for line in raw.splitlines()]
    assert result["exit"] == 0, (result,(destination/"execution/stderr.log").read_bytes())
    assert len(rows)==2 and rows[0]["limits"]==[8388608,8388608] and not rows[0]["raised"]
    assert rows[0]["write_error"]==errno.EFBIG and rows[0]["size"]<=8388608
    assert rows[1]["large_bytes"]==9437184 and rows[1]["large_sha256"]==hashlib.sha256(b"x"*LARGE).hexdigest()
    assert rows[1]["readonly_error"] in (errno.EACCES,errno.EROFS)
    summary=dict(scope="CONSTRUCTED_REAL_EXECUTOR_FILE_LIMIT_DISCRIMINATOR",authority="NONE",result=result,observations=rows,
                 descriptor_before=before_descriptors,descriptor_after=after_descriptors,
                 hard_descriptor_limit_unchanged=True)
    (destination/"SUMMARY.json").write_text(json.dumps(summary,sort_keys=True,indent=2)+"\n")
    print(json.dumps({"status":"PASS_CONSTRUCTED_NATIVE_FILE_LIMIT_DISCRIMINATOR","output":str(destination)}))


if __name__ == "__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--native",type=Path)
    args=parser.parse_args()
    if args.native:
        native_control(args.native.resolve())
    else:
        result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(PhaseControls))
        raise SystemExit(0 if result.wasSuccessful() else 1)
