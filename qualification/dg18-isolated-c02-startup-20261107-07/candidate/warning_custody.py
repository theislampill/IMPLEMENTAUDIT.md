#!/usr/bin/env python3
"""Closed, request-bound encrypted custody for one already observed OTHER warning.

No native launch, admission, network, provider, plaintext export or private-key lookup.
Authenticated encryption does not authenticate a sender holding only a public key;
the receiver also requires the separately received hosted artifact digest/provenance.
"""
from pathlib import Path
import base64
import hashlib
import importlib.machinery
import json
import os
import re
import stat
import sys
import types

SUITE = 'X25519-HKDF-SHA256-AES256GCM'
ENVELOPE_SCHEMA = 'dg18.c02.warning-envelope.v1'
RECIPIENT_SCHEMA = 'dg18.c02.warning-recipient.v1'
STATUS_SCHEMA = 'dg18.c02.warning-custody-status.v1'
RECIPIENT_SHA256 = '44ebd3403a81e99516a5f742a0886c018c444c982cce6e40d47110362f1543e4'
SOURCE = '35bf9823856eb4efe254b882954120480632230e'
UPSTREAM = '6ff1e1ca3b30fc8b914720681fcf5fe62e95f856'
MAX_FRAME = 65536
MAX_CAPTURE = 262144
PADDED_BYTES = 4 + MAX_FRAME
CIPHERTEXT_BYTES = PADDED_BYTES + 16
MAX_ENVELOPE = 90000
MAX_MANIFEST = 65536
DOMAIN = b'dg18.c02.warning-custody.v1\x00'
STAT_KEYS = ('st_dev','st_ino','st_mode','st_uid','st_nlink','st_size','st_mtime_ns','st_ctime_ns')
STATUSES = {'NOT_REACHED','NOT_REQUIRED','CLEANUP_UNRESOLVED','CAPTURE_REFUSED',
            'CRYPTO_REFUSED','WRITE_FAILED','SEALED'}
PREFLIGHT_ROLES = {'SOURCE','CACHE','EXTENSION','LIBRARY','UNKNOWN'}
PREFLIGHT_CODES = {'CRYPTO_VERSION_REFUSED','CRYPTO_UNAVAILABLE','CRYPTO_SYSTEM_LOCATION','CRYPTO_SYSTEM_OWNERSHIP',
    'CRYPTO_MEMBER_BOUND','CRYPTO_MEMBER_CHANGED','CRYPTO_MEMBER_UNREADABLE','CRYPTO_SELF_TEST','CRYPTO_BACKEND_VERSION',
    'CRYPTO_MODULE_NAME','CRYPTO_MODULE_PROXY','CRYPTO_EMBEDDED_MODULE','CRYPTO_IMPORT_LOADER','CRYPTO_MAPS_BOUND',
    'CRYPTO_LIBRARY_BOUND','CRYPTO_POPULATION','CRYPTO_TOTAL_BOUND','CRYPTO_MANIFEST_BOUND','CRYPTO_DEPENDENCY_REFUSED',
    'RECIPIENT_FILE_BOUND','RECIPIENT_CHANGED','RECIPIENT_DESCRIPTOR','RECIPIENT_PIN','RECIPIENT_KEY_REFUSED',
    'CUSTODY_JSON_BOUND','CUSTODY_DUPLICATE_KEY','CUSTODY_NONFINITE','CUSTODY_JSON_REFUSED',
    'CUSTODY_REQUEST_BINDING','CRYPTO_PREIMAGE_CHANGED','OTHER_CUSTODY_REFUSAL'}

class CustodyRefusal(ValueError):
    def __init__(self,code,role='UNKNOWN'):
        super().__init__(code)
        self.code=code
        self.role=role

def closed_preflight_failure(exc):
    if type(exc) is not CustodyRefusal:
        return None
    return {'reason':exc.code if type(exc.code) is str and exc.code in PREFLIGHT_CODES else 'OTHER_CUSTODY_REFUSAL',
            'module_role':exc.role if type(exc.role) is str and exc.role in PREFLIGHT_ROLES else 'UNKNOWN'}

