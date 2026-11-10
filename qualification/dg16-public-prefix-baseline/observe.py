"""Read-only finite public-prefix source proposal. Root host admission required.

No attribute names/values or stat fields are emitted. No aliases are followed,
no directory is enumerated, no files are read and no setup or command is run.
The caller receives stdout under its separate admitted evidence custody.
"""
import argparse,json,os,signal,stat,time

PREFIXES=(
    ('S00','/usr'),('S01','/usr/bin'),('S02','/usr/lib'),
    ('S03','/usr/lib/python3.12'),('S04','/usr/lib/x86_64-linux-gnu'),
    ('S05','/usr/lib64'),('S06','/usr/share'),('S07','/usr/share/git-core'),
    ('S08','/usr/share/git-core/templates'),('S09','/usr/share/git-core/templates/hooks'),
    ('S10','/usr/share/git-core/templates/info'),('S11','/etc'),
    ('S12','/bin'),('S13','/lib'),('S14','/lib64'),('S15','/lib/x86_64-linux-gnu'))
MAX_SECONDS=15


def stamp(s):
    return (s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_uid,s.st_gid)


def observe(identifier,path):
    fds=[];result=dict(id=identifier,status='UNAVAILABLE',opened_stamp_stable=None,xattr_present=None,closing_stamp_stable=None,errno=None)
    try:
        parent=os.open('/',os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC);fds.append(parent)
        parts=path[1:].split('/');assert 1<=len(parts)<=6
        for part in parts:
            info=os.stat(part,dir_fd=parent,follow_symlinks=False)
            if stat.S_ISLNK(info.st_mode):result['status']='ALIAS_NOT_DEREFERENCED';return result
            if not stat.S_ISDIR(info.st_mode):result['status']='NOT_DIRECTORY';return result
            child=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW|os.O_CLOEXEC,dir_fd=parent);fds.append(child)
            opened=os.fstat(child)
            if stamp(opened)!=stamp(info):result.update(status='OPEN_STATE_CHANGED',opened_stamp_stable=False);return result
            parent=child
        before=os.fstat(parent);present=bool(os.listxattr(parent));after=os.fstat(parent)
        result.update(status='OBSERVED',opened_stamp_stable=True,xattr_present=present,
                      closing_stamp_stable=stamp(before)==stamp(after))
        if not result['closing_stamp_stable']:result['status']='READ_STATE_CHANGED'
        return result
    except TimeoutError:
        raise
    except OSError as error:
        result['status']='MISSING' if error.errno==2 else 'UNAVAILABLE'
        result['errno']=error.errno if type(error.errno) is int and 0<=error.errno<=4095 else None
        return result
    finally:
        for fd in reversed(fds):os.close(fd)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--phase',choices=('IMAGE_BASELINE','AFTER_ALREADY_AUTHORIZED_SELECTED_SETUP'),required=True)
    args=p.parse_args()
    # This is the original R5 visibility contract, not a new root entitlement.
    if (os.getuid(),os.geteuid(),os.getgid(),os.getegid())!=(0,0,0,0):
        raise SystemExit('PUBLIC_PREFIX_OBSERVER_REQUIRES_SEPARATELY_ADMITTED_R5_UID0_HOST')
    if signal.getitimer(signal.ITIMER_REAL)!=(0.0,0.0):raise SystemExit('EXISTING_WATCHDOG_PRESENT')
    prior=signal.getsignal(signal.SIGALRM)
    def expired(*_):raise TimeoutError('PUBLIC_PREFIX_OBSERVATION_DEADLINE')
    signal.signal(signal.SIGALRM,expired);signal.setitimer(signal.ITIMER_REAL,MAX_SECONDS)
    start=time.monotonic_ns()
    try:
        rows=[observe(identifier,path) for identifier,path in PREFIXES]
        result=dict(schema='dg16.finite-public-system-prefix-xattr-presence.v1',authority='NONE',effect_grant=False,
            phase=args.phase,rows=rows,read_only_scope='EXACT_SOURCE_ALLOWLIST; NO_TRAVERSAL_BEYOND_DECLARED_COMPONENTS',
            observer_seconds=MAX_SECONDS,elapsed_ns=time.monotonic_ns()-start,
            host_identity='ROOT_MUST_BIND_ACTUAL_PROVIDER_RUN_JOB_ATTEMPT_IMAGE_AND_PHASE_LINEAGE',
            historical_G114_cause='NOT_ESTABLISHED_BY_A_NEW_HOST',
            scope_limit='PREFIX_ONLY_NOT_COMPLETE_RUNTIME_TOPOLOGY; ALIASES_AND_DEEPER_HOPS_UNPROVED',
            setup_executed=False,security_or_attribute_changes=0,native_or_G1_banks=0,original_awards=[])
        raw=(json.dumps(result,sort_keys=True,separators=(',',':'))+'\n').encode()
        if len(raw)>16384:raise ValueError('PUBLIC_PREFIX_OUTPUT_BOUND')
        os.write(1,raw)
    finally:
        signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,prior)


if __name__=='__main__':main()
