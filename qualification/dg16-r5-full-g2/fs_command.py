"""Fixed CMS command body and outcome checks. Importing this module has no effects."""
import os
import resource
import stat
import sys
import fs_protocol as P

CAPTURE_MAX=32768
# CMS buffering allowance only; enrollment retains its accepted ceiling.
MEMORY_BYTES=1024*1024**2
RECIPIENT_MEMORY_BYTES=512*1024**2
CPU_SECONDS=60
ROLES={'encrypt':('plain','certificate','cipher'),'decrypt':('cipher','certificate','key','quarantine'),
       'recipient':('key','certificate')}  # Only the separately admitted synthetic witness selects this role.

def cms_argv(operation,files):
    P.need(operation in ROLES and type(files) is dict and set(files)==set(ROLES[operation]),'FIXED_CMS_OPERATION')
    fds=list(files.values());P.need(all(P.integer(fd,3,2**20) for fd in fds) and len(set(fds))==len(fds),'HELD_FDS')
    f={name:'/proc/self/fd/'+str(fd) for name,fd in files.items()}
    if operation=='recipient':
        args=['req','-x509','-newkey','rsa:3072','-noenc','-sha256','-days','1','-subj','/CN=DG16-failed-stream-witness-recipient',
          '-keyout',f['key'],'-out',f['certificate']]
    elif operation=='encrypt':
        args=['cms','-encrypt','-binary','-aes-256-gcm','-in',f['plain'],'-outform','DER','-out',f['cipher'],
          '-recip',f['certificate'],'-keyopt','rsa_padding_mode:oaep','-keyopt','rsa_oaep_md:sha256','-keyopt','rsa_mgf1_md:sha256']
    else:
        args=['cms','-decrypt','-binary','-inform','DER','-in',f['cipher'],'-recip',f['certificate'],
          '-inkey',f['key'],'-out',f['quarantine']]
    return ['/usr/bin/env','-i','PATH=/usr/bin:/bin','LC_ALL=C','OPENSSL_CONF=/dev/null','/usr/bin/openssl',*args]

def validate_capture(records,rc,stdout,stderr):
    P.need(type(records) is list and len(records)==1 and type(records[0]) is dict,'COMMAND_CAPTURE_POPULATION')
    P.need(type(stdout) is bytes and type(stderr) is bytes and len(stdout)<=CAPTURE_MAX and len(stderr)<=CAPTURE_MAX,
      'COMMAND_STREAM_BOUND')
    r=records[0]
    P.need(P.integer(rc,-255,255) and type(r.get('returncode')) is int and r['returncode']==rc
      and r.get('process_started') is True and r.get('pidfd_acquired') is True and r.get('streams_complete') is True
      and type(r.get('cleanup')) is dict and r['cleanup'].get('echild') is True
      and r['cleanup'].get('restoration_complete') is True
      and 'internal_failure' in r and r['internal_failure'] is None and r.get('timeout') is False
      and r.get('output_bound_exceeded') is False,'COMMAND_CUSTODY_INCOMPLETE')
    for name,raw in (('stdout',stdout),('stderr',stderr)):
        P.need(type(r.get(name+'_bytes')) is int and r[name+'_bytes']==len(raw)
          and r.get(name+'_sha256')==P.sha(raw),'COMMAND_STREAM_JOIN')
    return rc