def need(ok, code):
    if not ok:
        raise CustodyRefusal(code)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(value):
    return (json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')

def digest(value):
    return type(value) is str and re.fullmatch('[0-9a-f]{64}',value) is not None

def parse(raw, maximum):
    need(type(raw) is bytes and 0 < len(raw) <= maximum, 'CUSTODY_JSON_BOUND')
    def pairs(items):
        out={}
        for key,value in items:
            need(key not in out, 'CUSTODY_DUPLICATE_KEY')
            out[key]=value
        return out
    def bad(_):
        raise CustodyRefusal('CUSTODY_NONFINITE')
    try:
        return json.loads(raw.decode('ascii'),object_pairs_hook=pairs,parse_constant=bad)
    except Exception:
        raise CustodyRefusal('CUSTODY_JSON_REFUSED') from None

def primitives():
    try:
        import cryptography
        from cryptography.hazmat.backends.openssl.backend import backend
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF
        need(re.fullmatch(r'[0-9]+(?:\.[0-9]+){1,3}',cryptography.__version__) is not None
             and int(cryptography.__version__.split('.')[0]) >= 41, 'CRYPTO_VERSION_REFUSED')
        return cryptography,backend,hashes,serialization,X25519PrivateKey,X25519PublicKey,AESGCM,HKDF
    except CustodyRefusal:
        raise
    except Exception:
        raise CustodyRefusal('CRYPTO_UNAVAILABLE') from None

def public_bytes(key, serialization):
    return key.public_bytes(serialization.Encoding.Raw,serialization.PublicFormat.Raw)

def system_file(path):
    """Exact imported source/cache/extension identity, restricted to system libraries."""
    p=Path(path)
    need(p.is_absolute() and '..' not in p.parts and any(p.is_relative_to(base)
        for base in (Path('/usr/lib'),Path('/usr/local/lib'))), 'CRYPTO_SYSTEM_LOCATION')
    for node in (p,*p.parents):
        st=node.lstat()
        need(not stat.S_ISLNK(st.st_mode) and st.st_uid==0 and not stat.S_IMODE(st.st_mode)&0o022,
             'CRYPTO_SYSTEM_OWNERSHIP')
    before=p.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and 0<before.st_size<=67108864,
         'CRYPTO_MEMBER_BOUND')
    stamp=lambda s: tuple(getattr(s,k) for k in STAT_KEYS)
    fd=os.open(p,os.O_RDONLY|os.O_NOFOLLOW)
    h=hashlib.sha256(); count=0
    try:
        need(stamp(before)==stamp(os.fstat(fd)), 'CRYPTO_MEMBER_CHANGED')
        while True:
            raw=os.read(fd,1048576)
            if not raw: break
            count+=len(raw);need(count<=67108864,'CRYPTO_MEMBER_BOUND');h.update(raw)
        need(count==before.st_size and stamp(before)==stamp(os.fstat(fd))==stamp(p.lstat()),
             'CRYPTO_MEMBER_CHANGED')
    finally:
        os.close(fd)
    return {'bytes':count,'sha256':h.hexdigest(),'identity':list(stamp(before))}

def openssl_map_paths(raw):
    """Return resolvable paths in the existing OpenSSL basename vocabulary.

    A deleted/ambiguous suffix is recognition evidence, never permission to strip
    it and hash a replacement file. No dynamic OpenSSL image is required: static
    implementations may have no relevant mappings. Malformed map records cannot
    establish an empty census. No pathname is included in a refusal.
    """
    try:
        lines=raw.decode('utf-8','strict').split('\n')
        if lines[-1]=='':
            lines.pop()
        libraries=set()
        for line in lines:
            parts=line.split(None,5)
            if len(parts) not in (5,6):
                raise ValueError
            address=re.fullmatch(r'([0-9a-fA-F]{1,16})-([0-9a-fA-F]{1,16})',parts[0])
            if (address is None or int(address[1],16)>=int(address[2],16) or
                re.fullmatch(r'[r-][w-][x-][ps]',parts[1]) is None or
                re.fullmatch(r'[0-9a-fA-F]{1,16}',parts[2]) is None or
                re.fullmatch(r'[0-9a-fA-F]{1,8}:[0-9a-fA-F]{1,8}',parts[3]) is None or
                re.fullmatch(r'[0-9]{1,20}',parts[4]) is None or int(parts[4])>18446744073709551615):
                raise ValueError
            if len(parts)==5:
                continue
            path=parts[5]
            name=Path(path).name
            match=re.match(r'lib(?:ssl|crypto)(?:-[0-9a-f]+)?\.so(?:\.[0-9]+)*(?=$|[\s\\\x00])',name)
            if match is None:
                continue
            if (match.end()!=len(name) or not Path(path).is_absolute() or
                '..' in Path(path).parts or '\\' in path or '\x00' in path or int(parts[4])==0):
                raise ValueError
            libraries.add(path)
        return libraries
    except Exception:
        raise CustodyRefusal('CRYPTO_MEMBER_UNREADABLE','LIBRARY') from None


