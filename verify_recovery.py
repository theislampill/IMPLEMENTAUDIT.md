#!/usr/bin/env python3
"""Verify an owner-pinned DG16 recovery ZIP; optionally recover into a NEW directory."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile

def need(value, message):
    if not value:
        raise ValueError(message)

def sha_file(path):
    with path.open('rb') as stream:
        digest = hashlib.sha256()
        for block in iter(lambda:stream.read(1024*1024), b''):
            digest.update(block)
        return digest.hexdigest()

def safe_name(name):
    pieces = name.split('/')
    need(name and not name.startswith('/') and '\\' not in name and ':' not in name and '\x00' not in name,
         'unsafe member path')
    for part in pieces:
        need(part not in ('','.','..') and not part.endswith((' ','.')) and all(ord(c)>=32 for c in part),
             'unsafe path component')
        need(not re.fullmatch(r'(?i)(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\..*)?',part),'device name')
    return PurePosixPath(name)

def verify(archive, expected, destination=None):
    archive=archive.resolve(strict=True)
    digest=sha_file(archive)
    need(re.fullmatch('[0-9a-f]{64}',expected.lower()) and digest==expected.lower(),'archive SHA-256 differs')
    with zipfile.ZipFile(archive) as src:
        entries=src.infolist()
        need(1<len(entries)<=30000 and sum(i.file_size for i in entries)<=640*1024**2,'archive bounds')
        names=[i.filename for i in entries]
        need(len(set(n.casefold() for n in names))==len(names),'duplicate or case-colliding names')
        for i in entries:
            safe_name(i.filename)
            need(stat.S_ISREG(i.external_attr>>16) and not i.is_dir() and not i.flag_bits&1,'unexpected member type or encryption')
        manifest=json.loads(src.read('MANIFEST.json'))
        rows={r['path']:r for r in manifest['files']}
        need(len(rows)==len(manifest['files']) and set(names)==set(rows)|{'MANIFEST.json'},'manifest population differs')
        need(manifest['files_count']==len(rows) and manifest['payload_bytes']==sum(r['bytes'] for r in rows.values()),'manifest totals differ')
        for i in entries:
            raw=src.read(i)
            mode=stat.S_IMODE(i.external_attr>>16)
            if i.filename=='MANIFEST.json':
                need(mode==0o644,'manifest mode')
                continue
            row=rows[i.filename]
            need(len(raw)==i.file_size==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256']
                 and format(mode,'04o')==row['mode'],'member mismatch: '+i.filename)
        if destination is not None:
            destination=destination.absolute()
            need(not os.path.lexists(destination) and destination.parent.is_dir(),'extraction requires a fresh destination')
            destination.mkdir(mode=0o700)
            for i in entries:
                path=destination.joinpath(*safe_name(i.filename).parts)
                path.parent.mkdir(parents=True,exist_ok=True)
                with path.open('xb') as out:out.write(src.read(i))
                if os.name=='posix':path.chmod(stat.S_IMODE(i.external_attr>>16))
                need(sha_file(path)==hashlib.sha256(src.read(i)).hexdigest(),'disk readback mismatch')
    return dict(archive_sha256=digest,archive_bytes=archive.stat().st_size,members=len(entries),
                manifest_payloads=len(rows),payload_bytes=manifest['payload_bytes'],extracted=str(destination) if destination else None)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('archive',type=Path)
    p.add_argument('--sha256',required=True);p.add_argument('--extract-to',type=Path);a=p.parse_args()
    print(json.dumps(verify(a.archive,a.sha256,a.extract_to),indent=2))
