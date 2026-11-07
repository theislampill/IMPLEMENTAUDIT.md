"""DG17 fixed D0 producer; inert import. POSIX adapter is not locally exercised.

The optional adapter is an in-memory test seam, never source/host authority.
Only produce() starts the data operation; no CLI, target launch or discovery.
"""
import errno, hashlib, json, os, re, stat, sys
from schema_data import BINDING, PRIVATE, PUBLIC

MIB=1048576
BODY_MAX=8*MIB
POP_MAX=32*MIB
PRIVATE_NAME='D0_PRIVATE_RECEIPT.json'
POPULATION=(
 ('USR_BIN_BASH','/usr/bin/bash','helper'),('BIN_BASH','/bin/bash','helper'),
 ('USR_BIN_PYTHON3','/usr/bin/python3','helper'),('BIN_PYTHON3','/bin/python3','helper'),
 ('ETC_PROFILE','/etc/profile','startup'),('ETC_BASH_BASHRC','/etc/bash.bashrc','startup'),
 ('ETC_BASH_BASH_LOGOUT','/etc/bash.bash_logout','startup'),('ETC_PROFILE_D','/etc/profile.d','metadata'),
 ('USR_BIN_ZSH','/usr/bin/zsh','metadata'),('BIN_ZSH','/bin/zsh','metadata'),
 ('USR_LOCAL_BIN_BASH','/usr/local/bin/bash','metadata'),('USR_LOCAL_BIN_ZSH','/usr/local/bin/zsh','metadata'),
 ('OPT_HOMEBREW_BIN_BASH','/opt/homebrew/bin/bash','metadata'),('OPT_HOMEBREW_BIN_ZSH','/opt/homebrew/bin/zsh','metadata'))

class Refused(Exception):
    def __init__(self,code,err=None):self.code=code; self.err=err; super().__init__(code)
def require(condition,code):
    if not condition:raise Refused(code)
def canonical(v):return (json.dumps(v,ensure_ascii=True,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode('ascii')
def sha(raw):return hashlib.sha256(raw).hexdigest()
def error(code,err=None):return dict(code=code,errno=err)
def os_errno(exc):
    return exc.errno if type(exc.errno) is int and 1<=exc.errno<=4095 else None

def validate(v,s,depth=0):
    require(depth<=20,'JSON_DEPTH')
    if 'anyOf' in s:
        for branch in s['anyOf']:
            try:validate(v,branch,depth); return
            except Refused:pass
        raise Refused('SCHEMA_UNION')
    if 'const'in s:require(type(v) is type(s['const']) and v==s['const'],'SCHEMA_CONST')
    if 'enum'in s:require(any(type(v) is type(x) and v==x for x in s['enum']),'SCHEMA_ENUM')
    t=s.get('type')
    if t=='object':
        require(type(v) is dict and set(v)==set(s['properties']),'SCHEMA_OBJECT')
        for k,x in v.items():validate(x,s['properties'][k],depth+1)
    elif t=='array':
        require(type(v) is list and len(v)<=s.get('maxItems',len(v)),'SCHEMA_ARRAY')
        for x in v:validate(x,s['items'],depth+1)
    elif t=='integer':require(type(v) is int and s.get('minimum',v)<=v<=s.get('maximum',v) and len(str(abs(v)))<=20,'SCHEMA_INTEGER')
    elif t=='boolean':require(type(v) is bool,'SCHEMA_BOOLEAN')
    elif t=='null':require(v is None,'SCHEMA_NULL')
    elif t=='string':
        require(type(v) is str and v.isascii() and s.get('minLength',0)<=len(v)<=s.get('maxLength',len(v)),'SCHEMA_STRING')
        if 'pattern'in s:require(re.fullmatch(s['pattern'],v) is not None,'SCHEMA_PATTERN')

def parts(path):
    require(type(path) is str and path.startswith('/') and path.isascii() and len(path)<=4096 and all(32<=ord(c)<127 for c in path),'PATH_SHAPE')
    xs=[] if path=='/' else path[1:].split('/')
    require(len(xs)<=16 and all(x not in ('','.','..') and len(x)<=255 for x in xs),'PATH_COMPONENTS')
    return xs

def identity(st):return {k:getattr(st,'st_'+k) for k in ('dev','ino','uid','gid','mode','nlink','size','mtime_ns','ctime_ns')}

class PosixIO:
    """Only descriptor-relative no-follow operations, except the literal root."""
    def runtime(self):return os.geteuid(),os.getegid(),sys.platform
    def root(self):return os.open('/',os.O_PATH|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC)
    def lstat(self,fd,name):return identity(os.stat(name,dir_fd=fd,follow_symlinks=False))
    def fstat(self,fd):return identity(os.fstat(fd))
    def directory(self,fd,name):return os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK,dir_fd=fd)
    def open_body(self,fd,name):return os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK,dir_fd=fd)
    def readlink(self,fd,name):return os.readlink(name,dir_fd=fd)
    def read(self,fd,n):return os.read(fd,n)
    def access(self,fd,name):return os.access(name,os.X_OK,dir_fd=fd,effective_ids=True,follow_symlinks=False)
    def capability(self,fd):return os.getxattr(fd,'security.capability')
    def close(self,fd):os.close(fd)
    def list_names(self,fd):return os.listdir(fd)
    def create(self,fd,name):return os.open(name,os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC|os.O_NONBLOCK,0o600,dir_fd=fd)
    def write(self,fd,raw):return os.write(fd,raw)
    def fsync(self,fd):os.fsync(fd)
    def rewind(self,fd):os.lseek(fd,0,os.SEEK_SET)

