"""Read the actual completed native event for one previously reserved root call."""
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import time

THREAD = '01a1953f-a15b-7811-aa72-3538ebb03562'
HEADER_SHA = 'e6fba7c217f360f6b6f6d3c11f42052131b89cf0042289e07902347ccf8d0389'
NAMES = {'mcp__codex_apps__github_fetch':'github.fetch',
         'mcp__codex_apps__github_download_workflow_artifact':'github.download_workflow_artifact'}
MAX_BODY = 4*1024**2
MAX_WINDOW = 12*1024**2
REL = 'Users/theis/.codex/sessions/2026/10/31/rollout-2026-10-31T23-55-37-'+THREAD+'.jsonl'
LEDGER = Path(('C:/' if os.name=='nt' else '/mnt/c/')+REL)


def need(test):
    if not test:
        raise ValueError('ROOT_HISTORY_REFUSED')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def open_ledger():
    need(LEDGER.resolve(strict=True)==LEDGER.absolute())
    before=LEDGER.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1)
    fd=os.open(LEDGER,os.O_RDONLY|getattr(os,'O_NOFOLLOW',0)|getattr(os,'O_NONBLOCK',0)|getattr(os,'O_CLOEXEC',0)|getattr(os,'O_BINARY',0))
    stream=os.fdopen(fd,'rb')
    try:
        held=os.fstat(fd)
        need((held.st_dev,held.st_ino)==(before.st_dev,before.st_ino))
        line=stream.readline(131072)
        need(digest(line)==HEADER_SHA and json.loads(line)['payload']['id']==THREAD)
        return stream,(str(held.st_dev),str(held.st_ino))
    except BaseException:
        stream.close()
        raise


def cursor(turn):
    need(type(turn) is str and re.fullmatch('[0-9a-f-]{36}',turn))
    stream,identity=open_ledger()
    with stream:
        stream.seek(0,2);end=stream.tell()
        need(end>0);stream.seek(end-1);need(stream.read(1)==b'\n')
        return dict(thread=THREAD,turn=turn,identity=list(identity),offset=end,header=HEADER_SHA)


def receive(mark,tool,arguments,wire_sha256,wire_bytes,deadline_ms):
    """Return signed-frame-bearing bytes only to the in-memory principal.
    
    The caller has already made one real tool call. Reading an incomplete journal
    append may wait within the existing deadline; this never calls the provider.
    """
    need(mark['thread']==THREAD and mark['header']==HEADER_SHA and tool in NAMES and type(arguments) is dict)
    need(type(mark['offset']) is int and mark['offset']>=0 and type(wire_bytes) is int and 0<wire_bytes<=MAX_BODY)
    need(re.fullmatch('[0-9a-f]{64}',wire_sha256) and type(deadline_ms) is int)
    stream,identity=open_ledger();start=mark['offset'];pos=start
    with stream:
        need(list(identity)==mark['identity'])
        while time.time_ns()//1000000<deadline_ms:
            opened=os.fstat(stream.fileno()); closing=LEDGER.lstat()
            need((str(closing.st_dev),str(closing.st_ino))==identity and opened.st_size>=pos and opened.st_size-start<=MAX_WINDOW)
            stream.seek(pos);found=[]
            while pos<opened.st_size:
                raw=stream.readline(min(opened.st_size-pos,MAX_BODY+1))
                need(len(raw)<=MAX_BODY)
                if not raw.endswith(b'\n'):break
                off=pos;pos+=len(raw); event=json.loads(raw)
                payload=event.get('payload',{});i=payload.get('item') or {}
                if (event.get('type')!='event_msg' or payload.get('type')!='item_completed' or
                    payload.get('thread_id')!=THREAD or payload.get('turn_id')!=mark['turn'] or
                    i.get('type')!='McpToolCall' or i.get('server')!='codex_apps' or
                    i.get('tool')!=NAMES[tool] or i.get('arguments')!=arguments):
                    continue
                need(i.get('status')=='completed' and type(i.get('result')) is dict and type(i.get('id')) is str)
                body=json.dumps(i['result'],separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf8')
                need(len(body)==wire_bytes and digest(body)==wire_sha256)
                found.append((body,raw,dict(offset=off,bytes=len(raw),sha256=digest(raw),tool_call_ref=i['id'],
                                           tool=tool,arguments=arguments,tool_result_sha256=digest(body),history_sha256=digest(raw))))
            need(len(found)<=1)
            if found:
                need(time.time_ns()//1000000<deadline_ms)
                held=os.fstat(stream.fileno());path=LEDGER.lstat()
                need((str(held.st_dev),str(held.st_ino))==identity==(str(path.st_dev),str(path.st_ino)) and held.st_size>=pos)
                return found[0]
            time.sleep(0.05)
    raise ValueError('ACTUAL_HISTORY_UNOBSERVED_NO_REPLAY')
