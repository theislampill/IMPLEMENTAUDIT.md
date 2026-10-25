#!/usr/bin/env python3
"""Explicit Linux qualification; not a registered canonical verifier family.

Run with system Python and a fresh evidence directory outside the repository:
  /usr/bin/python3 -B tests/work-graph-reuse-cases.py /tmp/r0035-reuse-evidence

This is a successor harness, reconstructed after workspace maintenance. Its
constructed candidate uses the actual byte-pinned checkers, existing compiler,
runner and evidence consumer. It does not qualify an authentic campaign.
All files, failures and Git fixture objects are retained; no cleanup runs.
"""
import copy
import fcntl
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1]).resolve()
OUT.mkdir(parents=True, exist_ok=False)


def load_driver(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


Q = load_driver(ROOT / "scripts/qualify-work-graph-verifier.py", "qualified_driver")
S = Q.VerifierTaskSession
rows = []
ENV = dict(PATH="/usr/bin:/bin", LANG="C", LC_ALL="C", TZ="UTC",
           GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null",
           GIT_AUTHOR_NAME="R0035 constructed fixture", GIT_AUTHOR_EMAIL="r0035@example.invalid",
           GIT_COMMITTER_NAME="R0035 constructed fixture", GIT_COMMITTER_EMAIL="r0035@example.invalid",
           GIT_AUTHOR_DATE="2026-10-17T00:00:00Z", GIT_COMMITTER_DATE="2026-10-17T00:00:00Z")


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    data = value if isinstance(value, bytes) else Q.WG.canonical_json_v1(value) + b"\n"
    with path.open("xb") as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


def record(control, **values):
    # A later mutation of a returned result must never change an earlier row.
    row = copy.deepcopy(dict(control=control, classification="CONSTRUCTED_REAL_CHECKER_SCOPE", **values))
    rows.append(row)
    with (OUT / "controls.jsonl").open("ab") as stream:
        stream.write(Q.WG.canonical_json_v1(row) + b"\n")
        stream.flush()
        os.fsync(stream.fileno())
    print("control %02d: %s" % (len(rows), control), flush=True)


def command(argv, cwd):
    completed = subprocess.run(argv, cwd=cwd, env=ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode:
        raise AssertionError((argv, completed.returncode, completed.stdout, completed.stderr))
    return completed.stdout


def git(*args):
    return command(["/usr/bin/git", *args], source)


source = OUT / "source"
source.mkdir()
names = ("README.md", "AGENTS.md", "scripts/verify-package.sh",
         "scripts/check-readme-toc.sh", "scripts/check-agents-bootstrap-budget.sh",
         "docs/audits/RETENTION.md", "tests/agents-bootstrap-budget.test.sh")
for name in names:
    target = source / name
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(ROOT / name, target)
git("init", "--quiet")
git("add", "--", *names)
git("commit", "--quiet", "-m", "Constructed R0035 checker inputs from candidate")
write(OUT / "harness.json", dict(schema="r0035.reuse-successor-harness.v1", harness_sha256=Q.sha(Path(__file__).read_bytes()),
      command=[sys.executable, "-B", str(Path(__file__).resolve()), str(OUT)], engine=Q.sha(Q.LOADED_DRIVER),
      compiler=Q.sha(Q.LOADED_COMPILER), runner=Q.sha((ROOT / S.ENGINE_PATHS[1]).read_bytes()),
      fixture_head=git("rev-parse", "HEAD").decode().strip(), source_files={n: Q.sha((source / n).read_bytes()) for n in names},
      historical_harness="MISSING_NOT_RECONSTRUCTED_AS_IDENTICAL", canonical_acceptance="UNQUALIFIED", authority="NONE"))
write(OUT / "harness.py", Path(__file__).read_bytes())
session = S(source, OUT / "consumer")


def run_case(label, expected, code=0, current=session):
    before = current.dispatch_count
    result = current.run()
    assert [n["disposition"] for n in result["nodes"]] == expected, (label, result)
    assert result["exit"] == code, (label, result)
    assert current.dispatch_count - before == expected.count("EXECUTED"), (label, result)
    directory = current.output / ("generation-%06d" % result["generation"])
    durable = json.loads((directory / "result.json").read_bytes())
    assert result == durable
    assert int((directory / "exit-code.txt").read_text()) == code
    for stream in ("stdout", "stderr"):
        assert (directory / (stream + ".log")).read_bytes() == b"".join(
            (Path(n["evidence_directory"]) / (stream + ".log")).read_bytes() for n in result["nodes"])
    record(label, result=result, dispatch_delta=current.dispatch_count - before,
           raw_stdout_sha256=Q.sha((directory / "stdout.log").read_bytes()),
           raw_stderr_sha256=Q.sha((directory / "stderr.log").read_bytes()))
    return result


def refuse(label, action, contains, current=session):
    before = current.dispatch_count
    try:
        action()
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        assert contains in str(exc), (label, type(exc).__name__, str(exc))
        assert current.dispatch_count == before
        record(label, error=type(exc).__name__, detail=str(exc), dispatch_delta=0)
    else:
        raise AssertionError("expected refusal: " + label)


EE, RR, ER, RE = ["EXECUTED"] * 2, ["REUSED"] * 2, ["EXECUTED", "REUSED"], ["REUSED", "EXECUTED"]
baseline = run_case("actual baseline", EE)
unchanged = run_case("positive unchanged reuse", RR)
assert [n["receipt_digest"] for n in baseline["nodes"]] == [n["receipt_digest"] for n in unchanged["nodes"]]
readme, agents = source / "README.md", source / "AGENTS.md"
readme_original, agents_original = readme.read_bytes(), agents.read_bytes()
readme.write_bytes(readme_original + b"\n<!-- R0035 finite README revision -->\n")
changed = run_case("README-only invalidation preserves AGENTS receipt", ER)
assert changed["nodes"][1]["receipt_digest"] == unchanged["nodes"][1]["receipt_digest"]
agents.write_bytes(agents_original + b"\n<!-- R0035 finite AGENTS revision -->\n")
run_case("AGENTS-only invalidation preserves README receipt", RE)
readme.write_bytes(readme_original + b"\n## R0035 intentionally unlisted section\n")
failed = run_case("changed meaningful README output is a real failure", ER, 1)
assert b"README sections missing from ToC: r0035-intentionally-unlisted-section" in (
    Path(failed["nodes"][0]["evidence_directory"]) / "stderr.log").read_bytes()
run_case("failed result is never reused", ER, 1)
readme.write_bytes(readme_original)
run_case("restored README requires fresh successful execution", ER)
probe = source / "docs/audits/RETENTION.md"
probe_original = probe.read_bytes()
probe.write_bytes(b"Changed content; exact checker observes only is_file.\n")
run_case("existence-only dependency content preserves qualified results", RR)
probe.unlink()
missing = run_case("missing existence dependency reruns affected checker", RE, 1)
assert (Path(missing["nodes"][1]["evidence_directory"]) / "stderr.log").read_bytes() == b"missing referenced file: docs/audits/RETENTION.md\n"
probe.write_bytes(probe_original)
returned = run_case("restored existence dependency", RE)
returned["nodes"][0]["exit"] = 93
assert rows[-1]["result"]["nodes"][0]["exit"] == 0
run_case("returned-result mutation cannot alter custody or prior report rows", RR)

# Actual evidence consumer rejects changed/missing durable outputs before reuse.
for operation in ("tamper", "remove"):
    for name in ("stdout.log", "stderr.log", "exit-code.txt", "receipt.json", "image.json", "dispatch.json"):
        prior = rows[-1]["result"]
        path = Path(prior["nodes"][0]["evidence_directory"]) / name
        data = path.read_bytes()
        witness = OUT / "mutation-witnesses" / ("%02d-%s-%s.original" % (len(rows) + 1, operation, name))
        write(witness, data)
        if operation == "tamper":
            path.write_bytes(data + b"\nR0035 controlled evidence mutation\n")
        else:
            path.unlink()
        result = run_case(operation + " " + name + " rejects cached README", ER)
        assert result["refused_cached_outputs"]

prior = rows[-1]["result"]
image = json.loads((Path(prior["nodes"][0]["evidence_directory"]) / "image.json").read_bytes())
digest = next(m["sha256"] for m in image["files"] if m["path"] == "/work/README.md")
obj = session.output / "objects" / digest
object_bytes = obj.read_bytes()
write(OUT / "mutation-witnesses" / "README-object.original", object_bytes)
obj.unlink()
run_case("missing input object is rejected before acquisition recreates it", ER)
obj.chmod(0o600)
obj.write_bytes(b"corrupted retained execution input\n")
refuse("corrupted retained input object refuses acquisition", session.run, "retained object changed")
obj.write_bytes(object_bytes)
obj.chmod(0o400)
run_case("owner-restored input object still requires new execution", ER)

registry = source / "scripts/verify-package.sh"
registry_original = registry.read_bytes()
registry.write_bytes(registry_original + b"\n# R0035 constructed registry revision\n")
refuse("unsupported registry tail refuses both", session.run, "unknown tail command")
registry.write_bytes(registry_original.replace(b"set -euo pipefail\n", b"set -euo pipefail\n# R0035 constructed registry revision\n", 1))
run_case("changed registry invalidates both", EE)
registry.write_bytes(registry_original)
run_case("restored registry invalidates both current receipts", EE)
guard = source / "source-guard.txt"
guard.write_bytes(b"first tracked source guard\n")
git("add", "source-guard.txt")
run_case("changed tracked population invalidates both", EE)
guard.write_bytes(b"revised unprojected tracked source\n")
run_case("changed unprojected source invalidates both", EE)
session.environment["BASH_ENV"] = "/not-admitted"
refuse("unsupported environment refuses reuse and execution", session.run, "environment changed")
session.environment = dict(S.ENVIRONMENT)
checker = source / "scripts/check-readme-toc.sh"
checker_bytes = checker.read_bytes()
checker.write_bytes(checker_bytes + b"\n# changed command implementation\n")
refuse("changed checker contract refuses execution", session.run, "contract")
checker.write_bytes(checker_bytes)

# Same retained bytes in a different host location are the same finite image.
runtime = OUT / "captured-runtime"
for name, (data, mode) in session._runtime().items():
    path = runtime / name.lstrip("/")
    write(path, data)
    path.chmod(mode)
session.runtime_root = runtime
run_case("same captured runtime bytes preserve both", RR)
runtime_member = runtime / "usr/lib/python3.12/antigravity.py"
runtime_member.chmod(0o644)
runtime_member.write_bytes(runtime_member.read_bytes() + b"\n# finite runtime revision\n")
run_case("changed runtime bytes invalidate both", EE)
parent = source / "docs"
original_mode = parent.stat().st_mode & 0o7777
parent.chmod(0o700)
run_case("changed source directory metadata invalidates both", EE)
parent.chmod(original_mode)
run_case("restored source directory metadata invalidates current receipts", EE)
readme.unlink()
readme.symlink_to(ROOT / "README.md")
refuse("source symlink refuses acquisition", session.run, "")
readme.unlink()
readme.write_bytes(readme_original)

foreign = S(source, OUT / "foreign-session", runtime_root=runtime)
shutil.copytree(session.output / "objects", foreign.output / "objects")
shutil.copytree(session.output / "generation-000001", foreign.output / "copied-prior-generation")
run_case("copied prior files give a fresh producer no receipt custody", EE, current=foreign)

# Expire real producer timestamps after the initial plan. The scheduling hook
# delays a boundary; it never supplies receipt fields or a claimed clock value.
expiry = S(source, OUT / "expiry-session", runtime_root=runtime, max_age=5)
run_case("expiry control baseline", EE, current=expiry)
acquire = expiry._acquire
observations = []
calls = 0
def delayed_acquire():
    global calls
    calls += 1
    if calls == 2:
        now = time.monotonic()
        recorded = {k: v["observed_at"] for k, v in expiry._issued.items()}
        delay = max(v + expiry.max_age - now for v in recorded.values()) + 0.05
        if delay > 0:
            time.sleep(delay)
        observations.append(dict(before_monotonic=repr(now), after_monotonic=repr(time.monotonic()),
                                 producer_observed_at={k: repr(v) for k, v in recorded.items()},
                                 delay_seconds=repr(max(0, delay))))
    return acquire()
expiry._acquire = delayed_acquire
expired = run_case("actual expiry after initial plan forces refreshed execution", EE, current=expiry)
write(OUT / "expiry-scheduling.json", observations)
initial = json.loads((expiry.output / ("generation-%06d" % expired["generation"]) / "plan.json").read_bytes())
assert [n["decision"] for n in initial["nodes"]] == ["CONSUME_PRIOR_SUCCESS"] * 2

# A scheduled host mutation cannot change mounted retained bytes, and the
# actual consumer must reject the changed post-execution candidate.
scheduled = S(source, OUT / "scheduled-change-session", runtime_root=runtime)
execute = scheduled._execute
def mutate_after_snapshot(acquired, node, decision, directory):
    readme.write_bytes(readme_original + b"\n## R0035 concurrent unlisted section\n")
    return execute(acquired, node, decision, directory)
scheduled._execute = mutate_after_snapshot
try:
    scheduled.run()
except Q.WG.WorkGraphError as exc:
    assert "during-consumption" in str(exc)
    directory = scheduled.output / "generation-000001"
    assert (directory / "node-00/exit-code.txt").read_bytes() == b"0\n"
    assert (directory / "node-00/stdout.log").read_bytes() == b"check-readme-toc: ok\n"
    assert (directory / "during-consumption-00-currentness-refusal.json").is_file()
    assert not scheduled._issued
    record("retained bytes execute while changed current source is refused", detail=str(exc), dispatch_count=scheduled.dispatch_count)
else:
    raise AssertionError("concurrent source change admitted")
readme.write_bytes(readme_original)

post = S(source, OUT / "postprocessing-session", runtime_root=runtime)
acquired = post._acquire()
plan = Q.WG.compile_verifier_reuse_v1(acquired["graph"], acquired["registry"], acquired["acquired"], {})
decision = plan["nodes"][0]
node = next(n for n in acquired["graph"]["nodes"] if n["id"] == decision["node"])
def recording_failure(data):
    raise Q.WG.WorkGraphError("constructed post-exit recording failure")
post._object = recording_failure
try:
    post._execute(acquired, node, decision, post.output / "actual-leaf")
except Q.WG.WorkGraphError as exc:
    assert "post-exit" in str(exc)
    assert (post.output / "actual-leaf/exit-code.txt").read_bytes() == b"0\n"
    assert not (post.output / "actual-leaf/receipt.json").exists()
    assert not post._issued
    record("actual exit survives later receipt recording failure", execution_scope="LOW_LEVEL_ACTUAL_CHECKER_CONTROL", detail=str(exc), dispatch_count=post.dispatch_count)
else:
    raise AssertionError("recording-failure control did not fail")

empty = OUT / "empty-runtime"
empty.mkdir()
unsupported = S(source, OUT / "unsupported-runtime-session", runtime_root=empty)
refuse("missing runtime refuses acquisition without success", unsupported.run, "", current=unsupported)
for which in ("scripts/qualify-work-graph-verifier.py", "skills/implementaudit/scripts/compile-work-graph.py"):
    engine = OUT / ("loaded-engine-" + Path(which).stem)
    for name in S.ENGINE_PATHS:
        write(engine / name, (ROOT / name).read_bytes())
    module = load_driver(engine / S.ENGINE_PATHS[0], "engine_" + Path(which).stem.replace("-", "_"))
    changed_path = engine / which
    changed_path.write_bytes(changed_path.read_bytes() + b"\n# Revision after module loading\n")
    refuse("loaded engine drift refuses " + which,
           lambda m=module, p=engine: m.VerifierTaskSession(source, p / "refused-session"), "loaded producer code")

fork_path = OUT / "fork-refusal.json"
pid = os.fork()
if pid == 0:
    try:
        session.run()
    except Q.WG.WorkGraphError as exc:
        write(fork_path, dict(detail=str(exc), inherited_producer_pid=session.producer_pid, actual_pid=os.getpid()))
        os._exit(0 if "producer process changed" in str(exc) else 1)
    os._exit(2)
_, status = os.waitpid(pid, 0)
assert os.waitstatus_to_exitcode(status) == 0
record("forked process cannot inherit live receipt custody", witness=json.loads(fork_path.read_bytes()))

# Finite executor-profile discriminator. It is deliberately outside the two
# checker contracts, never passed to the compiler or admitted to consumer reuse.
namespace = S(source, OUT / "namespace-control", runtime_root=runtime)
probe_source = r'''#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <sched.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/resource.h>
#include <sys/statvfs.h>
#include <sys/syscall.h>
#include <sys/wait.h>
#include <unistd.h>
int main(int argc, char **argv) {
  int bad=0, fd, leaked=0; long value; struct rlimit limit; struct statvfs fs;
#define CHECK(name, condition) do { int ok=(condition); printf("%s: %s\n",name,ok?"PASS":"FAIL"); if(!ok) bad++; } while(0)
  errno=0; value=syscall(SYS_unshare,0); CHECK("unshare denied",value==-1 && errno==EPERM);
  errno=0; value=syscall(SYS_setns,-1,0); CHECK("setns denied",value==-1 && errno==EPERM);
  errno=0; value=syscall(SYS_clone3,0,0); CHECK("clone3 unavailable",value==-1 && errno==ENOSYS);
  errno=0; value=syscall(SYS_clone,CLONE_NEWUSER|SIGCHLD,0,0,0,0);
  if(value==0) _exit(97); if(value>0) waitpid(value,0,0);
  CHECK("nested user namespace denied",value==-1 && errno==EPERM);
  for(fd=3;fd<4096;fd++) if(fcntl(fd,F_GETFD)!=-1) leaked++;
  CHECK("no inherited input descriptors",leaked==0);
  getrlimit(RLIMIT_NOFILE,&limit); CHECK("descriptor limit",limit.rlim_cur==4096 && limit.rlim_max==4096);
  errno=0; fd=open(argv[1],O_RDONLY); CHECK("host sentinel absent",fd==-1 && errno==ENOENT); if(fd>=0) close(fd);
  errno=0; fd=open("/proc/self/status",O_RDONLY); CHECK("host proc absent",fd==-1 && errno==ENOENT); if(fd>=0) close(fd);
  CHECK("read-only mount flag",statvfs("/work/README.md",&fs)==0 && (fs.f_flag & ST_RDONLY));
  errno=0; fd=open("/work/README.md",O_WRONLY); printf("candidate write-open: fd=%d errno=%d\n",fd,errno);
  CHECK("candidate write denied",fd==-1 && (errno==EROFS || errno==EACCES)); if(fd>=0) close(fd);
  fd=open("/tmp/r0035-scratch",O_CREAT|O_WRONLY,0600); CHECK("fresh scratch writable",fd>=0 && write(fd,"x",1)==1); if(fd>=0) close(fd);
  CHECK("ambient startup absent",getenv("BASH_ENV")==0 && getenv("PYTHONPATH")==0);
  return bad?1:0;
}
'''
write(namespace.output / "probe.c", probe_source.encode())
built = subprocess.run(["/usr/bin/cc", "-O2", "-o", str(namespace.output / "probe"), str(namespace.output / "probe.c")], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
write(namespace.output / "build.stdout", built.stdout)
write(namespace.output / "build.stderr", built.stderr)
write(namespace.output / "build.exit", (str(built.returncode) + "\n").encode())
assert built.returncode == 0
sentinel = OUT / "host-sentinel"
write(sentinel, b"Must remain absent from finite image.\n")
acquired = namespace._acquire()
files = dict(acquired["images"]["COMMAND:scripts/check-readme-toc.sh:0"][0])
files["/work/probe"] = ((namespace.output / "probe").read_bytes(), 0o555)
manifest, image_digest = namespace._image(files, {})
node = dict(id="CONSTRUCTED:NAMESPACE", source="/work/probe " + str(sentinel) + "\n")
node["source_sha256"] = Q.sha(node["source"].encode())
acquired["acquired"]["scope"] = "CONSTRUCTED_EXECUTOR_PROFILE_ONLY"
acquired["acquired"]["inputs"][node["id"]] = dict(image_digest=image_digest)
acquired["images"][node["id"]] = (files, manifest)
sealed = namespace._sealed
seals = []
def observed_seal(data):
    fd = sealed(data)
    seals.append(dict(sha256=Q.sha(data), actual_seals=fcntl.fcntl(fd, fcntl.F_GET_SEALS)))
    return fd
namespace._sealed = observed_seal
result, retained = namespace._execute(acquired, node, dict(key=Q.sha(b"constructed namespace discriminator")), namespace.output / "execution")
assert result["exit"] == 0
required_seals = fcntl.F_SEAL_WRITE | fcntl.F_SEAL_GROW | fcntl.F_SEAL_SHRINK | fcntl.F_SEAL_SEAL
assert seals and all(x["actual_seals"] & required_seals == required_seals for x in seals)
assert not namespace._issued
write(namespace.output / "actual-memfd-seals.json", seals)
record("namespace and descriptor controls execute with independently observed read-only flag", execution_scope="CONSTRUCTED_EXECUTOR_PROFILE_ONLY", result=result)

# A real child pre-exec limit failure must not invent a checker start or exit.
resource_dir = OUT / "resource-control"
resource_dir.mkdir()
pid = os.fork()
if pid == 0:
    try:
        limited = S(source, resource_dir / "consumer", runtime_root=runtime)
        resource.setrlimit(resource.RLIMIT_NOFILE, (1024, 1024))
        try:
            limited.run()
        except subprocess.SubprocessError as exc:
            launch = json.loads((limited.output / "generation-000001/node-00/launch-error.json").read_bytes())
            assert launch["launch_phase"] == "POPEN_DID_NOT_RETURN"
            assert launch["checker_started"] == launch["actual_exit"] == "UNOBSERVED"
            assert not (limited.output / "generation-000001/node-00/exit-code.txt").exists()
            assert limited.dispatch_count == 0 and not limited._issued
            write(resource_dir / "refusal.json", dict(detail=str(exc), launch=launch, successful_popen_count=limited.dispatch_count))
            os._exit(0)
        os._exit(2)
    except BaseException as exc:
        write(resource_dir / "harness-error.txt", repr(exc).encode())
        os._exit(3)
_, status = os.waitpid(pid, 0)
assert os.waitstatus_to_exitcode(status) == 0, status
record("unsupported inherited resource limit has no invented checker start or exit", witness=json.loads((resource_dir / "refusal.json").read_bytes()))

git("bundle", "create", str(OUT / "fixture.bundle"), "--all")
write(OUT / "qualification.json", rows)
write(OUT / "summary.json", dict(schema="r0035.reuse-successor-summary.v1", controls=len(rows),
      all_assertions_reached=True, classification="CONSTRUCTED_REAL_CHECKER_AND_EXECUTOR_CONTROLS",
      historical_discrepancy="PRESERVED_IN_ORIGINAL_BUNDLES", canonical_acceptance="UNQUALIFIED", authority="NONE"))
print("work-graph actual-consumer controls: %d passed (constructed scope)" % len(rows), flush=True)
