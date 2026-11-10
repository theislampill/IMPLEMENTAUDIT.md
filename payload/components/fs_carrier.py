"""Protected diagnostic copy; successful receiving is never original acceptance."""
from contextlib import ExitStack
import os
from pathlib import Path
import stat
import struct
import zipfile
import fs_protocol as P
import fs_command as C
import fs_io as F

def authenticated_unpack(records,rc,stdout,stderr,read_plain,ctx,recipient,sinks,check):
    C.validate_capture(records,rc,stdout,stderr)
    P.need(rc==0,'CMS_AUTHENTICATION_REFUSED')
    check()
    # Failed/incomplete decrypt never calls this supplier, parses or exposes
    # even a prefix that OpenSSL may have written before tag verification.
    reader=read_plain();check()
    return P.unpack(reader,ctx,recipient,sinks,check)

def small(directory,name,maximum,check):
    with F.Input(directory,name,maximum) as file:
        check();raw=file.read(maximum+1);check();file.verify()
        P.need(len(raw)<=maximum,'SMALL_FILE_BOUND');return raw

def store(directory,name,value,maximum=65536):
    raw=P.encode(value);P.need(len(raw)<=maximum,'RECORD_BOUND')
    with F.Output(directory,name,maximum) as file:
        file.write(raw);return file.descriptor(lambda:None)

PUBLIC_REASONS=frozenset(('SUPPLEMENTARY_RETENTION_REFUSED','SHARED_ALLOCATION_REFUSED',
  'RETENTION_DEADLINE','CMS_ENCRYPTION_NONZERO','CMS_AUTHENTICATION_REFUSED',
  'RETENTION_ALREADY_RESERVED','FAILED_PROJECTION_CURRENTNESS','FAILED_STREAM_CUSTODY_UNESTABLISHED',
  'ACTUAL_PROVIDER_BINDING_REQUIRED','ACTUAL_PROVIDER_ARTIFACT_BINDING','ARTIFACT_EXACT_POPULATION',
  'ARTIFACT_BODY_BOUND','ARTIFACT_EXACT_BODY_JOIN','DOWNLOAD_DEADLINE','RETENTION_COMPOSITION_UNBOUND'))

def reason(exc):
    # Exception messages can contain private data even when they look like
    # uppercase symbolic codes. Only these reviewed fixed literals may leave
    # the private component; unknown text is never copied or truncated.
    return str(exc) if type(exc) is P.Refusal and str(exc) in PUBLIC_REASONS else 'SUPPLEMENTARY_RETENTION_REFUSED'

def neutral(status,code=None):
    return dict(schema='dg16.protected-failed-stream-status.v1',authority='NONE',status=status,reason=code,
      custody_scope=P.COPY_SCOPE,original_acceptance=False)

def child_custody(attempted,command):
    if not attempted:return 'NOT_STARTED'
    if command is not None and command[0] and command[0][0].get('cleanup',{}).get('echild') is True:return 'ECHILD'
    return 'UNPROVED'

def command_record(directory,operation,files,maximum,deadline,result):
    records,rc,out,err=result
    for name,body in (('stdout',out),('stderr',err)):
        if type(body) is bytes:
            P.need(len(body)<=C.CAPTURE_MAX,'COMMAND_STREAM_BOUND')
            with F.Output(directory,'COMMAND.'+name,C.CAPTURE_MAX) as dest:dest.write(body)
    value=dict(schema='dg16.protected-stream-command.v1',authority='NONE',operation=operation,
      command=C.cms_argv(operation,{n:f.fd for n,f in files.items()}),capture=records,returncode=rc,
      stdout=P.desc(out) if type(out) is bytes else None,stderr=P.desc(err) if type(err) is bytes else None,
      file_limit=maximum,memory_limit=C.MEMORY_BYTES,cpu_limit=C.CPU_SECONDS,deadline=deadline.stop,
      original_acceptance=False)
    store(directory,'COMMAND.json',value)
    return C.validate_capture(records,rc,out,err)

