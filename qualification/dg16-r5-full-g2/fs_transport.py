"""Separate exact encrypted-role downloader. No network call on import."""
import hashlib
import time
import urllib.parse
import urllib.request
import fs_protocol as P
import fs_io as F
import fs_carrier as R

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs):return None

def acquire(url,expected_host,provider,ctx,artifact_id,expected_archive,destination,current,*,clock=time.monotonic,stop,opener=None):
    """Caller supplies the actual authorized download reference in memory.

    No URL enters argv, persisted intent, exception text or returned output.
    No retry/redirect/range request. Prefixes remain private and incomplete.
    This diagnostic copy supplies no original live-custody acceptance.
    """
    result=dict(schema='dg16.encrypted-artifact-download.v1',authority='NONE',status='REFUSED_OR_INCOMPLETE',
      body_get_attempts=0,signed_url_retained=False,automatic_retry=False,original_acceptance=False)
    directory=None;retained=0;h=hashlib.sha256()
    def check():
        P.need(clock()<stop,'DOWNLOAD_DEADLINE');current();P.need(clock()<stop,'DOWNLOAD_DEADLINE')
    try:
        check();R.validate_provider(provider,ctx,artifact_id,expected_archive)
        P.need(type(url) is str and 0<len(url)<=8192 and type(expected_host) is str and expected_host,'EPHEMERAL_INPUT')
        parsed=urllib.parse.urlsplit(url)
        P.need(parsed.scheme=='https' and parsed.hostname==expected_host and parsed.port in (None,443)
          and parsed.username is None and parsed.password is None and not parsed.fragment,'EPHEMERAL_REFERENCE_SCOPE')
        directory=F.create_directory(destination)
        R.store(directory,'INTENT.json',dict(schema='dg16.encrypted-artifact-download-intent.v1',provider=provider,
          expected_archive=expected_archive,deadline=stop,authority='NONE',automatic_retry=False),8192)
        open_=opener if opener is not None else urllib.request.build_opener(NoRedirect()).open
        request=urllib.request.Request(url,headers={'Accept':'application/zip','Accept-Encoding':'identity'},method='GET')
        check();result['body_get_attempts']=1
        with open_(request,timeout=max(0.001,min(10.0,stop-clock()))) as response,F.Output(directory,'ARTIFACT.zip',expected_archive['bytes']) as output:
            check();P.need(response.status==200,'ARTIFACT_HTTP_STATUS')
            length=response.headers.get('Content-Length')
            P.need(length is None or length==str(expected_archive['bytes']),'ARTIFACT_CONTENT_LENGTH')
            P.need(response.headers.get('Content-Encoding') in (None,'identity'),'ARTIFACT_ENCODING')
            while True:
                check();chunk=response.read(min(P.CHUNK,expected_archive['bytes']-retained+1));check()
                P.need(type(chunk) is bytes,'ARTIFACT_BODY_TYPE')
                if not chunk:break
                P.need(retained+len(chunk)<=expected_archive['bytes'],'ARTIFACT_BODY_BOUND')
                P.write_chunk(output,chunk,check);retained+=len(chunk);h.update(chunk)
            actual=dict(bytes=retained,sha256=h.hexdigest())
            P.need(actual==expected_archive and output.descriptor(check)==expected_archive,'ARTIFACT_EXACT_BODY_JOIN')
        check();result.update(status='EXACT_ENCRYPTED_ARCHIVE_DOWNLOADED',provider=provider,archive=actual)
    except BaseException as exc:
        result.update(refusal=R.reason(exc),retained_prefix=dict(bytes=retained,sha256=h.hexdigest()))
    finally:
        url=None
        if directory is not None:
            try:R.store(directory,'STATE.json',result,8192)
            finally:directory.close()
    return result
