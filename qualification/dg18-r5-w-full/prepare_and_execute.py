#!/usr/bin/env python3
"""One new Windows subject and one maintained W-FULL attempt, after external approval.

This adapter does not authenticate entitlement, award acceptance, retry, install
tools, fetch private evidence, or run a model. No Windows operation is simulated.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import time

SOURCE_HEAD='539aa846e37eab2dd527912d5e5eaa95f69d61cf'
SOURCE_TREE='6a278e8c95eb1812ce39ca1af288532d4951d860'
REPOSITORY='theislampill/IMPLEMENTAUDIT.md'
BRANCH='pro/dg18-r5-w-full-03-20261105'
BASH=Path(r'C:\Program Files\Git\bin\bash.exe')
DIRECT_GIT_PATHS=(r'C:\Program Files\Git\mingw64\bin\git.exe',
                  r'C:\Program Files\Git\ucrt64\bin\git.exe')
GIT=None
PUBLIC_FILES=('RESULT.json','SOURCE.json','TOOLS.json','CONTROL.json','MEASUREMENT.json',
              'TRANSITION.json','RECEIVING.json','FAILURE.json','ARTIFACT_MANIFEST.json')

def require(ok,reason):
    if not ok: raise RuntimeError(reason)
def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(value): return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+'\n').encode()
def save(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    raw=value if isinstance(value,bytes) else canonical(value)
    with path.open('xb') as stream: stream.write(raw);stream.flush();os.fsync(stream.fileno())
def physical(path):
    path=Path(path).absolute()
    require('..' not in path.parts,'parent traversal refused')
    for node in (path,*path.parents):
        info=node.lstat()
        require(not stat.S_ISLNK(info.st_mode) and not getattr(info,'st_file_attributes',0)&0x400,'reparse/symlink path refused')
    return path.resolve(strict=True)
def identity(path):
    path=physical(path);require(path.is_file(),'regular file required')
    raw=path.read_bytes();return {'bytes':len(raw),'sha256':sha(raw)}
def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module);return module
def clean_environment(python,tmp):
    root=GIT.parents[2];system=Path(os.environ.get('SystemRoot',r'C:\Windows'))
    return {'SystemRoot':str(system),'WINDIR':str(system),'PATHEXT':'.COM;.EXE;.BAT;.CMD',
       'PATH':os.pathsep.join([str(python.parent),str(GIT.parent),str(root/'cmd'),str(root/'bin'),str(root/'usr/bin'),str(system/'System32')]),
       'IMPLEMENTAUDIT_PYTHON':str(python),'PYTHONDONTWRITEBYTECODE':'1','LC_ALL':'C','LANG':'C',
       'MSYS2_ARG_CONV_EXCL':'*','TEMP':str(tmp),'TMP':str(tmp),
       'GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_GLOBAL':os.devnull,'GIT_CONFIG_SYSTEM':os.devnull,
       'GIT_OPTIONAL_LOCKS':'0','GIT_TERMINAL_PROMPT':'0'}

def verify_source(source,manifest,env):
    def git(*args): return subprocess.check_output([str(GIT),'-C',str(source),*args],env=env,timeout=30)
    require(git('rev-parse','HEAD','HEAD^{tree}').decode().splitlines()==[SOURCE_HEAD,SOURCE_TREE],'source commit/tree differs')
    require(git('status','--porcelain=v1','--untracked-files=normal')==b'','qualified source is dirty')
    require(manifest['source_commit']==SOURCE_HEAD and manifest['source_tree']==SOURCE_TREE,'source manifest ancestry differs')
    source_paths={row['path'] for row in manifest['members']}
    skills={p for p in git('ls-files','-z','--','skills').decode().split('\0') if p}
    require(skills=={p for p in source_paths if p.startswith('skills/')},'runtime population differs')
    for row in manifest['members']:
        relative=Path(row['path']);require(not relative.is_absolute() and '..' not in relative.parts,'unsafe manifest path')
        raw=physical(source/relative).read_bytes()
        require(len(raw)==row['bytes'] and sha(raw)==row['sha256'],'source member differs: '+row['path'])
        require(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob_oid'],'source blob differs')
        stage=git('ls-files','--stage','--',row['path']).decode().strip().split()
        require(len(stage)==4 and stage[:3]==[row['git_mode'],row['git_blob_oid'],'0'],'source index member differs')
    return {'source_commit':SOURCE_HEAD,'source_tree':SOURCE_TREE,'member_count':len(manifest['members']),
            'manifest_sha256':sha(canonical(manifest)),'source_status':'CLEAN'}


def read_json_file(path):
    raw=physical(path).read_bytes()
    text=raw.decode('utf-8'); json.loads(text)
    return raw

# Fixed observations derived only from the pinned public source. These are not
# causal conclusions, executable instructions, or claims of current authority.
STDERR_SCAN_LIMIT=65536
STDERR_SOURCE_CODE_LIMIT=16
STDERR_NUMERIC_CODE_LIMIT=16
SOURCE_REFUSAL_RULES=(('CLAIM_PYTHON_REQUIRED',
  'exact',
  (b'claim-run.sh: a supported physical Python 3 interpreter is required; set IMPLEMENTAUDIT_PYTHON to its ab'
   b'solute path',)),
 ('CLAIM_REF_READBACK_UNVERIFIED',
  'prefix',
  (b"claim-run.sh: controller ref readback is unverified; retained claim: '",)),
 ('CUSTODY_CANONICAL_LOCAL_DRIVE_REQUIRED',
  'exact',
  (b'claim-run.sh: custody requires a canonical absolute local-drive path',)),
 ('INIT_VALIDATION_REFUSED', 'prefix', (b'claim-run.sh: initialization validation refused: ',)),
 ('R5_REFUSAL_00105E981D8D1B24', 'exact', (b'claim-run.sh: custody ancestor is not a directory',)),
 ('R5_REFUSAL_007A955020BE38DF', 'exact', (b'claim-run.sh: canonical handle namespace is unsupported',)),
 ('R5_REFUSAL_019A12D5A1FAB9AE', 'exact', (b'claim-run.sh: Git object exceeds the bounded read',)),
 ('R5_REFUSAL_02564D26BECD8F06',
  'exact',
  (b'claim-run.sh: native ref custody requires the exact SHA-1 repository',)),
 ('R5_REFUSAL_02B8BC85689BF9DF', 'exact', (b'claim-run.sh: ref request changed its repository binding',)),
 ('R5_REFUSAL_0423D43CF2ED5C92', 'exact', (b'claim-run.sh: retained source bytes drifted',)),
 ('R5_REFUSAL_04891C2921B9D61A',
  'exact',
  (b'claim-run.sh: initialization predecessor is not the exact expected claim',)),
 ('R5_REFUSAL_05BFFE9A207341DE',
  'exact',
  (b'claim-run.sh: initialization validator source differs before execution',)),
 ('R5_REFUSAL_0D6042A0C488C955',
  'exact',
  (b'claim-run.sh: companion source executing claim code differs from the physical load snapshot',)),
 ('R5_REFUSAL_0F48318C80E02623', 'exact', (b'claim-run.sh: Git routing input changed during custody',)),
 ('R5_REFUSAL_0F4E8BF5EE8479BB', 'exact', (b'claim-run.sh: authority ref is physically present but broken',)),
 ('R5_REFUSAL_0F97D2827622B385', 'prefix', (b"claim-run.sh: governed-writer namespace gate is unsafe: '",)),
 ('R5_REFUSAL_0FEC1FA5CA417C7F', 'exact', (b'claim-run.sh: wire object requires exactly one terminal LF',)),
 ('R5_REFUSAL_10EE671100CEE34F',
  'exact',
  (b'claim-run.sh: Git refused the complete physical authority-ref population',)),
 ('R5_REFUSAL_12E0AA94A05357C7',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: .claimed v2 schema or claim_id inval'
   b'id',
   b'validate-run-root: .claimed v2 schema or claim_id invalid')),
 ('R5_REFUSAL_14A3E085A95D39C0',
  'exact',
  (b'claim-run.sh: Git returned a malformed authority-ref population',)),
 ('R5_REFUSAL_19CF20E26C30FE36',
  'exact',
  (b'claim-run.sh: Git object reader failed exact bounded readback',)),
 ('R5_REFUSAL_19DEAEE43BB2AE5B',
  'exact',
  (b'claim-run.sh: initialization controller marker does not bind the explicit controller',)),
 ('R5_REFUSAL_1A0ECC593B8BED52',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: run root is outside repository',
   b'validate-run-root: run root is outside repository')),
 ('R5_REFUSAL_1A6E34A7A218CD98', 'exact', (b'claim-run.sh: directory flush selected a different object',)),
 ('R5_REFUSAL_1AC05FCA906F071E', 'exact', (b'claim-run.sh: invalid bounded object request',)),
 ('R5_REFUSAL_1AE10D5091ED94E0',
  'exact',
  (b'claim-run.sh: directory spelling aliases a different canonical long name',)),
 ('R5_REFUSAL_1B0060301DFB3139',
  'exact',
  (b'claim-run.sh: companion source executing claim code source changed during load binding',)),
 ('R5_REFUSAL_1E230FF736D539F1', 'exact', (b'claim-run.sh: exclusive output readback differs',)),
 ('R5_REFUSAL_1EAA6133101EF3BF', 'prefix', (b"claim-run.sh: cannot create base dir '",)),
 ('R5_REFUSAL_24F4667B80D97A7A',
  'exact',
  (b'claim-run.sh: companion source retained source directory capability is unavailable',)),
 ('R5_REFUSAL_268A6B14B55094F9',
  'exact',
  (b'claim-run.sh: authority ref population changed during Git readback',)),
 ('R5_REFUSAL_27E26BF1D9CDFAC6',
  'exact',
  (b'claim-run.sh: exclusive output is not empty or exceeds the bound',)),
 ('R5_REFUSAL_2C42728C3AE467B7',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: repo root is not a Git worktree',
   b'validate-run-root: repo root is not a Git worktree')),
 ('R5_REFUSAL_2E00D078E049FADF',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: repo root is not a regular custody d'
   b'irectory',
   b'validate-run-root: repo root is not a regular custody directory')),
 ('R5_REFUSAL_2E6A900D6FC9E2B3',
  'prefix',
  (b"claim-run.sh: run and coordination custody contains a symlink or reparse point: '",)),
 ('R5_REFUSAL_2F32A51E0A0913ED', 'exact', (b'claim-run.sh: canonical handle name unavailable or unbounded',)),
 ('R5_REFUSAL_34FF7F5CEA34A3D1', 'exact', (b'claim-run.sh: ref escapes the exact authority namespace',)),
 ('R5_REFUSAL_3C15245FAF92651C',
  'exact',
  (b'claim-run.sh: loose authority ref is not one exact object ID line',)),
 ('R5_REFUSAL_3D3552966127E035',
  'exact',
  (b'claim-run.sh: companion source executing claim code source changed before load binding',)),
 ('R5_REFUSAL_408C658370EC5460', 'exact', (b'claim-run.sh: owned Git reader did not terminate',)),
 ('R5_REFUSAL_42633BAEFF5F622D',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: supplied repo root is not the canoni'
   b'cal Git worktree',
   b'validate-run-root: supplied repo root is not the canonical Git worktree')),
 ('R5_REFUSAL_42B65259ECBDDB36',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: .claimed run name is not claim-run s'
   b'haped',
   b'validate-run-root: .claimed run name is not claim-run shaped')),
 ('R5_REFUSAL_45AAED51798D3C01',
  'exact',
  (b'claim-run.sh: canonical directory identity or attributes changed',)),
 ('R5_REFUSAL_464E338E94753101', 'exact', (b'claim-run.sh: authority blob is outside bounded bytes',)),
 ('R5_REFUSAL_4745770A6CC47545',
  'exact',
  (b'claim-run.sh: Git object read timed out; no effect or retry authority',)),
 ('R5_REFUSAL_49BDB4DFC90FA603',
  'exact',
  (b'claim-run.sh: initialization source changed before preparation',)),
 ('R5_REFUSAL_49DC44847D7149A6', 'exact', (b'claim-run.sh: directory custody is closed',)),
 ('R5_REFUSAL_4AB00E4BB507B69D',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: .claimed claimed_at_utc is not RFC33'
   b'39 UTC whole seconds',
   b'validate-run-root: .claimed claimed_at_utc is not RFC3339 UTC whole seconds')),
 ('R5_REFUSAL_4B2F388B5F78333D', 'exact', (b'claim-run.sh: written authority blob failed exact readback',)),
 ('R5_REFUSAL_4C15FF371172581A', 'exact', (b'claim-run.sh: file is not a single-link regular object',)),
 ('R5_REFUSAL_4C248997E6A22B3E', 'exact', (b'claim-run.sh: authority ref is malformed',)),
 ('R5_REFUSAL_4DC2A682D72A8C8D',
  'exact',
  (b'claim-run.sh: another owner holds the rotation or namespace lease',)),
 ('R5_REFUSAL_57FB136A7861CE4E', 'exact', (b'claim-run.sh: retained ancestor is not a directory',)),
 ('R5_REFUSAL_5A1796A31F8044D7', 'exact', (b'claim-run.sh: ref is outside exact authority namespace',)),
 ('R5_REFUSAL_5BD541EA7B8509A3', 'exact', (b'claim-run.sh: authority object is not a blob',)),
 ('R5_REFUSAL_5C3B67CAF56FDAA3',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: .claimed v2 keys/order do not match '
   b'strict schema',
   b'validate-run-root: .claimed v2 keys/order do not match strict schema')),
 ('R5_REFUSAL_5E2E6C7FB84CC975',
  'exact',
  (b'claim-run.sh: initialization predecessor is foreign Git-common custody',)),
 ('R5_REFUSAL_5E44D2999175D526',
  'exact',
  (b'claim-run.sh: volume-root flushing is outside canonical custody',)),
 ('R5_REFUSAL_5F2D0BCB6853AE16',
  'exact',
  (b'claim-run.sh: nested Git custody changed the repository or executable binding',)),
 ('R5_REFUSAL_621BB9E9D6209D6E',
  'exact',
  (b'claim-run.sh: incomplete predecessor has prior continuity receipts; recovery is not initialization',)),
 ('R5_REFUSAL_622BCE2DD999F670', 'exact', (b'claim-run.sh: protected write made no progress',)),
 ('R5_REFUSAL_64702485447A19E9',
  'exact',
  (b'claim-run.sh: input is not a bounded single-link regular file',)),
 ('R5_REFUSAL_68C9F511BD41DEED',
  'exact',
  (b'claim-run.sh: publication did not have one exact verified effect',)),
 ('R5_REFUSAL_6930FBE0D5DC422C', 'exact', (b'claim-run.sh: Windows file handle cleanup failed',)),
 ('R5_REFUSAL_6AAFCCF5802C2E42',
  'exact',
  (b'claim-run.sh: companion source bytes differ from the selected owner',)),
 ('R5_REFUSAL_6E10710C5E9F4E68',
  'prefix',
  (b'claim-run.sh: initialization validation refused: validate-run-root: custody path is symlink/reparse: ',
   b'validate-run-root: custody path is symlink/reparse: ')),
 ('R5_REFUSAL_6EA584E6FA9105D2',
  'exact',
  (b'claim-run.sh: initialization predecessor run identity is malformed',)),
 ('R5_REFUSAL_6EAEE9EBC597CFF3',
  'prefix',
  (b'claim-run.sh: initialization validation refused: validate-run-root: claimed template is not regular cust'
   b'ody: ',
   b'validate-run-root: claimed template is not regular custody: ')),
 ('R5_REFUSAL_6ECBBAB63EF48BF2',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: .claimed template promise drift',
   b'validate-run-root: .claimed template promise drift')),
 ('R5_REFUSAL_6ECED1C8EEE9FB42',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: .claimed is not a regular custody fi'
   b'le',
   b'validate-run-root: .claimed is not a regular custody file')),
 ('R5_REFUSAL_6F1AD067F58728FA', 'exact', (b'claim-run.sh: Git operation has unknown effect',)),
 ('R5_REFUSAL_712C74EA8A0C823C',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: Python is required for strict claim '
   b'validation',
   b'validate-run-root: Python is required for strict claim validation')),
 ('R5_REFUSAL_714EF7C1B7196FE1',
  'exact',
  (b'claim-run.sh: directory population changed during enumeration',)),
 ('R5_REFUSAL_72EFC34B90746E97', 'exact', (b'claim-run.sh: custody path is missing',)),
 ('R5_REFUSAL_7650CD19FA108E93', 'exact', (b'claim-run.sh: native ref custody requires the files backend',)),
 ('R5_REFUSAL_76767BCDA0ECFFA3',
  'exact',
  (b'claim-run.sh: companion source ancestor is not an ordinary directory',)),
 ('R5_REFUSAL_7758B9CD77D56C0F',
  'exact',
  (b'claim-run.sh: loose authority ref is symbolic, broken or malformed',)),
 ('R5_REFUSAL_7797B7A6E0267C34',
  'exact',
  (b'ImportError: canonical custody substrate source identity mismatch',)),
 ('R5_REFUSAL_77DC9A5AC559935D',
  'exact',
  (b'ImportError: canonical custody substrate is aliased or nonregular',)),
 ('R5_REFUSAL_789C4EB0D12C6B8D',
  'exact',
  (b'claim-run.sh: initialization cannot replace established canonical migration authority',)),
 ('R5_REFUSAL_78E532C3622B9D8B',
  'exact',
  (b'claim-run.sh: Windows custody requires the actual Windows kernel',)),
 ('R5_REFUSAL_794AE38DAB7D50D0', 'exact', (b'claim-run.sh: symbolic authority ref is forbidden',)),
 ('R5_REFUSAL_7B7D1B36CAFE733C',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: .claimed mode/base is not R0024 stri'
   b'ct custody',
   b'validate-run-root: .claimed mode/base is not R0024 strict custody')),
 ('R5_REFUSAL_7C35BB4D3C96D838', 'exact', (b'claim-run.sh: packed authority ref is broken',)),
 ('R5_REFUSAL_7D27FF33E1958E26', 'exact', (b'claim-run.sh: component exceeds native length bound',)),
 ('R5_REFUSAL_7DBCAB50F98C1460', 'exact', (b'claim-run.sh: volume root aliases a different canonical name',)),
 ('R5_REFUSAL_7DC01925214D7269', 'exact', (b'claim-run.sh: retained input exceeded its bounded read',)),
 ('R5_REFUSAL_8030A890C2B27490',
  'exact',
  (b'claim-run.sh: canonical Windows custody is qualified only for NTFS',)),
 ('R5_REFUSAL_8365C41A629A358A',
  'exact',
  (b'claim-run.sh: Git routing changed while acquiring native custody',)),
 ('R5_REFUSAL_83BD0C9FBA4701DB', 'exact', (b'claim-run.sh: fixed platform Git is unavailable',)),
 ('R5_REFUSAL_868D074FD4906060',
  'exact',
  (b'claim-run.sh: bounded Git observation failed or timed out; no effect authority',)),
 ('R5_REFUSAL_892684D3F0860466',
  'exact',
  (b'claim-run.sh: initialization validator capture changed before execution',)),
 ('R5_REFUSAL_8979AD8E7AFBA9AD',
  'exact',
  (b'claim-run.sh: Git did not confirm exact authority-ref absence',)),
 ('R5_REFUSAL_8BFCF171F9F66362', 'prefix', (b"claim-run.sh: mktemp failed to claim a run dir under '",)),
 ('R5_REFUSAL_8DEED6621DDC45B8', 'exact', (b'claim-run.sh: custody requires a fixed local volume',)),
 ('R5_REFUSAL_8FF9B8478F425752', 'exact', (b'claim-run.sh: Windows directory handle cleanup failed',)),
 ('R5_REFUSAL_91E2648D5546A5DF', 'exact', (b'claim-run.sh: Git routing input disappeared before custody',)),
 ('R5_REFUSAL_92CC0E9C39313120', 'prefix', (b'claim-run.sh: Git operation failed: ',)),
 ('R5_REFUSAL_92DC1A4E6F2C9F9F', 'exact', (b'claim-run.sh: malformed native directory enumeration',)),
 ('R5_REFUSAL_940889779E6FC25E', 'exact', (b'claim-run.sh: symlink or reparse custody is forbidden',)),
 ('R5_REFUSAL_95C1040398E0D719', 'exact', (b'claim-run.sh: malformed native directory offset',)),
 ('R5_REFUSAL_95E0E6848752A9B1',
  'exact',
  (b'claim-run.sh: companion source executing claim code has no ordinary physical source',)),
 ('R5_REFUSAL_991E5243B04EDE69', 'exact', (b'claim-run.sh: file exceeds bounded allocation',)),
 ('R5_REFUSAL_9AD444E3EB8BF01E',
  'exact',
  (b'claim-run.sh: initialization requires the exact relative claimed root',)),
 ('R5_REFUSAL_9B9B1175A8A4556F', 'exact', (b'claim-run.sh: initialization predecessor claim changed',)),
 ('R5_REFUSAL_9CCE183487BBEC68', 'exact', (b'claim-run.sh: custody path is not canonical absolute',)),
 ('R5_REFUSAL_9D1DA16D12671676', 'exact', (b'claim-run.sh: retained input size changed during read',)),
 ('R5_REFUSAL_9E00E6F0B3B70876',
  'exact',
  (b'claim-run.sh: coordination gate is not an exact one-byte gate',)),
 ('R5_REFUSAL_9F066AECF594A141', 'exact', (b'claim-run.sh: retained ancestor is not a native directory',)),
 ('R5_REFUSAL_9FDFD856613505AA', 'exact', (b'claim-run.sh: packed ref population is malformed',)),
 ('R5_REFUSAL_A2A762A8C8EBED03', 'exact', (b'claim-run.sh: wire object is not bytes',)),
 ('R5_REFUSAL_A6AF6620003AD699',
  'exact',
  (b'claim-run.sh: coordination gate is not a single-link one-byte regular file',)),
 ('R5_REFUSAL_A6DC975FD9ADE2E3',
  'exact',
  (b'claim-run.sh: native process peak-memory observation unavailable',)),
 ('R5_REFUSAL_AA56AED120DAB7EC',
  'exact',
  (b'claim-run.sh: Git refused the physical authority ref or its current object',)),
 ('R5_REFUSAL_ABFCA87096DD0696',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: run root is not a directory',
   b'validate-run-root: run root is not a directory')),
 ('R5_REFUSAL_B0E0FB01ECEE64C5',
  'exact',
  (b'claim-run.sh: transaction contains overlapping guard and mutation refs',)),
 ('R5_REFUSAL_B12863FC2B1DC4E9',
  'exact',
  (b'claim-run.sh: companion source is not the selected bounded single-link regular file',)),
 ('R5_REFUSAL_B14FB49FBBCB12AC',
  'exact',
  (b'claim-run.sh: companion source identity changed during bounded capture',)),
 ('R5_REFUSAL_B1A1030C3CB262B8', 'prefix', (b"claim-run.sh: cannot write claim sentinel '",)),
 ('R5_REFUSAL_B297DAFDE0929258', 'exact', (b'claim-run.sh: object request changed its repository binding',)),
 ('R5_REFUSAL_B4238B87411FABA6',
  'exact',
  (b'claim-run.sh: retained file identity, mode, link count or change time drifted',)),
 ('R5_REFUSAL_B52AB45C6720BA6E',
  'exact',
  (b'claim-run.sh: initialization validator differs from the paired owner source',)),
 ('R5_REFUSAL_B71B82D42EBB485C', 'exact', (b'claim-run.sh: controller identity is invalid',)),
 ('R5_REFUSAL_B71DAE8DFFBC18AE',
  'exact',
  (b'claim-run.sh: initialization requires the qualified files ref backend',)),
 ('R5_REFUSAL_B8066DF6EC4ECE99',
  'exact',
  (b'claim-run.sh: incomplete predecessor has established boundary or migration authority',)),
 ('R5_REFUSAL_BA5C3BD182C0AD34',
  'exact',
  (b'claim-run.sh: Windows device, stream, traversal or alias spelling refused',)),
 ('R5_REFUSAL_BAA2ACC5666D65CE', 'exact', (b'claim-run.sh: blob identity is invalid',)),
 ('R5_REFUSAL_BCDD90DDBA988846',
  'exact',
  (b'claim-run.sh: retained file identity, content metadata or canonical name changed',)),
 ('R5_REFUSAL_C0CA0CF4B0A3CACF', 'exact', (b'claim-run.sh: directory flush handle cleanup failed',)),
 ('R5_REFUSAL_C1A56B27F0E54BB0', 'exact', (b'claim-run.sh: wire object field count mismatch',)),
 ('R5_REFUSAL_C1A5B9FC59125766',
  'exact',
  (b'claim-run.sh: Git returned a foreign or duplicate authority ref',)),
 ('R5_REFUSAL_C309126B9459033B',
  'exact',
  (b'claim-run.sh: packed ref has an orphan or repeated peeled record',)),
 ('R5_REFUSAL_C7536E99C8E8FCAC', 'exact', (b'claim-run.sh: bounded file changed while reading',)),
 ('R5_REFUSAL_C8110C08E8A5BF3A',
  'exact',
  (b'claim-run.sh: initialization expected a predecessor which is absent',)),
 ('R5_REFUSAL_C81AC5E9240546A9',
  'exact',
  (b'claim-run.sh: Git object byte readback differs from its exact identity',)),
 ('R5_REFUSAL_C932BB8E3516CACB',
  'exact',
  (b'claim-run.sh: initialization requires the qualified SHA-1 object store',)),
 ('R5_REFUSAL_C99C785C1F001E1F', 'exact', (b'claim-run.sh: coordination gate changed while opening',)),
 ('R5_REFUSAL_CDB569CC0421D478', 'exact', (b'claim-run.sh: transaction OID is malformed',)),
 ('R5_REFUSAL_CFB015FD17457842',
  'exact',
  (b'claim-run.sh: native retained-directory capability is unsupported on this host',)),
 ('R5_REFUSAL_D0F1B360239EDCD7',
  'exact',
  (b'claim-run.sh: canonical ancestor was replaced, renamed or redirected',)),
 ('R5_REFUSAL_D1433AE73E63201F', 'exact', (b'claim-run.sh: authority object exceeds bounded read',)),
 ('R5_REFUSAL_D320DE471B116DEA',
  'prefix',
  (b"claim-run.sh: governed-writer namespace custody contains a symlink or reparse point: '",)),
 ('R5_REFUSAL_D3EEBF9AAB75D034',
  'exact',
  (b'claim-run.sh: retained directory observation was already closed',)),
 ('R5_REFUSAL_DB6341FF9A0582C7',
  'exact',
  (b'claim-run.sh: expected-old authority or namespace guard changed',)),
 ('R5_REFUSAL_E09E9FB23497AD36', 'exact', (b'claim-run.sh: packed ref population is incomplete',)),
 ('R5_REFUSAL_E415B83D6FB85079', 'exact', (b'claim-run.sh: authority blob identity changed',)),
 ('R5_REFUSAL_E52BE6F62962A099',
  'prefix',
  (b'claim-run.sh: initialization validation refused: validate-run-root: custody path missing: ',
   b'validate-run-root: custody path missing: ')),
 ('R5_REFUSAL_E61922E61251A5B7', 'exact', (b'claim-run.sh: packed authority ref is duplicated',)),
 ('R5_REFUSAL_E63AE146B7B34BA8', 'exact', (b'claim-run.sh: reparse point or changing attributes refused',)),
 ('R5_REFUSAL_E68416BE375DB114',
  'exact',
  (b'claim-run.sh: companion source directory identity changed during capture',)),
 ('R5_REFUSAL_E8290A8B38A212E1', 'exact', (b'claim-run.sh: coordination gate opened an unsafe object',)),
 ('R5_REFUSAL_E85D7CE987A819C3',
  'exact',
  (b'claim-run.sh: native source/grant ref overlaps or conflicts with canonical CAS',)),
 ('R5_REFUSAL_E872EFF030CD9EE8', 'exact', (b'claim-run.sh: coordination gate was replaced or changed',)),
 ('R5_REFUSAL_ED0151130EBC353B',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: .claimed run identity drift',
   b'validate-run-root: .claimed run identity drift')),
 ('R5_REFUSAL_EFA39CB65688D29E', 'exact', (b'claim-run.sh: coordination gate creation was incomplete',)),
 ('R5_REFUSAL_F190F2BEDDA1A5E8',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: .claimed has blank or malformed key',
   b'validate-run-root: .claimed has blank or malformed key')),
 ('R5_REFUSAL_F22A6C4EC340F7DF', 'exact', (b'claim-run.sh: coordination gate has an unsupported format',)),
 ('R5_REFUSAL_F469F42ECB0CA0B0',
  'exact',
  (b'claim-run.sh: Git object reader refused a missing, non-blob or mismatched object',)),
 ('R5_REFUSAL_F90B7A543098C6D5',
  'exact',
  (b'claim-run.sh: directory population exceeds bounded enumeration',)),
 ('R5_REFUSAL_FC362BA583052FF7',
  'exact',
  (b'claim-run.sh: retained directory path is not canonical absolute',)),
 ('VALIDATION_REPOSITORY_CUSTODY_DRIFT',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: .claimed repository or common-dir cu'
   b'stody drift',
   b'validate-run-root: .claimed repository or common-dir custody drift')))
_SOURCE_EXACT_CODES={pattern:code for code,mode,patterns in SOURCE_REFUSAL_RULES
                     if mode=='exact' for pattern in patterns}
_SOURCE_PREFIX_CODES=tuple((pattern,code) for code,mode,patterns in SOURCE_REFUSAL_RULES
                          if mode=='prefix' for pattern in patterns)
_NUMERIC_OS_ERROR_PATTERN=re.compile(rb'\[(WinError|Errno) ([0-9]{1,10})\]')

def stderr_observations(raw):
    """Closed, bounded observations; neither stderr text nor its dynamic suffixes escape."""
    scanned=raw[:STDERR_SCAN_LIMIT]
    # A truncated final line cannot become an exact source message by truncation.
    source_scan=scanned
    if len(raw)>STDERR_SCAN_LIMIT and not source_scan.endswith(b'\n'):
        last_newline=source_scan.rfind(b'\n')
        source_scan=source_scan[:last_newline+1]
    source_codes=[]
    for line in source_scan.split(b'\n'):
        line=line.removesuffix(b'\r')
        exact=_SOURCE_EXACT_CODES.get(line)
        if exact is not None and exact not in source_codes:source_codes.append(exact)
        for prefix,code in _SOURCE_PREFIX_CODES:
            if line.startswith(prefix) and code not in source_codes:source_codes.append(code)
        if len(source_codes)>STDERR_SOURCE_CODE_LIMIT:break
    numeric=[];seen=set()
    for match in _NUMERIC_OS_ERROR_PATTERN.finditer(scanned):
        kind='WINERROR' if match[1]==b'WinError' else 'ERRNO'
        code=int(match[2])
        if code>(4294967295 if kind=='WINERROR' else 4095):continue
        key=(kind,code)
        if key in seen:continue
        seen.add(key);numeric.append({'kind':kind,'code':code})
        if len(numeric)>STDERR_NUMERIC_CODE_LIMIT:break
    return {'source_refusal_codes':source_codes[:STDERR_SOURCE_CODE_LIMIT],
        'stderr_numeric_errors':numeric[:STDERR_NUMERIC_CODE_LIMIT],
        'stderr_scan_bytes':len(scanned),'stderr_scan_limit_reached':len(raw)>STDERR_SCAN_LIMIT,
        'source_refusal_codes_limited':len(source_codes)>STDERR_SOURCE_CODE_LIMIT,
        'stderr_numeric_errors_limited':len(numeric)>STDERR_NUMERIC_CODE_LIMIT}

def stderr_codes(raw):
    """Fixed pattern labels only, never free-form process text or a causal verdict."""
    text=raw[:65536].decode('utf-8',errors='replace').lower()
    patterns=(('COMMAND_NOT_FOUND',('command not found',)),
        ('FILE_NOT_FOUND',('no such file or directory','cannot find the file specified')),
        ('GIT_DUBIOUS_OWNERSHIP',('detected dubious ownership',)),
        ('GIT_IDENTITY_REQUIRED',('author identity unknown','unable to auto-detect email address')),
        ('GIT_NOT_REPOSITORY',('not a git repository',)),
        ('PERMISSION_DENIED',('permission denied','access is denied')),
        ('PYTHON_TRACEBACK',('traceback (most recent call last)',)),
        ('ARGUMENT_REJECTED',('unrecognized arguments','unknown option','invalid option')),
        ('INITIALIZATION_TOKEN_REFUSAL',('initialization token is absent, stale, copied or belongs to another claim',)),
        ('PENDING_DECISION_MISSING',('missing concrete pending decision',)))
    return [code for code,needles in patterns if any(needle in text for needle in needles)]

def public_operation(record):
    if record is None:return None
    # Labels are fixed by this reviewed adapter; argv/cwd and arbitrary errors stay private.
    label=record.get('label','')
    require(bool(re.fullmatch(r'[A-Za-z0-9_.-]{1,80}',label)),'diagnostic operation label differs')
    keys=('ordinal','label','outcome','exit','expected_exit','elapsed_ms','stdout_bytes','stderr_bytes',
          'stdout_sha256','stderr_sha256','stderr_codes','exception_type','errno','winerror',
          'source_refusal_codes','stderr_numeric_errors','stderr_scan_bytes','stderr_scan_limit_reached',
          'source_refusal_codes_limited','stderr_numeric_errors_limited')
    return {key:record[key] for key in keys if key in record}

def primary_diagnostic(exc,campaign=None):
    sites=[];tb=exc.__traceback__;adapter=Path(__file__).resolve()
    while tb is not None:
        frame=tb.tb_frame
        if Path(frame.f_code.co_filename).resolve()==adapter:
            sites.append({'function':frame.f_code.co_name,'line':tb.tb_lineno})
        tb=tb.tb_next
    active=getattr(campaign,'active_command',None)
    last=campaign.commands[-1] if campaign is not None and campaign.commands else None
    failed=active if active and active.get('outcome')!='EXPECTED_EXIT' else None
    return {'exception_type':type(exc).__name__,'adapter_sites':sites[-16:],
        'operation':public_operation(failed),'last_completed_command':public_operation(last),
        'classification_scope':'FIXED_PATTERN_OBSERVATION_ONLY; NO_FREEFORM_TEXT_OR_CAUSAL_VERDICT'}

def export_available_evidence(campaign):
    """Read existing owned output only; preserve failed native measurements without retry."""
    public=campaign.public;operation=campaign.out/'operation'
    errors={}
    def keep(name,body):
        target=public/name;raw=body if isinstance(body,bytes) else canonical(body)
        if target.exists(): require(target.read_bytes()==raw,'public evidence collision: '+name)
        else: save(target,raw)
    def capture(name,paths):
        for relative in paths:
            source=operation/relative
            if not source.exists():continue
            try:
                raw=read_json_file(source)
                # A failed attempt never acquires a PASS by choosing a fallback file.
                keep(name,{'status':'UNQUALIFIED_RECORDED_EVIDENCE','origin':relative,
                    'original_bytes':len(raw),'original_sha256':sha(raw),'original_utf8_json':raw.decode('utf-8')})
            except Exception as error: errors[name]=type(error).__name__
            return
    for name,value in [('SOURCE.json',campaign.source_before),('TOOLS.json',campaign.tools)]:
        try:
            if not (public/name).exists():keep(name,value)
        except Exception as error:errors[name]=type(error).__name__
    if not (public/'CONTROL.json').exists():
        capture('CONTROL.json',('execution/native-control/control.json','execution/native-control/job/measurement.json'))
    if not (public/'MEASUREMENT.json').exists():
        capture('MEASUREMENT.json',('execution/MEASUREMENT.json','execution/operation/measurement.json'))
    observations={}
    for label,relative in [('maintained_failure','execution/FAILURE.json'),
                           ('unqualified_readback','execution/unqualified-readback/OBSERVATION.json'),
                           ('readback_failure','execution/READBACK_FAILURE.json')]:
        source=operation/relative
        if not source.exists():continue
        try:
            raw=read_json_file(source);data=json.loads(raw)
            # Free-form error details and ATTEMPT entitlement are not public data.
            if label=='unqualified_readback':
                if isinstance(data.get('errors'),dict):
                    data['errors']={key:{'exception':value.get('exception')} for key,value in data['errors'].items()}
            else:data={key:data[key] for key in ('status','exception','automatic_retry','cleanup_or_compensation','ended_utc') if key in data}
            observations[label]={'origin':relative,'source_bytes':len(raw),'source_sha256':sha(raw),'observation':data}
        except Exception as error:errors[label]=type(error).__name__
    if observations and not (public/'RECEIVING.json').exists():
        keep('RECEIVING.json',{'status':'UNQUALIFIED_POST_ATTEMPT_OBSERVATIONS','observations':observations,
            'authority_ceiling':'NO_CURRENTNESS_TRANSITION_OR_NATIVE_ACCEPTANCE','automatic_retry':False})
    transition={}
    for key,relative in [('current','execution/CURRENT.json'),('preserved_after','execution/PRESERVED_AFTER.json')]:
        source=operation/relative
        if source.exists():
            try:transition[key]=json.loads(read_json_file(source))
            except Exception as error:errors[key]=type(error).__name__
    receipt=operation/'execution/RECEIPT.raw'
    if receipt.exists():
        try:
            raw=physical(receipt).read_bytes();transition['receipt_raw']=raw.decode('utf-8');transition['receipt_sha256']=sha(raw)
        except Exception as error:errors['receipt']=type(error).__name__
    if transition and not (public/'TRANSITION.json').exists():
        keep('TRANSITION.json',{'status':'UNQUALIFIED_RECORDED_TRANSITION','scope':'THIS_FRESH_SUBJECT_ONLY',**transition})
    return errors

def emit_public(output):
    """Read-only ASCII log transport of the exact reviewed public artifact population."""
    public=physical(Path(output)/'public')
    names={p.name for p in public.iterdir()}
    require(names<=set(PUBLIC_FILES) and 'ARTIFACT_MANIFEST.json' in names,'public population or manifest differs')
    rows=[];total=0
    for name in sorted(names):
        raw=read_json_file(public/name);total+=len(raw)
        require(len(raw)<=1048576 and total<=4194304,'public log transport size limit exceeded; artifacts retained, no truncation')
        rows.append({'name':name,'bytes':len(raw),'sha256':sha(raw),'utf8_json':raw.decode('utf-8')})
    manifest=json.loads(next(row['utf8_json'] for row in rows if row['name']=='ARTIFACT_MANIFEST.json'))
    expected={row['name']:(row['bytes'],row['sha256']) for row in manifest['members']}
    actual={row['name']:(row['bytes'],row['sha256']) for row in rows if row['name']!='ARTIFACT_MANIFEST.json'}
    require(expected==actual,'public manifest differs; no log evidence emitted')
    lines=['DG18_PUBLIC_JSON '+json.dumps(row,ensure_ascii=True,separators=(',',':')) for row in rows]
    # Bound actual ASCII transport too; allow two bytes per native line ending.
    lengths=[len(line.encode('ascii'))+2 for line in lines]
    require(all(length<=1048576 for length in lengths) and sum(lengths)<=4194304,
        'encoded public log transport size limit exceeded; artifacts retained, no truncation')
    for line in lines: print(line)

def preflight_failure(args,exc):
    """Only metadata at this exact owned Actions output; no subject/owner operation."""
    require(os.name=='nt' and os.environ.get('GITHUB_ACTIONS')=='true','no Windows preflight output on another host')
    require(os.environ.get('GITHUB_REPOSITORY')==REPOSITORY and os.environ.get('GITHUB_REF')=='refs/heads/'+BRANCH
        and os.environ.get('GITHUB_EVENT_NAME')=='push' and os.environ.get('GITHUB_RUN_ATTEMPT')=='1','preflight context differs')
    run_id=os.environ.get('GITHUB_RUN_ID','');require(re.fullmatch('[0-9]{1,20}',run_id),'run identity absent')
    parent=physical(os.environ['RUNNER_TEMP']);out=parent/('dg18-w-full-'+run_id+'-1')
    require(Path(args.output).absolute()==out,'preflight output differs')
    if out.exists():
        physical(out);require((out/'ALLOCATION_INTENT.json').is_file(),'preexisting unowned output refused')
    else:out.mkdir(exist_ok=False)
    public=out/'public';public.mkdir(exist_ok=True);physical(public)
    require(not any(public.iterdir()),'preexisting public output refused')
    save(public/'FAILURE.json',{'status':'PREFLIGHT_FAILED_NO_OWNER_LAUNCH','stage':'CONSTRUCTOR_PREFLIGHT',
        'exception_type':type(exc).__name__,'source_commit':SOURCE_HEAD,'source_tree':SOURCE_TREE,
        'primary_diagnostic':primary_diagnostic(exc),
        'subject_directory_allocated':(out/'subject with space').exists(),'owner_execution_started':False,
        'automatic_retry':False,'original_acceptance_delta':0,'raw_console_uploaded':False})
    raw=(public/'FAILURE.json').read_bytes()
    save(public/'ARTIFACT_MANIFEST.json',{'schema':'r5.windows-fresh-public-artifact-selection.v1',
        'members':[{'name':'FAILURE.json','bytes':len(raw),'sha256':sha(raw)}],
        'selection':'SANITIZED_PREFLIGHT_METADATA_ONLY; NO_SUBJECT_OR_OWNER_LAUNCH'})

def task_bodies(meta,authored,owner_source_text):
    """Author only actual new-task facts; do not import fixture receipt/history values."""
    def group(owner,value): return {'owner':owner,'value':value}
    def record(identifier,description,status='ACTIVE'):
        return {'record_id':identifier,'status':status,'description':description,
                'scope':'this newly created Windows qualification subject only','evidence_refs':['authorization']}
    instruction={'record_id':'external-new-task-authorization','issuer':'external owner approval reference',
        'subject':'Perform one fresh Windows resume receiving campaign using the pinned public source',
        'scope':'this disposable subject only; the adapter does not authenticate entitlement',
        'applicability':'APPLIES','status':'ACTIVE','evidence_refs':['authorization'],
        'issued_epoch':'G0001','expires_at':None,'supersedes':[]}
    frontier={'DONE':['actual-initialization'],'ACTIVE':['new-windows-campaign'],
              'READY':[],'BLOCKED':['independent-original-receiving']}
    state={
        'identity':group('claim-run.sh',{'controller_id':meta['controller'],'claim_id':meta['claim_id'],
            'run_root_identity':meta['run_relative'],'audit_object':'Fresh Windows whole-owner resume receiving task',
            'candidate':meta['head'],'tree':meta['tree'],'package':'Exact copied runtime at '+SOURCE_HEAD,
            'pull_request':None,'release':None}),
        'continuation':group('STATE.md',{'phase':'1','status':'open','next_action':meta['next_action'],
            'route':'ordinary','last_check':'Actual pending initialization activated; no acceptance awarded'}),
        'instructions':group('STATE.md',[dict(instruction,record_id='new-task-scope-instruction')]),
        'authorisations':group('STATE.md',[instruction]),
        'terminal':group('STATE.md',{'one_shots':[],'markers':[],'handoffs':[],'external_effects':[]}),
        'andons':group('STATE.md',[]),'original_reds':group('STATE.md',[]),
        'pending_boundaries':group('R0033/continuity',[]),
        'non_verdicts':group('STATE.md',[record('no-acceptance','New task measurements do not award original acceptance')]),
        'evidence_ceilings':group('STATE.md',[record('no-native-history','No historic H0, model session, C02 adjudication or original controller custody is asserted')]),
        'steers':group('STATE.md',[record('one-fresh-attempt','No old effect replay, automatic retry, cleanup or compensation')]),
        'rollback':group('STATE.md',{'status':'AVAILABLE','target':None,
            'conditions':['Stop and retain this newly owned subject after any uncertain effect; no automatic compensation'],
            'evidence_refs':['authorization']}),
        'runtime_artifacts':group('STATE.md',['receipt','authorization','initialization','public_owner_source','work_graph'])}
    roadmap={
        'frontier':group('WORK_GRAPH.json',frontier),
        'obligations':group('ROADMAP.md',[record('receive-fresh-operation','Retain actual whole-Job measurement and independent receiving evidence','OPEN')]),
        'deferrals':group('ROADMAP.md',[]),
        'dependencies':group('ROADMAP.md',[{'record_id':'receiving-dependency','source':'independent-original-receiving',
            'target':'new-windows-campaign','status':'BLOCKED','evidence_refs':['authorization']}]),
        'compensations':group('ROADMAP.md',[]),
        'planning':group('ROADMAP.md',{'goal':'Measure one actual fresh Windows owner resume within the maintained whole-Job contract',
            'action_selection':{'selected':['truthful new subject','actual first rotation','fresh manual invalidation','one maintained prepare/execute'],
                'omitted':['model session','historic H0','C02 adjudication','protected historical operations'],
                'rationale':'Only a fresh isolated Windows qualification episode is selected'},
            'scope_boundaries':['New disposable subject only','No retry','No original acceptance grant'],
            'baseline_ref':meta['head']})}
    bodies={}
    for role,payload in [('STATE',state),('ROADMAP',roadmap)]:
        lines=authored[role].decode().splitlines()
        require([line for line in lines if re.search(r'current\s+epoch\s*:',line,re.I)]==(['Current epoch: G0001'] if role=='STATE' else []),'ordinary author epoch shape differs')
        payload['native_guards']=group(role+'.md',{'schema_version':'implementaudit.native-guard-profile.v1',
            'lines':[line for line in lines if line!='Current epoch: G0001']})
        bodies[role]={'schema_version':'implementaudit.canonical-pair.v2','role':role,
            'pair_id':'actual-windows-'+meta['controller'],'payload':payload,'transition':None,'history':[],
            'archive_pointers':[],'artifact_refs':[],
            'continuity':{'projection_generation_id':'G0001','continuity_epoch':'G0001','invalidation_oid':None,
                'predecessor_receipt_ref_oid':None,'expected_receipt_ref':'refs/implementaudit/continuity-receipts/'+meta['controller']+'/G0001',
                'expected_receipt_schema':'implementaudit.continuity-receipt.v2','boundary':'new-session','reconciled':True}}
    bodies['STATE']['artifact_refs']=[{'artifact_id':'receipt','owner':'claim-run.sh','role':'CONTINUITY_RECEIPT',
        'locator':'refs/implementaudit/continuity-receipts/'+meta['controller']+'/G0001','object_format':'sha1'}]
    for name in ('authorization','initialization','public_owner_source'):
        bodies['STATE']['artifact_refs'].append({'artifact_id':name,'owner':'STATE.md','role':'EVIDENCE',
            'locator':'evidence/'+name+'.txt','object_format':'sha1'})
    bodies['ROADMAP']['artifact_refs']=[{'artifact_id':'work_graph','owner':'WORK_GRAPH.json','role':'WORK_GRAPH',
        'locator':'WORK_GRAPH.json','object_format':'sha1'}]
    bodies['STATE']['history']=[{'record_id':'source-captured-in-this-new-task','record_kind':'artifact.historical',
        'owner':'STATE.md','status':'PRESERVED','payload':{'text':owner_source_text,'evidence_refs':['public_owner_source'],
        'original_scope':'Exact reviewed source of claim-run-rotation.py captured earlier during this new task preparation',
        'current_applicability':'UNCHANGED','historical_refusal':None}}]
    return bodies,frontier

class Campaign:
    def __init__(self,args):
        global GIT
        require(os.name=='nt' and sys.platform=='win32','authentic Windows required; no subject allocated')
        require(sys.version_info[:2]==(3,12),'physical Python 3.12 required')
        require(os.environ.get('GITHUB_ACTIONS')=='true' and os.environ.get('GITHUB_REPOSITORY')==REPOSITORY,
                'exact approved repository Actions host required')
        require(os.environ.get('GITHUB_EVENT_NAME')=='push' and os.environ.get('GITHUB_REF')=='refs/heads/'+BRANCH,
                'exact isolated push branch required')
        require(os.environ.get('GITHUB_RUN_ATTEMPT')=='1','workflow reruns refused; no old attempt replay')
        run_id=os.environ.get('GITHUB_RUN_ID','');require(re.fullmatch('[0-9]{1,20}',run_id),'actual workflow run identity missing')
        self.packet=physical(Path(__file__).parent);self.source=physical(args.source)
        self.python=physical(args.python);require(self.python.samefile(sys.executable),'selected Python differs from running physical interpreter')
        require(physical(BASH).is_file(),'fixed physical Bash required')
        available=[physical(path) for path in DIRECT_GIT_PATHS if Path(path).is_file()]
        require(available,'one maintained allowlisted direct mingw64/ucrt64 Git image required')
        GIT=available[0]
        self.entitlement=(self.packet/'entitlement-reference.txt').read_text().strip()
        require(self.entitlement and self.entitlement!='UNGRANTED' and len(self.entitlement)<=2048
                and '\n' not in self.entitlement and '\r' not in self.entitlement,
                'external owner entitlement reference has not been supplied')
        self.out=physical(Path(args.output).absolute().parent)/Path(args.output).name
        require(not self.out.exists() and not any(self.out.is_relative_to(root) for root in (self.source,self.packet)),
                'unused separated output required; no retry')
        self.repo=self.out/'subject with space';self.raw=self.out/'raw';self.public=self.out/'public';self.tmp=self.repo/'task-tmp'
        self.controller='r5-winfull-'+run_id
        require(len(self.controller)<=48,'controller namespace limit exceeded')
        self.env=clean_environment(self.python,self.tmp)
        self.manifest=json.loads((self.packet/'SOURCE_MANIFEST.json').read_text())
        self.source_before=verify_source(self.source,self.manifest,self.env)
        checker=load(self.source/'scripts/check-r0039-windows-resume.py','selected_direct_git_contract')
        require(tuple(checker.DIRECT_GIT_EXECUTABLES)==DIRECT_GIT_PATHS,'maintained direct Git allowlist differs')
        checker.direct_git_layout(str(GIT))
        self.out.mkdir(exist_ok=False)
        save(self.out/'ALLOCATION_INTENT.json',{'subject':str(self.repo),'raw_evidence':str(self.raw),'public_evidence':str(self.public),
            'controller':self.controller,'source_commit':SOURCE_HEAD,'source_tree':SOURCE_TREE,'github_run_id':run_id,
            'scope':'ONE_NEW_DISPOSABLE_WINDOWS_SUBJECT','automatic_retry':False,'original_acceptance_delta':0,
            'external_entitlement_reference_sha256':sha(self.entitlement.encode())})
        self.repo.mkdir();self.raw.mkdir();self.public.mkdir();self.tmp.mkdir()
        self.commands=[];self.stage='ALLOCATED';self.plan=None;self.initializer_controls=[];self.active_command=None
        self.tools={name:{'path':str(physical(path)),'sha256':identity(path)['sha256']}
                    for name,path in [('bash',BASH),('python',self.python),('git',GIT)]}
        self.runner=self.source/'scripts/run-r0039-windows-resume.py'

    def command(self,argv,label,expected=0,cwd=None,timeout=240):
        argv=list(map(str,argv));began=time.time_ns()
        self.active_command={'ordinal':len(self.commands)+1,'label':label,'expected_exit':expected,
                             'exit':None,'outcome':'PROCESS_START_PENDING'}
        try:
            result=subprocess.run(argv,cwd=cwd or self.repo,env=self.env,stdin=subprocess.DEVNULL,
                                  stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
        except BaseException as error:
            self.active_command.update(outcome='PROCESS_TIMEOUT' if isinstance(error,subprocess.TimeoutExpired)
                else 'PROCESS_START_FAILED' if isinstance(error,OSError) else 'COMMAND_INTERRUPTED',
                exception_type=type(error).__name__,errno=getattr(error,'errno',None),winerror=getattr(error,'winerror',None))
            raise
        prefix=f'{len(self.commands)+1:03d}-{label}'
        save(self.raw/(prefix+'.stdout'),result.stdout);save(self.raw/(prefix+'.stderr'),result.stderr)
        self.active_command.update(exit=result.returncode,outcome='EXPECTED_EXIT' if result.returncode==expected else 'UNEXPECTED_EXIT',
            elapsed_ms=(time.time_ns()-began)/1e6,stdout_bytes=len(result.stdout),stderr_bytes=len(result.stderr),
            stdout_sha256=sha(result.stdout),stderr_sha256=sha(result.stderr),stderr_codes=stderr_codes(result.stderr))
        self.active_command.update(stderr_observations(result.stderr))
        self.commands.append({'command':argv,'cwd':str(cwd or self.repo),**self.active_command})
        save(self.raw/(prefix+'.json'),self.commands[-1])
        require(result.returncode==expected,'command failed at '+label+'; evidence retained; no retry')
        return result.stdout
    def git(self,*args,label='git'): return self.command([GIT,'-C',self.repo,*args],label)
    def claim(self,*args,label='claim'): return self.command([BASH,'--noprofile','--norc',self.repo/'skills/implementaudit/scripts/claim-run.sh',*args],label)
    def refuse_activation(self,relative,token,label,reason):
        before=self.git('for-each-ref','--format=%(refname) %(objectname)','refs/implementaudit',label=label+'-refs-before')
        self.command([BASH,'--noprofile','--norc',self.repo/'skills/implementaudit/scripts/claim-run.sh',
            '--activate-controller',self.controller,'--run-root',relative,'--expected-initialization',token],label,expected=1)
        captured=self.raw/(f'{len(self.commands):03d}-'+label+'.stderr')
        require(reason in captured.read_text(encoding='utf-8'),'refusal reason differs at '+label)
        stderr_sha=identity(captured)['sha256']
        after=self.git('for-each-ref','--format=%(refname) %(objectname)','refs/implementaudit',label=label+'-refs-after')
        require(before==after,'refused activation changed an authority ref')
        self.initializer_controls.append({'case':label,'status':'EXPECTED_REFUSAL_NO_AUTHORITY_REF_CHANGE',
            'refs_before_sha256':sha(before),'refs_after_sha256':sha(after),'stderr_sha256':stderr_sha,
            'scope':'THIS_FRESH_SUBJECT_ONLY; UNUSED_GIT_BLOBS_ARE_NOT_AUTHORITY'})

    def run(self):
        self.stage='NEW_SUBJECT_INITIALIZATION'
        shutil.copytree(self.source/'skills',self.repo/'skills')
        for row in self.manifest['members']:
            if row['path'].startswith('skills/'):
                require(identity(self.repo/row['path'])=={'bytes':row['bytes'],'sha256':row['sha256']},'copied runtime differs')
        self.git('-c','init.templateDir=','init','-q','-b','qualification',label='init')
        save(self.repo/'.gitignore',b'.IMPLEMENTAUDIT/\ntask-tmp/\nskills/\n')
        save(self.repo/'TASK.md',('# Actual fresh Windows receiving task\n\nRuntime source '+SOURCE_HEAD+' / '+SOURCE_TREE+
            '\nOne new manual-resume campaign; no old history, native H0, model session, protected retry or acceptance award.\n').encode())
        self.git('add','--','TASK.md','.gitignore',label='add')
        self.git('-c','user.name=R5 Windows receiving','-c','user.email=r5-windows@example.invalid',
            '-c','commit.gpgsign=false','-c','core.hooksPath=NUL','commit','-qm','Define actual fresh Windows receiving task',label='baseline')
        head=self.git('rev-parse','HEAD',label='head').decode().strip();tree=self.git('rev-parse','HEAD^{tree}',label='tree').decode().strip()
        relative=self.claim('--controller',self.controller,'Fresh Windows W-FULL receiving',label='claim-pending').decode().strip()
        require(re.fullmatch(r'\.IMPLEMENTAUDIT/runs/[a-z0-9-]+-[A-Za-z0-9]{6}',relative),'unexpected claimed root')
        run=self.repo/relative;next_action='Receive the actual fresh Windows whole-owner resume and retain its measured transition'
        self.command([self.python,'-I','-X','utf8','-B',self.source/'fixtures/controller-initialization/author_checkpoint.py',
            '--repo',self.repo,'--run-root',relative,'--source',self.repo,
            '--purpose','Execute one externally authorized fresh Windows receiving campaign; no historical native occurrence or original acceptance is asserted.',
            '--next-action',next_action],'author-real-task')
        inspect=json.loads(self.claim('--inspect-controller-initialization',self.controller,'--run-root',relative,label='inspect-initialization'))
        require(not inspect['missing_files'] and inspect['current_controller_oid'] is None and inspect['binding_record_oid'] is None,'new pending initialization differs')
        invalid_token=inspect['initialization_token'].rsplit('@',1)[0]+'@'+'0'*40
        self.refuse_activation(relative,invalid_token,'invalid-initialization-token',
            'initialization token is absent, stale, copied or belongs to another claim')
        activation=json.loads(self.claim('--activate-controller',self.controller,'--run-root',relative,
            '--expected-initialization',inspect['initialization_token'],label='activate-exact'))
        require(activation['status']=='BOUND_ELIGIBLE_FOR_NORMAL_CURRENTNESS','activation failed')
        claim=dict(line.split('=',1) for line in (run/'.claimed').read_text().splitlines())
        authored={role:(run/(role+'.md')).read_bytes() for role in ('STATE','ROADMAP')}
        meta={'controller':self.controller,'claim_id':claim['claim_id'],'run_relative':relative,
              'head':head,'tree':tree,'next_action':next_action}
        owner_source=(self.source/'skills/implementaudit/scripts/claim-run-rotation.py').read_bytes()
        bodies,frontier=task_bodies(meta,authored,owner_source.decode())
        factory=load(self.source/'fixtures/canonical-state-rotation/protected_projection_v2_test.py','actual_task_format_helpers')
        artifacts={'authorization':canonical({'reference':self.entitlement,'scope':'this new Windows subject only',
            'authentication':'EXTERNAL_OWNER_REQUIRED; NOT_AUTHENTICATED_BY_ADAPTER'}),
            'initialization':canonical(activation),'public_owner_source':owner_source,
            'work_graph':canonical({'schema':'r5.new-task-frontier.v1','frontier':frontier,'authority':'TASK_FACTS_ONLY'})}
        for name in ('authorization','initialization','public_owner_source'): save(run/'evidence'/(name+'.txt'),artifacts[name])
        save(run/'WORK_GRAPH.json',artifacts['work_graph'])
        pair=factory.render_pair(bodies)
        require(sum(map(len,pair.values()))>131072,'actual captured public source workload does not trigger byte policy')
        for role in ('STATE','ROADMAP'):
            (run/(role+'.md')).write_bytes(pair[role])
            self.command([self.python,'-I','-X','utf8','-B','-c','from pathlib import Path;import sys;sys.stdout.buffer.write(Path(sys.argv[1]).read_bytes())',run/(role+'.md')],'read-'+role)
        legacy=self.claim('--resume-controller',self.controller,'--boundary','new-session','--epoch','G0001',label='normal-first-resume').decode().strip()
        require(self.claim('--verify-resume-receipt',legacy,label='verify-first').decode().strip()==legacy,'first receipt differs')
        require(self.claim('--require-current-continuity',self.controller,label='require-first').decode().strip()==legacy,'first currentness differs')
        # One pending successor proves the corrected controller wire is consumed by
        # the existing predecessor owner. It is never activated or resumed.
        controller_before=self.git('rev-parse','refs/implementaudit/controllers/'+self.controller,label='predecessor-controller-oid').decode().strip()
        successor_relative=self.claim('--controller',self.controller,'--supersede-claim',claim['claim_id'],
            'Inspect actual Windows initialization predecessor',label='prepare-pending-successor').decode().strip()
        self.command([self.python,'-I','-X','utf8','-B',self.source/'fixtures/controller-initialization/author_checkpoint.py',
            '--repo',self.repo,'--run-root',successor_relative,'--source',self.repo,
            '--purpose','Qualify exact initialized Windows predecessor parsing and stale expected-old refusal; no activation or new resume is intended.',
            '--next-action','After the measured owner transition, require this pending activation to refuse its stale expected-old guards'],
            'author-pending-successor-control')
        successor_inspect=json.loads(self.claim('--inspect-controller-initialization',self.controller,
            '--run-root',successor_relative,label='inspect-actual-predecessor'))
        require(successor_inspect['predecessor_kind']=='INITIALIZED_PREDECESSOR'
            and successor_inspect['current_controller_oid']==controller_before
            and successor_inspect['binding_record_oid'] is None and not successor_inspect['missing_files'],
            'exact initialized predecessor was not received')
        self.refuse_activation(successor_relative,inspect['initialization_token'],'foreign-claim-initialization-token',
            'initialization token is absent, stale, copied or belongs to another claim')
        require(self.claim('--require-current-continuity',self.controller,label='require-after-predecessor-inspection').decode().strip()==legacy,
            'pending predecessor inspection changed currentness')
        self.initializer_controls.append({'case':'actual-initialized-predecessor','status':'PASS_READ_EXISTING_PREDECESSOR_NO_ACTIVATION',
            'current_controller_oid':controller_before,'pending_run':successor_relative,
            'predecessor_kind':successor_inspect['predecessor_kind'],'binding_record_oid':None})
        artifacts['receipt']=self.git('cat-file','blob',legacy.split('@')[1],label='actual-first-receipt-blob')
        save(run/'owner-map.json',{'schema':'implementaudit.rotation-owner-map.v2','owner_map':factory.build_owner_map(bodies,pair,artifacts)})
        self.stage='ACTUAL_PREDECESSOR_ROTATION'
        rotation=json.loads(self.claim('--rotate-canonical-state',self.controller,'--owner-map','owner-map.json',label='first-rotation'))
        require(rotation['status']=='ROTATED','real byte-triggered predecessor rotation failed')
        self.claim('--require-current-continuity',self.controller,label='require-migrated-predecessor')
        self.stage='FRESH_MANUAL_BOUNDARY'
        self.claim('--invalidate-continuity',self.controller,'--boundary','manual-resume',
            '--event','new-windows-campaign-'+os.environ['GITHUB_RUN_ID']+'-manual-resume',label='fresh-manual-invalidation')
        self.stage='MAINTAINED_PREPARE'
        operation=self.out/'operation'
        prepared=json.loads(self.command([self.python,'-I','-X','utf8','-B',self.runner,'prepare','--source',self.source,
            '--repo',self.repo,'--controller',self.controller,'--source-head',SOURCE_HEAD,'--source-tree',SOURCE_TREE,
            '--bash',BASH,'--python',self.python,'--git',GIT,'--out',operation],'maintained-prepare'))
        self.plan=Path(prepared['plan']);plan_hash=identity(self.plan)['sha256']
        require(prepared['sha256']==plan_hash,'prepared plan digest differs')
        self.stage='MAINTAINED_SINGLE_EXECUTE'
        self.command([self.python,'-I','-X','utf8','-B',self.runner,'execute','--plan',self.plan,'--plan-sha256',plan_hash,
            '--entitlement-reference',self.entitlement],'maintained-execute',timeout=600)
        result=json.loads((operation/'execution/RESULT.json').read_bytes())
        require(result['status']=='RECORDED_OPERATION_READY_FOR_INDEPENDENT_RECEIVING','maintained operation not qualified for receiving')
        require(verify_source(self.source,self.manifest,self.env)==self.source_before,'source changed after operation')
        self.stage='STALE_INITIALIZATION_GUARD_RECEIVING'
        self.refuse_activation(successor_relative,successor_inspect['initialization_token'],'stale-expected-old-initialization',
            'initialization expected-old source/controller/boundary changed')
        current=json.loads((operation/'execution/CURRENT.json').read_bytes())
        require(self.claim('--require-current-continuity',self.controller,label='require-after-stale-initialization-refusal').decode().strip()==current['receipt_token'],
            'stale initialization refusal changed currentness')
        self.stage='PUBLISH_SELECTED_NEW_SUBJECT_EVIDENCE'
        for name,relative_path in [('CONTROL.json','execution/native-control/control.json'),
                                  ('MEASUREMENT.json','execution/MEASUREMENT.json')]:
            save(self.public/name,(operation/relative_path).read_bytes())
        current=json.loads((operation/'execution/CURRENT.json').read_bytes())
        save(self.public/'TRANSITION.json',{'assessment':result['transition'],'current':current,
              'receipt_raw':(operation/'execution/RECEIPT.raw').read_text(),'scope':'THIS_FRESH_SUBJECT_ONLY'})
        save(self.public/'RECEIVING.json',{'status':result['status'],'authority_ceiling':result['authority_ceiling'],
            'plan_sha256':plan_hash,'verify_stdout_sha256':identity(operation/'execution/verify-receipt.stdout')['sha256'],
            'require_stdout_sha256':identity(operation/'execution/require-current.stdout')['sha256'],
            'original_acceptance_delta':0,'initializer_controls':self.initializer_controls,
            'scope':'MAINTAINED_SEPARATE_PROCESS_RECEIVING; EXTERNAL_INDEPENDENT_REVIEW_PENDING'})
        save(self.public/'SOURCE.json',self.source_before);save(self.public/'TOOLS.json',self.tools)
        save(self.public/'RESULT.json',{'status':result['status'],'measurement':result['measurement'],
            'source_commit':SOURCE_HEAD,'source_tree':SOURCE_TREE,'controller':self.controller,
            'subject_head':head,'subject_tree':tree,'first_receipt':legacy,'final_receipt':current['receipt_token'],
            'source_manifest_sha256':self.source_before['manifest_sha256'],'plan_sha256':plan_hash,
            'authority_ceiling':result['authority_ceiling'],'original_acceptance_delta':0,
            'measurement_scope':'WHOLE_RESUME_OWNER_JOB; PREPARATION_CONTROL_HARNESS_AND_INDEPENDENT_RECEIVING_OUTSIDE_JOB',
            'maximum_ms':60000,'maximum_aggregate_job_committed_bytes':201326592,'baseline_subtracted_bytes':0})
        self.publish_manifest()
        print(json.dumps({'status':result['status'],'public_manifest_sha256':identity(self.public/'ARTIFACT_MANIFEST.json')['sha256'],
                          'original_acceptance_delta':0},sort_keys=True))

    def publish_manifest(self):
        present={path.name for path in self.public.iterdir()}
        require(present<=set(PUBLIC_FILES)-{'ARTIFACT_MANIFEST.json'},'unexpected public artifact')
        rows=[{'name':name,**identity(self.public/name)} for name in sorted(present)]
        save(self.public/'ARTIFACT_MANIFEST.json',{'schema':'r5.windows-fresh-public-artifact-selection.v1','members':rows,
            'selection':'EXPLICIT_NEW_SUBJECT_DATA_ONLY; NO_CONSOLE_HIDDEN_FILES_PRIVATE_ARCHIVE_OR_SEALED_ANSWERS'})
    def failure(self,exc):
        # The maintained runner owns post-attempt reconciliation. Never launch another resume here.
        diagnostic=primary_diagnostic(exc,self)
        final_refs={'status':'NOT_APPLICABLE_NO_SUBJECT_GIT'}
        if (self.repo/'.git').exists():
            try:
                raw=self.git('for-each-ref','--format=%(refname) %(objectname)','refs/implementaudit',label='failure-readback-refs')
                pairs=[line.split(' ',1) for line in raw.decode('utf-8').splitlines()]
                require(all(len(row)==2 and row[0].startswith('refs/implementaudit/')
                    and re.fullmatch('[0-9a-f]{40}',row[1]) for row in pairs),'final ref readback shape differs')
                final_refs={'status':'UNQUALIFIED_FINAL_REFS_OBSERVED','stdout_sha256':sha(raw),
                    'refs':dict(pairs),'scope':'AFTER_THE_ADAPTER_FAILURE; NOT_A_CURRENTNESS_OR_TRANSITION_VERDICT'}
            except Exception as error:
                final_refs={'status':'FINAL_REFS_QUERY_FAILED','exception_type':type(error).__name__}
                if self.commands and self.commands[-1]['label']=='failure-readback-refs':
                    final_refs.update({key:self.commands[-1][key] for key in ('exit','stdout_sha256','stderr_sha256')})
        export_errors=export_available_evidence(self)
        if not (self.public/'FAILURE.json').exists():
            save(self.public/'FAILURE.json',{'status':'FAILED_RETAINED_NO_RETRY','stage':self.stage,
                'exception_type':type(exc).__name__,'source_commit':SOURCE_HEAD,'controller':self.controller,
                'primary_diagnostic':diagnostic,
                'raw_evidence_uploaded':False,'authority':'NONE','original_acceptance_delta':0,
                'available_evidence_export_errors':export_errors,'initializer_controls':self.initializer_controls,
                'adapter_final_refs':final_refs})
        if not (self.public/'ARTIFACT_MANIFEST.json').exists(): self.publish_manifest()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source',type=Path);parser.add_argument('--python',type=Path)
    parser.add_argument('--output',required=True,type=Path);parser.add_argument('--emit-public',action='store_true')
    args=parser.parse_args()
    if args.emit_public:
        emit_public(args.output);return
    require(args.source is not None and args.python is not None,'source and physical Python are required')
    campaign=None
    try:
        campaign=Campaign(args)
        campaign.run()
    except BaseException as exc:
        try:
            if campaign is None:preflight_failure(args,exc)
            else:campaign.failure(exc)
        except Exception as evidence_error:
            # Preserve the primary exception; no retry or alternate operation follows.
            print(json.dumps({'status':'FAILURE_EXPORT_INCOMPLETE','exception_type':type(evidence_error).__name__,
                'original_acceptance_delta':0},sort_keys=True))
        raise

if __name__=='__main__': main()