def locate_capture(full_pair,projection):
    record=projection['observation']['record'];mode=projection['mode']
    choices={'ORIGINAL_WORKSPACE':full_pair/'captures/work','RENAMED_CAPTURE':full_pair/'captures'/mode/'capture'}
    P.need(record['capture_location'] in choices,'CAPTURE_LOCATION')
    present=[path for path in choices.values() if os.path.lexists(path)]
    P.need(present==[choices[record['capture_location']]],'CAPTURE_LOCATION_AMBIGUOUS')
    return present[0]

def envelope(manifest,plain,cipher):
    return dict(schema='dg16.encrypted-failed-stream-envelope.v1',authority='NONE',context=manifest['context'],
      recipient=manifest['recipient'],manifest=P.desc(P.encode(manifest)),plaintext=plain,ciphertext=cipher,
      failed_leg_sha256=P.sha(P.encode(manifest['failed_leg'])),outcome=manifest['outcome'],
      custody_scope=P.COPY_SCOPE,original_acceptance=False)

def validate_envelope(value,ctx,recipient,projection=None):
    P.exact(value,'schema authority context recipient manifest plaintext ciphertext failed_leg_sha256 outcome custody_scope original_acceptance')
    P.context(ctx);P.descriptor(recipient,8192)
    P.need(value['schema']=='dg16.encrypted-failed-stream-envelope.v1' and value['authority']=='NONE'
      and value['context']==ctx and value['recipient']==recipient and value['custody_scope']==P.COPY_SCOPE
      and value['original_acceptance'] is False,'ENVELOPE_CONTEXT')
    for name,maximum in (('manifest',P.HEADER_MAX),('plaintext',P.PLAIN_MAX),('ciphertext',P.CIPHER_MAX)):P.descriptor(value[name],maximum)
    P.need(value['ciphertext']['bytes']>0 and value['ciphertext']['bytes']<=value['plaintext']['bytes']+P.CIPHER_OVERHEAD
      and value['outcome'] in ('RETURNED_NONZERO','OWNER_RAISED','UNKNOWN') and P.digest(value['failed_leg_sha256']),'ENVELOPE_BOUNDS')
    if projection is not None:
        manifest=P.make_manifest(ctx,projection,recipient)
        P.need(value['failed_leg_sha256']==P.sha(P.encode(projection)) and value['outcome']==manifest['outcome']
          and value['manifest']==P.desc(P.encode(manifest))
          and value['plaintext']['bytes']==P.plain_size(len(P.encode(manifest)),manifest['streams']),'ENVELOPE_FAILED_LEG_JOIN')
    return value