def dependency_manifest():
    """Finite self-test and exact identities, before any admitted native allocation.

    No warning/private data enters this manifest. Python cache identities are retained
    as well as source identities so an imported cache is not silently omitted.
    """
    try:
        package,backend,hashes,s,Private,Public,AES,HKDF=primitives()
        a,b=Private.generate(),Private.generate()
        shared=a.exchange(Public.from_public_bytes(public_bytes(b.public_key(),s)))
        need(shared==b.exchange(a.public_key()),'CRYPTO_SELF_TEST')
        key=HKDF(algorithm=hashes.SHA256(),length=32,salt=b'\0'*32,info=DOMAIN).derive(shared)
        nonce=os.urandom(12); ciphertext=AES(key).encrypt(nonce,b'finite-self-test',DOMAIN)
        need(AES(key).decrypt(nonce,ciphertext,DOMAIN)==b'finite-self-test','CRYPTO_SELF_TEST')
        version=backend.openssl_version_text()
        need(type(version) is str and re.fullmatch(r'OpenSSL [0-9A-Za-z .+\-]{1,100}',version),
             'CRYPTO_BACKEND_VERSION')
        files=[]; embedded=[]; total=0
        def append_file(name,role,path):
            nonlocal total
            try:
                need(len(files)<128,'CRYPTO_POPULATION')
                declared=Path(path).lstat().st_size
                need(0<declared<=min(67108864,134217728-total),'CRYPTO_TOTAL_BOUND')
                row=system_file(path)
                need(row['bytes']==declared,'CRYPTO_MEMBER_CHANGED')
                total+=row['bytes'];need(total<=134217728,'CRYPTO_TOTAL_BOUND')
                files.append({'module':name,'role':role,**row})
            except CustodyRefusal as exc:
                raise CustodyRefusal(exc.code,role) from None
            except Exception:
                raise CustodyRefusal('CRYPTO_MEMBER_UNREADABLE',role) from None
        for name,module in sorted(tuple(sys.modules.items())):
            if not (name=='cryptography' or name.startswith('cryptography.') or
                    name=='cffi' or name.startswith('cffi.') or name=='_cffi_backend'):
                continue
            need(re.fullmatch('[A-Za-z0-9_.]{1,160}',name) is not None,'CRYPTO_MODULE_NAME')
            # cryptography replaces some modules with this exact deprecation proxy;
            # bind its underlying real module and the independently included utils code.
            proxy=getattr(package.utils,'_ModuleWithDeprecations',None)
            if proxy is not None and type(module) is proxy:
                module=vars(module).get('_module')
                need(type(module) is types.ModuleType and module.__name__==name,'CRYPTO_MODULE_PROXY')
            path=getattr(module,'__file__',None)
            if path is None:
                need(name.startswith('cryptography.hazmat.bindings._rust.'),'CRYPTO_EMBEDDED_MODULE')
                embedded.append(name);continue
            loader=getattr(getattr(module,'__spec__',None),'loader',None)
            need(type(loader) in (importlib.machinery.SourceFileLoader,importlib.machinery.ExtensionFileLoader),
                 'CRYPTO_IMPORT_LOADER')
            role='EXTENSION' if type(loader) is importlib.machinery.ExtensionFileLoader else 'SOURCE'
            append_file(name,role,path)
            cached=getattr(module,'__cached__',None)
            if cached is not None and Path(cached).exists():
                append_file(name,'CACHE',cached)
        # Bind any dynamically loaded OpenSSL libraries used by the imported extension.
        with open('/proc/self/maps','rb') as stream:
            maps=stream.read(1048577)
        need(len(maps)<=1048576,'CRYPTO_MAPS_BOUND')
        libraries=openssl_map_paths(maps)
        need(len(libraries)<=8,'CRYPTO_LIBRARY_BOUND')
        for path in sorted(libraries):
            append_file('openssl.'+Path(path).name,'LIBRARY',path)
        need(0<len(files)<=128 and any(row['role']=='EXTENSION' for row in files),'CRYPTO_POPULATION')
        need(total==sum(row['bytes'] for row in files),'CRYPTO_TOTAL_BOUND')
        out={'schema':'dg18.c02.crypto-dependencies.v1','suite':SUITE,'capability':'PASS',
             'cryptography_version':package.__version__,'openssl_version':version,
             'files':files,'embedded_modules':embedded,'total_bytes':total}
        need(len(canonical(out))<=MAX_MANIFEST,'CRYPTO_MANIFEST_BOUND')
        return out
    except CustodyRefusal:
        raise
    except Exception:
        raise CustodyRefusal('CRYPTO_DEPENDENCY_REFUSED') from None