def probe(fn,*args):
    try:return dict(identity=fn(*args),errno=None)
    except OSError as exc:return dict(identity=None,errno=os_errno(exc))
def linkprobe(io,fd,name):
    try:return dict(value=io.readlink(fd,name),errno=None)
    except OSError as exc:return dict(value=None,errno=os_errno(exc))
def stable(p,q):return p is not None and p==q and (p['identity'] is not None or p['errno']==errno.ENOENT)
def kind(i):
    if i is None:return 'UNKNOWN'
    m=i['mode']
    return 'REGULAR' if stat.S_ISREG(m) else 'DIRECTORY' if stat.S_ISDIR(m) else 'SYMLINK' if stat.S_ISLNK(m) else 'OTHER'
def protected(i):return i is not None and i['uid']==0 and not i['mode']&0o022

class Observer:
    def __init__(self,io):self.io=io; self.unique={}
    def body(self,fd,name,initial,helper):
        io=self.io
        b=dict(fd_before=None,fd_after=None,read_lengths=[],read_errno=None,eof=False,bytes_read=0,sha256=None,prefix_hex='',x_ok=None,access_errno=None,capability=None,error=None)
        opened=None; h=hashlib.sha256(); prefix=b''
        try:
            require(initial['size']<=BODY_MAX,'BODY_SIZE_LIMIT')
            key=(initial['dev'],initial['ino'])
            if key in self.unique:require(self.unique[key]==initial,'POPULATION_IDENTITY_DRIFT')
            else:
                require(sum(x['size'] for x in self.unique.values())+initial['size']<=POP_MAX,'POPULATION_BYTES_LIMIT')
                self.unique[key]=initial
            opened=io.open_body(fd,name); b['fd_before']=probe(io.fstat,opened)
            require(b['fd_before']==dict(identity=initial,errno=None),'BODY_OPEN_IDENTITY')
            for _ in range(129):
                try:chunk=io.read(opened,min(65536,BODY_MAX+1-b['bytes_read']))
                except OSError as exc:
                    b['read_errno']=os_errno(exc); raise Refused('BODY_READ_ERROR',os_errno(exc))
                require(type(chunk) is bytes and len(chunk)<=65536,'BODY_READ_SHAPE')
                b['read_lengths'].append(len(chunk)); b['bytes_read']+=len(chunk)
                h.update(chunk); prefix=(prefix+chunk)[:20]
                if not chunk:b['eof']=True; break
                require(b['bytes_read']<=BODY_MAX,'BODY_BYTES_LIMIT')
            b['sha256']=h.hexdigest(); b['prefix_hex']=prefix.hex()
            require(b['eof'] and b['bytes_read']==initial['size'],'BODY_EOF_SIZE')
            if helper:
                try:b['x_ok']=io.access(fd,name)
                except OSError as exc:b['access_errno']=os_errno(exc)
                try:
                    cap=io.capability(opened)
                    require(type(cap) is bytes and len(cap)<=65536,'CAPABILITY_BYTES_LIMIT')
                    b['capability']=dict(state='NONEMPTY' if cap else 'EMPTY',length=len(cap),sha256=sha(cap),errno=None)
                except OSError as exc:
                    e=os_errno(exc)
                    b['capability']=dict(state='NO_DATA' if e==errno.ENODATA else 'UNSUPPORTED' if e==errno.ENOTSUP else 'ERROR',length=0 if e in (errno.ENODATA,errno.ENOTSUP) else None,sha256=None,errno=e)
                if b['access_errno'] is not None:raise Refused('ACCESS_ERROR',b['access_errno'])
                require(type(b['x_ok']) is bool,'ACCESS_ERROR')
                if b['capability']['state']=='ERROR':raise Refused('CAPABILITY_ERROR',b['capability']['errno'])
        except (NotImplementedError,AttributeError):b['error']=error('UNSUPPORTED_PRIMITIVE')
        except Refused as exc:b['error']=error(exc.code,exc.err)
        except OSError as exc:b['error']=error('BODY_OPEN_ERROR',os_errno(exc))
        finally:
            if opened is not None:
                b['fd_after']=probe(io.fstat,opened)
                if not stable(b['fd_before'],b['fd_after']) and b['error'] is None:b['error']=error('BODY_FD_DRIFT')
                io.close(opened)
            if b['read_lengths'] and b['sha256'] is None:b['sha256']=h.hexdigest(); b['prefix_hex']=prefix.hex()
        return b
    def observe(self,path,role):
        io=self.io; cut=dict(walk=[],aliases=[],body=None,terminal=None)
        retained=[]; handles=[]; links=[]; root=None
        try:
            current=parts(path); root=io.root(); handles.append(root)
            while True:
                parent=root; prefix=''; rp=probe(io.fstat,root)
                node=dict(path='/',before=rp,after=None,directory_before=rp,directory_after=None)
                cut['walk'].append(node); retained.append((node,None,None,root))
                require(rp['identity'] is not None and kind(rp['identity'])=='DIRECTORY','ROOT_IDENTITY')
                restart=False
                for index,name in enumerate(current):
                    require(len(cut['walk'])<153,'WALK_LIMIT')
                    prefix+='/'+name; leaf=index==len(current)-1
                    before=probe(io.lstat,parent,name)
                    node=dict(path=prefix,before=before,after=None,directory_before=None,directory_after=None)
                    cut['walk'].append(node); retained.append((node,parent,name,None))
                    i=before['identity']
                    if i is None:
                        if before['errno']!=errno.ENOENT:raise Refused('PATH_PROBE_ERROR',before['errno'])
                        break
                    k=kind(i)
                    follow=k=='SYMLINK' and (role=='helper' or (not leaf and prefix=='/bin'))
                    if follow:
                        require(len(cut['aliases'])<8,'ALIAS_HOPS_LIMIT')
                        lp=linkprobe(io,parent,name); a=dict(walk_index=len(cut['walk'])-1,before=lp,after=None)
                        cut['aliases'].append(a); links.append((a,parent,name))
                        require(lp['value'] is not None,'READLINK_ERROR')
                        target=lp['value']; base=prefix.rsplit('/',1)[0]
                        expanded=target if target.startswith('/') else base+'/'+target
                        target_parts=parts(expanded)
                        if role!='helper':require(prefix=='/bin' and expanded=='/usr/bin','METADATA_ALIAS_TARGET')
                        current=target_parts+current[index+1:]; parts('/'+'/'.join(current))
                        restart=True; break
                    if not leaf:
                        require(k=='DIRECTORY','UNSELECTED_ANCESTOR_ALIAS' if k=='SYMLINK' else 'ANCESTOR_NOT_DIRECTORY')
                        opened=io.directory(parent,name); handles.append(opened)
                        node['directory_before']=probe(io.fstat,opened); retained[-1]=(node,parent,name,opened)
                        require(node['directory_before']==before,'DIRECTORY_OPEN_IDENTITY')
                        parent=opened
                    elif role in ('helper','startup') and k=='REGULAR':
                        cut['body']=self.body(parent,name,i,role=='helper')
                if not restart:break
        except (NotImplementedError,AttributeError):cut['terminal']=error('UNSUPPORTED_PRIMITIVE')
        except Refused as exc:cut['terminal']=error(exc.code,exc.err)
        except OSError as exc:cut['terminal']=error('WALK_OS_ERROR',os_errno(exc))
        finally:
            for a,fd,name in links:a['after']=linkprobe(io,fd,name)
            for node,fd,name,opened in reversed(retained):
                node['after']=probe(io.fstat,root) if fd is None else probe(io.lstat,fd,name)
                if opened is not None:node['directory_after']=probe(io.fstat,opened)
            for fd in reversed(handles):io.close(fd)
        return cut

