"""Read full frozen research records from one hash-bound local or HTTP tree, with no disk cache."""
import argparse
import hashlib
import io
import json
import zipfile
from pathlib import Path, PurePosixPath
from urllib.parse import quote, urlsplit
from urllib.request import urlopen

def sha(b):
    return hashlib.sha256(b).hexdigest()

def safe(name):
    p=PurePosixPath(name)
    if not name or p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name:
        raise ValueError('unsafe path')
    return p

def pointer(doc, ptr):
    if ptr == '': return doc
    if not ptr.startswith('/'): raise ValueError('JSON pointer must begin with /')
    for part in ptr[1:].split('/'):
        part=part.replace('~1','/').replace('~0','~')
        doc=doc[int(part)] if isinstance(doc,list) else doc[part]
    return doc

class Reader:
    def __init__(self, expected, root=None, base_url=None):
        if bool(root) == bool(base_url): raise ValueError('choose exactly one root or base URL')
        self.root=Path(root).resolve() if root else None
        self.base_url=base_url.rstrip('/')+'/' if base_url else None
        if self.base_url and urlsplit(self.base_url).scheme not in ('http','https'):
            raise ValueError('only HTTP(S) origins accepted')
        data=self.raw('docs/research/PUBLIC_CUSTODY_LOCK.json')
        if sha(data)!=expected: raise ValueError('custody lock digest mismatch')
        lock=json.loads(data)
        if lock.get('schema')!='research-public-custody-lock-v1': raise ValueError('unsupported lock')
        self.files={r['path']:r for r in lock['files']}
        if len(self.files)!=len(lock['files']): raise ValueError('duplicate locked path')
        self.source_lock=self.json('docs/research/genealogy/CORPUS_SOURCE_LOCK.json')

    def raw(self,path):
        safe(path)
        if self.root:
            p=(self.root / path).resolve()
            if not p.is_relative_to(self.root): raise ValueError('path escaped root')
            return p.read_bytes()
        with urlopen(self.base_url+quote(path,safe='/'),timeout=60) as response:
            return response.read()

    def read(self,path):
        row=self.files[path];data=self.raw(path)
        if len(data)!=row['bytes'] or sha(data)!=row['sha256']: raise ValueError('file digest mismatch: '+path)
        return data

    def json(self,path): return json.loads(self.read(path))

    def member(self,packet,member,chain=()):
        data=self.read(packet)
        for name in [*chain,member]:
            safe(name)
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                if z.namelist().count(name)!=1: raise ValueError('missing/duplicate member')
                data=z.read(name)
        return data

    def property(self,key):
        index=self.json('docs/research/genealogy/PROPERTY_MASTER_INDEX.json')
        matches=[r for r in index['properties'] if r['global_property_key']==key]
        if len(matches)!=1: raise ValueError('property key is absent or ambiguous')
        row=matches[0];loc=row['source_locator'];data=self.member(loc['packet_path'],loc['member'])
        if sha(data)!=loc['member_sha256']: raise ValueError('property member digest mismatch')
        if loc['format']=='json':
            record=pointer(json.loads(data),loc['json_pointer'])
            original_id=record.get('PROPERTY_ID',record.get('property_id',record.get('CANONICAL_PROPERTY_ID')))
            if original_id!=row['source_property_id']: raise ValueError('property identity/pointer mismatch')
            b=json.dumps(record,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')
        else:
            record='\n'.join(data.decode('utf-8').splitlines()[loc['line_start']-1:loc['line_end']]);b=record.encode('utf-8')
        if sha(b)!=row['source_row_sha256']: raise ValueError('original property row digest mismatch')
        return {'global_property_key':key,'source_locator':loc,'source_row_sha256':sha(b),'original_record':record,
                'boundary':'Full original source record or exact YAML record segment; navigational projection is not target adoption.'}

    def relation(self,family,identity):
        packets=[r for r in self.source_lock['trifecta_packets'] if r['trifecta']==family]
        if len(packets)!=1: raise ValueError('unknown trifecta')
        p=packets[0];data=self.member(p['packet_path'],p['relations_member']);doc=json.loads(data)
        rows=[(i,r) for i,r in enumerate(doc['relations']) if r.get('relation_id',r.get('id'))==identity]
        if len(rows)!=1: raise ValueError('relation absent or ambiguous')
        ordinal,row=rows[0]
        return {'source_locator':{'packet_path':p['packet_path'],'member':p['relations_member'],'json_pointer':f'/relations/{ordinal}','member_sha256':sha(data)},
                'original_record':row,'ledger_semantics':{k:v for k,v in doc.items() if k!='relations'},
                'boundary':'All original guard/authority/evidence fields retained. Referenced endpoints and profile members remain necessary; no relation adds an execution edge.'}

    def target(self,key):
        path='docs/research/implementaudit/triad-integration/DISPOSITIONS.json';doc=self.json(path)
        rows=[(i,r) for i,r in enumerate(doc['properties']) if r['key']==key]
        if len(rows)!=1: raise ValueError('target key absent or ambiguous')
        i,row=rows[0]
        return {'source_locator':{'path':path,'json_pointer':f'/properties/{i}','sha256':self.files[path]['sha256']},
                'original_target_disposition':row,'status':doc['status'],'proof_limit':doc['proof_limit'],
                'boundary':'Historical target projection; does not supersede the separate corrective audit or canonical successor adjudication.'}

def main():
    p=argparse.ArgumentParser();origin=p.add_mutually_exclusive_group(required=True)
    origin.add_argument('--root',type=Path);origin.add_argument('--base-url')
    p.add_argument('--expected-custody-lock-sha256',required=True)
    action=p.add_mutually_exclusive_group(required=True)
    action.add_argument('--property');action.add_argument('--relation');action.add_argument('--target-property');action.add_argument('--member')
    p.add_argument('--trifecta');p.add_argument('--packet');p.add_argument('--archive-chain',action='append',default=[]);p.add_argument('--json-pointer');p.add_argument('--output',type=Path)
    a=p.parse_args();r=Reader(a.expected_custody_lock_sha256,a.root,a.base_url)
    if a.property: result=r.property(a.property)
    elif a.relation: result=r.relation(a.trifecta,a.relation)
    elif a.target_property: result=r.target(a.target_property)
    else:
        data=r.member(a.packet,a.member,a.archive_chain)
        if a.json_pointer is None:
            if not a.output: raise ValueError('exact member extraction requires explicit --output')
            if a.output.exists(): raise ValueError('refuse to overwrite output')
            a.output.write_bytes(data);print('MEMBER_SHA256='+sha(data));return
        result={'original_record':pointer(json.loads(data),a.json_pointer),'member_sha256':sha(data),'archive_chain':a.archive_chain,'member':a.member,'json_pointer':a.json_pointer}
    text=json.dumps(result,indent=2,ensure_ascii=False)+'\n'
    if a.output:
        if a.output.exists(): raise ValueError('refuse to overwrite output')
        a.output.write_text(text,encoding='utf-8')
    else: print(text,end='')

if __name__=='__main__':
    try: main()
    except (ValueError,KeyError,IndexError,OSError,zipfile.BadZipFile) as exc:
        raise SystemExit('FAIL: '+str(exc))