def load_recipient():
    path=Path(__file__).resolve().parent/'RECIPIENT.json'
    before=path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and 0<before.st_size<=2048,'RECIPIENT_FILE_BOUND')
    stamp=lambda st:tuple(getattr(st,k) for k in STAT_KEYS)
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW)
    try:
        need(stamp(before)==stamp(os.fstat(fd)),'RECIPIENT_CHANGED')
        raw=os.read(fd,2049)
        need(len(raw)==before.st_size and stamp(before)==stamp(os.fstat(fd))==stamp(path.lstat()),'RECIPIENT_CHANGED')
    finally:
        os.close(fd)
    value=parse(raw,2048)
    need(type(value) is dict and set(value)=={'schema','suite','public_key_hex','recipient_sha256'}
         and value['schema']==RECIPIENT_SCHEMA and value['suite']==SUITE
         and digest(value['public_key_hex']) and value['recipient_sha256']==RECIPIENT_SHA256,
         'RECIPIENT_DESCRIPTOR')
    public=bytes.fromhex(value['public_key_hex'])
    need(sha(public)==RECIPIENT_SHA256,'RECIPIENT_PIN')
    _,_,_,_,Private,Public,_,_=primitives()
    try:
        Private.generate().exchange(Public.from_public_bytes(public))
    except Exception:
        raise CustodyRefusal('RECIPIENT_KEY_REFUSED') from None
    return value

def preflight(request):
    need(request.get('recipient_sha256')==RECIPIENT_SHA256 and digest(request.get('crypto_dependency_sha256')),
         'CUSTODY_REQUEST_BINDING')
    load_recipient()
    need(sha(canonical(dependency_manifest()))==request['crypto_dependency_sha256'],
         'CRYPTO_PREIMAGE_CHANGED')

def projection(raw, *, requested=False, replied=False, config=None):
    """Reuse the exact closed classifier without constructing or invoking a guard."""
    from startup_diagnostic import Observer,ConfigSnapshot,strict_json,load_pinned
    need(type(raw) is bytes and 0<len(raw)<=MAX_FRAME and b'\n' not in raw,'WARNING_FRAME_BOUND')
    message=strict_json(raw)
    need(type(message) is dict and message.get('method')=='configWarning','WARNING_METHOD')
    schema,variant,_,_=load_pinned()
    context=Observer.__new__(Observer)
    context.schema=schema;context.variant=variant;context.requested=requested;context.reply=replied
    context.config=config if config is not None else ConfigSnapshot(b'',sha(b''),'/fixture/home','/fixture/subject')
    result=Observer._warning(context,message)
    need(result['schema']=='VALID' and result['profile']=='CLOSED_STARTUP_WARNING'
         and result['category']=='OTHER_SCHEMA_VALID','OTHER_WARNING_REQUIRED')
    return result