# Public reconstruction is an independent interpreter of the written closed wire.
def normalized(cut):
    c=json.loads(canonical(cut))
    if c and c['body']:c['body'].pop('read_lengths',None)
    return c

def elf(prefix):
    h=bytes.fromhex(prefix)
    if len(h)<20 or h[:4]!=b'\x7fELF' or h[4] not in (1,2) or h[5] not in (1,2) or h[6]!=1:return (None,None,None)
    return (32 if h[4]==1 else 64,'LITTLE' if h[5]==1 else 'BIG',int.from_bytes(h[18:20],'little' if h[5]==1 else 'big'))

def wire_validate(v,s):
    if 'anyOf' in s:
        for option in s['anyOf']:
            try:wire_validate(v,option);return
            except Refused:pass
        raise Refused('WIRE_TYPE_OR_VALUE')
    if 'const' in s:require(canonical(v)==canonical(s['const']),'WIRE_CONSTANT')
    if 'enum' in s:require(any(canonical(v)==canonical(x) for x in s['enum']),'WIRE_ENUM')
    t=s.get('type');types={'object':dict,'array':list,'integer':int,'string':str,'boolean':bool,'null':type(None)}
    if t in types:require(type(v) is types[t],'WIRE_TYPE')
    if t=='object':
        require(set(v)==set(s['properties']),'WIRE_FIELDS')
        for k in s['properties']:wire_validate(v[k],s['properties'][k])
    elif t=='array':
        require(len(v)<=s.get('maxItems',len(v)),'WIRE_ARRAY_BOUND')
        for item in v:wire_validate(item,s['items'])
    elif t=='integer':require(s.get('minimum',v)<=v<=s.get('maximum',v),'WIRE_INTEGER_BOUND')
    elif t=='string':
        require(s.get('minLength',0)<=len(v)<=s.get('maxLength',len(v)),'WIRE_STRING_BOUND')
        require(v.isascii() and ('pattern' not in s or re.fullmatch(s['pattern'],v) is not None),'WIRE_STRING_LANGUAGE')

