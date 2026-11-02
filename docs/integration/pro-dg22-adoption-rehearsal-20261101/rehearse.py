#!/usr/bin/env python3
"""DG22 method-only empirical recipe. Every write stays in a new private directory.

This is an evidence harness, not a product command or live adoption tool. It
requires existing local Git objects and a byte-bound rehearsal commission. It
has no network protocol, real-main mode, package builder, or issue operation.
"""

import argparse
import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

METHOD = "single-parent-exact-tree/non-force-push-with-advertised-old-guard"
TARGET = "refs/heads/rehearsal-main"
DONOR_IDS = [246, 251, 252, 253, 254]
CLOSING = re.compile(
    r"\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+(?:[\w.-]+/[\w.-]+)?#\d+"
    r"|\b(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+https://github\.com/[^\s]+/issues/\d+",
    re.I,
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


class Refusal(Exception):
    pass


class Rehearsal:
    def __init__(self, args):
        self.args = args
        self.root = Path(args.out).resolve()
        if self.root.exists():
            raise Refusal("OUTPUT_ALREADY_EXISTS: preserve the previous attempt")
        self.source = Path(args.source_git).resolve()
        if not self.source.is_dir():
            raise Refusal("SOURCE_OBJECT_POOL_MISSING")
        self.authority = Path(args.authority_file).resolve()
        if digest(self.authority.read_bytes()) != args.authority_sha256:
            raise Refusal("REHEARSAL_AUTHORITY_DIGEST_MISMATCH")
        self.root.mkdir(parents=True)
        (self.root / "raw").mkdir()
        (self.root / "empty-hooks").mkdir()
        (self.root / "DG22_DISPOSABLE_SUBJECT").write_text("METHOD_ONLY\n")
        self.journal = self.root / "commands.jsonl"
        self.repo = self.root / "subject.git"
        self.env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        self.when = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
        self.env.update({
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0", "GIT_ALLOW_PROTOCOL": "file",
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_AUTHOR_NAME": "DG22 Disposable Rehearsal",
            "GIT_AUTHOR_EMAIL": "dg22-rehearsal@example.invalid",
            "GIT_COMMITTER_NAME": "DG22 Disposable Rehearsal",
            "GIT_COMMITTER_EMAIL": "dg22-rehearsal@example.invalid",
            "GIT_AUTHOR_DATE": self.when, "GIT_COMMITTER_DATE": self.when,
        })
        self.rows = []
        self.controls = []
        self.donors = json.loads(Path(args.donors_json).read_text())
        if set(self.donors) != {str(n) for n in DONOR_IDS}:
            raise Refusal("EXACT_FIVE_DONORS_REQUIRED")
        self.subjects = {
            "published": {"commit": args.published, "tree": args.published_tree},
            "engineering": {"commit": args.engineering, "tree": args.engineering_tree},
        }

    def raw(self, value):
        h = digest(value)
        p = self.root / "raw" / (h + ".bin")
        if not p.exists():
            p.write_bytes(value)
        return {"path": str(p.relative_to(self.root)), "sha256": h, "bytes": len(value)}

    def run(self, *args, cwd=None, data=None, check=True, extra_env=None, hooks=None):
        argv = ["git", "-c", "credential.helper=", "-c", "core.hooksPath=" +
                str(hooks or self.root / "empty-hooks"), "-C", str(cwd or self.repo), *args]
        env = dict(self.env)
        env.update(extra_env or {})
        b = data.encode() if isinstance(data, str) else data
        p = subprocess.run(argv, input=b, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)
        row = {"sequence": len(self.rows) + 1, "argv": argv,
               "stdin": self.raw(b) if b is not None else None,
               "returncode": p.returncode, "stdout": self.raw(p.stdout),
               "stderr": self.raw(p.stderr), "extra_env": extra_env or {}}
        self.rows.append(row)
        with self.journal.open("a") as f:
            f.write(json.dumps(row, sort_keys=True) + "\n")
        if check and p.returncode:
            raise Refusal("COMMAND_FAILED: " + json.dumps(row))
        return p

    def text(self, *args, **kw):
        return self.run(*args, **kw).stdout.decode().strip()

    def init(self, repo, objects):
        self.run("init", "--bare", str(repo), cwd=self.root)
        (repo / "objects/info/alternates").write_text(str(objects) + "\n")

    def ref(self, name, value):
        self.run("update-ref", name, value)

    def commit(self, tree, parents, message, ref):
        argv = ["commit-tree", tree]
        for parent in parents:
            argv.extend(["-p", parent])
        result = self.text(*argv, data=message + "\n")
        self.ref(ref, result)
        return result

    def refs(self, repo=None):
        return self.text("for-each-ref", "--format=%(refname) %(objectname)", cwd=repo or self.repo)

    def remote(self, name, old=None):
        remote = self.root / ("remote-" + name + ".git")
        self.init(remote, self.repo / "objects")
        self.run("config", "receive.denyNonFastForwards", "true", cwd=remote)
        self.run("update-ref", TARGET, old or self.args.main, cwd=remote)
        return remote

    def preflight(self, recipe, candidate, remote):
        if remote.resolve().parent != self.root or not remote.name.startswith("remote-"):
            raise Refusal("NOT_OWNED_DISPOSABLE_REMOTE")
        if self.text("remote", cwd=remote) or self.text("remote"):
            raise Refusal("CONFIGURED_REMOTE_ROUTE_PRESENT")
        if recipe.get("scope") != "METHOD_ONLY":
            raise Refusal("NO_LIVE_ADOPTION_MODE")
        if recipe.get("effects") != ["private_ref_update"]:
            raise Refusal("UNAPPROVED_EFFECTS")
        if recipe.get("authority_sha256") != self.args.authority_sha256:
            raise Refusal("MISSING_OR_CHANGED_REHEARSAL_AUTHORITY")
        if digest(self.authority.read_bytes()) != self.args.authority_sha256:
            raise Refusal("CHANGED_AUTHORITY_BYTES")
        if recipe.get("method") != METHOD:
            raise Refusal("AMBIGUOUS_OR_MISMATCHED_METHOD")
        if recipe.get("target_ref") != TARGET or recipe.get("expected_old") != self.args.main:
            raise Refusal("TARGET_OR_EXPECTED_INPUT_MISMATCH")
        s = self.subjects[recipe["role"]]
        if (recipe.get("source_commit"), recipe.get("source_tree")) != (s["commit"], s["tree"]):
            raise Refusal("SOURCE_BINDING_MISMATCH")
        if self.text("rev-parse", s["commit"] + "^{tree}") != s["tree"]:
            raise Refusal("SOURCE_OBJECT_TREE_MISMATCH")
        if self.text("rev-parse", "refs/retained/" + recipe["role"]) != s["commit"]:
            raise Refusal("CHANGED_SOURCE_REF")
        for n, sha in self.donors.items():
            ref = "refs/retained/pr" + n
            p = self.run("rev-parse", "--verify", ref, check=False)
            if p.returncode or p.stdout.decode().strip() != sha:
                raise Refusal("MISSING_OR_CHANGED_DONOR_HISTORY:" + n)
            if self.run("merge-base", "--is-ancestor", sha, ref, check=False).returncode:
                raise Refusal("DONOR_ANCESTRY_UNREACHABLE:" + n)
        if self.text("rev-parse", candidate + "^{tree}") != s["tree"]:
            raise Refusal("WRONG_CANDIDATE_TREE")
        if self.text("show", "-s", "--format=%P", candidate).split() != [self.args.main]:
            raise Refusal("WRONG_PARENT_COUNT_OR_ORDER")
        if self.run("merge-base", "--is-ancestor", self.args.main, candidate, check=False).returncode:
            raise Refusal("NOT_FAST_FORWARD")
        if CLOSING.search(self.text("show", "-s", "--format=%B", candidate)):
            raise Refusal("ISSUE_CLOSING_DIRECTIVE")

    def send(self, name, recipe, candidate, *, old=None, race=None, expected_success=False):
        remote = self.remote(name, old)
        before = self.refs(remote)
        first = len(self.rows) + 1
        refusal = None
        try:
            self.preflight(recipe, candidate, remote)
            hookdir = self.root / ("hooks-" + name)
            hookdir.mkdir()
            values = {"remote": str(remote), "candidate": candidate,
                      "target": TARGET, "old": self.args.main,
                      "trace": str(self.root / (name + "-hook.json")), "race": race}
            hook = "#!/usr/bin/env python3\nimport json,sys,subprocess,os\nV=" + repr(values) + "\n"
            hook += "rows=[x.split() for x in sys.stdin.read().splitlines()]\n"
            hook += "ok=(len(rows)==1 and len(rows[0])==4 and rows[0][1:]==[V['candidate'],V['target'],V['old']] and len(sys.argv)==3 and sys.argv[2]==V['remote'])\n"
            hook += "with open(V['trace'],'w') as f: json.dump({'argv':sys.argv[1:],'advertised':rows,'guard_pass':ok},f)\n"
            hook += "if not ok: print('DG22_EXPECTED_ADVERTISED_HEAD_REFUSED',file=sys.stderr); sys.exit(9)\n"
            if race:
                hook += "e={k:v for k,v in os.environ.items() if k not in ('GIT_DIR','GIT_WORK_TREE','GIT_INDEX_FILE','GIT_COMMON_DIR')}\n"
                hook += "subprocess.run(['git','-C',V['remote'],'update-ref',V['target'],V['race'],V['old']],check=True,env=e)\n"
            path = hookdir / "pre-push"
            path.write_text(hook)
            path.chmod(0o755)
            p = self.run("push", "--porcelain", "--atomic", "--no-follow-tags", "--no-force",
                         "--recurse-submodules=no", str(remote), candidate + ":" + TARGET,
                         hooks=hookdir, check=False)
            rc = p.returncode
            if rc:
                refusal = "NATIVE_GIT_PUSH_REFUSED"
        except Refusal as e:
            rc = 2
            refusal = str(e)
        after = self.refs(remote)
        actual = self.text("rev-parse", TARGET, cwd=remote)
        if expected_success:
            assert rc == 0 and actual == candidate, (name, rc, refusal, actual)
        elif race:
            assert rc != 0 and actual == race, (name, rc, actual)
        else:
            assert rc != 0 and before == after, (name, rc, refusal)
        row = {"control": name, "expected_success": expected_success, "returncode": rc,
               "refusal": refusal, "before_refs": before, "after_refs": after,
               "candidate": candidate, "remote_head": actual,
               "first_command": first, "last_command": len(self.rows),
               "unexpected_ref_effects": False,
               "race_fixture_effect": race, "verdict": "PASS"}
        self.controls.append(row)
        write_json(self.root / (name + "-result.json"), row)
        return row

    def execute(self):
        self.init(self.repo, self.source / "objects")
        self.ref("refs/retained/main", self.args.main)
        for role, s in self.subjects.items():
            assert self.text("rev-parse", s["commit"] + "^{tree}") == s["tree"]
            self.ref("refs/retained/" + role, s["commit"])
        for n, sha in self.donors.items():
            self.text("cat-file", "-e", sha + "^{commit}")
            self.ref("refs/retained/pr" + n, sha)
        self.inputs = self.refs()
        self.input_snapshot = self.refs(self.source)
        write_json(self.root / "inputs.json", {
            "created_utc": self.when, "method": METHOD, "main": self.args.main,
            "subjects": self.subjects, "donors": self.donors, "retained_refs": self.inputs,
            "authority_sha256": self.args.authority_sha256, "common_adoption": None,
            "source_roles_combined": False, "scope": "METHOD_ONLY",
            "git_version": self.text("--version"), "python_version": sys.version,
        })
        candidates = {}
        facts = {}
        for role, s in self.subjects.items():
            c = self.commit(s["tree"], [self.args.main],
                            "DG22 private METHOD_ONLY rehearsal: " + role + "\n\n"
                            "Source snapshot " + s["commit"] + ".\n"
                            "No live adoption, package acceptance, native grant or issue operation.",
                            "refs/rehearsal/candidate/" + role)
            candidates[role] = c
            source_diff = self.run("diff", "--binary", "--full-index", self.args.main, s["commit"]).stdout
            candidate_diff = self.run("diff", "--binary", "--full-index", self.args.main, c).stdout
            assert source_diff == candidate_diff
            assert self.text("rev-list", "--count", self.args.main + ".." + c) == "1"
            matrix = {}
            for n, head in {"source": s["commit"], **self.donors}.items():
                matrix[n] = {"ancestor_of_source": self.run("merge-base", "--is-ancestor", head, s["commit"], check=False).returncode == 0,
                             "ancestor_of_candidate": self.run("merge-base", "--is-ancestor", head, c, check=False).returncode == 0}
            assert not any(x["ancestor_of_candidate"] for x in matrix.values())
            facts[role] = {"source": s, "candidate": c, "parents": [self.args.main],
                           "tree_equal": True, "full_binary_diff_equal": True,
                           "diff": self.raw(source_diff), "new_main_commits": 1,
                           "ancestry": matrix}
        recipe = {"scope": "METHOD_ONLY", "effects": ["private_ref_update"],
                  "authority_sha256": self.args.authority_sha256, "method": METHOD,
                  "target_ref": TARGET, "expected_old": self.args.main, "role": "published",
                  "source_commit": self.args.published, "source_tree": self.args.published_tree}
        self.send("positive-published", recipe, candidates["published"], expected_success=True)
        private_recipe = {**recipe, "role": "engineering", "source_commit": self.args.engineering,
                          "source_tree": self.args.engineering_tree}
        self.send("positive-engineering", private_recipe, candidates["engineering"], expected_success=True)
        older = self.text("rev-parse", self.args.main + "^1")
        self.send("stale-expected-head", recipe, candidates["published"], old=older)
        old_tree = self.text("rev-parse", self.args.main + "^{tree}")
        wrong_tree = self.commit(old_tree, [self.args.main], "DG22 wrong-tree negative fixture",
                                 "refs/rehearsal/negative/wrong-tree")
        self.send("wrong-candidate-tree", recipe, wrong_tree)
        for name, delta in [
            ("wrong-source-tree", {"source_tree": old_tree}),
            ("ambiguous-method", {"method": [METHOD, "ordinary-merge"]}),
            ("mismatched-method", {"method": "ordinary-merge"}),
            ("unapproved-effects", {"effects": ["private_ref_update", "issue_close"]}),
            ("missing-authority", {"authority_sha256": None}),
            ("live-adoption-without-common", {"scope": "LIVE_ADOPTION"}),
            ("wrong-target-ref", {"target_ref": "refs/heads/main"}),
        ]:
            self.send(name, {**recipe, **delta}, candidates["published"])
        donor_ref = "refs/retained/pr246"
        self.run("update-ref", "-d", donor_ref, self.donors["246"])
        self.send("missing-donor-history", recipe, candidates["published"])
        self.ref(donor_ref, self.text("rev-parse", self.donors["246"] + "^1"))
        assert self.run("merge-base", "--is-ancestor", self.donors["246"], donor_ref, check=False).returncode == 1
        self.send("truncated-donor-ancestry", recipe, candidates["published"])
        self.ref(donor_ref, self.donors["246"])
        self.ref("refs/retained/published", self.args.engineering)
        self.send("changed-source-input", recipe, candidates["published"])
        self.ref("refs/retained/published", self.args.published)
        bad_parent = self.commit(self.args.published_tree, [older], "DG22 wrong-parent negative fixture",
                                 "refs/rehearsal/negative/wrong-parent")
        self.send("wrong-parent", recipe, bad_parent)
        reversed_parents = self.commit(self.args.published_tree, [self.args.published, self.args.main],
                                        "DG22 reversed-parent negative fixture",
                                        "refs/rehearsal/negative/reversed-parents")
        self.send("reversed-two-parents", recipe, reversed_parents)
        closing = self.commit(self.args.published_tree, [self.args.main], "Fixes #215",
                               "refs/rehearsal/negative/closing-message")
        self.send("closing-message", recipe, closing)
        self.send("post-advertisement-race", recipe, candidates["published"], race=wrong_tree)
        ordinary = self.root / "ordinary-merge"
        self.run("worktree", "add", "--detach", str(ordinary), self.args.main)
        self.run("merge", "--no-ff", "--no-edit", self.args.published, cwd=ordinary)
        merged = self.text("rev-parse", "HEAD", cwd=ordinary)
        self.ref("refs/rehearsal/ordinary-merge", merged)
        merge_parents = self.text("show", "-s", "--format=%P", merged).split()
        assert merge_parents == [self.args.main, self.args.published]
        assert self.text("rev-parse", merged + "^{tree}") == self.args.published_tree
        assert self.run("merge-base", "--is-ancestor", self.args.published, merged, check=False).returncode == 0
        conflict_path = "skills/implementaudit/SKILL.md"
        assert self.text("diff", "--name-only", self.args.main, self.args.published, "--", conflict_path) == conflict_path
        idx = {"GIT_INDEX_FILE": str(self.root / "conflict.index")}
        self.run("read-tree", self.args.main, extra_env=idx)
        blob = self.text("hash-object", "-w", "--stdin", data="DG22 disposable conflicting-main fixture\n")
        self.run("update-index", "--add", "--cacheinfo", "100644," + blob + "," + conflict_path, extra_env=idx)
        conflict_tree = self.text("write-tree", extra_env=idx)
        conflict_head = self.commit(conflict_tree, [self.args.main], "DG22 private conflict fixture",
                                     "refs/rehearsal/negative/conflicting-main")
        conflict = self.run("merge-tree", "--write-tree", conflict_head, self.args.published, check=False)
        assert conflict.returncode == 1 and b"CONFLICT" in conflict.stdout
        self.send("changed-conflicting-main", recipe, candidates["published"], old=conflict_head)
        assert self.text("for-each-ref", "--format=%(refname) %(objectname)", "refs/retained") == self.inputs
        assert self.refs(self.source) == self.input_snapshot
        self.run("fsck", "--connectivity-only")
        graph = self.run("rev-list", "--parents", "--all").stdout
        (self.root / "history-graph.txt").write_bytes(graph)
        retained = ["refs/retained/main", "refs/retained/published", "refs/retained/engineering"] + ["refs/retained/pr" + str(n) for n in DONOR_IDS]
        result_refs = self.text("for-each-ref", "--format=%(refname)", "refs/rehearsal").splitlines()
        self.run("bundle", "create", str(self.root / "rehearsal-results.bundle"), *result_refs,
                 *("^" + x for x in retained))
        self.run("bundle", "verify", str(self.root / "rehearsal-results.bundle"))
        result = {"schema": "dg22.private-method-rehearsal.v1", "scope": "METHOD_ONLY",
                  "status": "METHOD_CONTROLS_PASS_FINAL_ADOPTION_PENDING", "created_utc": self.when,
                  "method": METHOD, "main": self.args.main, "subjects": facts,
                  "ordinary_merge": {"commit": merged, "tree": self.args.published_tree,
                                     "parents": merge_parents, "source_ancestry_introduced": True},
                  "conflict_control": {"synthetic_main": conflict_head, "returncode": conflict.returncode,
                                       "raw": self.raw(conflict.stdout)},
                  "controls": self.controls, "retained_refs_unchanged": True,
                  "source_pool_refs_unchanged": True, "commands": len(self.rows),
                  "graph_sha256": digest(graph), "common_adoption_receipt": None,
                  "live_effects": 0, "packages_built": 0, "native_episodes": 0,
                  "approval": "NOT_REQUESTABLE_UNTIL_REAL_COMMON_AND_FINAL_SOURCE", "cleanup": {
                      "private_repositories": "retained for independent review and bundle return",
                      "processes": "all synchronous subprocesses reaped", "external_resources": "none"}}
        write_json(self.root / "RESULT.json", result)
        print(json.dumps({"status": result["status"], "controls": len(self.controls),
                          "candidates": candidates, "result": str(self.root / "RESULT.json")}))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ["source-git", "out", "authority-file", "authority-sha256", "main",
                 "published", "published-tree", "engineering", "engineering-tree", "donors-json"]:
        p.add_argument("--" + name, required=True)
    a = p.parse_args()
    Rehearsal(a).execute()


if __name__ == "__main__":
    main()
