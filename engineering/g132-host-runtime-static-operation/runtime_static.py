"""Bounded selected-public-runtime observation and receiving. Never load a subject.

The caller owns source/context/process custody. This module opens only the
source-selected data surface through a supplied root directory. A test root is
an ordinary fresh fixture; the production adapter passes '/'. No command,
subject import, provider allocation, cache adoption or original gate exists.
"""
from collections import defaultdict
import copy
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import stat
import struct
from zipfile import ZipFile

SCHEMA = 'g132.selected-public-static-observation.v1'
COMPACT_SCHEMA = 'g132.selected-public-static-observation.v2'
DERIVED_SECTIONS = ('expected_provider', 'layout', 'cache', 'graph', 'pin_comparisons', 'counters')
LIMITS = dict(entries=4096, depth=40, links=64, file_bytes=32*1024**2,
              total_bytes=128*1024**2, unique_bytes=128*1024**2,
              mounted_bytes=128*1024**2, read_bytes=256*1024**2,
              edges=4096, report_bytes=2*1024**2, program_headers=256,
              dynamic_records=4096, section_headers=4096, symbols=65536,
              version_records=4096)
SKIPS = ['dist-packages', 'site-packages', 'sitecustomize.py']
TOKEN = re.compile(r'[A-Za-z0-9_+.,@%:=~\-]{1,255}\Z')
NAME = re.compile(r'[A-Za-z0-9_+.\-]{1,255}\Z')
PYNAME = re.compile(r'(?:_?Py)[A-Za-z0-9_]{0,253}\Z')
PRIVATE = ('/etc/passwd','/etc/group','/etc/shadow','/etc/gshadow','/etc/nsswitch.conf')
PROVIDER = '/usr/lib/implementaudit-c5-r5-hosted-python312-05-v1'