def auth_enveloped(reader,size):
    """Bounded DER ContentInfo type check only. OpenSSL verifies the GCM tag."""
    P.need(P.integer(size,1,P.CIPHER_MAX),'CIPHERTEXT_BOUND');position=0
    def take(n):
        nonlocal position
        P.need(0<n<=32 and position+n<=min(size,96),'CMS_HEADER_BOUND')
        raw=reader.read(n);P.need(type(raw) is bytes and len(raw)==n,'CMS_HEADER_SHORT');position+=n;return raw
    def tlv(tag):
        P.need(take(1)[0]==tag,'CMS_AUTH_ENVELOPED_TYPE');b=take(1)[0]
        if b&128:
            width=b&127;P.need(1<=width<=4,'CMS_DEFINITE_DER_LENGTH');raw=take(width)
            P.need(raw[0]!=0,'CMS_DER_LENGTH');length=int.from_bytes(raw,'big');P.need(length>=128,'CMS_DER_LENGTH')
        else:length=b
        P.need(position+length<=size,'CMS_DER_LENGTH');return position,position+length
    _,end=tlv(0x30);P.need(end==size,'CMS_DER_TRAILING')
    start,oid_end=tlv(0x06);P.need(oid_end-start==11 and take(11)==bytes.fromhex('2a864886f70d0109100117'),'CMS_AUTH_ENVELOPED_TYPE')
    _,explicit_end=tlv(0xa0);inner_start,inner_end=tlv(0x30)
    P.need(explicit_end==end and inner_end==end and inner_start<inner_end,'CMS_AUTH_ENVELOPED_CONTAINER')
    return True

def bounded_limit(kind,maximum):
    soft,hard=resource.getrlimit(kind)
    target=min([maximum]+[n for n in (soft,hard) if n!=resource.RLIM_INFINITY])
    P.need(target>0,'RESOURCE_LIMIT_UNAVAILABLE');resource.setrlimit(kind,(target,target))
    P.need(resource.getrlimit(kind)==(target,target),'RESOURCE_LIMIT_READBACK')

def child_main(argv):
    """Only the separately admitted held-child command path calls this."""
    P.need(len(argv)>=3 and argv[0] in ROLES,'CHILD_ARGUMENTS')
    operation=argv[0];maximum=int(argv[1]);fds=tuple(int(n) for n in argv[2:])
    ceiling=P.CIPHER_MAX if operation=='encrypt' else P.PLAIN_MAX if operation=='decrypt' else 8192
    P.need(len(fds)==len(ROLES[operation]) and P.integer(maximum,1,ceiling),
      'CHILD_BOUND')
    files=dict(zip(ROLES[operation],fds));command=cms_argv(operation,files)
    for fd in fds:
        info=os.fstat(fd);P.need(stat.S_ISREG(info.st_mode) and info.st_uid==os.geteuid() and info.st_nlink==1
          and stat.S_IMODE(info.st_mode) in (0o400,0o600),'CHILD_HELD_FILE')
    outputs=('key','certificate') if operation=='recipient' else ('cipher',) if operation=='encrypt' else ('quarantine',)
    P.need(all(os.fstat(files[n]).st_size==0 for n in outputs),'CHILD_OUTPUT_NOT_EMPTY')
    bounded_limit(resource.RLIMIT_AS,RECIPIENT_MEMORY_BYTES if operation=='recipient' else MEMORY_BYTES);bounded_limit(resource.RLIMIT_CPU,CPU_SECONDS)
    bounded_limit(resource.RLIMIT_FSIZE,maximum)
    limits=b'DG16_CMS_LIMITS '+P.encode(dict(schema='dg16.cms-child-actual-limits.v1',
      address_space=list(resource.getrlimit(resource.RLIMIT_AS)),cpu=list(resource.getrlimit(resource.RLIMIT_CPU)),
      file_size=list(resource.getrlimit(resource.RLIMIT_FSIZE))))
    P.need(os.write(1,limits)==len(limits),'CHILD_LIMITS_RECORD')
    os.chdir('/')
    os.execve('/usr/bin/env',command,{'PATH':'/usr/bin:/bin','LC_ALL':'C','OPENSSL_CONF':'/dev/null'})

if __name__=='__main__':
    # The immutable loader supplies fs_protocol; isolated Python callers must
    # use the bound launcher that adds only this owned component directory.
    if len(sys.argv)>1 and sys.argv[1]=='--child':child_main(sys.argv[2:])
    else:raise SystemExit('EXPLICIT_BOUND_CHILD_REQUIRED')