def select_frame(capture, report, config=None):
    try:
        from startup_diagnostic import validate_public
        validate_public(report)
        need(type(capture) is bytes and len(capture)<=MAX_CAPTURE,'CAPTURE_BOUND')
        need(report['terminal'] in {'WARNING_GUARD_REFUSED','WARNING_UNEXPECTEDLY_ACCEPTED','UNSOLICITED_BEFORE_SEND'}
             and type(report['records']) is int and 1<=report['records']<=32,'CAPTURE_TERMINAL')
        lines=capture.split(b'\n',32)
        need(len(lines)>report['records'],'CAPTURE_INCOMPLETE')
        raw=lines[report['records']-1]
        observed=projection(raw,requested=report['initialize_requested'],replied=report['initialize_reply_observed'],config=config)
        need(observed==report['warning'],'CAPTURE_PROJECTION_CHANGED')
        return raw
    except Exception:
        raise CustodyRefusal('CAPTURE_REFUSED') from None

def metadata(request_digest,crypto_sha256,recipient_sha256,record_ordinal,ephemeral,nonce):
    need(all(digest(v) for v in (request_digest,crypto_sha256,recipient_sha256,ephemeral))
         and type(nonce) is str and re.fullmatch('[0-9a-f]{24}',nonce)
         and type(record_ordinal) is int and 1<=record_ordinal<=32,'ENVELOPE_METADATA')
    return {'schema':ENVELOPE_SCHEMA,'suite':SUITE,'request_digest':request_digest,
            'crypto_dependency_sha256':crypto_sha256,'recipient_sha256':recipient_sha256,
            'record_ordinal':record_ordinal,'ephemeral_public_key_hex':ephemeral,'nonce_hex':nonce,
            'source_commit':SOURCE,'upstream_commit':UPSTREAM,'native_version':'0.166.0',
            'profile':'CLOSED_STARTUP_WARNING','category':'OTHER_SCHEMA_VALID',
            'framing':'U32BE_LENGTH_RAW_FRAME_ZERO_PADDING','raw_frame_limit':MAX_FRAME,
            'padded_plaintext_bytes':PADDED_BYTES}

def encrypt_frame(raw, *, public_key,request_digest,crypto_sha256,record_ordinal):
    try:
        projection(raw)
        need(type(public_key) is bytes and len(public_key)==32,'RECIPIENT_KEY_BOUND')
        need(digest(crypto_sha256) and sha(canonical(dependency_manifest()))==crypto_sha256,
             'CRYPTO_PREIMAGE_CHANGED')
        _,_,hashes,s,Private,Public,AES,HKDF=primitives()
        ephemeral=Private.generate(); nonce=os.urandom(12)
        header=metadata(request_digest,crypto_sha256,sha(public_key),record_ordinal,
                        public_bytes(ephemeral.public_key(),s).hex(),nonce.hex())
        aad=canonical(header)
        shared=ephemeral.exchange(Public.from_public_bytes(public_key))
        key=HKDF(algorithm=hashes.SHA256(),length=32,salt=bytes.fromhex(request_digest),info=DOMAIN+aad).derive(shared)
        plaintext=len(raw).to_bytes(4,'big')+raw+b'\0'*(MAX_FRAME-len(raw))
        need(len(plaintext)==PADDED_BYTES,'PLAINTEXT_FRAME_BOUND')
        ciphertext=AES(key).encrypt(nonce,plaintext,aad)
        need(len(ciphertext)==CIPHERTEXT_BYTES,'CIPHERTEXT_BOUND')
        envelope=canonical(dict(header,ciphertext_b64=base64.b64encode(ciphertext).decode('ascii')))
        need(len(envelope)<=MAX_ENVELOPE,'ENVELOPE_BOUND')
        return envelope
    except Exception:
        raise CustodyRefusal('ENCRYPTION_REFUSED') from None