def base_row(fixed):
    r={k:None for k in PUBLIC['properties']['rows']['items']['properties']}
    r.update(fixed_id=fixed,kind='UNKNOWN',alias_hops=0,physical_ancestry_received=False,before_after_equal=False)
    return r

def selected_errno(cut):
    if cut is None:return None
    if cut['terminal'] is not None:return cut['terminal']['errno']
    if cut['body'] is not None and cut['body']['error'] is not None:return cut['body']['error']['errno']
    for node in cut['walk']:
        for key in ('before','after','directory_before','directory_after'):
            probe_value=node[key]
            if probe_value is not None and probe_value['errno'] not in (None,errno.ENOENT):return probe_value['errno']
    return None

def probe_relation(q):require((q['identity'] is None)!=(q['errno'] is None),'PROBE_RELATION')

def check_node(node,directory):
    probe_relation(node['before']);require(node['after'] is not None,'MISSING_NODE_BOOKEND');probe_relation(node['after'])
    require(node['before']==node['after'],'NODE_CHANGED')
    i=node['before']['identity']
    if directory:
        require(kind(i)=='DIRECTORY','ANCESTOR_NOT_DIRECTORY')
        require(node['directory_before'] is not None and node['directory_after'] is not None,'DIRECTORY_DESCRIPTOR_MISSING')
        probe_relation(node['directory_before']);probe_relation(node['directory_after'])
        require(node['directory_before']['identity']==i and node['directory_after']['identity']==i,'DIRECTORY_DESCRIPTOR_CHANGED')
    else:require(node['directory_before'] is None and node['directory_after'] is None,'UNEXPECTED_DIRECTORY_OPEN')
    return i

