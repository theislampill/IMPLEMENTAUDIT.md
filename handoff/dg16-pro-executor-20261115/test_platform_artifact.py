"""Offline controls; fixtures and injected transports never authenticate GitHub."""
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import time
import types
import unittest
from unittest.mock import patch
import zipfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('platform_artifact', HERE / 'platform_artifact.py')
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)


class Response:
    status = 200
    def __init__(self, body=b'abc', length='3', url='https://sdmntprtest.oaiusercontent.com/a?sig=fixture'):
        self.body, self.headers, self.url = body, {}, url
        if length is not None:
            self.headers['Content-Length'] = length
    def geturl(self): return self.url
    def read(self, size): return self.body[:size]
    def __enter__(self): return self
    def __exit__(self, *args): pass


class Controls(unittest.TestCase):
    url = 'https://sdmntprtest.oaiusercontent.com/a?sig=fixture'

    def call(self, response, maximum=3):
        class Opener:
            def open(inner, request, timeout):
                self.assertEqual(request.method, 'GET')
                self.assertEqual(timeout, 1)
                return response
        with patch.object(M.urllib.request, 'build_opener', return_value=Opener()) as factory:
            result = M.fetch_once(self.url, maximum, 1, 'http://127.0.0.1:41455')
        handlers = factory.call_args.args
        self.assertEqual(handlers[0].proxies, {'https': 'http://127.0.0.1:41455'})
        self.assertTrue(handlers[2]._context.check_hostname)
        self.assertEqual(handlers[2]._context.verify_mode, M.ssl.CERT_REQUIRED)
        return result

    def test_exact_single_get(self): self.assertEqual(self.call(Response()), b'abc')
    def test_missing_length_bounded(self): self.assertEqual(self.call(Response(length=None)), b'abc')
    def test_redirect_refused(self):
        with self.assertRaises(ValueError): M.NoRedirect().redirect_request(None,None,302,None,{},self.url)
    def test_response_url_changed(self):
        with self.assertRaises(ValueError): self.call(Response(url=self.url+'x'))
    def test_short_body(self):
        with self.assertRaises(ValueError): self.call(Response(body=b'ab'))
    def test_long_body(self):
        with self.assertRaises(ValueError): self.call(Response(body=b'abcd',length=None))
    def test_excess_length(self):
        with self.assertRaises(ValueError): self.call(Response(length='4'))
    def test_invalid_length(self):
        with self.assertRaises(ValueError): self.call(Response(length='-1'))
    def test_bad_status(self):
        response=Response(); response.status=403
        with self.assertRaises(ValueError): self.call(response)
    def test_cap_not_widened(self):
        with self.assertRaises(ValueError): M.fetch_once(self.url,262145,1,'http://127.0.0.1:41455')
    def test_timeout_not_widened(self):
        with self.assertRaises(ValueError): M.fetch_once(self.url,3,46,'http://127.0.0.1:41455')
    def test_proxy_exact_platform_loopback(self):
        with patch.object(M.urllib.request,'getproxies',return_value={'https':'http://127.0.0.1:41455'}):
            self.assertEqual(M.platform_proxy(),'http://127.0.0.1:41455')
    def test_proxy_missing_refused(self):
        with patch.object(M.urllib.request,'getproxies',return_value={}):
            with self.assertRaises(ValueError): M.platform_proxy()
    def test_proxy_arbitrary_or_credentials_refused(self):
        for p in ['http://example.com:80','http://u:p@127.0.0.1:80','http://127.0.0.1:80/x','socks5h://127.0.0.1:80']:
            with self.subTest(proxy=p),patch.object(M.urllib.request,'getproxies',return_value={'https':p}):
                with self.assertRaises(ValueError): M.platform_proxy()
    def test_no_proxy_cannot_bypass_declared_transport(self):
        with patch.dict(os.environ,{'no_proxy':'*'}),patch.object(M.urllib.request,'build_opener') as opener:
            with self.assertRaises(ValueError):M.fetch_once(self.url,3,1,'http://127.0.0.1:41455')
            opener.assert_not_called()
    def test_port_qualified_no_proxy_cannot_bypass(self):
        url='https://sdmntprtest.oaiusercontent.com:443/a?sig=fixture'
        with patch.dict(os.environ,{'no_proxy':'sdmntprtest.oaiusercontent.com:443'}),patch.object(M.urllib.request,'build_opener') as opener:
            with self.assertRaises(ValueError):M.fetch_once(url,3,1,'http://127.0.0.1:41455')
            opener.assert_not_called()
    def test_original_source_closure(self):
        core,resolver,acquire,receiver,writer=M.owners()
        self.assertEqual(core.desc(b'abc'),M.desc(b'abc'))
        self.assertEqual(receiver.expected_names('terminal'),set(receiver.NAMES))
    def test_original_metadata_consumer(self):
        _,_,_,receiver,_=M.owners()
        metadata={'run':{'id':1,'run_attempt':1,'head_sha':'a'*40,'head_branch':'pro/test','event':'push','repository':{'full_name':'theislampill/IMPLEMENTAUDIT.md'},'status':'completed'},'commit':{'sha':'a'*40,'tree':{'sha':'b'*40},'parents':[{'sha':'c'*40}]},'artifact':{'id':2,'name':'dg16-full-registry-1-1','expired':False,'size_in_bytes':3,'digest':'sha256:'+M.desc(b'abc')['sha256'],'workflow_run':{'id':1,'head_sha':'a'*40,'head_branch':'pro/test'}}}
        binding={'branch':'pro/test','repository':'theislampill/IMPLEMENTAUDIT.md','final_tree':'b'*40,'source_commit':'c'*40}
        self.assertIn('PROVIDED_METADATA_BINDINGS',receiver.metadata_bindings(metadata,'terminal','1','a'*40,M.desc(b'abc'),binding)['scope'])
        metadata['commit']['parents'][0]['sha']='d'*40
        with self.assertRaises(ValueError):receiver.metadata_bindings(metadata,'terminal','1','a'*40,M.desc(b'abc'),binding)


