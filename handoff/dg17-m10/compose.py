"""Compose only an externally authenticated and actually reviewed held template."""
import os
from pathlib import Path
import shutil
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from contract import (FILES, PREFIX, WORKFLOW, HELD, LIVE, decode, need, regular,
                      template_digest, validate_composition, wire)
def compose(candidate, binding_path, root_appointment_sha, destination):
    c=candidate.absolute()
    directory=c/PREFIX
    workflow=regular(c/WORKFLOW,64*1024)
    expected={PREFIX+n for n in FILES}|{WORKFLOW}
    need(c==c.resolve(strict=True) and {p.relative_to(c).as_posix() for p in c.rglob('*') if not p.is_dir()}==expected
         and not any(p.is_symlink() for p in c.rglob('*')),'held candidate population')
    need(workflow.count(HELD.encode())==1 and LIVE.encode() not in workflow,'held workflow expected')
    b=decode(regular(binding_path,1024*1024))
    validate_composition(b,template_digest(directory,workflow),root_appointment_sha)
    # Publish atomically to an absent user-named directory only after all checks.
    destination=destination.absolute()
    need(not os.path.lexists(destination),'composition destination already exists')
    with tempfile.TemporaryDirectory(dir=destination.parent) as temp:
        stage=Path(temp)/'tree'
        shutil.copytree(c,stage)
        (stage/WORKFLOW).write_bytes(workflow.replace(HELD.encode(),LIVE.encode()))
        (stage/PREFIX/'composition.json').write_bytes(wire(b)+b'\n')
        os.rename(stage,destination)
if __name__=='__main__':
    if len(sys.argv)!=5:
        raise SystemExit('usage: compose.py HELD_TREE AUTHENTICATED_BUNDLE ROOT_APPOINTMENT_SHA256 NEW_DESTINATION')
    compose(Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3],Path(sys.argv[4]))