def wire_parts(path):
    require(type(path) is str and path.startswith('/') and len(path)<=4096 and all(32<=ord(x)<=126 for x in path),'PATH_LANGUAGE')
    xs=[] if path=='/' else path[1:].split('/')
    require(all(x not in ('','.','..') and len(x)<=255 for x in xs),'PATH_LANGUAGE')
    require(len(xs)<=16,'ANCESTOR_BOUND');return xs

def expanded_alias(at,text,suffix):
    require(type(text) is str and 0<len(text)<=4096 and all(32<=ord(x)<=126 for x in text),'ALIAS_LANGUAGE')
    xs=text[1:].split('/') if text.startswith('/') else text.split('/')
    require(all(x not in ('','.','..') for x in xs),'ALIAS_SPELLING_UNSUPPORTED')
    path=text if text.startswith('/') else at.rsplit('/',1)[0]+'/'+text
    target=wire_parts(path)
    destination=target+suffix;wire_parts('/'+'/'.join(destination))
    return destination,path

def check_body(b,target,helper):
    require(b is not None,'BODY_MISSING')
    if b['error'] is not None:raise Refused(b['error']['code'])
    require(b['fd_before'] is not None and b['fd_after'] is not None,'BODY_DESCRIPTOR_MISSING')
    probe_relation(b['fd_before']);probe_relation(b['fd_after'])
    require(b['fd_before']['identity']==target and b['fd_after']['identity']==target,'BODY_DESCRIPTOR_CHANGED')
    lengths=b['read_lengths']
    require(bool(lengths) and lengths[-1]==0 and all(n>0 for n in lengths[:-1]),'EOF_MISSING')
    require(b['eof'] and b['read_errno'] is None and sum(lengths)==b['bytes_read']==target['size'] and b['bytes_read']<=BODY_MAX and b['sha256'] is not None,'BODY_NOT_COMPLETE')
    require(len(b['prefix_hex'])==2*min(20,b['bytes_read']),'PREFIX_LENGTH')
    if not helper:
        require(b['x_ok'] is None and b['access_errno'] is None and b['capability'] is None,'UNREQUESTED_HELPER_OBSERVATION');return
    require(type(b['x_ok']) is bool and b['access_errno'] is None,'EXEC_ACCESS_UNKNOWN')
    c=b['capability'];require(c is not None,'CAPABILITY_MISSING')
    if c['state'] in ('EMPTY','NONEMPTY'):
        require(c['errno'] is None and c['length'] is not None and c['sha256'] is not None,'CAPABILITY_RELATION')
        require((c['length']==0 and c['sha256']==sha(b'')) if c['state']=='EMPTY' else c['length']>0,'CAPABILITY_RELATION')
    elif c['state'] in ('NO_DATA','UNSUPPORTED'):
        require(c['errno']==(errno.ENODATA if c['state']=='NO_DATA' else errno.ENOTSUP) and c['length']==0 and c['sha256'] is None,'CAPABILITY_RELATION')
    else:raise Refused('CAPABILITY_UNKNOWN')