class FullOfflineComposition(unittest.TestCase):
    """Real journal/parser/decoder with explicitly inert frame and network seams."""
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.parent=Path(self.temp.name)
        self.parent.chmod(0o700)
        self.owners=M.owners()
        data=io.BytesIO()
        with zipfile.ZipFile(data,'w',zipfile.ZIP_DEFLATED) as archive:
            for name in self.owners[3].NAMES: archive.writestr(name,b'{}\n')
        self.body=data.getvalue(); self.digest=M.desc(self.body)
        now=int(time.time()*1000)
        context={'repository':'theislampill/IMPLEMENTAUDIT.md','run_id':'1','run_attempt':1,
            'branch':'pro/dg16-r5-full-g2-direct-host-99-20260101','workflow_commit':'a'*40,
            'workflow_tree':'b'*40,'source_commit':'c'*40}
        metadata={'run':{'id':1,'run_attempt':1,'head_sha':'a'*40,'head_branch':context['branch'],
            'event':'push','repository':{'full_name':context['repository']},'status':'completed'},
            'commit':{'sha':'a'*40,'tree':{'sha':'b'*40},'parents':[{'sha':'c'*40}]},
            'artifact':{'id':2,'name':'dg16-full-registry-1-1','expired':False,
            'size_in_bytes':self.digest['bytes'],'digest':'sha256:'+self.digest['sha256'],
            'workflow_run':{'id':1,'head_sha':'a'*40,'head_branch':context['branch']}}}
        receipt={'status':'PUBLIC_PROVIDER_OBSERVATION_REQUIRES_INDEPENDENT_RECEIVING',
            'operator':'PRO-EXECUTOR-01','actor':'/root','successor':'PRO-EXECUTOR-01, designated by owner',
            'original_acceptance':False,'private_or_cipher':False,'purpose':'SOURCE_QUALIFICATION',
            'role':'terminal','observed_start_ms':now,'observed_end_ms':now,'expires_ms':now+120000,
            'context':context,'public_metadata':metadata,'facts':{'public_metadata':metadata}}
        receipt['receipt_sha256']=M.desc(M.encode(receipt))['sha256']
        self.selection={'receipt':receipt,'journal_parent':str(self.parent),'authorization_sha256':'d'*64}
        self.wrapper={'content':[],'isError':False,'structuredContent':{'artifact_id':2,
            'file_name':'dg16-full-registry-1-1.zip','mime_type':'application/zip',
            'file_uri':{'file_id':'file_'+'f'*32,'file_name':'dg16-full-registry-1-1.zip',
                'mime_type':'application/zip','download_url':'https://sdmntprtest.oaiusercontent.com/a?sig=NEVER_RETAIN_ME'}}}
    def tearDown(self): self.temp.cleanup()
    def perform(self, body=None, frame_error=None):
        resolver=types.SimpleNamespace(**self.owners[1].__dict__)
        def frame(*args):
            self.assertEqual(len(list(self.parent.glob('*/DOWNLOAD_INTENT.json'))),1)
            if frame_error: raise frame_error
            return M.encode(self.wrapper)
        resolver.read_ephemeral_frame=frame
        owners=(self.owners[0],resolver,*self.owners[2:])
        def fetch(*args):
            self.assertEqual(len(list(self.parent.glob('*/BODY_GET_INTENT.json'))),1)
            return self.body if body is None else body
        with patch.object(M,'owners',return_value=owners),patch.object(M,'platform_proxy',return_value='http://127.0.0.1:41455'),patch.object(M,'fetch_once',side_effect=fetch) as get:
            result=M.run(self.selection)
            return result,get.call_count
    def test_complete_inert_composition(self):
        result,calls=self.perform()
        self.assertEqual((result['status'],calls),('EXACT_PUBLIC_BODY_RECEIVED',1))
        self.assertEqual(len(result['member_descriptors']),7)
        self.assertFalse(result['original_acceptance'])
        for file in self.parent.rglob('*'):
            if file.is_file(): self.assertNotIn(b'NEVER_RETAIN_ME',file.read_bytes())
    def test_tampered_body_preserves_unknown(self):
        result,calls=self.perform(self.body+b'altered')
        self.assertEqual((result['status'],result['stage'],calls),('REFUSED_OR_UNCERTAIN','body-digest',1))
        self.assertFalse(list(self.parent.glob('*/ARTIFACT.zip')))
        self.assertEqual(len(list(self.parent.glob('*/OUTCOME.json'))),1)
    def test_lost_frame_has_intent_no_body_call(self):
        result,calls=self.perform(frame_error=TimeoutError())
        self.assertEqual((result['status'],result['stage'],calls),('REFUSED_OR_UNCERTAIN','ephemeral-frame',0))
    def test_spent_slot_cannot_be_reopened(self):
        self.perform(frame_error=TimeoutError())
        with self.assertRaises(ValueError): self.perform()
        self.assertEqual(len(list(self.parent.iterdir())),1)
    def test_expired_receipt_refuses_before_intent(self):
        r=self.selection['receipt'];r['expires_ms']=r['observed_start_ms']-1
        r['receipt_sha256']=M.desc(M.encode({k:v for k,v in r.items() if k!='receipt_sha256'}))['sha256']
        with self.assertRaises(ValueError):self.perform()
        self.assertFalse(list(self.parent.iterdir()))
    def test_self_altered_receipt_refuses(self):
        self.selection['receipt']['context']['workflow_commit']='e'*40
        with self.assertRaises(ValueError):self.perform()
        self.assertFalse(list(self.parent.iterdir()))
    def test_durable_intent_delay_cannot_start_expired_get(self):
        receipt=self.selection['receipt']
        clock={'ms':receipt['observed_start_ms'],'mono':1.0}
        Writer=self.owners[4]
        class DelayedWriter(Writer):
            def write(inner,name,body):
                super().write(name,body)
                if name=='BODY_GET_INTENT.json':
                    clock.update(ms=receipt['expires_ms']+1,mono=400.0)
        resolver=types.SimpleNamespace(**self.owners[1].__dict__)
        resolver.read_ephemeral_frame=lambda *args:M.encode(self.wrapper)
        owners=(*self.owners[:1],resolver,*self.owners[2:4],DelayedWriter)
        with patch.object(M,'owners',return_value=owners),patch.object(M,'platform_proxy',return_value='http://127.0.0.1:41455'),patch.object(M,'fetch_once',return_value=self.body) as get,patch.object(M.time,'time',side_effect=lambda:clock['ms']/1000),patch.object(M.time,'monotonic',side_effect=lambda:clock['mono']):
            result=M.run(self.selection)
        self.assertEqual(result['status'],'REFUSED_OR_UNCERTAIN')
        self.assertEqual(result['body_get_attempts'],0)
        get.assert_not_called()


if __name__ == '__main__': unittest.main(verbosity=2)