def protect(full_pair,ctx,projection,certificate_path,recipient,execute,deadline,read_projection):
    """One reserved supplementary attempt. The caller's primary object is untouched."""
    full_pair=Path(full_pair).absolute();destination=full_pair/'failure-carrier'
    result=neutral('REFUSED');attempted=False;command=None;directory=None
    try:
        deadline.check();manifest=P.make_manifest(ctx,projection,recipient)
        P.need(read_projection()==projection,'FAILED_PROJECTION_CURRENTNESS');deadline.check()
        P.need(not os.path.lexists(destination),'RETENTION_ALREADY_RESERVED')
        before=F.usage(full_pair,deadline.check)
        capacity=P.allocation(before['bytes'],before['entries'],P.plain_size(len(P.encode(manifest)),manifest['streams']))
        with ExitStack() as stack:
            directory=stack.enter_context(F.create_directory(destination))
            store(directory,'INTENT.json',dict(schema='dg16.failed-stream-intent.v1',context=ctx,
              manifest=P.desc(P.encode(manifest)),capacity=capacity,deadline=deadline.stop,authority='NONE',original_acceptance=False))
            capture=stack.enter_context(F.Directory(locate_capture(full_pair,projection)))
            certdir=stack.enter_context(F.Directory(Path(certificate_path).absolute().parent))
            certificate=stack.enter_context(F.Input(certdir,Path(certificate_path).name,8192,recipient,private=True))
            certificate.descriptor(deadline.check)
            record=projection['observation']['record']
            physical_record=stack.enter_context(F.Input(capture,'result.json',P.STREAM_MAX,record['capture_record']['file']))
            physical_record.descriptor(deadline.check)
            if record['primary_file'] is not None:
                primary=stack.enter_context(F.Input(capture,'exit-code.txt',128,{k:record['primary_file'][k] for k in ('bytes','sha256')}))
                primary.descriptor(deadline.check)
            if record['custody_file'] is not None:
                side=stack.enter_context(F.Directory(full_pair/'captures'/projection['mode']))
                name='custody.json' if record['custody_source']=='MAINTAINED_SEAL_SIDECAR' else 'refusal.json'
                P.need(record['custody_source'] in ('MAINTAINED_SEAL_SIDECAR','MAINTAINED_REFUSAL_SIDECAR'),'CUSTODY_SIDECAR_SOURCE')
                custody=stack.enter_context(F.Input(side,name,P.STREAM_MAX,record['custody_file']));custody.descriptor(deadline.check)
            inputs={n:stack.enter_context(F.Input(capture,n+'.log',P.STREAM_MAX,manifest['streams'][n])) for n in P.STREAMS}
            plain=stack.enter_context(F.Output(directory,'FRAME.bin',capacity['plain_bytes']))
            plain_desc=P.pack(manifest,inputs,plain,deadline.check)
            P.need(plain.descriptor(deadline.check)==plain_desc,'FRAME_READBACK')
            for file in inputs.values():file.verify()
            physical_record.verify();certificate.verify();P.need(read_projection()==projection,'FAILED_PROJECTION_CURRENTNESS');deadline.check()
            # Recount before the command. Charge the cipher and auxiliary
            # ceiling against the actual existing tree; do not double-add the
            # plaintext already present in that census.
            usage=F.usage(full_pair,deadline.check)
            P.need(usage['bytes']+capacity['cipher_bytes']+P.AUX_BYTES<=P.TOTAL_MAX
              and usage['entries']+16<=P.ENTRY_MAX,'SHARED_ALLOCATION_REFUSED')
            cipher=stack.enter_context(F.Output(directory,'FAILED_STREAMS.cms',capacity['cipher_bytes']))
            files=dict(plain=plain,certificate=certificate,cipher=cipher)
            deadline.check();attempted=True;command=execute('encrypt',files,capacity['cipher_bytes'],deadline)
            rc=command_record(directory,'encrypt',files,capacity['cipher_bytes'],deadline,command);deadline.check()
            if rc!=0:result=neutral('ENCRYPTION_FAILED','CMS_ENCRYPTION_NONZERO')
            else:
                cipher_desc=cipher.descriptor(deadline.check);cipher.rewind();C.auth_enveloped(cipher,cipher_desc['bytes']);deadline.check()
                P.need(plain.descriptor(deadline.check)==plain_desc,'PLAIN_CLOSING_CHANGED')
                for file in inputs.values():file.verify()
                physical_record.verify();certificate.verify();P.need(read_projection()==projection,'FAILED_PROJECTION_CURRENTNESS');deadline.check()
                value=envelope(manifest,plain_desc,cipher_desc);validate_envelope(value,ctx,recipient,projection)
                # Remove only our extra plaintext inode, never the original
                # capture. A cleanup refusal does not expose a ready artifact.
                plain.unlink_owned();deadline.check()
                public=store(directory,'FAILURE_ENVELOPE.json',value,P.ENVELOPE_MAX)
                usage=F.usage(full_pair,deadline.check);P.need(usage['bytes']<=P.TOTAL_MAX,'CLOSING_ALLOCATION')
                result=neutral('ENCRYPTED_LOCAL_NOT_PROVIDER_RECEIVED')
                result.update(artifact_role=P.artifact_name(ctx),envelope=public,ciphertext=cipher_desc,
                  recipient_sha256=recipient['sha256'],failed_leg_sha256=value['failed_leg_sha256'],outcome=value['outcome'])
            result['crypto_child_custody']=child_custody(attempted,command)
            store(directory,'RETENTION.json',result,4096)
    except BaseException as exc:
        incomplete=attempted and (command is None or command[1] is None or
          not command[0] or command[0][0].get('cleanup',{}).get('echild') is not True)
        result=neutral('INCOMPLETE' if incomplete else 'REFUSED',reason(exc))
        result['crypto_child_custody']=child_custody(attempted,command)
        if destination.exists() and not (destination/'RETENTION.json').exists():
            try:
                with F.Directory(destination) as held:store(held,'RETENTION.json',result,4096)
            except BaseException:pass  # Existing intent/capture prefix remains the truthful boundary.
    return result

