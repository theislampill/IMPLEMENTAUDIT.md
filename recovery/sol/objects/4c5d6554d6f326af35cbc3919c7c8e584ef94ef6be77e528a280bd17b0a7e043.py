"""Public package authentication/extraction only; no installation or Git effects."""
import gzip, hashlib, io, json, lzma, os, re, stat, subprocess, sys, tarfile, urllib.request
from pathlib import Path

ROOT=Path('/home/agent/sol-git256-package-probe-20261109-01')
PPA='https://ppa.launchpadcontent.net/git-core/ppa/ubuntu/'
FPR='F911AB184317630C59970973E363C90F8F1B6217'
EXPECTED='824d5b2fffef332ec7ba053e579659bb12f26a0b4747da6f9c6dc0e71d36f235'

def need(ok, code):
    if not ok:raise ValueError(code)

def sha(raw):return hashlib.sha256(raw).hexdigest()

def fetch(url,name,cap):
    if (ROOT/name).exists():
        raw=(ROOT/name).read_bytes()
        need(0<len(raw)<=cap,'RETAINED_PUBLIC_DOWNLOAD_BOUND')
        return raw
    request=urllib.request.Request(url,headers={'User-Agent':'DG16-public-package-receiving/1'})
    with urllib.request.urlopen(request,timeout=30) as response:
        need(response.status==200 and response.geturl()==url,'PUBLIC_ENDPOINT_REDIRECT_OR_STATUS')
        raw=response.read(cap+1)
    need(0<len(raw)<=cap,'PUBLIC_DOWNLOAD_BOUND')
    with (ROOT/name).open('xb') as f:f.write(raw)
    return raw

def call(args,timeout=30):
    result=subprocess.run(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                          timeout=timeout,check=False)
    need(len(result.stdout)<=2*1024**2 and len(result.stderr)<=2*1024**2,'TOOL_OUTPUT_BOUND')
    return result

