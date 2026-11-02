#!/usr/bin/env python3
"""Actual resolver CLI controls for one exact package-local child population.

These are topology/selection checks only: no LOAD, model use or native admission.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CHILDREN = ("audit-state", "audit-assess", "audit-implement", "audit-andon")
RESOLVER = ROOT / "skills/implementaudit/scripts/resolve-internal-skill.py"


def main():
    results = []
    with tempfile.TemporaryDirectory(prefix="resolver-custody-") as temporary:
        base = Path(temporary)

        def fixture(name, layout="canonical"):
            skills = base / name / "skills"
            governor = skills / "implementaudit" / "SKILL.md"
            governor.parent.mkdir(parents=True)
            shutil.copyfile(ROOT / "skills/implementaudit/SKILL.md", governor)
            for child in CHILDREN:
                target = (skills / child / "SKILL.md" if layout == "canonical"
                          else governor.parent / "internal-procedures" / (child + ".md"))
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / "skills" / child / "SKILL.md", target)
            return governor

        def check(name, governor, child="audit-state", allowed=False):
            call = subprocess.run([sys.executable, str(RESOLVER), "--governor", str(governor),
                                   "--child", child], capture_output=True, text=True, timeout=5)
            correct = (call.returncode == 0) == allowed
            if allowed:
                selected = Path(call.stdout.strip()) if call.returncode == 0 else None
                correct = correct and selected is not None and selected.read_bytes() == (ROOT / "skills" / child / "SKILL.md").read_bytes()
            results.append({"case": name, "expected": "RESOLVE" if allowed else "REFUSE",
                            "exit": call.returncode, "passed": bool(correct), "stderr": call.stderr.strip()})

        for child in CHILDREN:
            check("canonical-" + child, fixture("canonical-" + child), child, True)
            check("standalone-" + child, fixture("standalone-" + child, "standalone"), child, True)
        governor = fixture("standalone-unrelated", "standalone")
        other = governor.parent.parent / "other-user-skill" / "SKILL.md"
        other.parent.mkdir(); other.write_text("unrelated installed skill\n")
        check("standalone-keeps-unrelated-user-siblings", governor, allowed=True)
        for count in (1, 4):
            governor = fixture("mixed-" + str(count), "standalone")
            for child in CHILDREN[:count]:
                target = governor.parent.parent / child / "SKILL.md"
                target.parent.mkdir(); shutil.copyfile(ROOT / "skills" / child / "SKILL.md", target)
            check("mixed-standalone-canonical-" + str(count), governor)
        for child in ("audit-state", "audit-assess"):
            governor = fixture("linked-" + child)
            original = governor.parent.parent / child
            moved = base / ("foreign-" + child)
            original.rename(moved); original.symlink_to(moved, target_is_directory=True)
            check("linked-atomic-member-" + child, governor)
        governor = fixture("linked-governor")
        original = governor.parent
        foreign = fixture("foreign-governor")
        original.rename(base / "retired-governor")
        original.symlink_to(foreign.parent, target_is_directory=True)
        check("linked-governor-directory", governor)
        governor = fixture("linked-skills")
        original = governor.parent.parent
        moved = base / "alternate" / "skills"
        moved.parent.mkdir(); original.rename(moved); original.symlink_to(moved, target_is_directory=True)
        check("linked-skills-directory", governor)
        for layout in ("canonical", "standalone"):
            for dangling in (False, True):
                governor = fixture("extra-link-" + layout + str(dangling), layout)
                if layout == "canonical":
                    extra = governor.parent.parent / "audit-extra" / "SKILL.md"
                    extra.parent.mkdir()
                else:
                    extra = governor.parent / "internal-procedures" / "audit-extra.md"
                extra.symlink_to(base / "absent-extra" if dangling else governor)
                check("extra-linked-child-" + layout + ("-dangling" if dangling else ""), governor)
        governor = fixture("dangling-alternate")
        (governor.parent / "internal-procedures").symlink_to(base / "absent", target_is_directory=True)
        check("dangling-standalone-alternate", governor)
    failed = [row for row in results if not row["passed"]]
    print(json.dumps({"scope": "PORTABLE_RESOLVER_SELECTION_ONLY", "controls": len(results),
                      "failed": len(failed), "results": results}, sort_keys=True))
    return bool(failed)


if __name__ == "__main__":
    raise SystemExit(main())