def upload_paths(full_pair,result,check=lambda:None):
    """Read-only exact upload eligibility; supplies no upload/admission API."""
    P.need(result.get('status')=='ENCRYPTED_LOCAL_NOT_PROVIDER_RECEIVED','CIPHERTEXT_NOT_READY')
    root=Path(full_pair)/'failure-carrier'
    with F.Directory(root) as directory:
        P.need(P.parse(small(directory,'RETENTION.json',4096,check),4096)==result,'RETENTION_RECORD_CHANGED')
        for name,row,maximum in (('FAILURE_ENVELOPE.json',result['envelope'],P.ENVELOPE_MAX),('FAILED_STREAMS.cms',result['ciphertext'],P.CIPHER_MAX)):
            with F.Input(directory,name,maximum,row) as file:file.descriptor(check)
    return {n:root/n for n in P.ARTIFACT_MEMBERS}

def validate_provider(provider,ctx,artifact_id,archive):
    P.exact(provider,'schema context artifact_id artifact_name archive expired');P.context(ctx);P.descriptor(archive,P.ZIP_MAX)
    P.need(provider['schema']=='dg16.failed-stream-provider-binding.v1' and provider['context']==ctx
      and P.integer(artifact_id,1,2**63-1) and type(provider['artifact_id']) is int and provider['artifact_id']==artifact_id
      and provider['artifact_name']==P.artifact_name(ctx) and provider['archive']==archive and provider['expired'] is False,
      'ACTUAL_PROVIDER_ARTIFACT_BINDING')
    return provider

def zip_metadata_bound(archive,check):
    """Bound metadata before zipfile materializes its member table.

    This fixed two-member, sub-4GiB route accepts a single-disk ZIP with an
    ordinary end record, at most8KiB of central directory and no trailing
    records. ZIP64/multi-disk/other layouts refuse without interpretation.
    """
    archive.verify();size=archive.opening[6];length=min(size,65557)
    check();tail=os.pread(archive.fd,length,size-length);check()
    end=tail.rfind(b'PK\x05\x06')
    P.need(end>=0 and len(tail)-end>=22,'ARTIFACT_METADATA_BOUND')
    signature,disk,central_disk,on_disk,total,central_bytes,central_offset,comment=struct.unpack('<4s4H2LH',tail[end:end+22])
    P.need(signature==b'PK\x05\x06' and disk==central_disk==0 and on_disk==total==2
      and 0<central_bytes<=8192 and end+22+comment==len(tail)
      and central_offset+central_bytes==size-length+end,'ARTIFACT_METADATA_BOUND')
    archive.verify();check()