def validate_envelope(raw, *, expected_request_digest,expected_crypto_sha256,expected_recipient_sha256):
    try:
        need(all(digest(v) for v in (expected_request_digest,expected_crypto_sha256,expected_recipient_sha256)),
             'EXPECTED_BINDING')
        value=parse(raw,MAX_ENVELOPE)
        need(type(value) is dict,'ENVELOPE_TYPE')
        header=metadata(expected_request_digest,expected_crypto_sha256,expected_recipient_sha256,
            value.get('record_ordinal'),value.get('ephemeral_public_key_hex'),value.get('nonce_hex'))
        need(set(value)==set(header)|{'ciphertext_b64'} and all(type(value[k]) is type(v) and value[k]==v
             for k,v in header.items()),'ENVELOPE_BINDING')
        need(type(value['ciphertext_b64']) is str and len(value['ciphertext_b64'])==87408,'CIPHERTEXT_TEXT_BOUND')
        ciphertext=base64.b64decode(value['ciphertext_b64'],validate=True)
        need(len(ciphertext)==CIPHERTEXT_BYTES and base64.b64encode(ciphertext).decode('ascii')==value['ciphertext_b64'],
             'CIPHERTEXT_BOUND')
        need(raw==canonical(value),'ENVELOPE_CANONICAL')
        return header,ciphertext
    except Exception:
        raise CustodyRefusal('ENVELOPE_REFUSED') from None

def decrypt_envelope(raw, private_key, *, expected_request_digest,expected_crypto_sha256,
                     expected_envelope_sha256,expected_recipient_sha256):
    try:
        need(type(raw) is bytes and 0<len(raw)<=MAX_ENVELOPE,'ENVELOPE_BOUND')
        need(digest(expected_envelope_sha256) and sha(raw)==expected_envelope_sha256,'ARTIFACT_BINDING')
        header,ciphertext=validate_envelope(raw,expected_request_digest=expected_request_digest,
            expected_crypto_sha256=expected_crypto_sha256,expected_recipient_sha256=expected_recipient_sha256)
        need(type(private_key) is bytes and len(private_key)==32,'PRIVATE_KEY_BOUND')
        _,_,hashes,s,Private,Public,AES,HKDF=primitives()
        recipient=Private.from_private_bytes(private_key)
        need(sha(public_bytes(recipient.public_key(),s))==expected_recipient_sha256,'RECIPIENT_BINDING')
        aad=canonical(header)
        shared=recipient.exchange(Public.from_public_bytes(bytes.fromhex(header['ephemeral_public_key_hex'])))
        key=HKDF(algorithm=hashes.SHA256(),length=32,salt=bytes.fromhex(expected_request_digest),info=DOMAIN+aad).derive(shared)
        plaintext=AES(key).decrypt(bytes.fromhex(header['nonce_hex']),ciphertext,aad)
        need(len(plaintext)==PADDED_BYTES,'PLAINTEXT_SIZE')
        length=int.from_bytes(plaintext[:4],'big')
        need(0<length<=MAX_FRAME and plaintext[4+length:]==b'\0'*(MAX_FRAME-length),'PLAINTEXT_FRAMING')
        frame=plaintext[4:4+length]
        projection(frame)
        return frame
    except Exception:
        raise CustodyRefusal('PRIVATE_RECEIVING_REFUSED') from None

def initial_status(request_digest,crypto_sha256):
    need(digest(request_digest) and digest(crypto_sha256),'STATUS_BINDING')
    return {'schema':STATUS_SCHEMA,'status':'NOT_REACHED','request_digest':request_digest,
            'recipient_sha256':RECIPIENT_SHA256,'crypto_dependency_sha256':crypto_sha256,
            'ciphertext_sha256':None,'ciphertext_bytes':0,'plaintext_exported':False}

def validate_status(value, *, expected_request_digest):
    need(type(value) is dict and set(value)=={'schema','status','request_digest','recipient_sha256',
         'crypto_dependency_sha256','ciphertext_sha256','ciphertext_bytes','plaintext_exported'},'STATUS_KEYS')
    need(value['schema']==STATUS_SCHEMA and value['recipient_sha256']==RECIPIENT_SHA256
         and digest(expected_request_digest) and value['request_digest']==expected_request_digest
         and digest(value['crypto_dependency_sha256']) and value['plaintext_exported'] is False
         and type(value['status']) is str and value['status'] in STATUSES,'STATUS_CONSTANTS')
    need(type(value['ciphertext_bytes']) is int,'STATUS_COUNT')
    if value['status']=='SEALED':
        need(digest(value['ciphertext_sha256']) and 87408<value['ciphertext_bytes']<=MAX_ENVELOPE,'STATUS_SEALED')
    else:
        need(value['ciphertext_sha256'] is None and value['ciphertext_bytes']==0,'STATUS_NOT_SEALED')
    return canonical(value)
