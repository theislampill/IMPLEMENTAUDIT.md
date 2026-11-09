"""One actual public packet readback. Never issues a review or Root decision."""
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import time
import types

ROOT=Path('/home/agent/dg16-g2-current04-public-20261109')
RECEIVER=ROOT/'bound-public-receiver'
LIVE=ROOT/'public-receiving/live'
RECEIVER_SHA='6839ac3a5d2f123711b86d92f93c55a00e7dd4b016ddfee3fbc16b97af0748e0'
WORKFLOW='7f618adc702912f760d87f68fe9c94cc419e844c'

def sha(raw):return hashlib.sha256(raw).hexdigest()
def desc(raw):return dict(bytes=len(raw),sha256=sha(raw))
def acquire(path,limit):
    before=path.lstat()
    assert stat.S_ISREG(before.st_mode) and before.st_nlink==1 and 0<before.st_size<=limit
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
    try:
        held=os.fstat(fd)
        mark=lambda s:(s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_uid,s.st_gid)
        assert stat.S_ISREG(held.st_mode) and mark(before)==mark(held)
        raw=b''
        while len(raw)<=limit:
            part=os.read(fd,min(65536,limit+1-len(raw)))
            if not part:break
            raw+=part
        assert len(raw)==before.st_size and mark(before)==mark(os.fstat(fd))==mark(path.lstat())
        return raw
    finally:os.close(fd)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--run-id',required=True)
    p.add_argument('--archive-sha256',required=True)
    a=p.parse_args()
    assert re.fullmatch('[1-9][0-9]{0,19}',a.run_id) and re.fullmatch('[0-9a-f]{64}',a.archive_sha256)
    assert os.getuid()==1000 and not LIVE.is_symlink() and LIVE.resolve(strict=True)==LIVE
    started=time.time()
    raw=acquire(RECEIVER/'public_receiver.py',65536)
    assert sha(raw)==RECEIVER_SHA
    forbidden={'subprocess.Popen','os.system','os.fork','os.forkpty','os.posix_spawn','socket.__new__','os.kill','os.killpg','ctypes.dlsym','ctypes.call_function','os.mkdir','os.remove','os.rename','os.rmdir','os.chmod','os.chown','os.link','os.symlink','os.truncate','os.utime'}
    def audit(event,args):
        assert event not in forbidden,'REVIEW_FORBIDDEN_EFFECT:'+event
        if event=='open':assert not (isinstance(args[2],int) and args[2]&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND))
        if event=='exec' and args and isinstance(args[0],types.CodeType):assert not args[0].co_filename.startswith(str(ROOT/'source')+'/')
    sys.addaudithook(audit)
    m=types.ModuleType('one_actual_public_live_packet');m.__file__=str(RECEIVER/'public_receiver.py')
    exec(compile(raw,m.__file__,'exec',dont_inherit=True,optimize=0),m.__dict__)
    archive=acquire(LIVE/'ARTIFACT.zip',400000)
    assert sha(archive)==a.archive_sha256
    metadata_raw=acquire(LIVE/'PUBLIC_METADATA.json',262144)
    metadata=m.strict(metadata_raw)
    files=m.decode_zip(archive,'live')
    request=m.strict(files['REQUEST.json']);proof=m.strict(files['PROOF.json'])
    assert request['created_utc_epoch']<=time.time()<request['expires_utc_epoch'] and request['hold_seconds']==300
    observation=m.inspect(files,'live',run_id=a.run_id,workflow_commit=WORKFLOW,metadata=metadata,archive=desc(archive))
    public={name:m.strict(files['public/'+name]) for name in m.NAMES}
    finished=time.time()
    assert request['created_utc_epoch']<=finished<request['expires_utc_epoch']
    print(json.dumps(dict(schema='dg16.one-actual-live-packet.review-readback.v1',reviewer='/root/dg16_bounded_andon',state='REQUIRES_ACTUAL_INDEPENDENT_DECISION',archive=desc(archive),metadata=desc(metadata_raw),request=request,proof=proof,receiving=observation,public=public,started_utc_epoch=started,finished_utc_epoch=finished,elapsed_seconds=finished-started,seconds_remaining=request['expires_utc_epoch']-finished,review_issued=False,root_consumption_issued=False,effect_grant=False),sort_keys=True,indent=2,allow_nan=False))

if __name__=='__main__':main()