def acquire_artifact(archive_path,provider,ctx,artifact_id,expected_archive,destination,check):
    validate_provider(provider,ctx,artifact_id,expected_archive);check()
    archive_path=Path(archive_path).absolute()
    with ExitStack() as stack:
        parent=stack.enter_context(F.Directory(archive_path.parent))
        archive=stack.enter_context(F.Input(parent,archive_path.name,P.ZIP_MAX,expected_archive));archive.descriptor(check)
        zip_metadata_bound(archive,check)
        # A dup of the held archive is used by zipfile; member names never
        # become filesystem paths and no extract/extractall operation is used.
        file=stack.enter_context(os.fdopen(os.dup(archive.fd),'rb'))
        z=stack.enter_context(zipfile.ZipFile(file));infos=z.infolist()
        P.need(len(infos)==2 and {i.filename for i in infos}==set(P.ARTIFACT_MEMBERS),'ARTIFACT_EXACT_POPULATION')
        for info in infos:
            maximum=P.ENVELOPE_MAX if info.filename=='FAILURE_ENVELOPE.json' else P.CIPHER_MAX
            P.need(info.orig_filename==info.filename and not info.is_dir() and not info.flag_bits&1
              and info.compress_type in (zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED)
              and stat.S_IFMT(info.external_attr>>16) in (0,stat.S_IFREG)
              and P.integer(info.file_size,1,maximum) and P.integer(info.compress_size,0,P.ZIP_MAX),'ARTIFACT_MEMBER_BOUND')
        directory=stack.enter_context(F.create_directory(destination));members={}
        for info in infos:
            maximum=P.ENVELOPE_MAX if info.filename=='FAILURE_ENVELOPE.json' else P.CIPHER_MAX
            with F.Output(directory,info.filename,maximum) as output,z.open(info,'r') as stream:
                left=info.file_size
                while left:
                    check();raw=stream.read(min(P.CHUNK,left));check();P.need(raw and len(raw)<=left,'ARTIFACT_SHORT_READ')
                    P.write_chunk(output,raw,check);left-=len(raw)
                P.need(stream.read(1)==b'','ARTIFACT_EXTRA_BYTES');check();members[info.filename]=output.descriptor(check)
        archive.verify();check()
        result=dict(schema='dg16.failed-stream-artifact-acquisition.v1',status='EXACT_CIPHERTEXT_ARTIFACT_RECEIVED',
          authority='NONE',provider=provider,members=members,original_acceptance=False)
        store(directory,'ACQUISITION.json',result,8192);return result

