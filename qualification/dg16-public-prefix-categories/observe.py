"""Source-bound category-only proposal. No host execution authority.

Names returned by listxattr remain process-local; no values are read. Output
contains only fixed IDs, availability and bounded category counts. This does
not authorize a metadata projection, omission, policy change or later read.
"""
import json,os,signal,stat,sys,time

PREFIXES=(('S06','/usr/share'),('S07','/usr/share/git-core'),
          ('S08','/usr/share/git-core/templates'),
          ('S09','/usr/share/git-core/templates/hooks'),
          ('S10','/usr/share/git-core/templates/info'))
CATEGORIES=('POSIX_ACCESS_ACL','POSIX_DEFAULT_ACL','USER_NAMESPACE','SECURITY_NAMESPACE','UNKNOWN')
MAX_SECONDS=15
MAX_NAMES_PER_DIRECTORY=64
MAX_NAME_BYTES=255
MAX_TOTAL_NAME_BYTES=16384
MAX_OUTPUT_BYTES=16384


class Refusal(ValueError):
    """Only fixed public reason enums may escape a source-control check."""


def stamp(s):
    return (s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_uid,s.st_gid)


def classify_names(names,budget):
    if type(names) is not list:raise Refusal('NAME_LIST_SHAPE')
    if len(names)>MAX_NAMES_PER_DIRECTORY:raise Refusal('NAME_COUNT_BOUND')
    counts={category:0 for category in CATEGORIES}
    seen=set();total=budget['name_bytes']
    try:
        for name in names:
            if type(name) is not str or not 0<len(name)<=MAX_NAME_BYTES:raise Refusal('NAME_LENGTH_OR_SHAPE')
            try:raw=os.fsencode(name)
            except UnicodeError:raise Refusal('NAME_LENGTH_OR_SHAPE') from None
            if not 0<len(raw)<=MAX_NAME_BYTES or b'\0' in raw:raise Refusal('NAME_LENGTH_OR_SHAPE')
            if raw in seen:raise Refusal('DUPLICATE_NAME')
            total+=len(raw)
            if total>MAX_TOTAL_NAME_BYTES:raise Refusal('TOTAL_NAME_BYTES_BOUND')
            seen.add(raw)
            if name=='system.posix_acl_access':category='POSIX_ACCESS_ACL'
            elif name=='system.posix_acl_default':category='POSIX_DEFAULT_ACL'
            elif name.startswith('user.') and len(name)>5:category='USER_NAMESPACE'
            elif name.startswith('security.') and len(name)>9:category='SECURITY_NAMESPACE'
            else:category='UNKNOWN'
            counts[category]+=1
        budget['name_bytes']=total
        return counts
    finally:
        # No attribute identity is retained in an output or persistent record.
        seen.clear()


def observe(identifier,path,budget):
    fds=[]
    result=dict(id=identifier,status='UNAVAILABLE',counts=None,errno=None)
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);fds.append(parent)
        parts=path[1:].split('/');assert 1<=len(parts)<=6
        for part in parts:
            info=os.stat(part,dir_fd=parent,follow_symlinks=False)
            if stat.S_ISLNK(info.st_mode):result['status']='ALIAS_NOT_DEREFERENCED';return result
            if not stat.S_ISDIR(info.st_mode):result['status']='NOT_DIRECTORY';return result
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);fds.append(child)
            if stamp(os.fstat(child))!=stamp(info):result['status']='OPEN_STATE_CHANGED';return result
            parent=child
        before=os.fstat(parent)
        names=os.listxattr(parent)  # Sole name observation, exactly once per selected directory.
        try:counts=classify_names(names,budget)
        finally:names.clear()
        if stamp(os.fstat(parent))!=stamp(before):result['status']='READ_STATE_CHANGED';return result
        result.update(status='OBSERVED',counts=counts)
        return result
    except TimeoutError:
        raise
    except OSError as error:
        result['status']='MISSING' if error.errno==2 else 'UNAVAILABLE'
        result['errno']=error.errno if type(error.errno) is int and 0<=error.errno<=4095 else None
        return result
    finally:
        for fd in reversed(fds):os.close(fd)


def emit(result):
    raw=(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n').encode()
    if len(raw)>MAX_OUTPUT_BYTES:raise Refusal('OUTPUT_BOUND')
    # Stdout only. The independently admitted caller owns its receiving path.
    view=memoryview(raw)
    while view:
        amount=os.write(1,view)
        if amount<=0:raise Refusal('OUTPUT_UNAVAILABLE')
        view=view[amount:]


def main():
    if len(sys.argv)!=1:raise Refusal('NO_UNBOUND_ARGUMENTS')
    if (os.getuid(),os.geteuid(),os.getgid(),os.getegid())!=(0,0,0,0):raise Refusal('ADMITTED_R5_UID0_REQUIRED')
    if signal.getitimer(signal.ITIMER_REAL)!=(0.0,0.0):raise Refusal('EXISTING_WATCHDOG_PRESENT')
    previous=signal.getsignal(signal.SIGALRM)
    def expired(*_):raise TimeoutError('CATEGORY_OBSERVATION_DEADLINE')
    signal.signal(signal.SIGALRM,expired);signal.setitimer(signal.ITIMER_REAL,MAX_SECONDS)
    try:
        budget={'name_bytes':0}
        rows=[observe(identifier,path,budget) for identifier,path in PREFIXES]
        # Incomplete or raced reads cannot be interpreted as absent categories.
        complete=all(row['status']=='OBSERVED' for row in rows)
        emit(dict(schema='dg16.fixed-public-prefix-xattr-categories.v1',authority='NONE',effect_grant=False,
            status='OBSERVED_FIXED_CATEGORIES' if complete else 'INCOMPLETE',rows=rows,
            metadata_values_read=False,names_exported=False,setup_executed=False,
            representation_or_later_access_authorized=False,original_awards=[]))
        return 0 if complete else 1
    except TimeoutError:
        emit(dict(schema='dg16.fixed-public-prefix-xattr-categories.v1',authority='NONE',effect_grant=False,
                  status='REFUSED_TIMEOUT',rows=[],original_awards=[]));return 1
    except Refusal as error:
        emit(dict(schema='dg16.fixed-public-prefix-xattr-categories.v1',authority='NONE',effect_grant=False,
                  status='REFUSED_BOUND_OR_SHAPE',reason=str(error),rows=[],original_awards=[]));return 1
    finally:
        signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,previous)


if __name__=='__main__':
    try:raise SystemExit(main())
    except Refusal:
        # Preconditions fail closed without echoing arguments, paths or names.
        os.write(1,b'{"authority":"NONE","effect_grant":false,"status":"REFUSED_PRECONDITION","rows":[]}\n')
        raise SystemExit(1)