def reconstruct(fixed,path,role,cut):
    require(cut is not None,'CUT_MISSING')
    wire_validate(cut,PRIVATE['properties']['records']['items']['properties']['before']['anyOf'][0])
    if cut['terminal'] is not None:raise Refused(cut['terminal']['code'])
    aliases={a['walk_index']:a for a in cut['aliases']}
    require(len(aliases)==len(cut['aliases']),'DUPLICATE_ALIAS')
    pending=wire_parts(path);cursor=0;used=set();requested=None;target=None;missing=False;safe=True;ancestors=[];target_path=None;hops=0
    walk=cut['walk']
    while True:
        require(cursor<len(walk),'WALK_TRUNCATED');root=walk[cursor];cursor+=1
        require(root['path']=='/','WALK_ROOT');ri=check_node(root,True);safe=safe and protected(ri)
        ancestors=[dict(path='/',identity=ri)];require(bool(pending),'HELPER_TARGET_IS_ROOT')
        restart=False
        for n,component in enumerate(pending):
            actual='/'+'/'.join(pending[:n+1]);leaf=n==len(pending)-1
            require(cursor<len(walk) and walk[cursor]['path']==actual,'WALK_PATH')
            index=cursor;node=walk[cursor];cursor+=1;probe_relation(node['before']);i=node['before']['identity'];k=kind(i)
            check_node(node,i is not None and not leaf and k!='SYMLINK')
            if i is None:
                require(node['before']['errno']==errno.ENOENT,'OBSERVATION_OS_ERROR');require(index not in aliases,'ALIAS_ON_ABSENCE')
                missing=True;target=None;break
            if leaf and requested is None:requested=i
            follow=k=='SYMLINK' and (role=='helper' or (not leaf and actual=='/bin'))
            if follow:
                hops+=1;require(hops<=8 and index in aliases,'ALIAS_BOUND_OR_MISSING')
                a=aliases[index];used.add(index)
                require(a['after'] is not None and a['before']==a['after'] and a['before']['errno'] is None and a['before']['value'] is not None,'READLINK_CHANGED_OR_ERROR')
                destination,alias_target=expanded_alias(actual,a['before']['value'],pending[n+1:])
                if role!='helper':require(actual=='/bin' and alias_target=='/usr/bin' and hops==1,'UNSELECTED_ANCESTOR_ALIAS')
                safe=safe and i['uid']==0;pending=destination;restart=True;break
            require(index not in aliases,'UNAUTHORIZED_READLINK')
            if not leaf:
                require(k!='SYMLINK','UNSELECTED_ANCESTOR_ALIAS');require(k=='DIRECTORY','ANCESTOR_NOT_DIRECTORY')
                safe=safe and protected(i);ancestors.append(dict(path=actual,identity=i))
            else:target=i;target_path=actual
        if not restart:break
    require(cursor==len(walk) and used==set(aliases),'EXTRA_WALK_OBSERVATION')
    require(len(ancestors)<=16,'ANCESTOR_BOUND')
    require(requested is not None or missing,'LEAF_UNOBSERVED')
    b=cut['body'];needs_body=role in ('helper','startup') and kind(target)=='REGULAR'
    if needs_body:check_body(b,target,role=='helper')
    else:require(b is None,'UNREQUESTED_BODY_READ')
    r=base_row(fixed);r.update(before_after_equal=True,physical_ancestry_received=safe,present=requested is not None,kind=kind(requested) if requested is not None else 'ABSENT',alias_hops=hops if requested is not None else 0)
    if requested is not None:
        for key in ('uid','gid','mode','nlink','dev','ino'):r[key]=requested[key]
        if needs_body:
            r.update(bytes=b['bytes_read'],sha256=b['sha256'])
            if role=='helper':
                ec,ee,em=elf(b['prefix_hex']);r.update(elf_class=ec,elf_endian=ee,elf_machine=em,file_capabilities_absent=b['capability']['state'] in ('EMPTY','NO_DATA','UNSUPPORTED'),canonical_identity_sha256=canonical_target(target_path,ancestors,target,b,(ec,ee,em)))
    return r