def main():
    need(sys.platform=='linux' and os.getuid()==os.geteuid()>0,'NONROOT_LINUX_REQUIRED')
    ROOT.mkdir(mode=0o700,exist_ok=True)
    need(ROOT.resolve()==ROOT and stat.S_IMODE(ROOT.stat().st_mode)==0o700 and ROOT.stat().st_uid==os.geteuid(),
         'PRIVATE_SCRATCH_CUSTODY')
    gpg=ROOT/'gpg';gpg.mkdir(mode=0o700,exist_ok=True)
    inrelease=fetch(PPA+'dists/noble/InRelease','InRelease',256*1024)
    key=fetch('https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x'+FPR,'KEY.asc',128*1024)
    imported=call(['/usr/bin/gpg','--no-options','--homedir',str(gpg),'--batch','--import',str(ROOT/'KEY.asc')])
    need(imported.returncode==0,'PUBLIC_KEY_IMPORT_FAILED')
    # The actual InRelease is co-signed by the published current key and the
    # older key named in its second signature. Preserve the failed first
    # verification and supply that public co-signing key in this scratch only.
    legacy='E1DD270288B4E6030699E45FA1715D88E1DF1F24'
    fetch('https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x'+legacy,'LEGACY_KEY.asc',128*1024)
    imported=call(['/usr/bin/gpg','--no-options','--homedir',str(gpg),'--batch','--import',str(ROOT/'LEGACY_KEY.asc')])
    need(imported.returncode==0,'PUBLIC_COSIGNING_KEY_IMPORT_FAILED')
    listed=call(['/usr/bin/gpg','--no-options','--homedir',str(gpg),'--batch','--with-colons','--fingerprint'])
    need(listed.returncode==0 and (':'+FPR+':').encode() in listed.stdout,'PUBLISHED_PPA_FINGERPRINT_MISMATCH')
    verified=call(['/usr/bin/gpg','--no-options','--homedir',str(gpg),'--batch','--status-fd','2','--decrypt',str(ROOT/'InRelease')])
    (ROOT/'GPG_VERIFICATION.txt').write_bytes(verified.stderr)
    need(verified.returncode==0 and b'[GNUPG:] VALIDSIG '+FPR.encode()+b' ' in verified.stderr
         and b'[GNUPG:] VALIDSIG '+legacy.encode()+b' ' in verified.stderr,'PPA_INRELEASE_SIGNATURE_FAILED')
    release=verified.stdout
    (ROOT/'VERIFIED_RELEASE.txt').write_bytes(release)
    members={}
    section=None
    for line in release.decode('utf8').splitlines():
        if line and not line.startswith(' '):section=line.split(':',1)[0]
        if section=='SHA256' and line.startswith(' '):
            digest,size,name=line.split();members[name]=(digest,int(size))
    rel='main/binary-amd64/Packages.xz';need(rel in members,'SIGNED_PACKAGES_INDEX_MISSING')
    packed=fetch(PPA+'dists/noble/'+rel,'Packages.xz',1024**2)
    need((sha(packed),len(packed))==members[rel],'SIGNED_PACKAGES_INDEX_CHANGED')
    index=lzma.decompress(packed);need(len(index)<=2*1024**2,'EXPANDED_PACKAGES_BOUND')
    (ROOT/'Packages').write_bytes(index)
    packages=[]
    for paragraph in index.decode().split('\n\n'):
        fields={}
        for line in paragraph.splitlines():
            if line and not line.startswith((' ','\t')) and ': ' in line:
                k,v=line.split(': ',1);fields[k]=v
        if fields.get('Package')=='git' and fields.get('Architecture')=='amd64':packages.append(fields)
    need(len(packages)==1,'EXACT_GIT_PACKAGE_POPULATION')
    package=packages[0];need(re.fullmatch(r'(?:1:)?2\.56\.0-[A-Za-z0-9.~+]+',package['Version']) is not None,'NO_VERSION_MATCHED_CHEAP_PACKAGE')
    name=package['Filename'];need(name.startswith('pool/main/g/git/') and '..' not in Path(name).parts,'FIXED_PUBLIC_PACKAGE_PATH')
    deb=fetch(PPA+name,'git.deb',16*1024**2)
    need(len(deb)==int(package['Size']) and sha(deb)==package['SHA256'],'SIGNED_DEB_DIGEST_CHANGED')
    tarpath=ROOT/'package.tar'
    with tarpath.open('xb') as target:
        unpacked=subprocess.run(['/usr/bin/dpkg-deb','--fsys-tarfile',str(ROOT/'git.deb')],
                                stdin=subprocess.DEVNULL,stdout=target,stderr=subprocess.PIPE,
                                timeout=30,check=False)
    need(unpacked.returncode==0 and 0<tarpath.stat().st_size<=128*1024**2,'PACKAGE_TAR_BOUND')
    package_root=ROOT/'package';package_root.mkdir(mode=0o700)
    with tarfile.open(tarpath) as archive:
        need(len(archive.getmembers())<=4096 and sum(m.size for m in archive.getmembers())<=128*1024**2,
             'PACKAGE_MEMBER_BOUND')
        archive.extractall(package_root,filter='data')
    executable=package_root/'usr/bin/git'
    need(executable.resolve(strict=True)==executable and stat.S_ISREG(executable.lstat().st_mode),
         'PACKAGE_EXECUTABLE_NOT_ORDINARY')
    executable_sha=sha(executable.read_bytes())
    env=dict(os.environ,GIT_CONFIG_NOSYSTEM='1',GIT_CONFIG_SYSTEM='/dev/null',GIT_CONFIG_GLOBAL='/dev/null',
             GIT_EXEC_PATH=str(package_root/'usr/lib/git-core'),GIT_TERMINAL_PROMPT='0')
    version=subprocess.run([str(executable),'--version'],env=env,stdin=subprocess.DEVNULL,
                           stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=10,check=False)
    need(version.returncode==0 and version.stdout==b'git version 2.56.0\n','EXTRACTED_VERSION_REFUSED')
    receipt=dict(schema='dg16.git256-public-package-receiving.v1',scope='PACKAGE_EXTRACTION_ONLY_NO_INSTALLATION',
        ppa=PPA,published_signing_fingerprint=FPR,signature_verified=True,
        inrelease_sha256=sha(inrelease),packages_sha256=sha(packed),package=package,
        executable=dict(path=str(executable),bytes=executable.stat().st_size,sha256=executable_sha,
                        matches_original_host_sha256=executable_sha==EXPECTED),
        version=dict(returncode=version.returncode,stdout=version.stdout.decode(),stderr=version.stderr.decode()),
        distro_git=dict(path='/usr/bin/git',sha256=sha(Path('/usr/bin/git').read_bytes())),
        git_repository_operations=0,installed=False,global_config_or_credentials_changed=False)
    (ROOT/'PACKAGE_RECEIVING.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))

if __name__=='__main__':main()