class Refusal(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def need(value, code):
    if not value: raise Refusal(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def canonical(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True) + '\n').encode()


def strict_json(raw):
    def unique(pairs):
        result = {}
        for key, value in pairs:
            need(key not in result, 'DUPLICATE_JSON_KEY'); result[key] = value
        return result
    try:
        return json.loads(raw, object_pairs_hook=unique,
                          parse_constant=lambda value: (_ for _ in ()).throw(Refusal('JSON_NONFINITE')))
    except (ValueError, UnicodeError, RecursionError) as error:
        if isinstance(error, Refusal): raise
        raise Refusal('INVALID_JSON') from None


def pin(raw):
    return dict(bytes=len(raw), sha256=sha(raw))


def stamp(info):
    return [str(info.st_dev), str(info.st_ino), info.st_mode, info.st_nlink,
            info.st_size, info.st_uid, info.st_gid, info.st_mtime_ns, info.st_ctime_ns]


def path_token(value):
    return (type(value) is str and value.isascii() and len(value) <= 4096 and value.startswith('/')
            and not value.startswith('//') and (value == '/' or
            all(TOKEN.fullmatch(x) and x not in ('.','..') for x in value[1:].split('/'))))


def elf_public_path(value):
    roots=('/usr/bin','/bin','/usr/lib','/lib','/lib64','/usr/lib64')
    return path_token(value) and any(value==root or value.startswith(root+'/') for root in roots)


def public_path(path, contract, ancestors=False):
    if not path_token(path) or path in PRIVATE: return False
    provider = contract['provider']['root']
    if path == provider or path.startswith(provider + '/'): return False
    roots = ('/usr/bin','/bin','/usr/lib','/lib','/lib64','/usr/lib64',
             '/usr/share/git-core','/etc/alternatives','/etc/python3.12')
    exact = {'/etc/ld.so.cache','/etc/ld.so.preload', *contract.get('public_absences', [])}
    if path in exact or any(path == r or path.startswith(r + '/') for r in roots): return True
    return ancestors and any(r.startswith(path.rstrip('/') + '/') for r in (*roots,*exact))


def bounded_limits(contract):
    result = dict(LIMITS)
    for key, value in contract.get('limits', {}).items():
        need(key in result and type(value) is int and 0 < value <= result[key], 'LIMIT_CONTRACT')
        result[key] = value
    return result


def elf_string(raw, offset, end, pattern=NAME, maximum=255):
    need(0 <= offset < end <= len(raw), 'ELF_STRING_RANGE')
    stop = raw.find(b'\0', offset, min(end, offset+maximum+1))
    need(stop >= offset, 'ELF_STRING_BOUND')
    try: result = raw[offset:stop].decode('ascii')
    except UnicodeError: raise Refusal('ELF_TOKEN') from None
    if pattern is not None: need(pattern.fullmatch(result), 'ELF_TOKEN')
    return result


def parse_elf(raw):
    """ELF64/LSB/x86-64 metadata from already budgeted bytes; no loader query."""
    need(type(raw) is bytes and len(raw) <= LIMITS['file_bytes'], 'ELF_FILE_BOUND')
    def block(off, size):
        need(type(off) is int and type(size) is int and 0 <= off <= len(raw)
             and 0 <= size <= len(raw)-off, 'ELF_RANGE')
        return raw[off:off+size]
    def unpack(fmt, off): return struct.unpack(fmt, block(off, struct.calcsize(fmt)))
    header = unpack('<16sHHIQQQIHHHHHH', 0)
    ident, kind, machine, version, entry, phoff, shoff, flags, ehsize, phsize, phnum, shsize, shnum, shstr = header
    need(ident[:7] == b'\x7fELF\x02\x01\x01' and ident[7] in (0,3) and ident[8] == 0
         and not any(ident[9:]) and kind in (2,3) and machine == 62 and version == 1
         and flags == 0 and ehsize == 64 and phsize == 56 and 0 < phnum <= 256, 'ELF_UNSUPPORTED_HEADER')
    programs = [unpack('<IIQQQQQQ', phoff+i*56) for i in range(phnum)]
    for p in programs:
        block(p[2], p[5]); need(p[5] <= p[6], 'ELF_SEGMENT_SIZE')
    loads = [p for p in programs if p[0] == 1]
    need(loads, 'ELF_LOAD_MAP')
    def mapped(address, size):
        choices = [p[2]+address-p[3] for p in loads if p[3] <= address and address+size <= p[3]+p[5]]
        need(len(choices) == 1, 'ELF_ADDRESS_MAP'); block(choices[0], size); return choices[0]
    result = dict(elf_class=64, endianness='little', machine=62, type=kind,
        program_header_count=phnum, interpreter=None, needed=[], soname=None,
        rpath=[], runpath=[], flags=0, flags_1=0, special_tags=[],
        version_needs={}, version_definitions=[], python_undefined=[], python_defined=[],
        dynamic_tags=[], symbol_table_status='NO_DYNAMIC_SYMBOL_TABLE',
        comparison_scope='VERSION_NODE_AND_PYTHON_DEFINITION_NAMES_ONLY_NO_ABI_OR_LOAD_CLAIM')
    interpreters = [p for p in programs if p[0] == 3]
    need(len(interpreters) <= 1, 'ELF_INTERPRETER_COUNT')
    if interpreters:
        p=interpreters[0]; need(1 < p[5] <= 4096, 'ELF_INTERPRETER_BOUND')
        value=elf_string(raw,p[2],p[2]+p[5],None,4095)
        need(elf_public_path(value) and len(value)+1 == p[5], 'ELF_INTERPRETER_TOKEN')
        result['interpreter']=dict(path=value, file_offset=p[2])
    dynamics = [p for p in programs if p[0] == 2]
    need(len(dynamics) <= 1, 'ELF_DYNAMIC_COUNT')
    if not dynamics: return result
    dynamic=dynamics[0]
    need(dynamic[5] % 16 == 0 and 0 < dynamic[5]//16 <= 4096
         and mapped(dynamic[3],dynamic[5]) == dynamic[2], 'ELF_DYNAMIC_RANGE')
    tags=defaultdict(list)
    for offset in range(dynamic[2],dynamic[2]+dynamic[5],16):
        tag,value=unpack('<qQ',offset)
        if tag == 0: break
        tags[tag].append((value,offset))
    else: raise Refusal('ELF_DYNAMIC_UNTERMINATED')
    result['dynamic_tags']=[dict(tag=tag,count=len(rows)) for tag,rows in sorted(tags.items())]
    def one(tag, required=False):
        values=tags.get(tag,[]); need(len(values) <= 1, 'ELF_DUPLICATE_SINGLETON')
        need(not required or values, 'ELF_MISSING_REQUIRED_TAG')
        return values[0][0] if values else None
    string_size=one(10,True); string_va=one(5,True)
    need(0 < string_size <= len(raw), 'ELF_STRING_TABLE_BOUND')
    string_offset=mapped(string_va,string_size)
    def string(index, pattern=NAME, maximum=255):
        need(type(index) is int and 0 <= index < string_size, 'ELF_STRING_INDEX')
        return elf_string(raw,string_offset+index,string_offset+string_size,pattern,maximum)
    result['string_table']=dict(offset=string_offset,bytes=string_size,sha256=sha(block(string_offset,string_size)))
    result['dynamic_segment']=dict(offset=dynamic[2],bytes=dynamic[5],sha256=sha(block(dynamic[2],dynamic[5])))
    for value,offset in tags.get(1,[]):
        name=string(value,None,4095)
        need(NAME.fullmatch(name) or elf_public_path(name), 'ELF_NEEDED_TOKEN')
        result['needed'].append(dict(name=name,dynamic_entry_file_offset=offset,string_file_offset=string_offset+value))
    if one(14) is not None: result['soname']=string(one(14))
    for tag,key in ((15,'rpath'),(29,'runpath')):
        if one(tag) is not None:
            value=string(one(tag),None,4095)
            # Only source-permitted public path forms survive to the report.
            for item in value.split(':'):
                replaced=item.replace('${ORIGIN}','/ORIGIN').replace('$ORIGIN','/ORIGIN')
                origin=(item.startswith('$ORIGIN') or item.startswith('${ORIGIN}')) and path_token(replaced)
                need(item and (origin or elf_public_path(item)), 'ELF_SEARCH_TOKEN')
            result[key]=value.split(':')
    for tag,key in ((30,'flags'),(0x6ffffffb,'flags_1')):
        if one(tag) is not None: result[key]=one(tag)
    ordinary_tags=set(range(1,38))|{0x6ffffef5,0x6ffffff0,0x6ffffff9,0x6ffffffa,
                                  0x6ffffffb,0x6ffffffc,0x6ffffffd,0x6ffffffe,0x6fffffff}
    for tag in sorted(set(tags)-ordinary_tags):
        for value,offset in tags.get(tag,[]):
            result['special_tags'].append(dict(tag=tag,value=value,file_offset=offset))
    count=one(0x6fffffff); address=one(0x6ffffffe)
    need((count is None) == (address is None), 'ELF_VERNEED_TAG_PAIR')
    total_versions=0
    if count is not None:
        need(0 < count <= 4096, 'ELF_VERSION_BOUND'); seen=set()
        for i in range(count):
            need(address not in seen, 'ELF_VERSION_CYCLE'); seen.add(address)
            v,n,name_index,aux,step=unpack('<HHIII',mapped(address,16))
            name=string(name_index)
            need(v == 1 and 0 < n <= 4096 and name in [x['name'] for x in result['needed']]
                 and name not in result['version_needs'] and aux >= 16, 'ELF_VERNEED_RECORD')
            total_versions += n; need(total_versions <= 4096,'ELF_VERSION_BOUND')
            cursor=address+aux; records=[]; aux_seen=set()
            for j in range(n):
                need(cursor not in aux_seen,'ELF_VERSION_CYCLE');aux_seen.add(cursor)
                _,vflags,index,nameoff,nextref=unpack('<IHHII',mapped(cursor,16))
                need(index & 0x7fff >= 2 and vflags & ~2 == 0,'ELF_VERSION_FLAGS')
                records.append(dict(name=string(nameoff),flags=vflags,index=index,record_file_offset=mapped(cursor,16)))
                need((nextref >= 16) if j+1<n else nextref == 0,'ELF_VERSION_CHAIN')
                cursor += nextref
            result['version_needs'][name]=records
            need((step >= 16) if i+1<count else step == 0,'ELF_VERSION_CHAIN'); address += step
    count=one(0x6ffffffd); address=one(0x6ffffffc)
    need((count is None) == (address is None),'ELF_VERDEF_TAG_PAIR')
    if count is not None:
        need(0 < count <= 4096,'ELF_VERSION_BOUND'); seen=set(); defined=set()
        for i in range(count):
            need(address not in seen,'ELF_VERSION_CYCLE');seen.add(address)
            v,vflags,index,n,_,aux,step=unpack('<HHHHIII',mapped(address,20))
            need(v==1 and 0<n<=4096 and vflags & ~3 == 0 and aux>=20,'ELF_VERDEF_RECORD')
            total_versions += n; need(total_versions <= 4096,'ELF_VERSION_BOUND')
            cursor=address+aux; names=[]; aux_seen=set()
            for j in range(n):
                need(cursor not in aux_seen,'ELF_VERSION_CYCLE');aux_seen.add(cursor)
                nameoff,nextref=unpack('<II',mapped(cursor,8)); names.append(string(nameoff))
                need((nextref >= 8) if j+1<n else nextref==0,'ELF_VERSION_CHAIN');cursor+=nextref
            need(names[0] not in defined,'ELF_DUPLICATE_VERSION');defined.add(names[0])
            result['version_definitions'].append(dict(name=names[0],parents=names[1:],flags=vflags,index=index,record_file_offset=mapped(address,20)))
            need((step>=20) if i+1<count else step==0,'ELF_VERSION_CHAIN');address+=step
    symbol_va=one(6)
    if symbol_va is None: return result
    need(one(11,True)==24,'ELF_SYMBOL_SIZE')
    symbol_offset=mapped(symbol_va,24); symbol_count=None
    # A fully bounded dynamic-symbol section supplies a count. Stripped section
    # tables are supported through DT_HASH or DT_GNU_HASH, never an unbounded scan.
    if shnum:
        need(0<shnum<=4096 and shsize==64 and shoff>0,'ELF_SECTION_BOUND')
        sections=[unpack('<IIQQQQIIQQ',shoff+i*64) for i in range(shnum)]
        dynsym=[s for s in sections if s[1]==11]
        need(len(dynsym)<=1,'ELF_SYMBOL_SECTION_COUNT')
        if dynsym:
            s=dynsym[0]
            need(s[9]==24 and s[5]%24==0 and s[3]==symbol_va and s[4]==symbol_offset
                 and 0<=s[6]<len(sections) and sections[s[6]][4:6]==(string_offset,string_size),'ELF_SYMBOL_SECTION')
            block(s[4],s[5]);symbol_count=s[5]//24
    if one(4) is not None:
        address=one(4); nbucket,nchain=unpack('<II',mapped(address,8))
        need(0<nbucket<=65536 and 0<nchain<=65536,'ELF_HASH_BOUND')
        mapped(address,8+4*(nbucket+nchain))
        need(symbol_count is None or symbol_count==nchain,'ELF_SYMBOL_COUNT_CONFLICT');symbol_count=nchain
    if symbol_count is None and one(0x6ffffef5) is not None:
        address=one(0x6ffffef5); nbuckets,base,bloom,shift=unpack('<IIII',mapped(address,16))
        need(0<nbuckets<=65536 and 0<bloom<=65536 and base<=65536,'ELF_GNU_HASH_BOUND')
        buckets=address+16+8*bloom; mapped(address,16+8*bloom+4*nbuckets)
        highest=base-1
        for i in range(nbuckets):
            index=unpack('<I',mapped(buckets+4*i,4))[0]
            if index==0: continue
            need(base<=index<65536,'ELF_GNU_HASH_INDEX')
            while True:
                need(index<65536,'ELF_SYMBOL_BOUND')
                value=unpack('<I',mapped(buckets+4*nbuckets+4*(index-base),4))[0]
                highest=max(highest,index)
                if value&1: break
                index+=1
        symbol_count=highest+1
    need(symbol_count is not None and 0<symbol_count<=65536,'ELF_SYMBOL_COUNT_UNSUPPORTED')
    mapped(symbol_va,24*symbol_count)
    definitions=set();undefined=set()
    for i in range(symbol_count):
        name_index,info,other,section,value,size=unpack('<IBBHQQ',symbol_offset+24*i)
        need(name_index<string_size,'ELF_SYMBOL_NAME_RANGE')
        # Only Py/_Py names are exported. Other symbol names never enter a report.
        start=string_offset+name_index
        if raw[start:start+2] != b'Py' and raw[start:start+3] != b'_Py': continue
        name=string(name_index,PYNAME)
        if info>>4 in (1,2) and (other&3) in (0,3):
            (undefined if section==0 else definitions).add(name)
    result['python_undefined']=sorted(undefined);result['python_defined']=sorted(definitions)
    result['symbol_table_status']='BOUNDED_DYNAMIC_TABLE'
    result['symbol_count']=symbol_count
    return result


def classify(raw):
    if raw.startswith(b'\x7fELF'):
        return dict(classification='ELF',elf=parse_elf(raw))
    if raw.startswith(b'#!'):
        line=raw[2:258].split(b'\n',1)[0]
        need(len(line)<=255 and b'\x00' not in line,'SCRIPT_HEADER_BOUND')
        try: parts=line.decode('ascii').strip().split(None,1)
        except UnicodeError: raise Refusal('SCRIPT_TOKEN') from None
        need(parts and elf_public_path(parts[0]),'SCRIPT_INTERPRETER_TOKEN')
        argument=parts[1] if len(parts)>1 else None
        if argument is not None:
            need(argument in ('bash','sh','python','python3','python3.12')
                 or re.fullmatch(r'-[A-Za-z0-9]{1,16}',argument),'SCRIPT_ARGUMENT_TOKEN')
        return dict(classification='SCRIPT',interpreter=parts[0],argument=argument)
    return dict(classification='NON_ELF_DATA')


def virtual_resolve(path, links, directory_trace=None):
    need(path_token(path),'LAYOUT_PATH_TOKEN')
    if directory_trace is not None:directory_trace.append('/')
    pending=path[1:].split('/') if path!='/' else []; current=[]; used=[]
    while pending:
        item=pending.pop(0)
        if item in ('','.'): continue
        if item=='..':
            need(current,'LAYOUT_ROOT_ESCAPE');current.pop();continue
        need(TOKEN.fullmatch(item) and len(current)<40,'LAYOUT_DEPTH')
        current.append(item); key='/'+'/'.join(current)
        if key in links:
            need(len(used)<64,'LAYOUT_LINK_BOUND'); used.append(key)
            value=links[key]; current.pop()
            if value.startswith('/'):current=[]
            pending=value.split('/')+pending
        elif directory_trace is not None:directory_trace.append(key)
    return '/'+('/'.join(current)), used


def expected_layer(contract, wheel, observed):
    """Expected provider bytes/pins only; never stat or allocate its real path."""
    spec=contract['provider']; root=spec['root']; files={}; bodies={}
    wanted=contract.get('expected_wheel')
    if wanted is not None:
        need(pin(wheel)=={k:wanted[k] for k in ('bytes','sha256')},'EXPECTED_WHEEL_PIN')
        members={x['name']:x for x in wanted['members']}
        need(len(members)==len(wanted['members'])==12,'EXPECTED_WHEEL_POPULATION')
        with ZipFile(io.BytesIO(wheel)) as archive:
            infos=archive.infolist()
            need(len(infos)==14 and len({x.filename for x in infos})==14,'EXPECTED_WHEEL_POPULATION')
            need(sorted(x.filename for x in infos if x.is_dir())==['zopfli-0.2.3.post1.dist-info/','zopfli/'],'EXPECTED_WHEEL_DIRECTORIES')
            need({x.filename for x in infos if not x.is_dir()}==set(members),'EXPECTED_WHEEL_POPULATION')
            for item in infos:
                need(not item.flag_bits&1,'EXPECTED_WHEEL_ENCRYPTION')
                if item.is_dir():
                    need(item.file_size==0 and stat.S_ISDIR(item.external_attr>>16),'EXPECTED_WHEEL_DIRECTORY');continue
                expected=members[item.filename];mode=item.external_attr>>16
                need(stat.S_ISREG(mode) and stat.S_IMODE(mode)==expected['mode']
                     and item.file_size==expected['bytes']<=LIMITS['file_bytes'],'EXPECTED_WHEEL_MEMBER')
                raw=archive.read(item)
                need(pin(raw)=={k:expected[k] for k in ('bytes','sha256')},'EXPECTED_WHEEL_MEMBER_PIN')
                bodies['lib/python3.12/site-packages/'+item.filename]=raw
    for name,expected in spec['files'].items():
        path=root+'/'+name
        row=dict(evidence='EXPECTED_ONLY',descriptor={k:expected[k] for k in ('bytes','sha256','mode')},
                 classification='EXPECTED_PIN_ONLY',actual_provider_observed=False)
        if name == 'lib/python3.12/site-packages/zopfli-0.2.3.post1.dist-info/RECORD':
            # The genuine installer regenerates this file. Its installed pin
            # is distinct from the authentic wheel member; neither is adopted.
            row['body_basis']='EXPECTED_INSTALLER_TRANSFORMATION_PIN_ONLY'
            row['uninstalled_wheel_member']=pin(bodies[name]) if name in bodies else None
        elif name in bodies:
            need(pin(bodies[name])=={k:expected[k] for k in ('bytes','sha256')},'EXPECTED_PROVIDER_WHEEL_JOIN')
            row.update(classify(bodies[name]));row['body_basis']='PINNED_PUBLIC_WHEEL'
        if name=='bin/python3.12':
            source=observed.get(contract['python_target'])
            row['body_basis']='EXPECTED_COPY_OF_PINNED_SYSTEM_INTERPRETER'
            row['system_copy_pin_matches']=bool(source and source.get('descriptor')==row['descriptor'])
            if row['system_copy_pin_matches']:
                row['classification']=source['classification']
                if 'elf' in source:row['elf']=source['elf']
        files[path]=row
    links={root+'/'+name:target for name,target in {**spec['file_aliases'],**spec['directory_links']}.items()}
    directories={root+('/'+name if name!='.' else ''):dict(evidence='EXPECTED_ONLY',names=names,mode=493)
                 for name,names in spec['directories'].items()}
    return dict(evidence='EXPECTED_ONLY',actual_provider_observed=False,files=files,links=links,directories=directories,
                installation='UNPERFORMED',copy='UNPERFORMED',aliases='EXPECTED_ONLY',native_load='UNPERFORMED')


def population_selection(contract, populations):
    """Rebuild the denominator from full owner-selected directory populations."""
    selected=set(contract['fixed_files'])|set(contract['optional_aliases'])
    pending=[(contract['stdlib_root'],0)]; seen=set()
    while pending:
        path,depth=pending.pop()
        need(path not in seen and depth<=40,'CENSUS_DEPTH_OR_CYCLE');seen.add(path)
        need(path in populations,'CENSUS_DIRECTORY_OMITTED')
        population=populations[path]
        need(population['rule']=='STDLIB_REAL_DIRECTORY','CENSUS_RULE')
        for name,row in population['members'].items():
            need(TOKEN.fullmatch(name) and name not in ('.','..'),'CENSUS_TOKEN')
            if name in SKIPS: continue
            child=path+'/'+name
            if row['kind']=='DIRECTORY':pending.append((child,depth+1))
            elif row['kind'] in ('FILE','SYMLINK'): selected.add(child)
            else:selected.add(child)  # Unsupported members stay in the denominator.
    need({p for p,r in populations.items() if r['rule']=='STDLIB_REAL_DIRECTORY'}==seen,'CENSUS_EXTRA_DIRECTORY')
    need({p for p,r in populations.items() if r['rule']=='EXACT_GIT_DIRECTORY'}==set(contract['git_directories']),
         'GIT_DIRECTORY_COVERAGE')
    return selected


def budget_counts(report, contract):
    # Owner-known expected pins consume the same prospective layout budget
    # before any observed body is read. Parsing the wheel is not needed here.
    expected=report.get('expected_provider')
    if expected is None:
        provider=contract['provider'];root=provider['root']
        expected=dict(files={root+'/'+p:dict(descriptor=r) for p,r in provider['files'].items()},
                      links={**provider['file_aliases'],**provider['directory_links']},
                      directories=provider['directories'])
    objects=report['objects']; unique={}
    canonical_bytes=0
    for path,row in {**objects,**expected['files']}.items():
        descriptor=row['descriptor'];size=descriptor['bytes'];digest=descriptor['sha256']
        need(type(size) is int and 0<=size<=LIMITS['file_bytes'],'FILE_BOUND')
        need(digest not in unique or unique[digest]==size,'DIGEST_LENGTH_CONFLICT')
        unique[digest]=size;canonical_bytes+=size
    expected_files=len(expected['files']);expected_dirs=len(expected['directories']);expected_links=len(expected['links'])
    selection_entries=len(report['selected'])+len(report['populations'])+expected_files+expected_dirs
    topology_entries=len(report['selected'])+len(report['links'])+len(report['directories'])+expected_files+expected_dirs+expected_links
    layout_entries=len(objects)+len(report['links'])+len(report['directories'])+expected_files+expected_dirs+expected_links
    member_entries=sum(len(r['members']) for r in report['populations'].values())
    return dict(selected_spellings=len(report['selected']),canonical_observed_files=len(objects),
                expected_provider_files=expected_files,directory_populations=len(report['populations']),
                topology_links=len(report['links']),topology_directories=len(report['directories']),
                selection_entries=selection_entries,topology_entries=topology_entries,
                layout_entries=layout_entries,population_members=member_entries,
                entries=max(selection_entries,topology_entries,layout_entries,member_entries),
                total_bytes=canonical_bytes,mounted_bytes=canonical_bytes,unique_bytes=sum(unique.values()),
                elf_objects=sum(row.get('classification')=='ELF' for row in objects.values()),
                read_bytes=report.get('read_bytes',0))


class Capture:
    """One opening and one closing census. No retry and no host target search."""
    def __init__(self, root, contract, wheel, retained_cache):
        need(contract.get('schema')=='g132.selected-public-static-contract.v1','CONTRACT_SCHEMA')
        need(contract['skip_names']==SKIPS,'OWNER_SKIP_RULE')
        self.root=Path(root);self.contract=contract;self.wheel=wheel;self.retained_cache=retained_cache
        self.limits=bounded_limits(contract);self.started=False;self.finished=False
        self.rootfd=None;self.read_bytes=0;self.object_anchors={}
        self.report=dict(schema=SCHEMA,authority='NONE',contract_sha256=sha(canonical(contract)),
            selected={},objects={},links={},directories={},populations={},absences={},issues=[],
            observed_provider=False,actual_runtime_constructed=False,cache_pin_adopted=False,
            source_profile_adopted=False,original_awards=0,census_complete=False,
            complete_selected_public_static_surface=False,read_bytes=0,
            evidence_scope='SELECTED_PUBLIC_STATIC_DATA_AND_EXPECTED_PROVIDER_ONLY',
            limits=dict(self.limits))

    def __enter__(self):return self

    def __exit__(self,kind,value,traceback):
        if self.rootfd is not None:
            os.close(self.rootfd);self.rootfd=None
        return False

    def issue(self, code, path=None):
        row=dict(code=code)
        if path is not None:
            if public_path(path,self.contract,True): row['path']=path
            else:row['token_sha256']=sha(str(path).encode())
        if row not in self.report['issues']:
            need(len(self.report['issues'])<4096,'ISSUE_BOUND');self.report['issues'].append(row)

    def _budget(self):
        self.report['read_bytes']=self.read_bytes
        counts=budget_counts(self.report,self.contract)
        for key,code in (('entries','ENTRY_BOUND'),('total_bytes','TOTAL_BOUND'),
                         ('unique_bytes','UNIQUE_BOUND'),('mounted_bytes','MOUNTED_BOUND'),('read_bytes','READ_BOUND')):
            need(counts[key]<=self.limits[key],code)
        return counts

    def _record(self, group, path, row):
        previous=self.report[group].get(path)
        need(previous is None or previous==row,'TOPOLOGY_CHANGED_DURING_OPENING')
        self.report[group][path]=row
        try:self._budget()
        except BaseException:
            if previous is None:del self.report[group][path]
            else:self.report[group][path]=previous
            raise

    def _reserve_object(self, identity, descriptor=None):
        size=identity[4]
        need(type(size) is int and 0<=size<=self.limits['file_bytes'],'FILE_BOUND')
        counts=self._budget()
        for key,code in (('total_bytes','TOTAL_BOUND'),('mounted_bytes','MOUNTED_BOUND')):
            need(counts[key]+size<=self.limits[key],code)
        known={r['descriptor']['sha256'] for r in self.report['objects'].values()}
        known.update(r['sha256'] for r in self.contract['provider']['files'].values())
        extra=0 if descriptor is not None and descriptor['sha256'] in known else size
        need(counts['unique_bytes']+extra<=self.limits['unique_bytes'],'UNIQUE_BOUND')

    def _resolve(self, path, *, opening, directory=False, metadata=False):
        need(public_path(path,self.contract,True),'UNEXPECTED_PUBLIC_TARGET')
        need(path=='/' or len(path.split('/'))-1<=self.limits['depth'],'PATH_DEPTH_BOUND')
        flags=os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC
        rootfd=os.dup(self.rootfd);stack=[rootfd];names=[];pending=path[1:].split('/') if path!='/' else []
        followed=0;trace=dict(links={},directories={}); terminal=None;result=None;returned=False
        def directory_row(fd):return dict(identity=stamp(os.fstat(fd)))
        trace['directories']['/']=directory_row(rootfd)
        try:
            while pending:
                part=pending.pop(0)
                if part in ('','.'):continue
                if part=='..':
                    need(names,'PATH_ROOT_ESCAPE');names.pop();os.close(stack.pop());continue
                need(TOKEN.fullmatch(part) and len(names)<self.limits['depth'],'PATH_TOKEN_OR_DEPTH')
                physical='/'+('/'.join([*names,part]))
                need(public_path(physical,self.contract,True),'UNEXPECTED_PUBLIC_TARGET')
                parent=stack[-1]
                try:info=os.stat(part,dir_fd=parent,follow_symlinks=False)
                except FileNotFoundError:
                    return dict(kind='MISSING',missing_at=physical,trace=trace)
                if stat.S_ISLNK(info.st_mode):
                    followed+=1;need(followed<=self.limits['links'],'LINK_BOUND')
                    target=os.readlink(part,dir_fd=parent)
                    need(type(target) is str and target.isascii() and 0<len(target)<=4096
                         and all(x in ('','.','..') or TOKEN.fullmatch(x) for x in target.split('/')),'LINK_TOKEN')
                    prospective=posixpath.normpath(posixpath.join('/'+'/'.join(names),target))
                    need(public_path(prospective,self.contract,True),'UNEXPECTED_PUBLIC_TARGET')
                    need(stamp(os.stat(part,dir_fd=parent,follow_symlinks=False))==stamp(info),'LINK_CHANGED')
                    trace['links'][physical]=dict(identity=stamp(info),target=target)
                    if target.startswith('/'):
                        while len(stack)>1:os.close(stack.pop())
                        names=[]
                    pending=target.split('/')+pending;continue
                names.append(part)
                if stat.S_ISDIR(info.st_mode):
                    child=os.open(part,flags,dir_fd=parent);stack.append(child)
                    need(stamp(os.fstat(child))==stamp(info),'DIRECTORY_CHANGED')
                    trace['directories'][physical]=dict(identity=stamp(info));terminal=info
                    if not pending:
                        need(directory or metadata,'SELECTED_DIRECTORY_NOT_FILE')
                        held=os.dup(child)
                        result=dict(kind='DIRECTORY',resolved=physical,identity=stamp(info),mode=stat.S_IMODE(info.st_mode),fd=held,trace=trace)
                        break
                else:
                    need(not pending,'UNSUPPORTED_INTERMEDIATE')
                    if not stat.S_ISREG(info.st_mode):return dict(kind='UNSUPPORTED',resolved=physical,identity=stamp(info),trace=trace)
                    need(public_path(physical,self.contract),'UNEXPECTED_PUBLIC_TARGET')
                    result=dict(kind='FILE',resolved=physical,identity=stamp(info),mode=stat.S_IMODE(info.st_mode),trace=trace)
                    if not metadata:
                        fd=os.open(part,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC,dir_fd=parent)
                        try:need(stamp(os.fstat(fd))==stamp(info),'OBJECT_CHANGED')
                        except BaseException:os.close(fd);raise
                        result['fd']=fd
                    break
            else:
                need(directory or metadata,'SELECTED_ROOT_NOT_FILE')
                result=dict(kind='DIRECTORY',resolved='/'+('/'.join(names)),identity=stamp(os.fstat(stack[-1])),
                            mode=stat.S_IMODE(os.fstat(stack[-1]).st_mode),fd=os.dup(stack[-1]),trace=trace)
            for index,fd in enumerate(stack):
                physical='/'+'/'.join(names[:index]) if index else '/'
                if physical in trace['directories']:
                    need(stamp(os.fstat(fd))==trace['directories'][physical]['identity'],'DIRECTORY_CHANGED')
            returned=True;return result
        finally:
            for fd in reversed(stack):os.close(fd)
            if not returned and result is not None and 'fd'in result:os.close(result['fd'])

    def _accept_trace(self, trace, opening):
        for group in ('links','directories'):
            for path,value in trace[group].items():
                if opening:self._record(group,path,value)
                else:
                    old=self.report[group].get(path)
                    if old is None or any(old.get(key)!=val for key,val in value.items()):
                        self.issue('TOPOLOGY_CHANGED',path)
                    if old is not None:
                        old['closing_identity']=value['identity']
                        if group=='links':old['closing_target']=value['target']

    def _read(self, fd, identity):
        size=identity[4]
        need(type(size) is int and 0<=size<=self.limits['file_bytes'],'FILE_BOUND')
        # Reserve the optional EOF probe too, so a concurrent growth cannot
        # cause even a refused observation to consume a byte over the ceiling.
        need(self.read_bytes+size+1<=self.limits['read_bytes'],'READ_BOUND')
        data=bytearray();offset=0
        while offset<size:
            chunk=os.pread(fd,min(1024**2,size-offset),offset)
            need(chunk,'SHORT_READ');self.read_bytes+=len(chunk);data.extend(chunk);offset+=len(chunk)
        extra=os.pread(fd,1,size);self.read_bytes+=len(extra)
        need(not extra and stamp(os.fstat(fd))==identity,'OBJECT_CHANGED')
        return bytes(data)

    def _select(self,path):
        result=None
        try:
            result=self._resolve(path,opening=True)
            self._accept_trace(result['trace'],True)
            row={key:result[key] for key in ('kind','resolved','missing_at') if key in result}
            self._record('selected',path,row)
            if result['kind']=='MISSING':
                row['allowed_missing']=path in self.contract['optional_aliases']
                if not row['allowed_missing']:self.issue('REQUIRED_MISSING',path)
            elif result['kind']!='FILE':self.issue('UNSUPPORTED_MEMBER',path)
            else:
                resolved=result['resolved'];existing=self.report['objects'].get(resolved)
                if existing is not None:need(existing['identity']==result['identity'],'DESCRIPTOR_CONFLICT')
                else:
                    anchor=tuple(result['identity'][:2]);previous=self.object_anchors.get(anchor)
                    self._reserve_object(result['identity'],previous['descriptor'] if previous is not None else None)
                    if previous is not None:
                        need(previous['identity']==result['identity'],'OBJECT_CHANGED')
                        obj=dict(previous)
                    else:
                        raw=self._read(result['fd'],result['identity'])
                        obj=dict(identity=result['identity'],descriptor=dict(pin(raw),mode=result['mode']),evidence='OBSERVED')
                        try:obj.update(classify(raw))
                        except Refusal as error:
                            obj.update(classification='ELF_UNSUPPORTED' if raw.startswith(b'\x7fELF') else 'UNSUPPORTED',reason=error.code)
                            self.issue('ELF_UNSUPPORTED' if raw.startswith(b'\x7fELF') else 'CLASSIFICATION_UNSUPPORTED',path)
                        self.object_anchors[anchor]=obj
                    self._record('objects',resolved,obj)
                self._budget()
        except (OSError,Refusal) as error:
            code=error.code if isinstance(error,Refusal) else 'SELECTOR_IO'
            self.issue(code,path)
            if path not in self.report['selected']:
                try:self._record('selected',path,dict(kind='REFUSED',reason=code))
                except Refusal:pass
            if code.endswith('_BOUND') or code in ('FILE_BOUND','ENTRY_BOUND'):raise Refusal(code)
        finally:
            if result is not None and 'fd' in result:os.close(result['fd'])

    def _population(self,path,rule,opening):
        result=None
        try:
            result=self._resolve(path,opening=opening,directory=True)
            need(result['kind']=='DIRECTORY' and result['resolved']==path,'CENSUS_REAL_DIRECTORY_REQUIRED')
            self._accept_trace(result['trace'],opening);fd=result['fd'];before=stamp(os.fstat(fd));members={}
            # A closing population replaces its own opening count; all other
            # directories keep their cumulative reservations. Reserve each
            # next member before statting or retaining it.
            other_members=sum(len(row['members']) for p,row in self.report['populations'].items() if p!=path)
            value=dict(rule=rule,members=members,identity=before)
            if opening:self._record('populations',path,value)
            with os.scandir(fd) as entries:
                for entry in entries:
                    need(TOKEN.fullmatch(entry.name) and entry.name not in ('.','..'),'CENSUS_TOKEN')
                    need(other_members+len(members)<self.limits['entries'],'ENTRY_BOUND')
                    info=os.stat(entry.name,dir_fd=fd,follow_symlinks=False)
                    kind=('DIRECTORY' if stat.S_ISDIR(info.st_mode) else 'FILE' if stat.S_ISREG(info.st_mode)
                          else 'SYMLINK' if stat.S_ISLNK(info.st_mode) else 'UNSUPPORTED')
                    members[entry.name]=dict(kind=kind,identity=stamp(info))
            need(stamp(os.fstat(fd))==before,'DIRECTORY_CHANGED')
            if opening:
                self._budget()
                if rule=='EXACT_GIT_DIRECTORY' and sorted(members)!=self.contract['git_directories'][path]:
                    self.issue('GIT_POPULATION_MISMATCH',path)
            else:
                old=self.report['populations'][path]
                old['closing_identity']=before
                old['closing_population_sha256']=sha(canonical(members))
                old['closing_population_count']=len(members)
                if old['identity']!=before or old['members']!=members:self.issue('DIRECTORY_POPULATION_CHANGED',path)
            return members
        finally:
            if result is not None and 'fd' in result:os.close(result['fd'])

    def opening(self):
        need(not self.started,'CAPTURE_ALREADY_STARTED');self.started=True
        try:
            self._budget()
            self.rootfd=os.open(self.root,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
            pending=[(self.contract['stdlib_root'],0)];dynamic=set()
            while pending:
                path,depth=pending.pop();need(depth<=self.limits['depth'],'DEPTH_BOUND')
                members=self._population(path,'STDLIB_REAL_DIRECTORY',True)
                for name,row in sorted(members.items()):
                    if name in SKIPS:continue
                    child=path+'/'+name
                    if row['kind']=='DIRECTORY':pending.append((child,depth+1))
                    else:dynamic.add(child)
                need(len(dynamic)+len(pending)+len(self.report['populations'])<=self.limits['entries'],'ENTRY_BOUND')
            for path in self.contract['git_directories']:self._population(path,'EXACT_GIT_DIRECTORY',True)
            for path in sorted(set(self.contract['fixed_files'])|set(self.contract['optional_aliases'])|dynamic):self._select(path)
            for path in self.contract.get('public_absences',[]):
                result=None
                try:
                    result=self._resolve(path,opening=True,metadata=True);self._accept_trace(result['trace'],True)
                    self.report['absences'][path]={k:result[k] for k in ('kind','resolved','missing_at','identity') if k in result}
                    if result['kind']!='MISSING':self.issue('PUBLIC_STARTUP_ABSENCE_CHANGED',path)
                finally:
                    if result is not None and 'fd'in result:os.close(result['fd'])
        except (Refusal,OSError) as error:
            self.issue(error.code if isinstance(error,Refusal) else 'CENSUS_IO')
            self.report['opening_aborted']=True
        return self.report

    def closing(self):
        need(self.started and not self.finished,'CAPTURE_LIFECYCLE');self.finished=True
        closed={}
        try:
            for path,old in list(self.report['selected'].items()):
                result=None
                try:
                    result=self._resolve(path,opening=False);self._accept_trace(result['trace'],False)
                    now={k:result[k] for k in ('kind','resolved','missing_at') if k in result}
                    if any(old.get(k)!=v for k,v in now.items()) or old.get('kind')!=now['kind']:
                        self.issue('SELECTOR_CHANGED',path);continue
                    old['closing']=now
                    if result['kind']=='FILE':
                        resolved=result['resolved'];obj=self.report['objects'].get(resolved)
                        need(obj is not None and obj['identity']==result['identity'],'OBJECT_CHANGED')
                        anchor=tuple(result['identity'][:2])
                        if anchor not in closed:
                            raw=self._read(result['fd'],result['identity'])
                            closed[anchor]=dict(pin(raw),mode=result['mode'])
                        obj['closing_identity']=result['identity'];obj['closing_descriptor']=closed[anchor]
                        if obj['closing_descriptor']!=obj['descriptor']:self.issue('OBJECT_CHANGED',path)
                except (Refusal,OSError) as error:self.issue(error.code if isinstance(error,Refusal) else 'SELECTOR_CLOSING_IO',path)
                finally:
                    if result is not None and 'fd'in result:os.close(result['fd'])
            for path,population in list(self.report['populations'].items()):
                try:self._population(path,population['rule'],False)
                except (Refusal,OSError) as error:self.issue(error.code if isinstance(error,Refusal) else 'CENSUS_CLOSING_IO',path)
            for path,old in self.report['absences'].items():
                result=None
                try:
                    result=self._resolve(path,opening=False,metadata=True);self._accept_trace(result['trace'],False)
                    now={k:result[k] for k in ('kind','resolved','missing_at','identity') if k in result};old['closing']=now
                    if {k:v for k,v in old.items() if k!='closing'}!=now:self.issue('PUBLIC_STARTUP_ABSENCE_CHANGED',path)
                except (Refusal,OSError) as error:self.issue(error.code if isinstance(error,Refusal) else 'ABSENCE_CLOSING_IO',path)
                finally:
                    if result is not None and 'fd'in result:os.close(result['fd'])
        finally:
            if self.rootfd is not None:os.close(self.rootfd);self.rootfd=None
        report=self.report;report['read_bytes']=self.read_bytes
        for path,obj in report['objects'].items():
            if 'closing_descriptor' not in obj:self.issue('OBJECT_CLOSING_MISSING',path)
        try:
            report['expected_provider']=expected_layer(self.contract,self.wheel,report['objects'])
            report['layout']=make_layout(report,self.contract)
            report['cache']=cache_join(report,self.contract,self.retained_cache)
            report['graph']=join_graph(report,self.contract,self.retained_cache)
            report['pin_comparisons']=compare_pins(report,self.contract)
            report['counters']=self._budget()
            report['counters']['edges']=len(report['graph']['edges'])
            need(report['counters']['edges']<=self.limits['edges'],'EDGE_BOUND')
            expected=population_selection(self.contract,report['populations'])
            need(set(report['selected'])==expected,'CENSUS_SELECTOR_COVERAGE')
            structural=[x for x in report['issues'] if x['code'] not in ('ELF_UNSUPPORTED','CLASSIFICATION_UNSUPPORTED')]
            report['census_complete']=not structural
            report['complete_selected_public_static_surface']=complete_predicate(report)
        except (Refusal,OSError,ValueError) as error:
            self.issue(error.code if isinstance(error,Refusal) else 'STATIC_PROJECTION_REFUSED')
            report['census_complete']=False;report['complete_selected_public_static_surface']=False
        return report


def make_layout(report,contract):
    links={p:r['target'] for p,r in report['links'].items()}
    expected=report['expected_provider'];logical={};files={};directories={}
    for path,row in report['directories'].items():
        directories[path]=dict(mode=stat.S_IMODE(row['identity'][2]),evidence='OBSERVED')
    for path,row in report['selected'].items():
        if row['kind']!='FILE':continue
        resolved,_=virtual_resolve(path,links)
        need(resolved==row['resolved'] and resolved in report['objects'],'LAYOUT_SELECTED_JOIN')
        logical[path]=resolved
        descriptor=report['objects'][resolved]['descriptor']
        need(resolved not in files or files[resolved]['descriptor']==descriptor,'LAYOUT_DESCRIPTOR_CONFLICT')
        files[resolved]=dict(descriptor=descriptor,evidence='OBSERVED')
    for path,row in expected['files'].items():
        need(path not in files,'EXPECTED_OBSERVED_COLLISION')
        files[path]=dict(descriptor=row['descriptor'],evidence='EXPECTED_ONLY');logical[path]=path
    for path,target in expected['links'].items():
        need(path not in links,'EXPECTED_OBSERVED_COLLISION');links[path]=target
    for path,row in expected['directories'].items():
        need(path not in directories,'EXPECTED_OBSERVED_COLLISION')
        directories[path]=dict(mode=row['mode'],evidence='EXPECTED_ONLY')
    for path in expected['links']:
        resolved,_=virtual_resolve(path,links)
        if resolved in files:logical[path]=resolved
        else:need(resolved in directories,'EXPECTED_LINK_TARGET')
    for path in set(files)|set(links):
        for parent in PurePosixPath(path).parents:
            directories.setdefault(str(parent),dict(mode=493,evidence='EXPECTED_SCAFFOLD'))
    need(not set(files)&set(links) and not (set(files)|set(links))&set(directories),'LAYOUT_TYPE_CONFLICT')
    return dict(files=files,links=links,directories=directories,logical=logical,
                semantics='ALL_SELECTED_SPELLINGS_AND_INTERMEDIATE_LINKS_PRESERVED',
                actual_image_constructed=False,provider_layer='EXPECTED_ONLY')


def compare_pins(report,contract):
    comparisons=[];links=report['layout']['links']
    for path,wanted in sorted(contract['pins'].items()):
        selected=report['selected'].get(path,{});obj=report['objects'].get(selected.get('resolved'),{})
        actual=dict(obj.get('descriptor',{}),resolved=selected.get('resolved'))
        parent,_=virtual_resolve(str(PurePosixPath(path).parent),links)
        actual['link']=links.get(parent.rstrip('/')+'/'+PurePosixPath(path).name)
        comparisons.append(dict(path=path,match=selected.get('kind')=='FILE' and
                                all(actual.get(k)==v for k,v in wanted.items() if k in ('bytes','sha256','mode','resolved','link'))))
    policy=contract['directory_mode_policy']
    for path,row in report['directories'].items():
        wanted=policy['exceptions'].get(path,policy['default'])
        if stat.S_IMODE(row['identity'][2])!=wanted:
            comparisons.append(dict(path=path,match=False,reason='DIRECTORY_MODE_PIN'))
    return comparisons


def cache_join(report,contract,retained):
    need(pin(retained)==contract['retained_cache'],'RETAINED_CACHE_PIN')
    selected=report['selected'].get('/etc/ld.so.cache',{})
    obj=report['objects'].get(selected.get('resolved'),{})
    descriptor=obj.get('descriptor',{})
    matches=(selected.get('kind')=='FILE' and selected.get('resolved')=='/etc/ld.so.cache'
             and descriptor.get('mode')==420 and
             {k:descriptor.get(k) for k in ('bytes','sha256')}==contract['retained_cache']
             and obj.get('closing_descriptor')==descriptor and obj.get('closing_identity')==obj.get('identity'))
    return dict(path='/etc/ld.so.cache',retained_body=contract['retained_cache'],
        same_operation_descriptor_matches_retained=matches,retained_body_parsing_permitted=matches,
        observed_descriptor=descriptor,maintained_pin=contract['maintained_cache_pin'],
        maintained_pin_matches=all(descriptor.get(k)==v for k,v in contract['maintained_cache_pin'].items() if k in ('bytes','sha256','mode')),
        cache_pin_adopted=False,new_body_exported=False,
        relation='SAME_BYTES_FOR_PARSING_ONLY' if matches else 'DISTINCT_OR_UNRESOLVED_SUBJECT_NO_ADOPTION')


def cache_rows(raw,wanted):
    """Parse only the retained, descriptor-joined format; export requested names."""
    need(len(raw)<=65536 and raw[:20]==b'glibc-ld.so.cache1.1','CACHE_FORMAT')
    def unpack(fmt,offset):
        length=struct.calcsize(fmt);need(0<=offset<=len(raw)-length,'CACHE_RANGE')
        return struct.unpack_from(fmt,raw,offset)
    size,strings,flags,ext=unpack('<IIB3xI',20)
    start=48+24*size;end=start+strings
    need(size<=4096 and flags==2 and not any(raw[29:32]+raw[36:48]) and
         48<=start<=end<=ext==(end+3)//4*4 and ext+24<=len(raw) and not any(raw[end:ext]),'CACHE_HEADER')
    magic,nsections,tag,reserved,pos,length=unpack('<6I',ext)
    need((magic,nsections,tag,reserved,pos,pos+length)==(0xeaa42174,1,0,0,ext+24,len(raw)),'CACHE_EXTENSION_UNSUPPORTED')
    result={name:[] for name in wanted}
    for index in range(size):
        flag,keyoffset,targetoffset,osversion,hwcap=unpack('<iIIIQ',48+24*index)
        need(start<=keyoffset<end and start<=targetoffset<end,'CACHE_STRING_RANGE')
        name=elf_string(raw,keyoffset,end,NAME)
        if name not in wanted:continue
        target=elf_string(raw,targetoffset,end,None,4095)
        need(path_token(target),'CACHE_TARGET_TOKEN')
        result[name].append(dict(index=index,target=target,flags=flag,osversion=osversion,hwcap=hwcap))
    return result


def join_graph(report,contract,retained):
    observed=report['objects'];expected=report['expected_provider'];layout=report['layout']
    nodes={**observed,**expected['files']};links=layout['links'];edges=[];unsupported=[]
    roots=[p for p,r in nodes.items() if r.get('classification') in ('ELF','ELF_UNSUPPORTED','SCRIPT')]
    wanted={n['name'] for row in nodes.values() if row.get('classification')=='ELF' for n in row['elf']['needed'] if '/'not in n['name']}
    cache={};cache_error=None
    if report['cache']['retained_body_parsing_permitted']:
        try:cache=cache_rows(retained,wanted)
        except Refusal as error:cache_error=error.code
    else:cache_error='CACHE_DESCRIPTOR_NOT_JOINED'
    def target(path):
        if not path_token(path):return None
        try:resolved,_=virtual_resolve(path,links)
        except Refusal:return None
        return resolved if resolved in nodes else None
    def add(source,kind,name,chosen=None,reason=None,metadata=None):
        need(len(edges)<bounded_limits(contract)['edges'],'EDGE_BOUND')
        row=dict(source=source,source_evidence=nodes[source]['evidence'],kind=kind,name=name,
                 status='JOINED' if chosen is not None and reason is None else 'UNRESOLVED')
        if chosen is not None:
            row.update(target=chosen,target_evidence=nodes[chosen]['evidence'],target_descriptor=nodes[chosen]['descriptor'])
        if reason is not None:row['reason']=reason
        if metadata:row.update(metadata)
        edges.append(row);return row
    def executable_edge(source,kind,path):
        chosen=target(path)
        if chosen is None:add(source,kind,path,reason='INTERPRETER_OUTSIDE_SELECTED_LAYOUT')
        elif nodes[chosen].get('classification')!='ELF':add(source,kind,path,chosen,'INTERPRETER_NOT_SUPPORTED_ELF')
        elif not nodes[chosen]['descriptor']['mode']&0o111:add(source,kind,path,chosen,'INTERPRETER_NOT_EXECUTABLE')
        else:add(source,kind,path,chosen)
    for path in sorted(roots):
        row=nodes[path];classification=row['classification']
        if classification=='ELF_UNSUPPORTED':unsupported.append(dict(path=path,reason='ELF_UNSUPPORTED'));continue
        if classification=='SCRIPT':
            executable_edge(path,'SCRIPT_INTERPRETER',row['interpreter'])
            if row['interpreter']=='/usr/bin/env':
                command=row.get('argument')
                if command in ('bash','sh','python','python3','python3.12'):
                    choices=[target(root+'/'+command) for root in (contract['provider']['root']+'/bin','/usr/bin','/bin')]
                    chosen=next((p for p in choices if p),None)
                    add(path,'SCRIPT_ENV_COMMAND',command,chosen, None if chosen else 'ENV_COMMAND_OUTSIDE_SELECTED_LAYOUT')
                else:add(path,'SCRIPT_ENV_COMMAND','UNSUPPORTED_ARGUMENT',reason='ENV_DISPATCH_UNSUPPORTED')
            continue
        elf=row['elf']
        if elf['interpreter'] is not None:executable_edge(path,'PT_INTERP',elf['interpreter']['path'])
        lookup_issue=None
        if elf['rpath']:lookup_issue='RPATH_INHERITANCE_UNSUPPORTED'
        if elf['special_tags']:lookup_issue='DYNAMIC_FILTER_AUDIT_OR_POSITION_UNSUPPORTED'
        if elf['flags']&~0x1f or elf['flags_1']&~0x080000eb:lookup_issue='DYNAMIC_FLAGS_UNSUPPORTED'
        if lookup_issue:unsupported.append(dict(path=path,reason=lookup_issue))
        for dependency in elf['needed']:
            name=dependency['name'];reason=lookup_issue;chosen=None;basis=None;candidate_records=[]
            if reason is None and '/'in name:
                chosen=target(name);basis='ABSOLUTE_NEEDED_PATH'
                if chosen is None:reason='NEEDED_PATH_OUTSIDE_SELECTED_LAYOUT'
            elif reason is None:
                for directory in elf['runpath']:
                    expanded=directory.replace('${ORIGIN}',posixpath.dirname(path)).replace('$ORIGIN',posixpath.dirname(path))
                    if not path_token(expanded) or not (public_path(expanded,contract,True) or expanded.startswith(contract['provider']['root']+'/')):
                        reason='RUNPATH_OUTSIDE_SELECTED_LAYOUT';break
                    chosen=target(expanded.rstrip('/')+'/'+name)
                    if chosen is not None:basis='DIRECT_OBJECT_RUNPATH';break
                if chosen is None and reason is None:
                    if cache_error:reason=cache_error
                    else:
                        records=cache.get(name,[])
                        # No cache target string outside this source-owned path
                        # policy is exported or inspected; a hash binds refusal.
                        for candidate in records:
                            if public_path(candidate['target'],contract):candidate_records.append(candidate)
                            else:candidate_records.append(dict(index=candidate['index'],flags=candidate['flags'],
                                osversion=candidate['osversion'],hwcap=candidate['hwcap'],target_sha256=sha(candidate['target'].encode())))
                        eligible=[r for r in records if r['flags']==0x303 and r['osversion']==r['hwcap']==0]
                        if any(r['osversion'] or r['hwcap'] for r in records if r['flags']==0x303):reason='CACHE_HWCAP_OR_OSVERSION_UNSUPPORTED'
                        elif len(eligible)>1:reason='CACHE_ALTERNATIVES_AMBIGUOUS'
                        elif eligible:
                            chosen=target(eligible[0]['target']);basis='ONE_ELIGIBLE_JOINED_CACHE_ROW'
                            if chosen is None:reason='CACHE_TARGET_OUTSIDE_SELECTED_LAYOUT'
                        else:
                            candidates=[target(root+'/'+name) for root in ('/lib/x86_64-linux-gnu','/usr/lib/x86_64-linux-gnu','/lib','/usr/lib')]
                            choices=list(dict.fromkeys(p for p in candidates if p))
                            if len(choices)==1:chosen=choices[0];basis='SELECTED_DEFAULT_PATH'
                            else:reason='DEFAULT_PATH_AMBIGUOUS' if choices else 'DEPENDENCY_OUTSIDE_SELECTED_LAYOUT'
            required=elf['version_needs'].get(name,[]);provided=[];missing=[]
            if chosen is not None:
                targetrow=nodes[chosen]
                if targetrow.get('classification')!='ELF':reason='DEPENDENCY_NOT_SUPPORTED_ELF'
                else:
                    provided=sorted(v['name'] for v in targetrow['elf']['version_definitions'])
                    missing=sorted(v['name'] for v in required if v['name']not in provided)
                    if missing:reason='REQUIRED_VERSION_NODE_ABSENT'
            add(path,'DT_NEEDED',name,chosen,reason,dict(lookup_basis=basis,cache_candidates=candidate_records,
                required_versions=required,provided_version_names=provided,missing_version_names=missing,
                dynamic_entry_file_offset=dependency['dynamic_entry_file_offset'],
                string_file_offset=dependency['string_file_offset'],comparison='VERSION_NODE_NAMES_ONLY'))
    python=[];system=observed.get(contract['python_target'],{})
    defined=set(system.get('elf',{}).get('python_defined',[]))
    for path,row in sorted(nodes.items()):
        required=row.get('elf',{}).get('python_undefined',[])
        if required:
            python.append(dict(source=path,source_evidence=row['evidence'],interpreter=contract['python_target'],
                required_names=required,missing_names=sorted(set(required)-defined),
                interpreter_descriptor=system.get('descriptor'),comparison='DEFINITION_NAMES_ONLY_NO_BINDING_OR_ABI_CLAIM'))
    copy=expected['files'].get(contract['provider']['root']+'/bin/python3.12')
    if copy and not copy.get('system_copy_pin_matches'):
        unsupported.append(dict(path=contract['provider']['root']+'/bin/python3.12',reason='EXPECTED_INTERPRETER_COPY_PIN_NOT_JOINED'))
    return dict(roots=sorted(roots),edges=edges,unsupported_objects=unsupported,python_comparisons=python,
        complete=not unsupported and all(e['status']=='JOINED' for e in edges) and all(not p['missing_names'] for p in python),
        semantics='PROSPECTIVE_SELECTED_LAYOUT_CORRESPONDENCE_ONLY',
        runtime_selected_loads_observed=False,symbol_binding_qualified=False,abi_qualified=False)


def complete_predicate(report):
    terminals=all(row.get('kind')=='FILE' or (row.get('kind')=='MISSING' and row.get('allowed_missing')is True)
                  for row in report['selected'].values())
    classified=all(row.get('classification')in ('ELF','SCRIPT','NON_ELF_DATA')for row in report['objects'].values())
    absences=all(type(row)is dict and set(row)=={'kind','missing_at','closing'}
                 and row['kind']=='MISSING' and type(row['missing_at'])is str and path_token(row['missing_at'])
                 and row['closing']=={'kind':'MISSING','missing_at':row['missing_at']}
                 for row in report['absences'].values())
    return bool(terminals and classified and absences and report.get('census_complete') and not report['issues'] and report.get('graph',{}).get('complete')
                and all(x['match'] for x in report.get('pin_comparisons',[]))
                and not report.get('opening_aborted'))


def validate_export_shapes(report,contract):
    top={'schema','authority','contract_sha256','selected','objects','links','directories','populations','absences','issues',
         'observed_provider','actual_runtime_constructed','cache_pin_adopted','source_profile_adopted','original_awards',
         'census_complete','complete_selected_public_static_surface','read_bytes','evidence_scope','limits','opening_aborted',
         'expected_provider','layout','cache','graph','pin_comparisons','counters'}
    def shape(value,required,optional=(),code='UNEXPECTED_PROJECTION_FIELD'):
        need(type(value)is dict and set(required)<=set(value)<=set(required)|set(optional),code)
    shape(report,top-{'opening_aborted'},{'opening_aborted'},'UNEXPECTED_REPORT_FIELD')
    def numeric(value,maximum=2**64-1,minimum=0):
        return type(value)is int and minimum<=value<=maximum
    def code(value):return type(value)is str and re.fullmatch('[A-Z][A-Z0-9_]{0,127}',value)
    def digest(value):return type(value)is str and re.fullmatch('[0-9a-f]{64}',value)
    def identity(value):
        need(type(value)is list and len(value)==9 and all(type(x)is str and re.fullmatch('[0-9]{1,20}',x)for x in value[:2])
             and all(numeric(x)for x in value[2:7]) and all(numeric(x,2**63-1,-2**63)for x in value[7:]),'IDENTITY_PROJECTION')
    def descriptor(value,ident):
        shape(value,{'bytes','sha256','mode'},code='OBJECT_DESCRIPTOR')
        need(numeric(value['bytes'],bounded_limits(contract)['file_bytes']) and digest(value['sha256'])
             and numeric(value['mode'],0o7777) and value['bytes']==ident[4]
             and value['mode']==stat.S_IMODE(ident[2]) and stat.S_ISREG(ident[2]),'OBJECT_DESCRIPTOR')
    for group in ('selected','objects','links','directories','populations','absences'):
        need(type(report[group])is dict and len(report[group])<=4096
             and all(type(path)is str for path in report[group]),'REPORT_MAP_PROJECTION')
    need(report['evidence_scope']=='SELECTED_PUBLIC_STATIC_DATA_AND_EXPECTED_PROVIDER_ONLY'
         and all(type(report[k])is bool for k in ('observed_provider','actual_runtime_constructed','cache_pin_adopted',
               'source_profile_adopted','census_complete','complete_selected_public_static_surface'))
         and type(report['original_awards'])is int and ('opening_aborted'not in report or type(report['opening_aborted'])is bool),
         'REPORT_SCALAR_PROJECTION')
    need(type(report['issues'])is list and len(report['issues'])<=4096,'ISSUE_BOUND')
    for issue in report['issues']:
        shape(issue,{'code'},{'path','token_sha256'},'ISSUE_TOKEN')
        need(code(issue['code']) and not {'path','token_sha256'}<=set(issue),'ISSUE_TOKEN')
        if 'path'in issue:need(public_path(issue['path'],contract,True),'ISSUE_PATH_TOKEN')
        if 'token_sha256'in issue:need(digest(issue['token_sha256']),'ISSUE_HASH_TOKEN')
    classes={'ELF':{'elf'},'SCRIPT':{'interpreter','argument'},'NON_ELF_DATA':set(),
             'ELF_UNSUPPORTED':{'reason'},'UNSUPPORTED':{'reason'}}
    for path,obj in report['objects'].items():
        need(type(obj)is dict and type(obj.get('classification'))is str
             and obj['classification']in classes,'UNCLASSIFIED_TERMINAL')
        shape(obj,{'identity','descriptor','evidence','classification'}|classes[obj['classification']],
              {'closing_identity','closing_descriptor'},'UNEXPECTED_OBJECT_FIELD')
        identity(obj['identity'])
        descriptor(obj['descriptor'],obj['identity'])
        need(('closing_identity'in obj)==('closing_descriptor'in obj),'OBJECT_CLOSING_PAIR')
        if 'closing_identity'in obj:
            identity(obj['closing_identity']);descriptor(obj['closing_descriptor'],obj['closing_identity'])
        if 'reason'in obj:need(code(obj['reason']),'OBJECT_REASON_TOKEN')
        if obj.get('classification')=='SCRIPT':
            need(elf_public_path(obj.get('interpreter')),'SCRIPT_INTERPRETER_TOKEN')
            argument=obj.get('argument')
            need(argument is None or (type(argument)is str and (argument in ('bash','sh','python','python3','python3.12')
                 or re.fullmatch(r'-[A-Za-z0-9]{1,16}',argument))),'SCRIPT_ARGUMENT_TOKEN')
        if obj.get('classification')!='ELF':continue
        e=obj['elf']
        keys={'elf_class','endianness','machine','type','program_header_count','interpreter','needed','soname','rpath','runpath',
              'flags','flags_1','special_tags','version_needs','version_definitions','python_undefined','python_defined','dynamic_tags',
              'symbol_table_status','comparison_scope','string_table','dynamic_segment','symbol_count'}
        shape(e,keys-{'string_table','dynamic_segment','symbol_count'},
              {'string_table','dynamic_segment','symbol_count'},'ELF_PROJECTION_SCHEMA')
        need(type(e['elf_class'])is int and e['elf_class']==64 and e['endianness']=='little'
             and type(e['machine'])is int and e['machine']==62 and type(e['type'])is int and e['type']in(2,3)
             and type(e['program_header_count'])is int and 0<e['program_header_count']<=256,'ELF_PROJECTION_SCHEMA')
        size=obj['descriptor']['bytes']
        need(e['comparison_scope']=='VERSION_NODE_AND_PYTHON_DEFINITION_NAMES_ONLY_NO_ABI_OR_LOAD_CLAIM'
             and e['symbol_table_status']in('NO_DYNAMIC_SYMBOL_TABLE','BOUNDED_DYNAMIC_TABLE'),'ELF_COMPARISON_SCOPE')
        need(('symbol_count'in e)==(e['symbol_table_status']=='BOUNDED_DYNAMIC_TABLE')
             and ('string_table'in e)==('dynamic_segment'in e)
             and (e['symbol_table_status']!='BOUNDED_DYNAMIC_TABLE' or 'dynamic_segment'in e),'ELF_PROJECTION_PAIR')
        if 'symbol_count'in e:need(numeric(e['symbol_count'],65536,1),'ELF_SYMBOL_BOUND')
        need(type(e['dynamic_tags'])is list and len(e['dynamic_tags'])<=4096,'ELF_DYNAMIC_BOUND')
        for item in e['dynamic_tags']:
            need(type(item)is dict and set(item)=={'tag','count'} and numeric(item['tag'],2**63-1,-2**63)
                 and numeric(item['count'],4096,1),'ELF_DYNAMIC_NUMERIC_PROJECTION')
        need(sum(x['count']for x in e['dynamic_tags'])<=4096,'ELF_DYNAMIC_BOUND')
        need(type(e['special_tags'])is list and len(e['special_tags'])<=4096,'ELF_SPECIAL_BOUND')
        for item in e['special_tags']:
            need(type(item)is dict and set(item)=={'tag','value','file_offset'} and numeric(item['tag'],2**63-1,-2**63)
                 and numeric(item['value']) and numeric(item['file_offset'],size),'ELF_SPECIAL_NUMERIC_PROJECTION')
        need(type(e['flags'])is int and type(e['flags_1'])is int and 0<=e['flags']<2**64 and 0<=e['flags_1']<2**64,'ELF_FLAG_PROJECTION')
        if e['interpreter'] is not None:
            need(type(e['interpreter'])is dict and set(e['interpreter'])=={'path','file_offset'} and elf_public_path(e['interpreter']['path'])
                 and numeric(e['interpreter']['file_offset'],size),'ELF_INTERPRETER_TOKEN')
        need(e['soname']is None or (type(e['soname'])is str and NAME.fullmatch(e['soname'])),'ELF_SONAME_TOKEN')
        need(type(e['needed'])is list and len(e['needed'])<=4096,'ELF_NEEDED_BOUND')
        for dependency in e['needed']:
            need(type(dependency)is dict and set(dependency)=={'name','dynamic_entry_file_offset','string_file_offset'}
                 and type(dependency['name'])is str
                 and (NAME.fullmatch(dependency['name']) or elf_public_path(dependency['name']))
                 and numeric(dependency['dynamic_entry_file_offset'],size)
                 and numeric(dependency['string_file_offset'],size),'ELF_NEEDED_TOKEN')
        for group in ('rpath','runpath'):
            need(type(e[group])is list and len(e[group])<=4096,'ELF_SEARCH_BOUND')
            for value in e[group]:
                need(type(value)is str,'ELF_SEARCH_TOKEN')
                replaced=value.replace('${ORIGIN}','/ORIGIN').replace('$ORIGIN','/ORIGIN')
                need(elf_public_path(value) or ((value.startswith('$ORIGIN') or value.startswith('${ORIGIN}'))
                     and path_token(replaced)),'ELF_SEARCH_TOKEN')
        for group in ('python_undefined','python_defined'):
            need(type(e[group])is list and len(e[group])<=65536 and all(type(name)is str for name in e[group])
                 and e[group]==sorted(set(e[group]))
                 and all(PYNAME.fullmatch(name)for name in e[group]),'PYTHON_SYMBOL_TOKEN')
        need(type(e['version_needs'])is dict and all(type(x)is list for x in e['version_needs'].values())
             and sum(len(x)for x in e['version_needs'].values())<=4096
             and type(e['version_definitions'])is list and len(e['version_definitions'])<=4096,'ELF_VERSION_BOUND')
        for library,versions in e['version_needs'].items():
            need(type(library)is str and NAME.fullmatch(library),'ELF_VERSION_LIBRARY_TOKEN')
            for version in versions:
                need(type(version)is dict and set(version)=={'name','flags','index','record_file_offset'}
                     and type(version['name'])is str and NAME.fullmatch(version['name'])
                     and numeric(version['flags'],65535) and numeric(version['index'],65535)
                     and numeric(version['record_file_offset'],size),'ELF_VERSION_TOKEN')
        for version in e['version_definitions']:
            need(type(version)is dict and set(version)=={'name','parents','flags','index','record_file_offset'}
                 and type(version['name'])is str and NAME.fullmatch(version['name'])
                 and type(version['parents'])is list and len(version['parents'])<=4096
                 and all(type(name)is str and NAME.fullmatch(name)for name in version['parents']) and numeric(version['flags'],65535)
                 and numeric(version['index'],65535) and numeric(version['record_file_offset'],size),'ELF_VERSION_TOKEN')
        for key in ('string_table','dynamic_segment'):
            if key in e:
                need(type(e[key])is dict and set(e[key])=={'offset','bytes','sha256'} and digest(e[key]['sha256'])
                     and type(e[key]['offset'])is int and type(e[key]['bytes'])is int
                     and 0<=e[key]['offset']<=obj['descriptor']['bytes']
                     and 0<=e[key]['bytes']<=obj['descriptor']['bytes']-e[key]['offset'],'ELF_RANGE_PROJECTION')
    for path,row in report['selected'].items():
        need(type(row)is dict,'SELECTOR_PROJECTION')
        for closing,value in [(False,row)]+([(True,row['closing'])]if 'closing'in row else[]):
            kinds={'FILE':{'resolved'},'MISSING':{'missing_at'},'UNSUPPORTED':{'resolved'}}
            if not closing:kinds['REFUSED']={'reason'}
            need(type(value)is dict and type(value.get('kind'))is str and value['kind']in kinds,'SELECTOR_KIND')
            required={'kind'}|kinds[value['kind']]
            if value['kind']=='MISSING' and not closing:required|={'allowed_missing'}
            shape(value,required,set()if closing else{'closing'},'UNEXPECTED_SELECTOR_FIELD')
            if 'reason'in value:need(code(value['reason']),'SELECTOR_REASON_TOKEN')
            if 'allowed_missing'in value:need(type(value['allowed_missing'])is bool,'SELECTOR_MISSING_FLAG')
            for key in ('resolved','missing_at'):
                if key in value:need(public_path(value[key],contract,True),'SELECTOR_PATH_TOKEN')
    for path,row in report['links'].items():
        shape(row,{'identity','target'},{'closing_identity','closing_target'},'UNEXPECTED_LINK_FIELD')
        need(('closing_identity'in row)==('closing_target'in row),'LINK_CLOSING_PAIR')
        identity(row['identity'])
        if 'closing_identity'in row:identity(row['closing_identity'])
        for key in ('target','closing_target'):
            if key in row:
                value=row[key]
                need(type(value)is str and 0<len(value)<=4096 and value.isascii()
                     and all(x in ('','.','..') or TOKEN.fullmatch(x)for x in value.split('/')),'LINK_TOKEN')
    for path,row in report['directories'].items():
        shape(row,{'identity'},{'closing_identity'},'UNEXPECTED_DIRECTORY_FIELD')
        identity(row['identity'])
        if 'closing_identity'in row:identity(row['closing_identity'])
    for path,row in report['populations'].items():
        closing={'closing_identity','closing_population_sha256','closing_population_count'}
        shape(row,{'rule','members','identity'},closing,'UNEXPECTED_POPULATION_FIELD')
        need(not set(row)&closing or closing<=set(row),'POPULATION_CLOSING_PAIR')
        need(row['rule']in('STDLIB_REAL_DIRECTORY','EXACT_GIT_DIRECTORY')
             and type(row['members'])is dict and len(row['members'])<=4096,'POPULATION_PROJECTION')
        identity(row['identity'])
        if 'closing_identity'in row:identity(row['closing_identity'])
        if 'closing_population_sha256'in row:need(digest(row['closing_population_sha256']),'POPULATION_HASH')
        if 'closing_population_count'in row:need(numeric(row['closing_population_count'],4096),'POPULATION_COUNT')
        for name,member in row['members'].items():
            need(type(member)is dict and set(member)=={'kind','identity'} and type(name)is str and TOKEN.fullmatch(name)
                 and member['kind']in('FILE','DIRECTORY','SYMLINK','UNSUPPORTED'),'UNEXPECTED_MEMBER_FIELD');identity(member['identity'])
            mode=member['identity'][2]
            kind='FILE'if stat.S_ISREG(mode)else'DIRECTORY'if stat.S_ISDIR(mode)else'SYMLINK'if stat.S_ISLNK(mode)else'UNSUPPORTED'
            need(member['kind']==kind,'MEMBER_IDENTITY_KIND')
    for path,row in report['absences'].items():
        need(type(row)is dict,'ABSENCE_PROJECTION')
        for closing,value in [(False,row)]+([(True,row['closing'])]if 'closing'in row else[]):
            kinds={'MISSING':{'missing_at'},'FILE':{'resolved','identity'},
                   'DIRECTORY':{'resolved','identity'},'UNSUPPORTED':{'resolved','identity'}}
            need(type(value)is dict and type(value.get('kind'))is str and value['kind']in kinds,'ABSENCE_KIND')
            shape(value,{'kind'}|kinds[value['kind']],set()if closing else{'closing'},'UNEXPECTED_ABSENCE_FIELD')
            if 'identity'in value:
                identity(value['identity']);mode=value['identity'][2]
                need((value['kind']=='FILE' and stat.S_ISREG(mode))
                     or (value['kind']=='DIRECTORY' and stat.S_ISDIR(mode))
                     or (value['kind']=='UNSUPPORTED' and not stat.S_ISREG(mode) and not stat.S_ISDIR(mode)
                         and not stat.S_ISLNK(mode)),'ABSENCE_IDENTITY_KIND')
            for key in ('resolved','missing_at'):
                if key in value:need(public_path(value[key],contract,True),'ABSENCE_PATH_TOKEN')


def report_commitment(report):
    """Hash the exact v1 representation without creating an expanded wire body."""
    encoder = json.JSONEncoder(sort_keys=True, separators=(',', ':'), ensure_ascii=True)
    digest = hashlib.sha256()
    length = 1
    for fragment in encoder.iterencode(report):
        data = fragment.encode('ascii')
        length += len(data)
        digest.update(data)
    digest.update(b'\n')
    return {'bytes': length, 'sha256': digest.hexdigest()}


def equal_bookends(report, *, restore):
    """Omit only bookends the complete-report predicate requires to match."""
    for group in ('objects', 'links', 'directories', 'populations', 'selected', 'absences'):
        need(type(report.get(group)) is dict, 'COMPACT_BOOKEND_GROUP')
        for row in report[group].values():
            need(type(row) is dict, 'COMPACT_BOOKEND_ROW')
            if group == 'selected':
                observed = {key: row[key] for key in ('kind', 'resolved', 'missing_at') if key in row}
                matching = {'closing': observed}
            elif group == 'absences':
                matching = {'closing': {key: value for key, value in row.items() if key != 'closing'}}
            else:
                need('identity' in row, 'COMPACT_IDENTITY')
                matching = {'closing_identity': row['identity']}
                if group == 'objects':
                    need('descriptor' in row, 'COMPACT_DESCRIPTOR')
                    matching['closing_descriptor'] = row['descriptor']
                elif group == 'links':
                    need('target' in row, 'COMPACT_LINK_TARGET')
                    matching['closing_target'] = row['target']
                elif group == 'populations':
                    need(type(row.get('members')) is dict, 'COMPACT_POPULATION')
                    matching.update(closing_population_count=len(row['members']),
                                    closing_population_sha256=sha(canonical(row['members'])))
            if restore:
                need(set(row).isdisjoint(matching), 'COMPACT_DUPLICATE_BOOKEND')
                row.update(matching)
            else:
                need(set(matching) <= set(row)
                     and canonical({key: row[key] for key in matching}) == canonical(matching),
                     'COMPACT_UNMATCHED_BOOKEND')
                for key in matching:
                    del row[key]


def encode_report(report,maximum=LIMITS['report_bytes']):
    need(type(maximum)is int and 256<=maximum<=LIMITS['report_bytes'],'REPORT_LIMIT')
    original = report_commitment(report)
    if original['bytes'] <= maximum:
        return canonical(report)
    if report.get('schema') == SCHEMA and report.get('complete_selected_public_static_surface') is True:
        compact = copy.deepcopy(report)
        equal_bookends(compact, restore=False)
        for name in DERIVED_SECTIONS:
            del compact[name]
        compact.update(schema=COMPACT_SCHEMA, original=original)
        wire = canonical(compact)
        if len(wire) <= maximum:
            return wire
    refusal=dict(schema='g132.selected-public-static-refusal.v1',authority='NONE',
        complete_selected_public_static_surface=False,code='REPORT_BOUND',
        refused_bytes=original['bytes'],refused_sha256=original['sha256'],report_bound=maximum)
    result=canonical(refusal);need(len(result)<=maximum,'REPORT_REFUSAL_BOUND');return result


def receive(raw,contract,wheel,retained_cache):
    """Validate the closed finite projection, recomputing its denominator/joins.

    This validates an exact source-bound observer projection. It does not claim
    independent custody or reparsing of host ELF bytes that were not exported.
    The enclosing receiver must additionally join the actual run/job/boot,
    observer/source hashes, terminal statuses and delivery manifest.
    """
    need(type(raw)is bytes and len(raw)<=bounded_limits(contract)['report_bytes'],'REPORT_BOUND')
    report=strict_json(raw)
    need(type(report) is dict, 'REPORT_SCHEMA_OR_INCOMPLETE_STUB')
    if report.get('schema') == COMPACT_SCHEMA:
        need(canonical(report) == raw and report.get('complete_selected_public_static_surface') is True,
             'COMPACT_REPORT_FRAME')
        original = report.pop('original', None)
        need(type(original) is dict and set(original) == {'bytes', 'sha256'} and
             type(original['bytes']) is int and original['bytes'] > len(raw) and
             type(original['sha256']) is str and re.fullmatch('[0-9a-f]{64}', original['sha256']),
             'COMPACT_ORIGINAL_DESCRIPTOR')
        need(set(report).isdisjoint(DERIVED_SECTIONS), 'COMPACT_DUPLICATE_DERIVATION')
        report.update(schema=SCHEMA, **dict.fromkeys(DERIVED_SECTIONS))
        equal_bookends(report, restore=True)
        validate_export_shapes(report, contract)
        limits = bounded_limits(contract)
        counts = budget_counts(report, contract)
        for name in ('entries', 'total_bytes', 'unique_bytes', 'mounted_bytes', 'read_bytes'):
            need(counts[name] <= limits[name], 'GLOBAL_BOUND')
        report['expected_provider'] = expected_layer(contract, wheel, report['objects'])
        report['layout'] = make_layout(report, contract)
        report['cache'] = cache_join(report, contract, retained_cache)
        report['graph'] = join_graph(report, contract, retained_cache)
        need(len(report['graph']['edges']) <= limits['edges'], 'GLOBAL_BOUND')
        report['pin_comparisons'] = compare_pins(report, contract)
        report['counters'] = dict(counts, edges=len(report['graph']['edges']))
        need(report_commitment(report) == original, 'COMPACT_ORIGINAL_COMMITMENT')
    need(report.get('schema') == SCHEMA,'REPORT_SCHEMA_OR_INCOMPLETE_STUB')
    validate_export_shapes(report,contract)
    need(report.get('authority')=='NONE' and report.get('contract_sha256')==sha(canonical(contract)),'REPORT_CONTRACT_BINDING')
    need(report.get('observed_provider')is False and report.get('actual_runtime_constructed')is False
         and report.get('cache_pin_adopted')is False and report.get('source_profile_adopted')is False
         and report.get('original_awards')==0,'REPORT_AUTHORITY_OR_MIXED_EVIDENCE')
    need(canonical(report.get('limits'))==canonical(bounded_limits(contract)),'REPORT_LIMITS')
    selected=population_selection(contract,report['populations'])
    need(set(report['selected'])==selected,'CENSUS_SELECTOR_COVERAGE')
    need(set(report['absences'])==set(contract.get('public_absences',[])),'ABSENCE_COVERAGE')
    for path in report['selected']:
        need(public_path(path,contract),'UNEXPECTED_OBSERVED_SELECTOR')
    expected_objects={r['resolved'] for r in report['selected'].values() if r['kind']=='FILE'}
    need(set(report['objects'])==expected_objects,'UNEXPECTED_OR_OMITTED_OBJECT')
    physical={}
    for obj in report['objects'].values():
        key=tuple(obj['identity'][:2]);value=(obj['identity'],obj['descriptor'],obj.get('closing_descriptor'))
        need(key not in physical or physical[key]==value,'PHYSICAL_DESCRIPTOR_CONFLICT');physical[key]=value
    minimum_reads=sum(opened['bytes']+(closed['bytes']if closed else 0)for _,opened,closed in physical.values())
    need(type(report.get('read_bytes'))is int and report['read_bytes']>=minimum_reads,'READ_UNDERCOUNT')
    if report['complete_selected_public_static_surface']:
        need(report['read_bytes']==minimum_reads,'READ_COUNT_CONFLICT')
    for path,obj in report['objects'].items():
        need(public_path(path,contract) and obj.get('evidence')=='OBSERVED','EXPECTED_OBSERVED_MIX')
        need(obj.get('classification')in ('ELF','SCRIPT','NON_ELF_DATA','ELF_UNSUPPORTED','UNSUPPORTED'),'UNCLASSIFIED_TERMINAL')
        need(type(obj.get('identity'))is list and len(obj['identity'])==9,'OBJECT_IDENTITY')
        descriptor=obj['descriptor']
        need(set(descriptor)=={'bytes','sha256','mode'} and descriptor['bytes']==obj['identity'][4]
             and descriptor['mode']==stat.S_IMODE(obj['identity'][2]) and stat.S_ISREG(obj['identity'][2])
             and re.fullmatch('[0-9a-f]{64}',descriptor['sha256']),'OBJECT_DESCRIPTOR')
        if report['complete_selected_public_static_surface']:
            need(obj.get('closing_identity')==obj['identity'] and obj.get('closing_descriptor')==descriptor,'OBJECT_CHANGED')
    links={p:r['target'] for p,r in report['links'].items()}
    used_links=set();used_directories={'/'}
    for path,row in report['selected'].items():
        resolved,used=virtual_resolve(path,links);used_links.update(used)
        if row['kind']=='FILE':need(resolved==row['resolved'],'SELECTED_TOPOLOGY_JOIN')
        if row['kind']=='MISSING':need(row.get('allowed_missing')==(path in contract['optional_aliases']),'MISSING_CLASSIFICATION')
        if report['complete_selected_public_static_surface']:
            need(row.get('closing')=={k:row[k] for k in ('kind','resolved','missing_at') if k in row},'SELECTOR_CLOSING')
        for node in (path,resolved,*used):
            for parent in PurePosixPath(node).parents:
                physical,_=virtual_resolve(str(parent),links);used_directories.add(physical)
    for path,population in report['populations'].items():
        need(path_token(path),'CENSUS_DIRECTORY_TOKEN')
        if report['complete_selected_public_static_surface']:
            need(population.get('closing_identity')==population['identity']
                 and population.get('closing_population_count')==len(population['members'])
                 and population.get('closing_population_sha256')==sha(canonical(population['members'])),'DIRECTORY_POPULATION_CHANGED')
        for parent in (PurePosixPath(path),*PurePosixPath(path).parents):
            physical,used=virtual_resolve(str(parent),links);used_directories.add(physical);used_links.update(used)
    for path,row in report['absences'].items():
        if report['complete_selected_public_static_surface']:
            need(row['kind']=='MISSING' and row.get('closing')=={k:v for k,v in row.items()if k!='closing'},'ABSENCE_CHANGED')
        trace=[] if row['kind']=='DIRECTORY' else None
        resolved,used=virtual_resolve(path,links,directory_trace=trace);used_links.update(used)
        if trace is not None:
            # Only opening DIRECTORY facts supply this trace. A directory
            # first seen at closing never enlarges the opening census.
            need(row['resolved']==resolved and report['directories'].get(resolved,{}).get('identity')==row['identity'],
                 'ABSENCE_DIRECTORY_JOIN')
            need(all(node in report['directories']for node in trace),'ABSENCE_DIRECTORY_TRACE')
            used_directories.update(trace)
        for parent in PurePosixPath(path).parents:
            physical,_=virtual_resolve(str(parent),links)
            # A missing selector can have several missing ancestors; only the
            # nearest actual ancestor is part of topology.
            if physical in report['directories']:used_directories.add(physical)
    need(set(report['links'])==used_links,'UNEXPECTED_OR_OMITTED_LINK')
    need(set(report['directories'])==used_directories,'UNEXPECTED_OR_OMITTED_DIRECTORY')
    for path,row in report['links'].items():
        need(public_path(path,contract,True) and stat.S_ISLNK(row['identity'][2]),'LINK_DESCRIPTOR')
        if report['complete_selected_public_static_surface']:
            need(row.get('closing_identity')==row['identity'] and row.get('closing_target')==row['target'],'LINK_CHANGED')
    for path,row in report['directories'].items():
        need(public_path(path,contract,True) and stat.S_ISDIR(row['identity'][2]),'DIRECTORY_DESCRIPTOR')
        if report['complete_selected_public_static_surface']:need(row.get('closing_identity')==row['identity'],'DIRECTORY_CHANGED')
    layer=expected_layer(contract,wheel,report['objects'])
    # Canonical JSON equality also closes nested scalar types (True != 1),
    # as well as exact fields, against the independently rebuilt projection.
    need(canonical(report.get('expected_provider'))==canonical(layer),'EXPECTED_PROVIDER_CHANGED_OR_MIXED')
    need(canonical(report.get('layout'))==canonical(make_layout(report,contract)),'LAYOUT_RECOMPUTATION')
    need(canonical(report.get('cache'))==canonical(cache_join(report,contract,retained_cache)),'CACHE_RECOMPUTATION')
    need(canonical(report.get('graph'))==canonical(join_graph(report,contract,retained_cache)),'GRAPH_RECOMPUTATION')
    need(canonical(report.get('pin_comparisons'))==canonical(compare_pins(report,contract)),'PIN_RECOMPUTATION')
    counts=budget_counts(report,contract);counts['edges']=len(report['graph']['edges'])
    need(canonical(report.get('counters'))==canonical(counts),'COUNTER_RECOMPUTATION')
    for key in ('entries','file_bytes','total_bytes','unique_bytes','mounted_bytes','read_bytes','edges'):
        if key!='file_bytes':need(counts[key]<=bounded_limits(contract)[key],'GLOBAL_BOUND')
    complete=complete_predicate(report)
    need(report.get('complete_selected_public_static_surface')==complete,'COMPLETE_PREDICATE')
    need(not complete or report.get('census_complete')is True,'CENSUS_COMPLETE_PREDICATE')
    return dict(accepted=True,complete_selected_public_static_surface=complete,
                report=pin(raw),authority='NONE',claim='SOURCE_BOUND_PROJECTION_RECOMPUTED',
                host_elf_bytes_received=False,actual_provider_observed=False,
                source_profile_cache_adopted=False,original_awards=0)