def project_record(fixed,path,role,before,after):
    try:
        reconstruct(fixed,path,role,before)
        r=reconstruct(fixed,path,role,after)
        require(normalized(before)==normalized(after),'OBSERVATION_CHANGED')
        return r
    except Refused as exc:
        r=base_row(fixed);e=selected_errno(after)
        r.update(error_code=exc.code,errno=e if e is not None else selected_errno(before));return r

def population_failure(records):
    for side in ('before','after'):
        sizes={}
        for record in records:
            cut=record[side];b=cut['body'] if cut else None
            i=b['fd_before']['identity'] if b and b['fd_before'] else None
            if i is not None:sizes[i['dev'],i['ino']]=max(i['size'],sizes.get((i['dev'],i['ino']),0))
        if sum(sizes.values())>POP_MAX:return 'REGULAR_POPULATION_BOUND'
    return None

def canonical_target(path,ancestors,target,b,ef):
    h=bytes.fromhex(b['prefix_hex'])
    status='NOT_ELF' if len(h)<4 or h[:4]!=b'\x7fELF' else 'MALFORMED_ELF' if ef[0] is None else 'ELF'
    preimage=dict(path=path,physical_ancestors=ancestors,identity=target,bytes=b['bytes_read'],sha256=b['sha256'],elf=dict(status=status,elf_class=ef[0],elf_endian=ef[1],elf_machine=ef[2]),prefix_hex=b['prefix_hex'],capability=b['capability'],x_ok=b['x_ok'])
    return sha(canonical(preimage))

def directory_ok(i,b):return kind(i)=='DIRECTORY' and i['uid']==b['evidence_uid'] and i['gid']==b['evidence_gid'] and i['mode']&0o7777==0o700

def file_ok(i,b):return kind(i)=='REGULAR' and i['uid']==b['evidence_uid'] and i['gid']==b['evidence_gid'] and i['mode']&0o7777==0o600 and i['nlink']==1 and 0<i['size']<=BODY_MAX

def custody(i):return {k:i[k] for k in ('dev','ino','uid','gid','mode','nlink')}

def output(io,episode,private_fd,initial,b,raw):
    require(len(raw)<=BODY_MAX,'PRIVATE_BYTES_LIMIT')
    require(io.fstat(private_fd)==initial and io.lstat(episode,'private')==initial,'PRIVATE_DIRECTORY_DRIFT')
    require(io.list_names(private_fd)==[],'PRIVATE_INVENTORY')
    fd=io.create(private_fd,PRIVATE_NAME)
    try:
        created=io.fstat(fd)
        require(kind(created)=='REGULAR' and created['size']==0 and created['nlink']==1 and created['uid']==b['evidence_uid'] and created['gid']==b['evidence_gid'] and created['mode']&0o7777==0o600,'PRIVATE_CREATED_SHAPE')
        require(io.lstat(private_fd,PRIVATE_NAME)==created,'PRIVATE_CREATE_PATH')
        require(io.write(fd,raw)==len(raw),'PRIVATE_SHORT_WRITE')
        io.fsync(fd); before=io.fstat(fd)
        require(file_ok(before,b) and before['size']==len(raw) and custody(before)==custody(created),'PRIVATE_WRITTEN_SHAPE')
        require(io.lstat(private_fd,PRIVATE_NAME)==before,'PRIVATE_WRITE_PATH')
        io.rewind(fd); chunks=[]; total=0; eof=False
        for _ in range(129):
            part=io.read(fd,min(65536,BODY_MAX+1-total)); chunks.append(part); total+=len(part)
            require(total<=BODY_MAX,'PRIVATE_READBACK_LIMIT')
            if not part:eof=True; break
        actual=b''.join(chunks)
        require(eof and actual==raw,'PRIVATE_READBACK_BYTES')
        require(io.fstat(fd)==before and io.lstat(private_fd,PRIVATE_NAME)==before,'PRIVATE_READBACK_IDENTITY')
        final=io.fstat(private_fd)
        require(directory_ok(final,b) and custody(final)==custody(initial) and io.lstat(episode,'private')==final,'PRIVATE_DIRECTORY_FINAL')
        require(io.list_names(private_fd)==[PRIVATE_NAME],'PRIVATE_FINAL_INVENTORY')
        return sha(actual)
    finally:io.close(fd)