def receive_private(staged,destination,ctx,projection,certificate_path,key_path,recipient,execute,deadline,provider=None):
    """Actual provider binding is a required root input, never synthesized here."""
    result=neutral('REFUSED');attempted=False;command=None;destination=Path(destination)
    try:
        P.need(type(provider) is dict,'ACTUAL_PROVIDER_BINDING_REQUIRED')
        validate_provider(provider,ctx,provider['artifact_id'],provider['archive']);deadline.check()
        expected_manifest=P.make_manifest(ctx,projection,recipient)
        with ExitStack() as stack:
            source=stack.enter_context(F.Directory(staged))
            acquisition=P.parse(small(source,'ACQUISITION.json',8192,deadline.check),8192)
            P.need(acquisition.get('status')=='EXACT_CIPHERTEXT_ARTIFACT_RECEIVED' and acquisition.get('provider')==provider
              and acquisition.get('authority')=='NONE' and acquisition.get('original_acceptance') is False,'ACTUAL_ACQUISITION_JOIN')
            value=validate_envelope(P.parse(small(source,'FAILURE_ENVELOPE.json',P.ENVELOPE_MAX,deadline.check),P.ENVELOPE_MAX),ctx,recipient,projection)
            P.need(acquisition['members']=={'FAILURE_ENVELOPE.json':P.desc(P.encode(value)),'FAILED_STREAMS.cms':value['ciphertext']},'ACQUIRED_MEMBER_JOIN')
            cipher=stack.enter_context(F.Input(source,'FAILED_STREAMS.cms',P.CIPHER_MAX,value['ciphertext']));cipher.descriptor(deadline.check)
            cipher.rewind();C.auth_enveloped(cipher,value['ciphertext']['bytes']);deadline.check()
            cd=stack.enter_context(F.Directory(Path(certificate_path).absolute().parent));kd=stack.enter_context(F.Directory(Path(key_path).absolute().parent))
            cert=stack.enter_context(F.Input(cd,Path(certificate_path).name,8192,recipient,private=True));cert.descriptor(deadline.check)
            key=stack.enter_context(F.Input(kd,Path(key_path).name,8192,private=True));key.verify()
            # Count retained provider archive + staged cipher/envelope + key
            # and cert allowance, then quarantine and decoded-stream copies.
            P.allocation(provider['archive']['bytes']+value['ciphertext']['bytes']+P.ENVELOPE_MAX+16384,8,value['plaintext']['bytes'])
            target=stack.enter_context(F.create_directory(destination))
            store(target,'INTENT.json',dict(schema='dg16.failed-stream-private-receive-intent.v1',context=ctx,
              provider=provider,manifest=value['manifest'],deadline=deadline.stop,authority='NONE',original_acceptance=False))
            quarantine=stack.enter_context(F.Output(target,'QUARANTINE.bin',value['plaintext']['bytes']))
            files=dict(cipher=cipher,certificate=cert,key=key,quarantine=quarantine)
            deadline.check();attempted=True;command=execute('decrypt',files,value['plaintext']['bytes'],deadline)
            rc=command_record(target,'decrypt',files,value['plaintext']['bytes'],deadline,command);deadline.check()
            if rc!=0:
                # No hash, parse or body read of failed-decrypt plaintext.
                quarantine.unlink_owned();result=neutral('AUTHENTICATION_FAILED','CMS_AUTHENTICATION_REFUSED')
            else:
                P.need(quarantine.descriptor(deadline.check)==value['plaintext'],'PLAINTEXT_DESCRIPTOR_JOIN')
                quarantine.rewind()
                sinks={n:stack.enter_context(F.Output(target,n+'.bin',P.STREAM_MAX)) for n in P.STREAMS}
                manifest=authenticated_unpack(*command,lambda:quarantine,ctx,recipient,sinks,deadline.check)
                P.need(manifest==expected_manifest and P.desc(P.encode(manifest))==value['manifest'],'AUTHENTICATED_MANIFEST_JOIN')
                for n,sink in sinks.items():P.need(sink.descriptor(deadline.check)==manifest['streams'][n],'PRIVATE_STREAM_READBACK')
                cipher.verify();cert.verify();key.verify();deadline.check()
                P.need(P.parse(small(source,'ACQUISITION.json',8192,deadline.check),8192)==acquisition,'PROVIDER_RECEIPT_CHANGED')
                quarantine.unlink_owned();deadline.check()
                result=neutral('AUTHENTICATED_DIAGNOSTIC_STREAMS_RECEIVED')
                result.update(outcome=manifest['outcome'],streams=manifest['streams'],provider_artifact_id=provider['artifact_id'],
                  failed_leg_sha256=P.sha(P.encode(projection)),manifest=value['manifest'])
            result['crypto_child_custody']=child_custody(attempted,command)
            store(target,'RECEIVING.json',result,4096)
    except BaseException as exc:
        incomplete=attempted and (command is None or command[1] is None or not command[0]
          or command[0][0].get('cleanup',{}).get('echild') is not True)
        result=neutral('INCOMPLETE' if incomplete else 'REFUSED',reason(exc))
        result['crypto_child_custody']=child_custody(attempted,command)
        if destination.exists() and not (destination/'RECEIVING.json').exists():
            try:
                with F.Directory(destination) as target:store(target,'RECEIVING.json',result,4096)
            except BaseException:pass
    return result