def produce(episode_fd:int,expected_binding:dict,public_schema_bytes:bytes,io=None)->bytes:
    """Return closed public JSON; retain sole exclusive private receipt if possible."""
    io=PosixIO() if io is None else io
    public=dict(schema='dg17.claude.routing.fixed-host-census.v1',status='INCOMPLETE_OR_REFUSED',rows=[],private_receipt_sha256=None,body_content_published=False,startup_semantics_accepted=False,native_processes_started=0,target_commands_started=0,source_effect_authority='NONE',failure=None)
    private_fd=None
    try:
        require(type(episode_fd) is int and episode_fd>=3,'EPISODE_DESCRIPTOR')
        validate(expected_binding,BINDING); b=json.loads(canonical(expected_binding))
        require(type(public_schema_bytes) is bytes and sha(public_schema_bytes)==b['public_schema_sha256'],'PUBLIC_SCHEMA_BINDING')
        uid,gid,platform=io.runtime()
        require((uid,gid,platform)==(b['execution_uid'],b['execution_gid'],b['platform']) and (uid,gid)==(b['evidence_uid'],b['evidence_gid']),'EXECUTION_BINDING')
        require(kind(io.fstat(episode_fd))=='DIRECTORY','EPISODE_KIND')
        initial=io.lstat(episode_fd,'private'); require(directory_ok(initial,b),'PRIVATE_DIRECTORY_SHAPE')
        private_fd=io.directory(episode_fd,'private')
        require(io.fstat(private_fd)==initial and io.lstat(episode_fd,'private')==initial,'PRIVATE_DIRECTORY_OPEN')
        require(io.list_names(private_fd)==[],'PRIVATE_INVENTORY')
        cuts=[]
        for _ in range(2):
            observer=Observer(io); cuts.append([observer.observe(path,role) for _,path,role in POPULATION])
        records=[]
        for index,(fixed,path,role) in enumerate(POPULATION):
            a,z=cuts[0][index],cuts[1][index]
            records.append(dict(fixed_id=fixed,before=a,after=z))
            public['rows'].append(project_record(fixed,path,role,a,z))
        receipt=dict(schema='dg17.claude.d0.private-receipt.v1',binding=b,records=records,retained_evidence_files=[PRIVATE_NAME],root_failure=None)
        validate(receipt,PRIVATE)
        raw=canonical(receipt)
        public['private_receipt_sha256']=output(io,episode_fd,private_fd,initial,b,raw)
        public['failure']=population_failure(records) or next((r['error_code'] for r in public['rows'] if r['error_code'] is not None),None)
        if public['failure'] is None:public['status']='RECEIVED_FIXED_HOST_INPUTS'
    except (NotImplementedError,AttributeError):public['failure']='UNSUPPORTED_PRIMITIVE'
    except Refused as exc:public['failure']=exc.code
    except OSError:public['failure']='PRODUCER_OS_ERROR'
    finally:
        if private_fd is not None:io.close(private_fd)
    validate(public,PUBLIC); raw=canonical(public)
    require(len(raw)<=16384,'PUBLIC_BYTES_LIMIT')
    return raw
