#!/usr/bin/env python3
"""One new Windows subject and one maintained W-FULL attempt, after external approval.

This adapter does not authenticate entitlement, award acceptance, retry, install
tools, fetch private evidence, or run a model. No Windows operation is simulated.
"""
from __future__ import annotations
import argparse
import base64
import math
import struct
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

SOURCE_HEAD='8ee4ae44d67eb7ac8e8c7d8530c455ae1768605b'
SOURCE_TREE='0da374609f7fea2463a2926f3603b976620bd10e'
REPOSITORY='theislampill/IMPLEMENTAUDIT.md'
BRANCH='pro/dg18-isolated-windows14-20261106'
NATIVE_CHECKS_SHA256='add9bce3a9d1128680eed274e65abcd6a442eabf15fd8a8382b198b25765fcd9'
BASH=Path(r'C:\Program Files\Git\bin\bash.exe')
DIRECT_GIT_PATHS=(r'C:\Program Files\Git\mingw64\bin\git.exe',
                  r'C:\Program Files\Git\ucrt64\bin\git.exe')
GIT=None
PUBLIC_FILES=('RESULT.json','SOURCE.json','TOOLS.json','CONTROL.json','MEASUREMENT.json',
              'TRANSITION.json','RECEIVING.json','NATIVE_CAPTURE.json','NATIVE_RECEIVING.json','FAILURE.json','ARTIFACT_MANIFEST.json')

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
    return {'SystemRoot':str(system),'WINDIR':str(system),'ProgramFiles':str(BASH.parents[2]),'PATHEXT':'.COM;.EXE;.BAT;.CMD',
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
  (b'claim-run.sh: a supported physical Python 3 interpreter is required; set IMPLEMENTAUDIT_PYTH'
   b'ON to its absolute path',)),
 ('CLAIM_REF_READBACK_UNVERIFIED',
  'prefix',
  (b"claim-run.sh: controller ref readback is unverified; retained claim: '",)),
 ('CUSTODY_CANONICAL_LOCAL_DRIVE_REQUIRED',
  'exact',
  (b'claim-run.sh: custody requires a canonical absolute local-drive path',)),
 ('INIT_VALIDATION_REFUSED', 'prefix', (b'claim-run.sh: initialization validation refused: ',)),
 ('R5_REFUSAL_00105E981D8D1B24', 'exact', (b'claim-run.sh: custody ancestor is not a directory',)),
 ('R5_REFUSAL_007A955020BE38DF',
  'exact',
  (b'claim-run.sh: canonical handle namespace is unsupported',)),
 ('R5_REFUSAL_019A12D5A1FAB9AE', 'exact', (b'claim-run.sh: Git object exceeds the bounded read',)),
 ('R5_REFUSAL_02564D26BECD8F06',
  'exact',
  (b'claim-run.sh: native ref custody requires the exact SHA-1 repository',)),
 ('R5_REFUSAL_02B8BC85689BF9DF',
  'exact',
  (b'claim-run.sh: ref request changed its repository binding',)),
 ('R5_REFUSAL_0423D43CF2ED5C92', 'exact', (b'claim-run.sh: retained source bytes drifted',)),
 ('R5_REFUSAL_04891C2921B9D61A',
  'exact',
  (b'claim-run.sh: initialization predecessor is not the exact expected claim',)),
 ('R5_REFUSAL_05BFFE9A207341DE',
  'exact',
  (b'claim-run.sh: initialization validator source differs before execution',)),
 ('R5_REFUSAL_0D6042A0C488C955',
  'exact',
  (b'claim-run.sh: companion source executing claim code differs from the physical load snaps'
   b'hot',)),
 ('R5_REFUSAL_0F48318C80E02623',
  'exact',
  (b'claim-run.sh: Git routing input changed during custody',)),
 ('R5_REFUSAL_0F4E8BF5EE8479BB',
  'exact',
  (b'claim-run.sh: authority ref is physically present but broken',)),
 ('R5_REFUSAL_0F97D2827622B385',
  'prefix',
  (b"claim-run.sh: governed-writer namespace gate is unsafe: '",)),
 ('R5_REFUSAL_0FEC1FA5CA417C7F',
  'exact',
  (b'claim-run.sh: wire object requires exactly one terminal LF',)),
 ('R5_REFUSAL_10EE671100CEE34F',
  'exact',
  (b'claim-run.sh: Git refused the complete physical authority-ref population',)),
 ('R5_REFUSAL_12E0AA94A05357C7',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: .claimed v2 schema or cl'
   b'aim_id invalid',
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
  (b'claim-run.sh: initialization validation refused: validate-run-root: run root is outside repo'
   b'sitory',
   b'validate-run-root: run root is outside repository')),
 ('R5_REFUSAL_1A6E34A7A218CD98',
  'exact',
  (b'claim-run.sh: directory flush selected a different object',)),
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
 ('R5_REFUSAL_28C304C2D83A64A5',
  'exact',
  (b'claim-run.sh: companion source Windows capture identity metadata is unavailable',)),
 ('R5_REFUSAL_2C42728C3AE467B7',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: repo root is not a Git w'
   b'orktree',
   b'validate-run-root: repo root is not a Git worktree')),
 ('R5_REFUSAL_2E00D078E049FADF',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: repo root is not a regul'
   b'ar custody directory',
   b'validate-run-root: repo root is not a regular custody directory')),
 ('R5_REFUSAL_2E6A900D6FC9E2B3',
  'prefix',
  (b"claim-run.sh: run and coordination custody contains a symlink or reparse point: '",)),
 ('R5_REFUSAL_2F32A51E0A0913ED',
  'exact',
  (b'claim-run.sh: canonical handle name unavailable or unbounded',)),
 ('R5_REFUSAL_34FF7F5CEA34A3D1',
  'exact',
  (b'claim-run.sh: ref escapes the exact authority namespace',)),
 ('R5_REFUSAL_3C15245FAF92651C',
  'exact',
  (b'claim-run.sh: loose authority ref is not one exact object ID line',)),
 ('R5_REFUSAL_3D3552966127E035',
  'exact',
  (b'claim-run.sh: companion source executing claim code source changed before load binding',)),
 ('R5_REFUSAL_408C658370EC5460', 'exact', (b'claim-run.sh: owned Git reader did not terminate',)),
 ('R5_REFUSAL_42633BAEFF5F622D',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: supplied repo root is no'
   b't the canonical Git worktree',
   b'validate-run-root: supplied repo root is not the canonical Git worktree')),
 ('R5_REFUSAL_42B65259ECBDDB36',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: .claimed run name is not'
   b' claim-run shaped',
   b'validate-run-root: .claimed run name is not claim-run shaped')),
 ('R5_REFUSAL_45AAED51798D3C01',
  'exact',
  (b'claim-run.sh: canonical directory identity or attributes changed',)),
 ('R5_REFUSAL_464E338E94753101',
  'exact',
  (b'claim-run.sh: authority blob is outside bounded bytes',)),
 ('R5_REFUSAL_4745770A6CC47545',
  'exact',
  (b'claim-run.sh: Git object read timed out; no effect or retry authority',)),
 ('R5_REFUSAL_49BDB4DFC90FA603',
  'exact',
  (b'claim-run.sh: initialization source changed before preparation',)),
 ('R5_REFUSAL_49DC44847D7149A6', 'exact', (b'claim-run.sh: directory custody is closed',)),
 ('R5_REFUSAL_4AB00E4BB507B69D',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: .claimed claimed_at_utc '
   b'is not RFC3339 UTC whole seconds',
   b'validate-run-root: .claimed claimed_at_utc is not RFC3339 UTC whole seconds')),
 ('R5_REFUSAL_4B2F388B5F78333D',
  'exact',
  (b'claim-run.sh: written authority blob failed exact readback',)),
 ('R5_REFUSAL_4C15FF371172581A',
  'exact',
  (b'claim-run.sh: file is not a single-link regular object',)),
 ('R5_REFUSAL_4C248997E6A22B3E', 'exact', (b'claim-run.sh: authority ref is malformed',)),
 ('R5_REFUSAL_4DC2A682D72A8C8D',
  'exact',
  (b'claim-run.sh: another owner holds the rotation or namespace lease',)),
 ('R5_REFUSAL_57FB136A7861CE4E', 'exact', (b'claim-run.sh: retained ancestor is not a directory',)),
 ('R5_REFUSAL_5A1796A31F8044D7',
  'exact',
  (b'claim-run.sh: ref is outside exact authority namespace',)),
 ('R5_REFUSAL_5BD541EA7B8509A3', 'exact', (b'claim-run.sh: authority object is not a blob',)),
 ('R5_REFUSAL_5C3B67CAF56FDAA3',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: .claimed v2 keys/order d'
   b'o not match strict schema',
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
  (b'claim-run.sh: incomplete predecessor has prior continuity receipts; recovery is not initiali'
   b'zation',)),
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
  (b'claim-run.sh: initialization validation refused: validate-run-root: custody path is symlink/'
   b'reparse: ',
   b'validate-run-root: custody path is symlink/reparse: ')),
 ('R5_REFUSAL_6EA584E6FA9105D2',
  'exact',
  (b'claim-run.sh: initialization predecessor run identity is malformed',)),
 ('R5_REFUSAL_6EAEE9EBC597CFF3',
  'prefix',
  (b'claim-run.sh: initialization validation refused: validate-run-root: claimed template is not '
   b'regular custody: ',
   b'validate-run-root: claimed template is not regular custody: ')),
 ('R5_REFUSAL_6ECBBAB63EF48BF2',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: .claimed template promis'
   b'e drift',
   b'validate-run-root: .claimed template promise drift')),
 ('R5_REFUSAL_6ECED1C8EEE9FB42',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: .claimed is not a regula'
   b'r custody file',
   b'validate-run-root: .claimed is not a regular custody file')),
 ('R5_REFUSAL_6F1AD067F58728FA', 'exact', (b'claim-run.sh: Git operation has unknown effect',)),
 ('R5_REFUSAL_712C74EA8A0C823C',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: Python is required for s'
   b'trict claim validation',
   b'validate-run-root: Python is required for strict claim validation')),
 ('R5_REFUSAL_714EF7C1B7196FE1',
  'exact',
  (b'claim-run.sh: directory population changed during enumeration',)),
 ('R5_REFUSAL_72EFC34B90746E97', 'exact', (b'claim-run.sh: custody path is missing',)),
 ('R5_REFUSAL_7650CD19FA108E93',
  'exact',
  (b'claim-run.sh: native ref custody requires the files backend',)),
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
  (b'claim-run.sh: initialization validation refused: validate-run-root: .claimed mode/base is no'
   b't R0024 strict custody',
   b'validate-run-root: .claimed mode/base is not R0024 strict custody')),
 ('R5_REFUSAL_7C35BB4D3C96D838', 'exact', (b'claim-run.sh: packed authority ref is broken',)),
 ('R5_REFUSAL_7D27FF33E1958E26',
  'exact',
  (b'claim-run.sh: component exceeds native length bound',)),
 ('R5_REFUSAL_7DBCAB50F98C1460',
  'exact',
  (b'claim-run.sh: volume root aliases a different canonical name',)),
 ('R5_REFUSAL_7DC01925214D7269',
  'exact',
  (b'claim-run.sh: retained input exceeded its bounded read',)),
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
 ('R5_REFUSAL_8BFCF171F9F66362',
  'prefix',
  (b"claim-run.sh: mktemp failed to claim a run dir under '",)),
 ('R5_REFUSAL_8DEED6621DDC45B8',
  'exact',
  (b'claim-run.sh: custody requires a fixed local volume',)),
 ('R5_REFUSAL_8FF9B8478F425752',
  'exact',
  (b'claim-run.sh: Windows directory handle cleanup failed',)),
 ('R5_REFUSAL_91E2648D5546A5DF',
  'exact',
  (b'claim-run.sh: Git routing input disappeared before custody',)),
 ('R5_REFUSAL_92CC0E9C39313120', 'prefix', (b'claim-run.sh: Git operation failed: ',)),
 ('R5_REFUSAL_92DC1A4E6F2C9F9F',
  'exact',
  (b'claim-run.sh: malformed native directory enumeration',)),
 ('R5_REFUSAL_940889779E6FC25E',
  'exact',
  (b'claim-run.sh: symlink or reparse custody is forbidden',)),
 ('R5_REFUSAL_95C1040398E0D719', 'exact', (b'claim-run.sh: malformed native directory offset',)),
 ('R5_REFUSAL_95E0E6848752A9B1',
  'exact',
  (b'claim-run.sh: companion source executing claim code has no ordinary physical source',)),
 ('R5_REFUSAL_991E5243B04EDE69', 'exact', (b'claim-run.sh: file exceeds bounded allocation',)),
 ('R5_REFUSAL_9AD444E3EB8BF01E',
  'exact',
  (b'claim-run.sh: initialization requires the exact relative claimed root',)),
 ('R5_REFUSAL_9B9B1175A8A4556F',
  'exact',
  (b'claim-run.sh: initialization predecessor claim changed',)),
 ('R5_REFUSAL_9CCE183487BBEC68',
  'exact',
  (b'claim-run.sh: custody path is not canonical absolute',)),
 ('R5_REFUSAL_9D1DA16D12671676',
  'exact',
  (b'claim-run.sh: retained input size changed during read',)),
 ('R5_REFUSAL_9E00E6F0B3B70876',
  'exact',
  (b'claim-run.sh: coordination gate is not an exact one-byte gate',)),
 ('R5_REFUSAL_9F066AECF594A141',
  'exact',
  (b'claim-run.sh: retained ancestor is not a native directory',)),
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
  (b'claim-run.sh: initialization validation refused: validate-run-root: run root is not a direct'
   b'ory',
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
 ('R5_REFUSAL_B297DAFDE0929258',
  'exact',
  (b'claim-run.sh: object request changed its repository binding',)),
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
 ('R5_REFUSAL_C0CA0CF4B0A3CACF',
  'exact',
  (b'claim-run.sh: directory flush handle cleanup failed',)),
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
 ('R5_REFUSAL_C99C785C1F001E1F',
  'exact',
  (b'claim-run.sh: coordination gate changed while opening',)),
 ('R5_REFUSAL_CDB569CC0421D478', 'exact', (b'claim-run.sh: transaction OID is malformed',)),
 ('R5_REFUSAL_CFB015FD17457842',
  'exact',
  (b'claim-run.sh: native retained-directory capability is unsupported on this host',)),
 ('R5_REFUSAL_D0F1B360239EDCD7',
  'exact',
  (b'claim-run.sh: canonical ancestor was replaced, renamed or redirected',)),
 ('R5_REFUSAL_D1433AE73E63201F',
  'exact',
  (b'claim-run.sh: authority object exceeds bounded read',)),
 ('R5_REFUSAL_D320DE471B116DEA',
  'prefix',
  (b"claim-run.sh: governed-writer namespace custody contains a symlink or reparse point: '",)),
 ('R5_REFUSAL_D32A0D99D3260B4D',
  'exact',
  (b'ImportError: Windows load identity metadata is unavailable',
   b'claim-run.sh: companion source Windows load identity metadata is unavailable')),
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
 ('R5_REFUSAL_E63AE146B7B34BA8',
  'exact',
  (b'claim-run.sh: reparse point or changing attributes refused',)),
 ('R5_REFUSAL_E68416BE375DB114',
  'exact',
  (b'claim-run.sh: companion source directory identity changed during capture',)),
 ('R5_REFUSAL_E8290A8B38A212E1',
  'exact',
  (b'claim-run.sh: coordination gate opened an unsafe object',)),
 ('R5_REFUSAL_E85D7CE987A819C3',
  'exact',
  (b'claim-run.sh: native source/grant ref overlaps or conflicts with canonical CAS',)),
 ('R5_REFUSAL_E872EFF030CD9EE8',
  'exact',
  (b'claim-run.sh: coordination gate was replaced or changed',)),
 ('R5_REFUSAL_ED0151130EBC353B',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: .claimed run identity dr'
   b'ift',
   b'validate-run-root: .claimed run identity drift')),
 ('R5_REFUSAL_EFA39CB65688D29E',
  'exact',
  (b'claim-run.sh: coordination gate creation was incomplete',)),
 ('R5_REFUSAL_F190F2BEDDA1A5E8',
  'exact',
  (b'claim-run.sh: initialization validation refused: validate-run-root: .claimed has blank or ma'
   b'lformed key',
   b'validate-run-root: .claimed has blank or malformed key')),
 ('R5_REFUSAL_F22A6C4EC340F7DF',
  'exact',
  (b'claim-run.sh: coordination gate has an unsupported format',)),
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
  (b'claim-run.sh: initialization validation refused: validate-run-root: .claimed repository or c'
   b'ommon-dir custody drift',
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
    for name,relatives in [('NATIVE_CAPTURE.json',('native-capture/SUMMARY.json','native-metadata/SUMMARY.json')),
                           ('NATIVE_RECEIVING.json',('native-receiving/SUMMARY.json',))]:
        for relative in relatives:
            source=campaign.out/relative
            if source.exists() and not (public/name).exists():
                try:
                    body=json.loads(read_json_file(source))
                    bootstrap=campaign.out/'native-metadata/SUMMARY.json'
                    if name=='NATIVE_CAPTURE.json' and relative!=relatives[-1] and bootstrap.exists():
                        body['bootstrap_observation']=json.loads(read_json_file(bootstrap))
                    keep(name,body)
                except Exception as error:errors[name]=type(error).__name__
                break
    return errors

PUBLIC_LITERAL_VALUES = frozenset(('\x00',
 '\x00\x00',
 ' ',
 ' / ',
 ' failed; Win32 error ',
 '%02d-%s',
 '(?m)^OK\\s*$',
 '*',
 ',',
 '-',
 '--',
 '--activate-controller',
 '--bash',
 '--boundary',
 '--controller',
 '--current-controller',
 '--current-receipt',
 '--emit-diagnostic',
 '--emit-public',
 '--entitlement-reference',
 '--epoch',
 '--event',
 '--expected-initialization',
 '--expected-invalidation',
 '--expected-pointer',
 '--format=%(refname) %(objectname)',
 '--git',
 '--inspect-controller-initialization',
 '--invalidate-continuity',
 '--manifest',
 '--manifest-sha256',
 '--next-action',
 '--noprofile',
 '--norc',
 '--operation',
 '--out',
 '--output',
 '--owner-map',
 '--plan',
 '--plan-sha256',
 '--porcelain=v1',
 '--purpose',
 '--python',
 '--read-canonical-state',
 '--read-resume-state',
 '--repo',
 '--repo-root',
 '--request',
 '--require-current-continuity',
 '--resolve-canonical-generation',
 '--resolve-resume-generation',
 '--resume-controller',
 '--role',
 '--rotate-canonical-state',
 '--run-root',
 '--scan-root',
 '--source',
 '--source-head',
 '--source-tree',
 '--stage',
 '--subject',
 '--supersede-claim',
 '--untracked-files=normal',
 '--validate-diagnostic-artifact',
 '--verify-resume-receipt',
 '-1',
 '-B',
 '-C',
 '-I',
 '-X',
 '-b',
 '-c',
 '-manual-resume',
 '-publication',
 '-q',
 '-qm',
 '-refs-after',
 '-refs-before',
 '-z',
 '.',
 '..',
 '.COM;.EXE;.BAT;.CMD',
 '.IMPLEMENTAUDIT/runs',
 '.bin',
 '.claimed',
 '.claude-plugin/marketplace.json',
 '.claude-plugin/plugin.json',
 '.codex-plugin/plugin.json',
 '.git',
 '.gitignore',
 '.json',
 '.md',
 '.projection.tmp',
 '.py',
 '.stderr',
 '.stdout',
 '.tmp',
 '.txt',
 '.v1',
 '/',
 '/G0001',
 '/G0001@',
 '0',
 '01-resolve',
 '02-invalidated',
 '03d',
 '8ee4ae44d67eb7ac8e8c7d8530c455ae1768605b',
 '1',
 'add9bce3a9d1128680eed274e65abcd6a442eabf15fd8a8382b198b25765fcd9',
 ':',
 ': ',
 '; evidence retained; no retry',
 '<selected-native-capture-identities>',
 '=',
 '>BI',
 '>I32sB',
 '@',
 'A broken output channel must not recursively fail while reporting itself.',
 'A complete native Job diagnostic could not be established.',
 'ABNORMAL_EXIT_PROCESS',
 'ACTIVE',
 'ACTIVE_PROCESS_ZERO',
 'ACTUAL_COMPANION_METADATA',
 'ACTUAL_COPIED_SKILL_AND_PHASE_VALIDATOR_ONLY',
 'ACTUAL_FIRST_RECEIPT_VERIFIED_AND_REQUIRED_IN_THIS_PROCESS',
 'ACTUAL_NATIVE_MEASUREMENT_CONTROL_ONLY',
 'ACTUAL_PREDECESSOR_ROTATION',
 'ACTUAL_WINDOWS_CAPTURE_AND_SELECTED_CONTROLS_ONLY; NO_NATIVE_MODEL_OR_ORIGINAL_ACCEPTANCE',
 'ADAPTER_COMPLETED',
 'AFTER_THE_ADAPTER_FAILURE; NOT_A_CURRENTNESS_OR_TRANSITION_VERDICT',
 'ALLOCATED',
 'ALLOCATION_INTENT.json',
 'APPLIES',
 'ARGUMENT_REJECTED',
 'ARTIFACT_MANIFEST.json',
 'ATTEMPT.json',
 'AVAILABLE',
 'Accounting',
 'Actual Windows kernel is required before output or process creation',
 'Actual launch-chain/memory control before any owner effect; no authority.',
 'Actual pending initialization activated; no acceptance awarded',
 'After the measured owner transition, require this pending activation to refuse its stale '
 'expected-old guards',
 'AssertionError',
 'AssignProcessToJobObject',
 'Author only actual new-task facts; do not import fixture receipt/history values.',
 'BLOCKED',
 'BOOTSTRAP_CAPTURE_METADATA',
 'BOUNDED_OBSERVATIONS_ONLY; NO_CURRENTNESS_TRANSFER_OR_ACCEPTANCE',
 'BOUNDED_PACKAGE_INSTALL_AND_SOURCE_CONTROLS; NOT_THE_60000MS_PRODUCT_INTERVAL',
 'BOUND_ELIGIBLE_FOR_NORMAL_CURRENTNESS',
 'C',
 'C02 adjudication',
 'C:\\Program Files\\Git\\bin\\bash.exe',
 'C:\\Program Files\\Git\\mingw64\\bin\\git.exe',
 'C:\\Program Files\\Git\\ucrt64\\bin\\git.exe',
 'C:\\Windows',
 'CHECKPOINT.json',
 'CHECKPOINT.tmp',
 'CHECKPOINT_ONLY_UNOBSERVED',
 'CLAIM_PYTHON_REQUIRED',
 'CLAIM_REF_READBACK_UNVERIFIED',
 'CLEAN',
 'CLOSED_PUBLIC_PROJECTIONS_ONLY; EXACT_RAW_RECORDS_RETAINED_PRIVATELY',
 'COMMAND_INTERRUPTED',
 'COMMAND_NOT_FOUND',
 'COMPLETE',
 'COMPLETE_UNADMITTED',
 'CONSTRUCTOR_PREFLIGHT',
 'CONTINUITY_RECEIPT',
 'CONTROL.json',
 'CURRENT.json',
 'CURRENTNESS_AFTER_NATIVE_SHELL_CONTROLS',
 'CURRENTNESS_BEFORE_NATIVE_SHELL_CONTROLS',
 'CURRENT_FIXED_RECEIVER_ACCEPTED_EXACT_LIVE_CLOSURE',
 'CURRENT_FOCUSED_SOURCE_DIAGNOSTICS',
 'CURRENT_NATIVE_CAPTURE_CONTROLS',
 'CUSTODY_CANONICAL_LOCAL_DRIVE_REQUIRED',
 'Campaign',
 'CloseHandle',
 'Closed field/type/value projection; unknown text and dynamic keys stay private.',
 'Closed, bounded observations; neither stderr text nor its dynamic suffixes escape.',
 'CompanionIdentityPredicate.test_required_windows_metadata_refuses_missing_and_wrong_types',
 'CompanionIdentityPredicate.test_unqualified_runtime_retains_strict_chain',
 'CompanionIdentityPredicate.test_windows_api_difference_preserves_both_mutation_checks',
 'CompanionLoadIdentityPredicate.test_each_common_or_same_api_field_mutation_is_refused',
 'CompanionLoadIdentityPredicate.test_missing_or_wrong_type_common_metadata_fails_closed',
 'CompanionLoadIdentityPredicate.test_other_runtimes_keep_the_strict_chain',
 'CompanionLoadIdentityPredicate.test_qualified_windows_split_is_accepted_by_each_binder',
 'CompletionAssociation',
 'CompositeSourceCases.test_engineered_profiles_select_current_bytes_and_preserve_every_historical_domain',
 'CompositeSourceCases.test_prior_windows_capture_profile_has_exact_physical_members',
 'CompositeSourceCases.test_prior_windows_load_binding_profile_has_exact_physical_members',
 'CompositeSourceCases.test_retained_native_dependency_and_new_core_profiles_are_distinct',
 'CreateIoCompletionPort',
 'CreateJobObjectW',
 'CreateProcessW',
 'Current epoch: G0001',
 'DG18_PUBLIC_DIAGNOSTIC ',
 'DG18_PUBLIC_JSON ',
 'DG18_PUBLIC_REFUSAL ',
 'DG18_PUBLIC_REFUSAL '
 '{"status":"UNQUALIFIED_PUBLICATION_REFUSED","code":"DIAGNOSTIC_CHECKPOINT_OR_OUTPUT_REFUSED","authority":"NONE","automatic_retry":false}',
 'DG18_PUBLIC_REFUSAL '
 '{"status":"UNQUALIFIED_PUBLICATION_REFUSED","code":"DIAGNOSTIC_RECORD_REFUSED","authority":"NONE","automatic_retry":false}',
 'DG18_PUBLIC_REFUSAL '
 '{"status":"UNQUALIFIED_PUBLICATION_REFUSED","code":"PUBLIC_SCHEMA_OR_BOUND_REFUSED","authority":"NONE","automatic_retry":false}',
 'DIAGNOSTIC.json',
 'DIAGNOSTIC_CHECKPOINT_WRITE_REFUSED',
 'DIRECTORY',
 'DONE',
 'DUPLICATE_OBSERVED_PID_INDEX_ONLY; COMPLETE_EVENT_CENSUS_RETAINED_SEPARATELY',
 'Define actual fresh Windows receiving task',
 'DeleteProcThreadAttributeList',
 'EMISSION',
 'ENCODING',
 'ERRNO',
 'EVIDENCE',
 'EXACT_CURRENT_WINDOWS_CALLER_AND_RECEIVER',
 'EXACT_SOURCE_PROFILE_AND_PHYSICAL_HISTORY_CONTROLS_ONLY; NO_HISTORICAL_PASS_INHERITED',
 'EXACT_TYPED_PUBLIC_PROCESS_METADATA; NO_PATHS_COMMANDS_OR_QUALIFICATION',
 'EXIT_PROCESS',
 'EXPECTED_EXIT',
 'EXPECTED_REFUSAL_NO_AUTHORITY_REF_CHANGE',
 'EXTERNAL_ENTITLEMENT_NOT_AUTHENTICATED_BY_THIS_TOOL',
 'EXTERNAL_OWNER_REQUIRED; NOT_AUTHENTICATED_BY_ADAPTER',
 'Enable default MSYS argument conversion only for the three fixed Bash diagnostics.',
 'Exact copied runtime at ',
 'Exact reviewed source of claim-run-rotation.py captured earlier during this new task preparation',
 'Exception',
 'Execute one externally authorized fresh Windows receiving campaign; no historical native '
 'occurrence or original acceptance is asserted.',
 'Extended',
 'FAILED_PRESERVED_NO_RETRY',
 'FAILED_RETAINED_NO_RETRY',
 'FAILURE.json',
 'FAILURE_EXPORT_INCOMPLETE',
 'FAIL_INCOMPLETE',
 'FAIL_NATIVE_CAPTURE_OBSERVATION',
 'FILE',
 'FILE_NOT_FOUND',
 'FINAL_REFS_QUERY_FAILED',
 'FIXED_INSTALLED_SCANNER_PATTERN_ONLY; NO_FREEFORM_TEXT_OR_CAUSAL_VERDICT',
 'FIXED_PATTERN_OBSERVATION_ONLY; NO_FREEFORM_TEXT_OR_CAUSAL_VERDICT',
 'FIXED_PUBLIC_PROJECTION_ONLY; RAW_RECORD_PRIVATE; NO_AUTHORITY_TRANSFER',
 'FIXED_REASON_COUNTS_ONLY_V1',
 'FRESH_MANUAL_BOUNDARY',
 'FileExistsError',
 'FileNotFoundError',
 'Fixed pattern labels only, never free-form process text or a causal verdict.',
 'Fixed source/package diagnostics; no caller-selected command or program.',
 'Fresh Windows W-FULL receiving',
 'Fresh Windows whole-owner resume receiving task',
 'G%04X',
 'G0001',
 'GITHUB_ACTIONS',
 'GITHUB_EVENT_NAME',
 'GITHUB_REF',
 'GITHUB_REPOSITORY',
 'GITHUB_RUN_ATTEMPT',
 'GITHUB_RUN_ID',
 'GIT_CONFIG_GLOBAL',
 'GIT_CONFIG_NOSYSTEM',
 'GIT_CONFIG_SYSTEM',
 'GIT_DUBIOUS_OWNERSHIP',
 'GIT_IDENTITY_REQUIRED',
 'GIT_NOT_REPOSITORY',
 'GIT_OPTIONAL_LOCKS',
 'GIT_TERMINAL_PROMPT',
 'G[0-9A-F]{4}',
 'GetExitCodeProcess',
 'GetQueuedCompletionStatus',
 'Git identity/readback failed: ',
 'HEAD',
 'HEAD^{tree}',
 'Hash one held image file and reject changes during its readback.',
 'IMAGE_OBSERVATION_FAILURES; NOT_THE_COMPLETE_JOB_EVENT_CENSUS',
 'IMAGE_UNAVAILABLE',
 'IMPLEMENTAUDIT_PYTHON',
 'INCOMPLETE',
 'INCOMPLETE_UNADMITTED',
 'INDEPENDENT_MEASUREMENT_READ',
 'INDEPENDENT_NATIVE_RECEIVING',
 'INDEPENDENT_OWNER_AND_TRANSITION_READBACK',
 'INITIALIZATION_TOKEN_REFUSAL',
 'INITIALIZED_PREDECESSOR',
 'INIT_VALIDATION_REFUSED',
 'INSTALLED_DEPENDENCY_SCAN_ONLY',
 'INSTALLED_DEPENDENCY_SOURCE_REPO_LABEL_MISSING',
 'IO',
 'Independent exact small-record validation. Never grants main artifact eligibility.',
 'InitializeProcThreadAttributeList',
 'Inspect actual Windows initialization predecessor',
 'IsProcessInJob',
 'JSONDecodeError',
 'Job ceased to be terminal during final accounting',
 'KeyError',
 'KeyboardInterrupt',
 'LANG',
 'LAUNCH_INTENT.json',
 'LC_ALL',
 'Limits',
 'Lossless typed event/PID/hash transport. No command, image path or text payload.',
 'MAINTAINED_PREPARE',
 'MAINTAINED_SEPARATE_PROCESS_RECEIVING; EXTERNAL_INDEPENDENT_REVIEW_PENDING',
 'MAINTAINED_SINGLE_EXECUTE',
 'MALFORMED_OR_UNKNOWN',
 'MANIFEST',
 'MEASUREMENT.json',
 'MEASUREMENT_UNAVAILABLE',
 'MSYS2_ARG_CONV_EXCL',
 'Measure one actual fresh Windows owner resume within the maintained whole-Job contract',
 'MeasurementError',
 'MemoryError',
 'NATIVE_CAPTURE.json',
 'NATIVE_DIAGNOSTIC_CONTROLS; NOT_THE_60000MS_PRODUCT_INTERVAL',
 'NATIVE_RECEIVING.json',
 'NEW_PROCESS',
 'NEW_SUBJECT_INITIALIZATION',
 'NONE',
 'NOT_APPLICABLE_NO_SUBJECT_GIT',
 'NOT_STARTED',
 'NO_CURRENTNESS_TRANSITION_OR_NATIVE_ACCEPTANCE',
 'NO_H0_OR_C02_DG30_OR_ISSUE_ACCEPTANCE',
 'NO_NATIVE_OR_ISSUE_ACCEPTANCE',
 'NO_OWNER_LAUNCH',
 'New disposable subject only',
 'New task measurements do not award original acceptance',
 'No historic H0, model session, C02 adjudication or original controller custody is asserted',
 'No old effect replay, automatic retry, cleanup or compensation',
 'No original acceptance grant',
 'No retry',
 'OBSERVATION.json',
 'ONE_NEW_DISPOSABLE_WINDOWS_SUBJECT',
 'OPEN',
 'OPERATION.json',
 'OSError',
 'OTHER_EXCEPTION',
 'OTHER_FIXED_OPERATION',
 'OWNER_LAUNCH_ATTEMPTED_UNQUALIFIED',
 'O_BINARY',
 'O_NOFOLLOW',
 'O_NONBLOCK',
 'Only a fresh isolated Windows qualification episode is selected',
 'Only metadata at this exact owned Actions output; no subject/owner operation.',
 'OpenProcess',
 'OverflowError',
 'PACKAGE_DECLARATION_ONLY; NO_RELEASE_BUILD_OR_G1_QUALIFICATION',
 'PASS',
 'PASS_INDEPENDENT_NATIVE_READBACK',
 'PASS_NATIVE_CAPTURE_CONTROLS',
 'PASS_NATIVE_CAPTURE_METADATA',
 'PASS_NATIVE_METADATA_AND_SELECTED_PREDICATE',
 'PASS_READ_EXISTING_PREDECESSOR_NO_ACTIVATION',
 'PATH',
 'PATHEXT',
 'PENDING_DECISION_MISSING',
 'PERMISSION_DENIED',
 'POPULATION',
 'PREFLIGHT_FAILED_NO_OWNER_LAUNCH',
 'PREFLIGHT_ONLY',
 'PREPARED_ONLY_ENTITLED_EXECUTOR_REQUIRED',
 'PRESERVED',
 'PRESERVED_AFTER.json',
 'PRE_RESUME_EVIDENCE',
 'PROCESS_ALREADY_GONE_OR_UNOPENABLE',
 'PROCESS_START_FAILED',
 'PROCESS_START_PENDING',
 'PROCESS_TIMEOUT',
 'PROJECTION',
 'PROJECTION_BINDING_REFUSED',
 'PUBLIC_DIRECTORY_UNAVAILABLE',
 'PUBLIC_ENCODED_FILE_SIZE_REFUSED',
 'PUBLIC_ENCODED_TOTAL_SIZE_REFUSED',
 'PUBLIC_EXPORT_INTERNAL_REFUSED',
 'PUBLIC_FILE_SHAPE_REFUSED',
 'PUBLIC_FILE_SIZE_REFUSED',
 'PUBLIC_JSON_READ_REFUSED',
 'PUBLIC_MANIFEST_BINDING_REFUSED',
 'PUBLIC_MANIFEST_SCHEMA_REFUSED',
 'PUBLIC_OUTPUT_TRANSPORT_REFUSED',
 'PUBLIC_POPULATION_REFUSED',
 'PUBLIC_TOTAL_SIZE_REFUSED',
 'PUBLISH_SELECTED_NEW_SUBJECT_EVIDENCE',
 'PYTHONDONTWRITEBYTECODE',
 'PYTHON_TRACEBACK',
 'Perform one fresh Windows resume receiving campaign using the pinned public source',
 'PermissionError',
 'ProcessInfo',
 'ProgramFiles',
 'PublicExportError',
 'QualificationError',
 'Qualify exact initialized Windows predecessor parsing and stale expected-old refusal; no '
 'activation or new resume is intended.',
 'QueryFullProcessImageNameW',
 'QueryInformationJobObject',
 'R0033/continuity',
 'R5_REFUSAL_00105E981D8D1B24',
 'R5_REFUSAL_007A955020BE38DF',
 'R5_REFUSAL_019A12D5A1FAB9AE',
 'R5_REFUSAL_02564D26BECD8F06',
 'R5_REFUSAL_02B8BC85689BF9DF',
 'R5_REFUSAL_0423D43CF2ED5C92',
 'R5_REFUSAL_04891C2921B9D61A',
 'R5_REFUSAL_05BFFE9A207341DE',
 'R5_REFUSAL_0D6042A0C488C955',
 'R5_REFUSAL_0F48318C80E02623',
 'R5_REFUSAL_0F4E8BF5EE8479BB',
 'R5_REFUSAL_0F97D2827622B385',
 'R5_REFUSAL_0FEC1FA5CA417C7F',
 'R5_REFUSAL_10EE671100CEE34F',
 'R5_REFUSAL_12E0AA94A05357C7',
 'R5_REFUSAL_14A3E085A95D39C0',
 'R5_REFUSAL_19CF20E26C30FE36',
 'R5_REFUSAL_19DEAEE43BB2AE5B',
 'R5_REFUSAL_1A0ECC593B8BED52',
 'R5_REFUSAL_1A6E34A7A218CD98',
 'R5_REFUSAL_1AC05FCA906F071E',
 'R5_REFUSAL_1AE10D5091ED94E0',
 'R5_REFUSAL_1B0060301DFB3139',
 'R5_REFUSAL_1E230FF736D539F1',
 'R5_REFUSAL_1EAA6133101EF3BF',
 'R5_REFUSAL_24F4667B80D97A7A',
 'R5_REFUSAL_268A6B14B55094F9',
 'R5_REFUSAL_27E26BF1D9CDFAC6',
 'R5_REFUSAL_28C304C2D83A64A5',
 'R5_REFUSAL_2C42728C3AE467B7',
 'R5_REFUSAL_2E00D078E049FADF',
 'R5_REFUSAL_2E6A900D6FC9E2B3',
 'R5_REFUSAL_2F32A51E0A0913ED',
 'R5_REFUSAL_34FF7F5CEA34A3D1',
 'R5_REFUSAL_3C15245FAF92651C',
 'R5_REFUSAL_3D3552966127E035',
 'R5_REFUSAL_408C658370EC5460',
 'R5_REFUSAL_42633BAEFF5F622D',
 'R5_REFUSAL_42B65259ECBDDB36',
 'R5_REFUSAL_45AAED51798D3C01',
 'R5_REFUSAL_464E338E94753101',
 'R5_REFUSAL_4745770A6CC47545',
 'R5_REFUSAL_49BDB4DFC90FA603',
 'R5_REFUSAL_49DC44847D7149A6',
 'R5_REFUSAL_4AB00E4BB507B69D',
 'R5_REFUSAL_4B2F388B5F78333D',
 'R5_REFUSAL_4C15FF371172581A',
 'R5_REFUSAL_4C248997E6A22B3E',
 'R5_REFUSAL_4DC2A682D72A8C8D',
 'R5_REFUSAL_57FB136A7861CE4E',
 'R5_REFUSAL_5A1796A31F8044D7',
 'R5_REFUSAL_5BD541EA7B8509A3',
 'R5_REFUSAL_5C3B67CAF56FDAA3',
 'R5_REFUSAL_5E2E6C7FB84CC975',
 'R5_REFUSAL_5E44D2999175D526',
 'R5_REFUSAL_5F2D0BCB6853AE16',
 'R5_REFUSAL_621BB9E9D6209D6E',
 'R5_REFUSAL_622BCE2DD999F670',
 'R5_REFUSAL_64702485447A19E9',
 'R5_REFUSAL_68C9F511BD41DEED',
 'R5_REFUSAL_6930FBE0D5DC422C',
 'R5_REFUSAL_6AAFCCF5802C2E42',
 'R5_REFUSAL_6E10710C5E9F4E68',
 'R5_REFUSAL_6EA584E6FA9105D2',
 'R5_REFUSAL_6EAEE9EBC597CFF3',
 'R5_REFUSAL_6ECBBAB63EF48BF2',
 'R5_REFUSAL_6ECED1C8EEE9FB42',
 'R5_REFUSAL_6F1AD067F58728FA',
 'R5_REFUSAL_712C74EA8A0C823C',
 'R5_REFUSAL_714EF7C1B7196FE1',
 'R5_REFUSAL_72EFC34B90746E97',
 'R5_REFUSAL_7650CD19FA108E93',
 'R5_REFUSAL_76767BCDA0ECFFA3',
 'R5_REFUSAL_7758B9CD77D56C0F',
 'R5_REFUSAL_7797B7A6E0267C34',
 'R5_REFUSAL_77DC9A5AC559935D',
 'R5_REFUSAL_789C4EB0D12C6B8D',
 'R5_REFUSAL_78E532C3622B9D8B',
 'R5_REFUSAL_794AE38DAB7D50D0',
 'R5_REFUSAL_7B7D1B36CAFE733C',
 'R5_REFUSAL_7C35BB4D3C96D838',
 'R5_REFUSAL_7D27FF33E1958E26',
 'R5_REFUSAL_7DBCAB50F98C1460',
 'R5_REFUSAL_7DC01925214D7269',
 'R5_REFUSAL_8030A890C2B27490',
 'R5_REFUSAL_8365C41A629A358A',
 'R5_REFUSAL_83BD0C9FBA4701DB',
 'R5_REFUSAL_868D074FD4906060',
 'R5_REFUSAL_892684D3F0860466',
 'R5_REFUSAL_8979AD8E7AFBA9AD',
 'R5_REFUSAL_8BFCF171F9F66362',
 'R5_REFUSAL_8DEED6621DDC45B8',
 'R5_REFUSAL_8FF9B8478F425752',
 'R5_REFUSAL_91E2648D5546A5DF',
 'R5_REFUSAL_92CC0E9C39313120',
 'R5_REFUSAL_92DC1A4E6F2C9F9F',
 'R5_REFUSAL_940889779E6FC25E',
 'R5_REFUSAL_95C1040398E0D719',
 'R5_REFUSAL_95E0E6848752A9B1',
 'R5_REFUSAL_991E5243B04EDE69',
 'R5_REFUSAL_9AD444E3EB8BF01E',
 'R5_REFUSAL_9B9B1175A8A4556F',
 'R5_REFUSAL_9CCE183487BBEC68',
 'R5_REFUSAL_9D1DA16D12671676',
 'R5_REFUSAL_9E00E6F0B3B70876',
 'R5_REFUSAL_9F066AECF594A141',
 'R5_REFUSAL_9FDFD856613505AA',
 'R5_REFUSAL_A2A762A8C8EBED03',
 'R5_REFUSAL_A6AF6620003AD699',
 'R5_REFUSAL_A6DC975FD9ADE2E3',
 'R5_REFUSAL_AA56AED120DAB7EC',
 'R5_REFUSAL_ABFCA87096DD0696',
 'R5_REFUSAL_B0E0FB01ECEE64C5',
 'R5_REFUSAL_B12863FC2B1DC4E9',
 'R5_REFUSAL_B14FB49FBBCB12AC',
 'R5_REFUSAL_B1A1030C3CB262B8',
 'R5_REFUSAL_B297DAFDE0929258',
 'R5_REFUSAL_B4238B87411FABA6',
 'R5_REFUSAL_B52AB45C6720BA6E',
 'R5_REFUSAL_B71B82D42EBB485C',
 'R5_REFUSAL_B71DAE8DFFBC18AE',
 'R5_REFUSAL_B8066DF6EC4ECE99',
 'R5_REFUSAL_BA5C3BD182C0AD34',
 'R5_REFUSAL_BAA2ACC5666D65CE',
 'R5_REFUSAL_BCDD90DDBA988846',
 'R5_REFUSAL_C0CA0CF4B0A3CACF',
 'R5_REFUSAL_C1A56B27F0E54BB0',
 'R5_REFUSAL_C1A5B9FC59125766',
 'R5_REFUSAL_C309126B9459033B',
 'R5_REFUSAL_C7536E99C8E8FCAC',
 'R5_REFUSAL_C8110C08E8A5BF3A',
 'R5_REFUSAL_C81AC5E9240546A9',
 'R5_REFUSAL_C932BB8E3516CACB',
 'R5_REFUSAL_C99C785C1F001E1F',
 'R5_REFUSAL_CDB569CC0421D478',
 'R5_REFUSAL_CFB015FD17457842',
 'R5_REFUSAL_D0F1B360239EDCD7',
 'R5_REFUSAL_D1433AE73E63201F',
 'R5_REFUSAL_D320DE471B116DEA',
 'R5_REFUSAL_D32A0D99D3260B4D',
 'R5_REFUSAL_D3EEBF9AAB75D034',
 'R5_REFUSAL_DB6341FF9A0582C7',
 'R5_REFUSAL_E09E9FB23497AD36',
 'R5_REFUSAL_E415B83D6FB85079',
 'R5_REFUSAL_E52BE6F62962A099',
 'R5_REFUSAL_E61922E61251A5B7',
 'R5_REFUSAL_E63AE146B7B34BA8',
 'R5_REFUSAL_E68416BE375DB114',
 'R5_REFUSAL_E8290A8B38A212E1',
 'R5_REFUSAL_E85D7CE987A819C3',
 'R5_REFUSAL_E872EFF030CD9EE8',
 'R5_REFUSAL_ED0151130EBC353B',
 'R5_REFUSAL_EFA39CB65688D29E',
 'R5_REFUSAL_F190F2BEDDA1A5E8',
 'R5_REFUSAL_F22A6C4EC340F7DF',
 'R5_REFUSAL_F469F42ECB0CA0B0',
 'R5_REFUSAL_F90B7A543098C6D5',
 'R5_REFUSAL_FC362BA583052FF7',
 'READBACK_FAILURE.json',
 'READY',
 'READ_BOUND_RECORD',
 'READ_ONLY_PREPARATION_NO_NATIVE_OPERATION_GRANT',
 'READ_REFUSED',
 'RECEIPT.raw',
 'RECEIVING.json',
 'RECORDED_FRESH_ORIGINAL14_TRANSITION_CONSISTENT',
 'RECORDED_OPERATION_READY_FOR_INDEPENDENT_RECEIVING',
 'REFUSED',
 'RESULT.json',
 'ROADMAP',
 'ROADMAP.md',
 'ROOT_EXITED_AND_JOB_EMPTY',
 'ROTATED',
 'RUNNER_TEMP',
 'RUNNING',
 'RUNNING_IN_JOB',
 'Ran ([0-9]+) tests? in',
 'Read existing owned output only; preserve failed native measurements without retry.',
 'Read fixed retained observations only. Never query an owner, launch or retry.',
 'Read-only ASCII log transport of the exact reviewed public artifact population.',
 'Receive the actual fresh Windows whole-owner resume and retain its measured transition',
 'ResumeThread',
 'Retain actual whole-Job measurement and independent receiving evidence',
 'RetainedObservation',
 'Return a fixed scanner observation only; never return private stderr text.',
 'RuntimeError',
 'SELECTED_NATIVE_SHELL_CONTROLS',
 'SEPARATE_PROCESS_SAME_LIVE_WINDOWS_SUBJECT; NO_INDEPENDENT_MODEL_OR_ORIGINAL_ACCEPTANCE',
 'SOURCE.json',
 'SOURCE_AND_CUSTODY_BOOTSTRAP_OBSERVATION_ONLY; NO_OWNER_CONTROLLER_OR_CURRENTNESS_OPERATION',
 'SOURCE_BINDING',
 'SOURCE_MANIFEST.json',
 'STALE_INITIALIZATION_GUARD_RECEIVING',
 'STATE',
 'STATE.md',
 'SUMMARY.json',
 'SUSPENDED_IN_JOB',
 'SUSPENDED_UNASSIGNED',
 'SYNTHETIC_METADATA_PREDICATES_ONLY; NO_NATIVE_QUALIFICATION',
 'SetInformationJobObject',
 'ShellCompanionSourceCustody.',
 'Startup',
 'StartupEx',
 'Stop and retain this newly owned subject after any uncertain effect; no automatic compensation',
 'System32',
 'SystemExit',
 'SystemRoot',
 'TASK.md',
 'TASK_FACTS_ONLY',
 'TEMP',
 'TERMINATED_AND_JOB_EMPTY',
 'TERMINATED_UNASSIGNED_ROOT',
 'TERMINATION_REQUESTED',
 'THIS_FRESH_SUBJECT_ONLY',
 'THIS_FRESH_SUBJECT_ONLY; UNUSED_GIT_BLOBS_ARE_NOT_AUTHORITY',
 'THREE_REAL_READONLY_CALLS_AND_EXACT_CORE8_RECEIVER; NOT_FULL_NATIVE18_CAMPAIGN',
 'TMP',
 'TOOLS.json',
 'TRANSITION.json',
 'TerminateJobObject',
 'TerminateProcess',
 'TimeoutError',
 'TimeoutExpired',
 'TypeError',
 'U32BE_PID_SHA256_32BYTES_U8_MEMBERSHIP_V1',
 'U8_WIN32_EVENT_U32BE_PID_V1',
 'UNADMITTED_DIAGNOSTIC',
 'UNCHANGED',
 'UNEXPECTED_EXIT',
 'UNGRANTED',
 'UNKNOWN_',
 'UNKNOWN_COMPLETION_KEY_',
 'UNOBSERVED',
 'UNQUALIFIED_FINAL_REFS_OBSERVED',
 'UNQUALIFIED_POST_ATTEMPT_OBSERVATION',
 'UNQUALIFIED_POST_ATTEMPT_OBSERVATIONS',
 'UNQUALIFIED_PUBLICATION_REFUSED',
 'UNQUALIFIED_RECORDED_EVIDENCE',
 'UNQUALIFIED_RECORDED_TRANSITION',
 'UpdateProcThreadAttribute',
 'VALIDATION_REPOSITORY_CUSTODY_DRIFT',
 'VERIFIED',
 'Validate the complete original population before any main evidence output.',
 'ValueError',
 'WHOLE_RESUME_OWNER_JOB; PREPARATION_CONTROL_HARNESS_AND_INDEPENDENT_RECEIVING_OUTSIDE_JOB',
 'WINDIR',
 'WINDOWS07_FRESH_SUBJECT',
 'WINDOWS08_FRESH_SUBJECT',
 'WINERROR',
 'WITHIN_WINDOWS_ENVELOPE_AT_RECORDED_SCOPE',
 'WORK_GRAPH',
 'WORK_GRAPH.json',
 'WRITTEN',
 'WaitForSingleObject',
 'Windows Job measurement cleanup was incomplete',
 'Windows Job measurement failed: ',
 '[0-9]{1,20}',
 '[0-9a-f]{40}',
 '[0-9a-f]{64}',
 '[A-Za-z0-9_.-]{1,80}',
 '[a-zA-Z0-9][a-zA-Z0-9._-]*',
 '\\',
 '\\.IMPLEMENTAUDIT/runs/[a-z0-9-]+-[A-Za-z0-9]{6}',
 '_',
 '_WindowsAPI',
 '__init__',
 '__main__',
 '_image_hash',
 'abnormal_exit_event_count',
 'absolute physical Windows executable path required',
 'access is denied',
 'action',
 'action_selection',
 'activate-exact',
 'activation failed',
 'active',
 'active_command',
 'active_limit',
 'active_process_zero_count',
 'actual Windows required',
 'actual caller output differs from direct owner',
 'actual captured public source workload does not trigger byte policy',
 'actual executable/membership observations are absent',
 'actual first receipt required',
 'actual first rotation',
 'actual initialized currentness did not verify',
 'actual source ancestry differs',
 'actual workflow run identity missing',
 'actual-first-receipt-blob',
 'actual-initialization',
 'actual-initialized-predecessor',
 'actual-windows-',
 'actual_task_format_helpers',
 'adapter_final_refs',
 'adapter_sites',
 'add',
 'affinity',
 'after',
 'aggregate committed memory control did not discriminate a single-process peak',
 'aliased direct Git path refused',
 'andons',
 'applicability',
 'architecture_bits',
 'archive',
 'archive_manifest_path',
 'archive_manifest_sha256',
 'archive_pointers',
 'archive_ref_oid',
 'artifact.historical',
 'artifact_id',
 'artifact_refs',
 'ascii',
 'assessment',
 'assign suspended root to Job',
 'assigned_before_resume',
 'associate inactive Job completion port',
 'at_utc',
 'attempt',
 'attribute cleanup: ',
 'attributes',
 'audit_object',
 'authentic Windows execution unavailable; nothing launched',
 'authentic Windows required; no subject allocated',
 'authentication',
 'author identity unknown',
 'author-pending-successor-control',
 'author-real-task',
 'authorisations',
 'authority',
 'authority_ceiling',
 'authorization',
 'automatic_retry',
 'available_evidence_export_errors',
 'baseline',
 'baseline_commit',
 'baseline_ref',
 'baseline_subtracted_bytes',
 'bash',
 'basic',
 'before',
 'bin',
 'bind',
 'binding',
 'binding_record_oid',
 'blob',
 'blob_oid',
 'boolean',
 'bootstrap_metadata',
 'bootstrap_observation',
 'boundary',
 'bounded single-link file required',
 'bytes',
 'caller closure changed',
 'caller selected a different source profile',
 'caller selected another Bash',
 'caller_observations',
 'caller_profile',
 'caller_receiving',
 'candidate',
 'cannot find the file specified',
 'canonical',
 'canonical evidence escapes run root',
 'canonical_custody.py',
 'canonical_hot_projection.py',
 'canonical_rotation_inputs.py',
 'capture',
 'capture byte pins absent',
 'capture identity function population differs',
 'capture_metadata',
 'capture_observations',
 'capture_pins',
 'captured_bytes',
 'captured_sha256',
 'case',
 'cases',
 'cat-file',
 'cb',
 'check-r0039-windows-resume',
 'check-r0039-windows-resume.py',
 'checked',
 'checkpoint',
 'checkpoint_initial',
 'checkpoint_observe',
 'checkpoint_read',
 'checkpoint_record',
 'checkpoint_retention',
 'checkpoint_seq',
 'checkpoint_validate',
 'checkpoint_write',
 'child_exit',
 'child_pid',
 'claim',
 'claim-pending',
 'claim-run-rotation.py',
 'claim-run.sh',
 'claim_id',
 'claim_sha256',
 'classification_scope',
 'clean_environment',
 'cleanup_complete',
 'cleanup_errors',
 'cleanup_or_compensation',
 'close native handle; Win32 error ',
 'close resumed thread handle',
 'closure',
 'cmd',
 'code',
 'command',
 'command failed at ',
 'command not found',
 'commit',
 'commit.gpgsign=false',
 'compensations',
 'compiler',
 'complete independent receiving input required',
 'complete_memory_scope_valid',
 'completed',
 'completion dequeue failed; Win32 error ',
 'completion_port_associated_before_assignment',
 'composite-20261105-r5-h0-mechanical-template-v1-core',
 'conditions',
 'confirm root Job membership',
 'containment',
 'containment: ',
 'containment_status',
 'continuation',
 'continuity',
 'continuity-invalidations',
 'continuity-receipts',
 'continuity_epoch',
 'control.json',
 'controller',
 'controller namespace limit exceeded',
 'controller_id',
 'controllers',
 'controls',
 'copied runtime differs',
 'copied subject runtime differs',
 'copied-install-smoke',
 'core.hooksPath=NUL',
 'count',
 'cpython',
 'create Job',
 'create completion port',
 'create suspended root',
 'creation_event_count',
 'cross_api_identity',
 'current',
 'current generation readback missing',
 'current original generation-v1 pointer missing',
 'current-',
 'current-and-prior-source-profiles',
 'current-controller',
 'current-generation-migrations',
 'current-generations',
 'current\\s+epoch\\s*:',
 'current_applicability',
 'current_controller_oid',
 'current_gate',
 'currentness already satisfied; no fresh operation to measure',
 'currentness_after',
 'currentness_before',
 'currentness_exported_to_other_host',
 'cwd',
 'data_base64',
 'data_bytes',
 'data_sha256',
 'deferrals',
 'dependencies',
 'description',
 'descriptor_after',
 'descriptor_opened',
 'desktop',
 'detail',
 'detected dubious ownership',
 'dg18-iw14-',
 'dg18-w-full-',
 'dg30-job-control',
 'diagnostic artifact custody refused',
 'diagnostic artifact exact readback refused',
 'diagnostic artifact physical bound refused',
 'diagnostic artifact retention refused',
 'diagnostic atomic temporary readback differs',
 'diagnostic byte bound refused',
 'diagnostic checkpoint exact bytes refused',
 'diagnostic checkpoint physical bound refused',
 'diagnostic checkpoint readback differs',
 'diagnostic command refused',
 'diagnostic exception refused',
 'diagnostic existing file shape refused',
 'diagnostic exporter observation refused',
 'diagnostic final public readback differs',
 'diagnostic fixed binding refused',
 'diagnostic fixed traceback site refused',
 'diagnostic immutable public readback differs',
 'diagnostic log bound refused',
 'diagnostic milestone refused',
 'diagnostic native observation refused',
 'diagnostic observation object required',
 'diagnostic observation physical bound refused',
 'diagnostic operation label differs',
 'diagnostic owner binding refused',
 'diagnostic owner boolean refused',
 'diagnostic owner census refused',
 'diagnostic owner duration refused',
 'diagnostic owner memory refused',
 'diagnostic owner terminal observation refused',
 'diagnostic population refused',
 'diagnostic reader observation refused',
 'diagnostic section schema refused',
 'diagnostic sequence refused',
 'diagnostic source code refused',
 'diagnostic status or phase refused',
 'diagnostic top schema refused',
 'diagnostic traceback bound refused',
 'diagnostic_atomic_write',
 'diagnostic_timeout_seconds',
 'digest',
 'direct-',
 'direct_git_layout',
 'directory_identity',
 'document',
 'duplicate JSON key',
 'duplicate JSON member',
 'duplicate creation for a live process PID',
 '0da374609f7fea2463a2926f3603b976620bd10e',
 'elapsed_ms',
 'emit_diagnostic',
 'emit_public',
 'emit_public_retained',
 'encoded public log transport size limit exceeded; artifacts retained, no truncation',
 'encoded_file_bytes',
 'encoded_total_bytes',
 'encoding',
 'ended_utc',
 'entitlement-reference.txt',
 'entitlement_reference',
 'enum',
 'environment',
 'environment_sha256',
 'epoch_ref_oid',
 'epochs/',
 'errno',
 'error',
 'errors',
 'event',
 'event_counts',
 'evidence',
 'evidence output must be separate from source and governed subject',
 'evidence/',
 'evidence_ceilings',
 'evidence_refs',
 'exact',
 'exact Bash, Python and Git identities required',
 'exact approved repository Actions host required',
 'exact capture bootstrap absent',
 'exact initialized controller required',
 'exact initialized predecessor was not received',
 'exact isolated push branch required',
 'exact native-resume source readback required',
 'exact original14 receipt-v3 required',
 'exact physical CPython 3.12.10 required',
 'exact protected projection JSON body required',
 'exact published capture commit/tree required',
 'exact_checked_out_companion',
 'exact_copytree_subject_companion',
 'exact_next_action',
 'exception',
 'exception_type',
 'exec',
 'exec "$1" -I "$2" "$3"',
 'execute',
 'executed_count',
 'execution',
 'execution/CURRENT.json',
 'execution/FAILURE.json',
 'execution/MEASUREMENT.json',
 'execution/PRESERVED_AFTER.json',
 'execution/READBACK_FAILURE.json',
 'execution/RECEIPT.raw',
 'execution/RESULT.json',
 'execution/native-control/control.json',
 'execution/native-control/job/measurement.json',
 'execution/operation/measurement.json',
 'execution/operation/stdout.bin',
 'execution/require-current.stdout',
 'execution/unqualified-readback/OBSERVATION.json',
 'execution/verify-receipt.stdout',
 'exit',
 'exit_code',
 'exit_event_count',
 'expected_bytes',
 'expected_exit',
 'expected_receipt_ref',
 'expected_receipt_schema',
 'expected_sha256',
 'expires_at',
 'explicit external entitlement reference required',
 'export',
 'export_available_evidence',
 'external owner approval reference',
 'external owner entitlement reference has not been supplied',
 'external-new-task-authorization',
 'external_effects',
 'external_entitlement_reference_sha256',
 'failure',
 'failure-readback-refs',
 'faults',
 'file',
 'file changed during independent read',
 'file_bytes',
 'files',
 'files_checked',
 'fill',
 'final ref readback shape differs',
 'final_receipt',
 'first currentness differs',
 'first receipt differs',
 'first-rotation',
 'first_receipt',
 'first_receipt_verified_and_required',
 'fixed direct Git required',
 'fixed physical Bash required',
 'fixtures/canonical-state-rotation/protected_projection_v2_test.py',
 'fixtures/controller-initialization/author_checkpoint.py',
 'flag',
 'flags',
 'focused diagnostic count differs or skipped',
 'focused package diagnostic did not reach its exact success marker',
 'focused source diagnostic failed or cleanup unverified',
 'focused stderr bytes required',
 'focused-',
 'focused_case',
 'focused_cleanup_complete',
 'focused_controls',
 'focused_diagnostics',
 'focused_environment',
 'focused_executed',
 'focused_selection',
 'focused_stderr_observations',
 'for-each-ref',
 'foreign-claim-initialization-token',
 'foreign-claim-initialization-token-refs-after',
 'foreign-claim-initialization-token-refs-before',
 'fresh manual invalidation',
 'fresh-manual-invalidation',
 'fresh_manual_boundary',
 'fresh_slots',
 'from pathlib import Path;import sys;sys.stdout.buffer.write(Path(sys.argv[1]).read_bytes())',
 'frontier',
 'function',
 'gate',
 'generation_path_exists',
 'git',
 'git_blob_oid',
 'git_exit',
 'git_mode',
 'git_pid',
 'github_run_id',
 'goal',
 'group',
 'handoff-resume',
 'handoffs',
 'harness_included',
 'head',
 'historic H0',
 'historical_refusal',
 'history',
 'host',
 'host-reported-compaction',
 'ident',
 'identity',
 'identity_functions',
 'image',
 'image_sha256',
 'implementation',
 'implementaudit.canonical-generation-resolution.v1',
 'implementaudit.canonical-pair.v2',
 'implementaudit.continuity-receipt.v2',
 'implementaudit.continuity-receipt.v3',
 'implementaudit.current-generation.v1',
 'implementaudit.dg30-windows-operation.v1',
 'implementaudit.native-continuity-closure.v1',
 'implementaudit.native-guard-profile.v1',
 'implementaudit.native-resume-source.v1',
 'implementaudit.rotation-owner-map.v2',
 'implementaudit.windows-job-measurement.v1',
 'in_job',
 'incomplete kernel/process-event reconciliation',
 'incomplete root termination did not become observable',
 'independent-original-receiving',
 'inferred-context-gap',
 'inheritance reset: ',
 'init',
 'init.templateDir=',
 'initial_job_flags',
 'initialization',
 'initialization expected-old source/controller/boundary changed',
 'initialization token is absent, stale, copied or belongs to another claim',
 'initialization_activated',
 'initialization_token',
 'initialize process attributes',
 'initializer_controls',
 'inspect-actual-predecessor',
 'inspect-initialization',
 'installed-dependency-boundary',
 'instructions',
 'integer',
 'invalid Windows measurement command, paths, environment or timeout',
 'invalid controller identity',
 'invalid option',
 'invalid or over-envelope aggregate Job committed memory',
 'invalid or over-envelope time: ',
 'invalid or unbounded process-event accounting input',
 'invalid pinned executable identity',
 'invalid qualification JSON',
 'invalid-initialization-token',
 'invalid-initialization-token-refs-after',
 'invalid-initialization-token-refs-before',
 'invalidation_oid',
 'invalidation_token',
 'io',
 'issued_epoch',
 'issuer',
 'job',
 'job/stdout.bin',
 'job_limit',
 'job_summary',
 'job_time',
 'keep',
 'kernel',
 'kernel32',
 'kernel_terminated_processes',
 'kernel_total_processes',
 'key',
 'kind',
 'label',
 'last_check',
 'last_completed_command',
 'launch-preflight',
 'limit inherited handles',
 'line',
 'lines',
 'live canonical resolution differs from primary observation',
 'live receipt differs from primary bytes',
 'load',
 'load_job',
 'locator',
 'ls-files',
 'main',
 'maintained direct Git allowlist differs',
 'maintained operation not qualified for receiving',
 'maintained-execute',
 'maintained-prepare',
 'maintained_execute_returned_zero',
 'maintained_failure',
 'maintained_failure_status',
 'maintained_prepared',
 'maintained_result_received',
 'manifest',
 'manifest subject differs',
 'manifest-sha256',
 'manifest_sha256',
 'manual-resume',
 'marker_oid',
 'markers',
 'max_ws',
 'maximum_aggregate_job_committed_bytes',
 'maximum_ms',
 'measure',
 'measured command is not the exact requested operation',
 'measurement',
 'measurement must be an object',
 'measurement.json',
 'measurement_bytes',
 'measurement_file',
 'measurement_read',
 'measurement_scope',
 'measurement_sha256',
 'member_count',
 'members',
 'message',
 'metadata',
 'metric_admission',
 'min_ws',
 'mingw64',
 'missing concrete pending decision',
 'missing exact authority token: ',
 'missing or impossible measurement: ',
 'missing, incomplete or mismatched measurement: ',
 'missing_files',
 'mode',
 'model session',
 'name',
 'native',
 'native ancestor changed',
 'native capture bytes differ',
 'native capture identity differs',
 'native capture preflight differs',
 'native checking dependency omitted',
 'native companion changed',
 'native companion did not complete its exact scope',
 'native companion digest differs',
 'native controls changed actual currentness',
 'native executable identity changed',
 'native launch-chain control failed',
 'native metadata case failed',
 'native operation must be the next unreused generation',
 'native shell controls incomplete or skipped',
 'native-',
 'native-capture',
 'native-capture/SUMMARY.json',
 'native-control',
 'native-metadata',
 'native-metadata/SUMMARY.json',
 'native-receive',
 'native-receiving',
 'native-receiving/SUMMARY.json',
 'native_capture_controls',
 'native_capture_sha256',
 'native_check',
 'native_checks.py',
 'native_control',
 'native_guards',
 'native_receiving',
 'native_receiving_sha256',
 'new generation does not match the measured operation',
 'new pending initialization differs',
 'new-session',
 'new-task-scope-instruction',
 'new-windows-campaign',
 'new-windows-campaign-',
 'next action changed',
 'next generation already exists or is unknown; no replay or reuse qualifies a full operation',
 'next_',
 'next_action',
 'next_continuity_epoch',
 'next_projection_generation_id',
 'no Windows preflight output on another host',
 'no such file or directory',
 'no-acceptance',
 'no-native-history',
 'non_verdicts',
 'noncanonical prior generation',
 'nonfinite JSON',
 'normal-first-resume',
 'not a git repository',
 'nt',
 'number',
 'object_format',
 'obligations',
 'observation',
 'observations',
 'observe',
 'observe process Job membership',
 'observe_process',
 'observed process image changed during hashing',
 'observed process is outside the exact Job or PID identity was recycled',
 'observed_processes',
 'observed_refs',
 'omitted',
 'one maintained allowlisted direct mingw64/ucrt64 Git image required',
 'one maintained prepare/execute',
 'one separately entitled operation; no automatic retry',
 'one-fresh-attempt',
 'one_shots',
 'open',
 'operation',
 'operation subject binding differs',
 'operation was already satisfied',
 'operation/execution/FAILURE.json',
 'operation/execution/MEASUREMENT.json',
 'operation/execution/RESULT.json',
 'operation/execution/operation/measurement.json',
 'operation/execution/unqualified-readback/OBSERVATION.json',
 'operation/stdout.bin',
 'ordinal',
 'ordinary',
 'ordinary author epoch shape differs',
 'origin',
 'original JSON wrapper binding differs',
 'original JSON wrapper refused',
 'original generation-v1 pointer required',
 'original_acceptance_delta',
 'original_bytes',
 'original_reds',
 'original_scope',
 'original_sha256',
 'original_utf8_json',
 'os',
 'os_name',
 'other_bytes',
 'other_ops',
 'out',
 'out-of-job, unknown or unrelated required process',
 'outcome',
 'output',
 'owned-rewritten-companion.py',
 'owned_same_size_rewritten_companion',
 'owner',
 'owner failed or returned no receipt; preserve effect for independent readback',
 'owner-map.json',
 'owner_call',
 'owner_execution_started',
 'owner_map',
 'package',
 'package-contract',
 'package/implementaudit-package.json',
 'pair_id',
 'paired readback differs from canonical bytes',
 'pairs',
 'parent traversal in evidence output refused',
 'parent traversal refused',
 'parent traversal refused: ',
 'partial_accounting_error',
 'path',
 'path_before',
 'path_current',
 'payload',
 'payloads',
 'peak_job_commit',
 'peak_job_committed_bytes',
 'peak_process_commit',
 'peak_single_process_committed_bytes',
 'pending predecessor inspection changed currentness',
 'pending_boundaries',
 'pending_claim',
 'pending_run',
 'pending_successor_inspected',
 'period_kernel',
 'period_user',
 'permanent marker changed',
 'permanent migration marker required',
 'permission denied',
 'phase',
 'physical',
 'physical CPython 3.12.10 x64 required',
 'pid',
 'plan',
 'plan_sha256',
 'planning',
 'platform',
 'pointer',
 'pointer bytes do not bind their Git object identity',
 'pointer_token',
 'port',
 'pre-containment evidence save: ',
 'predecessor pair/archive/retired-root bytes were not preserved',
 'predecessor-controller-oid',
 'predecessor_kind',
 'predecessor_receipt_ref_oid',
 'predecessor_rotated',
 'preexisting public output refused',
 'preexisting unowned output refused',
 'prefix',
 'preflight',
 'preflight context differs',
 'preflight output differs',
 'preflight_failure',
 'prepare',
 'prepare-pending-successor',
 'prepared',
 'prepared operation digest changed',
 'prepared plan digest differs',
 'prepared source, exact subject or preimage changed',
 'prepared tool identities differ',
 'prepared_utc',
 'preserved_after',
 'primary_diagnostic',
 'priority',
 'private Job exceeded diagnostic containment timeout',
 'private Job flags changed or breakaway became admissible',
 'private original readback differs',
 'private unnamed job; owner and descendants; KILL_ON_JOB_CLOSE',
 'private-diagnostic',
 'private-diagnostic/CHECKPOINT.json',
 'private-public-records',
 'private-traceback.txt',
 'pro/dg18-isolated-windows14-20261106',
 'pro/dg18-r5-w-full-06-20261105',
 'probe.py',
 'process',
 'process attribute-list sizing failed',
 "process event capture exceeds the recorder's physical bound",
 'process event has an invalid PID or follows terminal zero',
 'process event has an unknown schema',
 'process events are incomplete or differ from the kernel total',
 'process exit has no unique preceding creation',
 "process image custody exceeds the recorder's physical bound",
 'process_event_count',
 'process_events',
 'process_limit',
 'process_observation_failures',
 'process_readback',
 'process_time',
 'profile',
 'project_public_value',
 'projected public readback differs',
 'projection_generation_id',
 'protected',
 'protected historical operations',
 'protected payload changed or is incomplete',
 'protected payload missing',
 'protected_manifest_path',
 'protected_manifest_sha256',
 'protected_payloads_sha256',
 'public',
 'public census list required',
 'public document name refused',
 'public event census exceeds unchanged source bound',
 'public event census schema refused',
 'public evidence collision: ',
 'public failure census schema refused',
 'public file shape refused',
 'public image census exceeds unchanged source bound',
 'public image census schema refused',
 'public log transport size limit exceeded; artifacts retained, no truncation',
 'public manifest canonical bytes refused',
 'public manifest differs; no log evidence emitted',
 'public manifest member count refused',
 'public manifest member refused',
 'public manifest schema refused',
 'public observation failure census bound refused',
 'public population or manifest differs',
 'public projection binding differs',
 'public projection nesting bound exceeded',
 'public record must be an object',
 'public refusal transport bound refused',
 'public sampled PID shape refused',
 'public-diagnostic',
 'public/private record collision',
 'public_census',
 'public_document',
 'public_evidence',
 'public_export_rows',
 'public_manifest_created',
 'public_manifest_sha256',
 'public_operation',
 'public_original_path',
 'public_owner_source',
 'public_safe_print',
 'public_withheld',
 'publication_ref_oid',
 'publish_manifest',
 'publish_public_manifest',
 'pull_request',
 'push',
 'python',
 'python_pid',
 'qualification',
 'qualified source commit/tree changed',
 'qualified source is dirty',
 'queries',
 'query',
 'query Job peak',
 'query accounting',
 'r0039-windows-job',
 'r0039-windows-job.py',
 'r0039_job_gate',
 'r5.new-task-frontier.v1',
 'r5.windows-fresh-public-artifact-selection.v1',
 'r5.windows05.native-',
 'r5.windows07.public-diagnostic.v1',
 'r5.windows07.public-summary.v1',
 'r5.windows14.public-diagnostic.v1',
 'r5.windows14.public-summary.v1',
 'rationale',
 'raw',
 'raw_console_uploaded',
 'raw_evidence',
 'raw_evidence_uploaded',
 'rb',
 'read',
 'read bound exceeded',
 'read root exit code',
 'read-',
 'read-ROADMAP',
 'read-STATE',
 'read-canonical-pair.py',
 'read-only exact-current preparation; creates no native boundary',
 'read_bytes',
 'read_json_file',
 'read_ops',
 'read_request_bytes',
 'readback changed source or controller refs',
 'readback failed: ',
 'readback_failure',
 'reader',
 'real byte-triggered predecessor rotation failed',
 'reason',
 'reason_counts',
 'receipt',
 'receipt bytes do not bind their Git object identity',
 'receipt is not the exact measured successor',
 'receipt verify/currentness/owner outputs disagree',
 'receipt_raw',
 'receipt_ref_oid',
 'receipt_sha256',
 'receipt_token',
 'receive',
 'receive-fresh-operation',
 'receiver',
 'receiving-dependency',
 'reconcile_process_events',
 'reconciled',
 'record',
 'record_id',
 'record_kind',
 'recorder identity changed; unqualified owner query refused: ',
 'recorders',
 'ref_count',
 'ref_scans_equal',
 'reference',
 'refs',
 'refs/heads/',
 'refs/implementaudit',
 'refs/implementaudit/',
 'refs/implementaudit/continuity-receipts/',
 'refs/implementaudit/controllers/',
 'refs/implementaudit/current-generation-migrations/',
 'refs/implementaudit/current-generations/',
 'refs/implementaudit/state-archives/',
 'refs_after_queries',
 'refs_after_sha256',
 'refs_before_queries',
 'refs_before_sha256',
 'refs_sha256',
 'refusal reason differs at ',
 'refuse_activation',
 'refused activation changed an authority ref',
 'regular evidence file required',
 'regular file required',
 'release',
 'reparse or symlink path refused',
 'reparse/symlink path refused',
 'reparse/symlink path refused: ',
 'replace',
 'repo',
 'reported process counts do not reconcile',
 'request',
 'requested controller differs from actual source',
 'require',
 'require-after-predecessor-inspection',
 'require-after-stale-initialization-refusal',
 'require-current',
 'require-first',
 'require-first-',
 'require-migrated-predecessor',
 'require_current_exit',
 'require_stdout_sha256',
 'required executable was not observed in the Job: ',
 'required native control process escaped measured Job',
 'reserved',
 'reserved2',
 'reserved2_size',
 'resolve-canonical',
 'resolve-current',
 'resolve-resume',
 'resolve_canonical_exit',
 'resolve_resume_exit',
 'result_file',
 'result_status',
 'retained',
 'retained receipt, marker and archive ref population is incomplete',
 'retained root PID was recreated',
 'retained-',
 'retained_files',
 'retained_paths',
 'retained_state',
 'retired_ROADMAP',
 'retired_STATE',
 'returncode',
 'rev-parse',
 'roadmap_path',
 'roadmap_sha256',
 'role',
 'rollback',
 'root command is not the pinned Bash executable',
 'root exit observation failed',
 'root is not in its private Job before resume',
 'root resume failed; Win32 error ',
 'root suspension changed before the sole resume',
 'root_exit_observed_ms',
 'root_job_membership_confirmed',
 'root_pid',
 'root_prior_suspend_count',
 'rotate-canonical-state.py',
 'route',
 'run',
 'run escapes its subject',
 'run identity absent',
 'run using the exact selected physical Python',
 'run-r0039-windows-resume.py',
 'run_relative',
 'run_root_identity',
 'runner is not the qualified source copy',
 'runner_dispatch_started',
 'runtime',
 'runtime identity changed; unqualified owner query refused: ',
 'runtime population differs',
 'runtime source population incomplete',
 'runtime_artifacts',
 'same_api_pairs_equal',
 'same_json',
 'sampled_pid_census_complete',
 'sampled_pids',
 'sampled_process_images',
 'save',
 'scheduling',
 'schema',
 'schema_version',
 'scope',
 'scope_boundaries',
 'scripts',
 'scripts/check-installed-payload-self-contained.sh',
 'scripts/check-package-contract.sh',
 'scripts/check-r0039-windows-resume.py',
 'scripts/operational-evidence.py',
 'scripts/operational_query_policy.py',
 'scripts/package-contract.py',
 'scripts/r0039-windows-job.py',
 'scripts/run-r0039-windows-resume.py',
 'scripts/work-graph-continuity-transport.py',
 'selected',
 'selected Python differs from running physical interpreter',
 'selected native shell controls failed or cleanup unverified',
 'selected_count',
 'selected_cross_api_equal',
 'selected_direct_git_contract',
 'selected_shell',
 'selection',
 'separated_output',
 'set Job containment',
 'sha',
 'sha1',
 'sha256',
 'shell-evidence',
 'shell-job',
 'shell-job/measurement.json',
 'shell-job/stderr.bin',
 'shell-work',
 'shell_cleanup_complete',
 'shell_controls',
 'shell_executed',
 'show',
 'skills',
 'skills/',
 'skills/implementaudit/scripts',
 'skills/implementaudit/scripts/',
 'skills/implementaudit/scripts/claim-run-rotation.py',
 'skills/implementaudit/scripts/claim-run.sh',
 'skills/implementaudit/scripts/compile-work-graph.py',
 'skills/implementaudit/templates',
 'skipped=',
 'skipped_count',
 'snapshot',
 'snapshot_capture',
 'snapshot_job',
 'snapshots',
 'source',
 'source Git blob differs',
 'source and physical Python are required',
 'source and subject must be separate',
 'source blob differs',
 'source changed after operation',
 'source changed during capture controls',
 'source changed during separate receiving',
 'source checkout is dirty',
 'source checkout must be clean; do not stash or repair it in this runner',
 'source commit/tree differs',
 'source index member differs',
 'source manifest ancestry differs',
 'source manifest digest differs',
 'source member differs',
 'source member differs: ',
 'source or authority changed during preflight',
 'source-captured-in-this-new-task',
 'source-head',
 'source-peers/native-runtime/SOURCE_MANIFEST.json',
 'source-peers/native-runtime/skills/implementaudit/scripts/canonical_hot_projection.py',
 'source-peers/native-runtime/skills/implementaudit/scripts/canonical_rotation_inputs.py',
 'source-peers/native-runtime/skills/implementaudit/scripts/claim-run-rotation.py',
 'source-peers/native-runtime/skills/implementaudit/scripts/claim-run.sh',
 'source-peers/native-runtime/skills/implementaudit/scripts/rotate-canonical-state.py',
 'source-peers/native-runtime/skills/implementaudit/scripts/validate-run-root.sh',
 'source-tree',
 'source/authority changed during native measurement controls',
 'source/runtime/tool identities changed during operation',
 'source/runtime/tool snapshot changed',
 'source_and_refs_unchanged',
 'source_bytes',
 'source_commit',
 'source_head',
 'source_manifest_sha256',
 'source_record',
 'source_refusal_codes',
 'source_refusal_codes_limited',
 'source_root',
 'source_sha256',
 'source_snapshot',
 'source_status',
 'source_tree',
 'st_atime_ns',
 'st_birthtime_ns',
 'st_ctime_ns',
 'st_dev',
 'st_file_attributes',
 'st_gid',
 'st_ino',
 'st_mode',
 'st_mtime_ns',
 'st_nlink',
 'st_reparse_tag',
 'st_size',
 'st_uid',
 'stage',
 'stale initialization refusal changed currentness',
 'stale-expected-old-initialization',
 'stale-expected-old-initialization-refs-after',
 'stale-expected-old-initialization-refs-before',
 'stale_initialization_guard',
 'started_suspended',
 'started_utc',
 'startup',
 'stat',
 'state',
 'state-archives',
 'state-generations',
 'state_path',
 'state_sha256',
 'status',
 'stderr',
 'stderr.bin',
 'stderr_bytes',
 'stderr_codes',
 'stderr_numeric_errors',
 'stderr_numeric_errors_limited',
 'stderr_observations',
 'stderr_scan_bytes',
 'stderr_scan_limit_reached',
 'stderr_sha256',
 'stdin',
 'stdio close: ',
 'stdout',
 'stdout.bin',
 'stdout_bytes',
 'stdout_sha256',
 'steers',
 'store_true',
 'strict_four_way_equal',
 'strict_json',
 'subject',
 'subject identity changed: ',
 'subject runtime differs from qualified source: ',
 'subject with space',
 'subject_created',
 'subject_directory_allocated',
 'subject_head',
 'subject_head_tree',
 'subject_root',
 'subject_status',
 'subject_tree',
 'summary_sha256',
 'supersedes',
 'supported fixed direct Git executable required',
 'suspended root preparation exceeded diagnostic containment timeout',
 'synthetic-binder-predicates',
 'sys',
 'target',
 'task-tmp',
 'task_bodies',
 'terminal',
 'terminal zero event is early, repeated or inconsistent',
 'terminal_active_processes',
 'terminal_breakaway_allowed',
 'terminal_job_flags',
 'terminate incomplete Job',
 'terminate unassigned suspended root',
 'terminated',
 'terminated Job did not become observably empty',
 'test-support/r5-h0-template-history/eb504b84-source/skills/implementaudit/scripts/claim-run-rotation.py',
 'test-support/r5-h0-template-history/eb504b84-source/skills/implementaudit/scripts/claim-run.sh',
 'test-support/r5-windows-load-binding-history/35bf982-source/skills/implementaudit/scripts/claim-run-rotation.py',
 'test-support/r5-windows-load-binding-history/35bf982-source/skills/implementaudit/scripts/claim-run.sh',
 'test_caller_directory_cannot_select_companion_or_bootstrap_import',
 'test_capture_to_compile_path_change_never_executes_replacement',
 'test_exact_companion_executes_in_both_package_layouts',
 'test_hardlinked_companion_is_refused',
 'test_initial_binder_equal_byte_replacement_refuses',
 'test_real_main_module_args_path_import_path_and_stdin_are_preserved',
 'test_same_size_unselected_companion_is_not_executed',
 'test_substrate_equal_byte_replacement_refuses',
 'test_wrong_lengths_and_missing_source_are_refused',
 'tests/composite-source-cases.py',
 'tests/install-copy-smoke.test.sh',
 'tests/shell_companion_source_custody.py',
 'text',
 'theislampill/IMPLEMENTAUDIT.md',
 'this disposable subject only; the adapter does not authenticate entitlement',
 'this new Windows subject only',
 'this newly created Windows qualification subject only',
 'thread',
 'tid',
 'title',
 'token',
 'tool identity changed; unqualified query refused',
 'tools',
 'total',
 'total_bytes',
 'traceback (most recent call last)',
 'transition',
 'transport',
 'tree',
 'true',
 'truthful new subject',
 'type',
 'ucrt64',
 'unable to auto-detect email address',
 'unchanged',
 'unexpected claimed root',
 'unexpected public artifact',
 'unknown Job completion notification',
 'unknown diagnostic milestone',
 'unknown diagnostic phase',
 'unknown option',
 'unknown public census field',
 'unknown public export refusal code',
 'unknown, lost or untyped process event',
 'unqualified-readback',
 'unqualified_readback',
 'unqualified_readback_present',
 'unqualified_ref_scans_equal',
 'unrecognized arguments',
 'unrecognized original boundary',
 'unsafe manifest member',
 'unsafe manifest path',
 'unused separated diagnostic output required',
 'unused separated output required; no retry',
 'user',
 'user.email=r5-windows@example.invalid',
 'user.name=R5 Windows receiving',
 'usr/bin',
 'utc',
 'utf-8',
 'utf8',
 'utf8_json',
 'validate-run-root.sh',
 'validate_diagnostic_artifact',
 'validate_fresh_preflight',
 'validate_measurement',
 'validate_sha256',
 'validate_transition',
 'value',
 'verify-first',
 'verify-first-',
 'verify-receipt',
 'verify_public_projection',
 'verify_source',
 'verify_stdout_sha256',
 'version',
 'wb',
 'whole interval ends before root exit',
 'win32',
 'windows04_diagnostic_job',
 'windows04_fixed_compiler',
 'windows04_independent_driver',
 'windows_path',
 'winerror',
 'withheld',
 'withheld_fields',
 'work_graph',
 'workflow reruns refused; no old attempt replay',
 'write_bytes',
 'write_ops',
 'x',
 'x+',
 'x64 Python required',
 'xb',
 'xchars',
 'xsize',
 'y',
 'ychars',
 'ysize'))

CHECKPOINT_SITE_FUNCTIONS = frozenset(('Campaign',
 'PublicExportError',
 'RetainedObservation',
 '__init__',
 'boolean',
 'canonical',
 'capture',
 'checkpoint_initial',
 'checkpoint_observe',
 'checkpoint_read',
 'checkpoint_record',
 'checkpoint_validate',
 'checkpoint_write',
 'claim',
 'clean_environment',
 'command',
 'count',
 'diagnostic_atomic_write',
 'emit_diagnostic',
 'emit_public',
 'emit_public_retained',
 'enum',
 'export_available_evidence',
 'failure',
 'flag',
 'gate',
 'git',
 'group',
 'identity',
 'integer',
 'keep',
 'load',
 'main',
 'native_check',
 'number',
 'physical',
 'preflight_failure',
 'primary_diagnostic',
 'project_public_value',
 'public_census',
 'public_document',
 'public_export_rows',
 'public_operation',
 'public_original_path',
 'public_safe_print',
 'public_withheld',
 'publish_manifest',
 'publish_public_manifest',
 'read',
 'read_json_file',
 'record',
 'refuse_activation',
 'require',
 'run',
 'save',
 'sha',
 'stderr_codes',
 'stderr_observations',
 'task_bodies',
 'validate_diagnostic_artifact',
 'verify_public_projection',
 'verify_source'))
CHECKPOINT_COMMAND_LABELS = frozenset(('-',
 '--',
 '--activate-controller',
 '--bash',
 '--boundary',
 '--controller',
 '--current-receipt',
 '--entitlement-reference',
 '--epoch',
 '--event',
 '--expected-initialization',
 '--git',
 '--inspect-controller-initialization',
 '--invalidate-continuity',
 '--manifest',
 '--manifest-sha256',
 '--next-action',
 '--noprofile',
 '--norc',
 '--operation',
 '--out',
 '--output',
 '--owner-map',
 '--plan',
 '--plan-sha256',
 '--purpose',
 '--python',
 '--repo',
 '--require-current-continuity',
 '--resume-controller',
 '--rotate-canonical-state',
 '--run-root',
 '--source',
 '--source-head',
 '--source-tree',
 '--subject',
 '--supersede-claim',
 '--verify-resume-receipt',
 '-B',
 '-C',
 '-I',
 '-X',
 '-b',
 '-c',
 '-manual-resume',
 '-q',
 '-qm',
 '-refs-after',
 '-refs-before',
 '.claimed',
 '.git',
 '.gitignore',
 '.json',
 '.md',
 '.stderr',
 '.stdout',
 '.txt',
 '0',
 '03d',
 '1',
 'ACTUAL_PREDECESSOR_ROTATION',
 'ALLOCATED',
 'ALLOCATION_INTENT.json',
 'ARTIFACT_MANIFEST.json',
 'BOOTSTRAP_CAPTURE_METADATA',
 'BOUND_ELIGIBLE_FOR_NORMAL_CURRENTNESS',
 'COMMAND_INTERRUPTED',
 'CONTROL.json',
 'CURRENT_NATIVE_CAPTURE_CONTROLS',
 'EXPECTED_EXIT',
 'EXPECTED_REFUSAL_NO_AUTHORITY_REF_CHANGE',
 'FAILED_RETAINED_NO_RETRY',
 'FAILURE.json',
 'FINAL_REFS_QUERY_FAILED',
 'FRESH_MANUAL_BOUNDARY',
 'G0001',
 'GITHUB_ACTIONS',
 'GITHUB_EVENT_NAME',
 'GITHUB_REF',
 'GITHUB_REPOSITORY',
 'GITHUB_RUN_ATTEMPT',
 'GITHUB_RUN_ID',
 'HEAD',
 'INDEPENDENT_NATIVE_RECEIVING',
 'INITIALIZED_PREDECESSOR',
 'MAINTAINED_PREPARE',
 'MAINTAINED_SINGLE_EXECUTE',
 'MEASUREMENT.json',
 'NATIVE_CAPTURE.json',
 'NATIVE_RECEIVING.json',
 'NEW_SUBJECT_INITIALIZATION',
 'NONE',
 'NOT_APPLICABLE_NO_SUBJECT_GIT',
 'ONE_NEW_DISPOSABLE_WINDOWS_SUBJECT',
 'OTHER_FIXED_OPERATION',
 'PASS_INDEPENDENT_NATIVE_READBACK',
 'PASS_NATIVE_CAPTURE_CONTROLS',
 'PASS_NATIVE_CAPTURE_METADATA',
 'PASS_READ_EXISTING_PREDECESSOR_NO_ACTIVATION',
 'PROCESS_START_FAILED',
 'PROCESS_START_PENDING',
 'PROCESS_TIMEOUT',
 'PUBLISH_SELECTED_NEW_SUBJECT_EVIDENCE',
 'RECEIVING.json',
 'RECORDED_OPERATION_READY_FOR_INDEPENDENT_RECEIVING',
 'RESULT.json',
 'ROADMAP',
 'ROTATED',
 'SOURCE.json',
 'SOURCE_MANIFEST.json',
 'STALE_INITIALIZATION_GUARD_RECEIVING',
 'STATE',
 'SUMMARY.json',
 'TASK.md',
 'TASK_FACTS_ONLY',
 'THIS_FRESH_SUBJECT_ONLY',
 'TOOLS.json',
 'TRANSITION.json',
 'UNEXPECTED_EXIT',
 'UNGRANTED',
 'UNQUALIFIED_FINAL_REFS_OBSERVED',
 'WORK_GRAPH.json',
 'activate-exact',
 'actual-first-receipt-blob',
 'actual-initialized-predecessor',
 'actual_task_format_helpers',
 'adapter_final_refs',
 'add',
 'assessment',
 'authentication',
 'author-pending-successor-control',
 'author-real-task',
 'authority',
 'authority_ceiling',
 'authorization',
 'automatic_retry',
 'available_evidence_export_errors',
 'baseline',
 'baseline_subtracted_bytes',
 'bash',
 'binding_record_oid',
 'blob',
 'bootstrap_observation',
 'bytes',
 'caller_profile',
 'capture',
 'case',
 'cat-file',
 'claim',
 'claim-pending',
 'claim_id',
 'command',
 'commit',
 'composite-20261105-r5-h0-mechanical-template-v1-core',
 'controller',
 'cpython',
 'current',
 'current_controller_oid',
 'cwd',
 'entitlement-reference.txt',
 'errno',
 'evidence',
 'exception_type',
 'execute',
 'exit',
 'expected_exit',
 'external_entitlement_reference_sha256',
 'failure-readback-refs',
 'final_receipt',
 'first-rotation',
 'first_receipt',
 'for-each-ref',
 'foreign-claim-initialization-token',
 'foreign-claim-initialization-token-refs-after',
 'foreign-claim-initialization-token-refs-before',
 'fresh-manual-invalidation',
 'frontier',
 'git',
 'github_run_id',
 'head',
 'implementaudit.rotation-owner-map.v2',
 'init',
 'initialization',
 'initialization_token',
 'initializer_controls',
 'inspect-actual-predecessor',
 'inspect-initialization',
 'invalid-initialization-token',
 'invalid-initialization-token-refs-after',
 'invalid-initialization-token-refs-before',
 'label',
 'maintained-execute',
 'maintained-prepare',
 'manifest_sha256',
 'manual-resume',
 'maximum_aggregate_job_committed_bytes',
 'maximum_ms',
 'measurement',
 'measurement_scope',
 'members',
 'metadata',
 'missing_files',
 'native-',
 'native-capture',
 'native-metadata',
 'native-receive',
 'native-receiving',
 'native_capture_sha256',
 'native_checks.py',
 'native_receiving_sha256',
 'new-session',
 'new-windows-campaign-',
 'next_action',
 'normal-first-resume',
 'nt',
 'operation',
 'ordinal',
 'original_acceptance_delta',
 'outcome',
 'owner-map.json',
 'owner_map',
 'path',
 'pending_run',
 'plan',
 'plan_sha256',
 'predecessor-controller-oid',
 'predecessor_kind',
 'prepare',
 'prepare-pending-successor',
 'primary_diagnostic',
 'public',
 'public_evidence',
 'public_manifest_sha256',
 'public_owner_source',
 'push',
 'python',
 'qualification',
 'dg18-iw14-',
 'r5.new-task-frontier.v1',
 'raw',
 'raw_evidence',
 'raw_evidence_uploaded',
 'read-',
 'read-ROADMAP',
 'read-STATE',
 'receipt',
 'receipt_raw',
 'receipt_token',
 'receive',
 'reference',
 'refs',
 'refs_after_sha256',
 'refs_before_sha256',
 'require-after-predecessor-inspection',
 'require-after-stale-initialization-refusal',
 'require-first',
 'require-migrated-predecessor',
 'require_stdout_sha256',
 'rev-parse',
 'run_relative',
 'schema',
 'scope',
 'selected_direct_git_contract',
 'sha256',
 'skills',
 'source_commit',
 'source_manifest_sha256',
 'source_tree',
 'stage',
 'stale-expected-old-initialization',
 'stale-expected-old-initialization-refs-after',
 'stale-expected-old-initialization-refs-before',
 'status',
 'stderr_sha256',
 'stdout_sha256',
 'subject',
 'subject_head',
 'subject_tree',
 'task-tmp',
 'transition',
 'tree',
 'true',
 'utf-8',
 'utf8',
 'verify-first',
 'verify_stdout_sha256',
 'win32',
 'winerror',
 'work_graph'))
CHECKPOINT_REFUSAL_CODES = frozenset(('CLAIM_PYTHON_REQUIRED',
 'CLAIM_REF_READBACK_UNVERIFIED',
 'CUSTODY_CANONICAL_LOCAL_DRIVE_REQUIRED',
 'INIT_VALIDATION_REFUSED',
 'R5_REFUSAL_00105E981D8D1B24',
 'R5_REFUSAL_007A955020BE38DF',
 'R5_REFUSAL_019A12D5A1FAB9AE',
 'R5_REFUSAL_02564D26BECD8F06',
 'R5_REFUSAL_02B8BC85689BF9DF',
 'R5_REFUSAL_0423D43CF2ED5C92',
 'R5_REFUSAL_04891C2921B9D61A',
 'R5_REFUSAL_05BFFE9A207341DE',
 'R5_REFUSAL_0D6042A0C488C955',
 'R5_REFUSAL_0F48318C80E02623',
 'R5_REFUSAL_0F4E8BF5EE8479BB',
 'R5_REFUSAL_0F97D2827622B385',
 'R5_REFUSAL_0FEC1FA5CA417C7F',
 'R5_REFUSAL_10EE671100CEE34F',
 'R5_REFUSAL_12E0AA94A05357C7',
 'R5_REFUSAL_14A3E085A95D39C0',
 'R5_REFUSAL_19CF20E26C30FE36',
 'R5_REFUSAL_19DEAEE43BB2AE5B',
 'R5_REFUSAL_1A0ECC593B8BED52',
 'R5_REFUSAL_1A6E34A7A218CD98',
 'R5_REFUSAL_1AC05FCA906F071E',
 'R5_REFUSAL_1AE10D5091ED94E0',
 'R5_REFUSAL_1B0060301DFB3139',
 'R5_REFUSAL_1E230FF736D539F1',
 'R5_REFUSAL_1EAA6133101EF3BF',
 'R5_REFUSAL_24F4667B80D97A7A',
 'R5_REFUSAL_268A6B14B55094F9',
 'R5_REFUSAL_27E26BF1D9CDFAC6',
 'R5_REFUSAL_28C304C2D83A64A5',
 'R5_REFUSAL_2C42728C3AE467B7',
 'R5_REFUSAL_2E00D078E049FADF',
 'R5_REFUSAL_2E6A900D6FC9E2B3',
 'R5_REFUSAL_2F32A51E0A0913ED',
 'R5_REFUSAL_34FF7F5CEA34A3D1',
 'R5_REFUSAL_3C15245FAF92651C',
 'R5_REFUSAL_3D3552966127E035',
 'R5_REFUSAL_408C658370EC5460',
 'R5_REFUSAL_42633BAEFF5F622D',
 'R5_REFUSAL_42B65259ECBDDB36',
 'R5_REFUSAL_45AAED51798D3C01',
 'R5_REFUSAL_464E338E94753101',
 'R5_REFUSAL_4745770A6CC47545',
 'R5_REFUSAL_49BDB4DFC90FA603',
 'R5_REFUSAL_49DC44847D7149A6',
 'R5_REFUSAL_4AB00E4BB507B69D',
 'R5_REFUSAL_4B2F388B5F78333D',
 'R5_REFUSAL_4C15FF371172581A',
 'R5_REFUSAL_4C248997E6A22B3E',
 'R5_REFUSAL_4DC2A682D72A8C8D',
 'R5_REFUSAL_57FB136A7861CE4E',
 'R5_REFUSAL_5A1796A31F8044D7',
 'R5_REFUSAL_5BD541EA7B8509A3',
 'R5_REFUSAL_5C3B67CAF56FDAA3',
 'R5_REFUSAL_5E2E6C7FB84CC975',
 'R5_REFUSAL_5E44D2999175D526',
 'R5_REFUSAL_5F2D0BCB6853AE16',
 'R5_REFUSAL_621BB9E9D6209D6E',
 'R5_REFUSAL_622BCE2DD999F670',
 'R5_REFUSAL_64702485447A19E9',
 'R5_REFUSAL_68C9F511BD41DEED',
 'R5_REFUSAL_6930FBE0D5DC422C',
 'R5_REFUSAL_6AAFCCF5802C2E42',
 'R5_REFUSAL_6E10710C5E9F4E68',
 'R5_REFUSAL_6EA584E6FA9105D2',
 'R5_REFUSAL_6EAEE9EBC597CFF3',
 'R5_REFUSAL_6ECBBAB63EF48BF2',
 'R5_REFUSAL_6ECED1C8EEE9FB42',
 'R5_REFUSAL_6F1AD067F58728FA',
 'R5_REFUSAL_712C74EA8A0C823C',
 'R5_REFUSAL_714EF7C1B7196FE1',
 'R5_REFUSAL_72EFC34B90746E97',
 'R5_REFUSAL_7650CD19FA108E93',
 'R5_REFUSAL_76767BCDA0ECFFA3',
 'R5_REFUSAL_7758B9CD77D56C0F',
 'R5_REFUSAL_7797B7A6E0267C34',
 'R5_REFUSAL_77DC9A5AC559935D',
 'R5_REFUSAL_789C4EB0D12C6B8D',
 'R5_REFUSAL_78E532C3622B9D8B',
 'R5_REFUSAL_794AE38DAB7D50D0',
 'R5_REFUSAL_7B7D1B36CAFE733C',
 'R5_REFUSAL_7C35BB4D3C96D838',
 'R5_REFUSAL_7D27FF33E1958E26',
 'R5_REFUSAL_7DBCAB50F98C1460',
 'R5_REFUSAL_7DC01925214D7269',
 'R5_REFUSAL_8030A890C2B27490',
 'R5_REFUSAL_8365C41A629A358A',
 'R5_REFUSAL_83BD0C9FBA4701DB',
 'R5_REFUSAL_868D074FD4906060',
 'R5_REFUSAL_892684D3F0860466',
 'R5_REFUSAL_8979AD8E7AFBA9AD',
 'R5_REFUSAL_8BFCF171F9F66362',
 'R5_REFUSAL_8DEED6621DDC45B8',
 'R5_REFUSAL_8FF9B8478F425752',
 'R5_REFUSAL_91E2648D5546A5DF',
 'R5_REFUSAL_92CC0E9C39313120',
 'R5_REFUSAL_92DC1A4E6F2C9F9F',
 'R5_REFUSAL_940889779E6FC25E',
 'R5_REFUSAL_95C1040398E0D719',
 'R5_REFUSAL_95E0E6848752A9B1',
 'R5_REFUSAL_991E5243B04EDE69',
 'R5_REFUSAL_9AD444E3EB8BF01E',
 'R5_REFUSAL_9B9B1175A8A4556F',
 'R5_REFUSAL_9CCE183487BBEC68',
 'R5_REFUSAL_9D1DA16D12671676',
 'R5_REFUSAL_9E00E6F0B3B70876',
 'R5_REFUSAL_9F066AECF594A141',
 'R5_REFUSAL_9FDFD856613505AA',
 'R5_REFUSAL_A2A762A8C8EBED03',
 'R5_REFUSAL_A6AF6620003AD699',
 'R5_REFUSAL_A6DC975FD9ADE2E3',
 'R5_REFUSAL_AA56AED120DAB7EC',
 'R5_REFUSAL_ABFCA87096DD0696',
 'R5_REFUSAL_B0E0FB01ECEE64C5',
 'R5_REFUSAL_B12863FC2B1DC4E9',
 'R5_REFUSAL_B14FB49FBBCB12AC',
 'R5_REFUSAL_B1A1030C3CB262B8',
 'R5_REFUSAL_B297DAFDE0929258',
 'R5_REFUSAL_B4238B87411FABA6',
 'R5_REFUSAL_B52AB45C6720BA6E',
 'R5_REFUSAL_B71B82D42EBB485C',
 'R5_REFUSAL_B71DAE8DFFBC18AE',
 'R5_REFUSAL_B8066DF6EC4ECE99',
 'R5_REFUSAL_BA5C3BD182C0AD34',
 'R5_REFUSAL_BAA2ACC5666D65CE',
 'R5_REFUSAL_BCDD90DDBA988846',
 'R5_REFUSAL_C0CA0CF4B0A3CACF',
 'R5_REFUSAL_C1A56B27F0E54BB0',
 'R5_REFUSAL_C1A5B9FC59125766',
 'R5_REFUSAL_C309126B9459033B',
 'R5_REFUSAL_C7536E99C8E8FCAC',
 'R5_REFUSAL_C8110C08E8A5BF3A',
 'R5_REFUSAL_C81AC5E9240546A9',
 'R5_REFUSAL_C932BB8E3516CACB',
 'R5_REFUSAL_C99C785C1F001E1F',
 'R5_REFUSAL_CDB569CC0421D478',
 'R5_REFUSAL_CFB015FD17457842',
 'R5_REFUSAL_D0F1B360239EDCD7',
 'R5_REFUSAL_D1433AE73E63201F',
 'R5_REFUSAL_D320DE471B116DEA',
 'R5_REFUSAL_D32A0D99D3260B4D',
 'R5_REFUSAL_D3EEBF9AAB75D034',
 'R5_REFUSAL_DB6341FF9A0582C7',
 'R5_REFUSAL_E09E9FB23497AD36',
 'R5_REFUSAL_E415B83D6FB85079',
 'R5_REFUSAL_E52BE6F62962A099',
 'R5_REFUSAL_E61922E61251A5B7',
 'R5_REFUSAL_E63AE146B7B34BA8',
 'R5_REFUSAL_E68416BE375DB114',
 'R5_REFUSAL_E8290A8B38A212E1',
 'R5_REFUSAL_E85D7CE987A819C3',
 'R5_REFUSAL_E872EFF030CD9EE8',
 'R5_REFUSAL_ED0151130EBC353B',
 'R5_REFUSAL_EFA39CB65688D29E',
 'R5_REFUSAL_F190F2BEDDA1A5E8',
 'R5_REFUSAL_F22A6C4EC340F7DF',
 'R5_REFUSAL_F469F42ECB0CA0B0',
 'R5_REFUSAL_F90B7A543098C6D5',
 'R5_REFUSAL_FC362BA583052FF7',
 'VALIDATION_REPOSITORY_CUSTODY_DRIFT'))

# This source is embedded into the Windows05 adapter by its source-bound builder.
# It is an output projection only; it never calls an owner or qualification tool.
PUBLIC_SUMMARY_SCHEMA = 'r5.windows14.public-summary.v1'
PUBLIC_MAP_FIELDS = frozenset((
    'source', 'measurement', 'process_readback', 'runtime', 'python', 'bash', 'git',
    'selected_shell', 'capture_pins', 'snapshots', 'path_before', 'descriptor_opened',
    'descriptor_after', 'path_current', 'shell_controls', 'focused_controls', 'job', 'stdout', 'stderr',
    'bootstrap_observation', 'currentness_before', 'currentness_after', 'transition',
    'assessment', 'receipt', 'retained_state', 'files', 'STATE', 'ROADMAP', 'protected',
    'archive', 'retired_STATE', 'retired_ROADMAP', 'caller_receiving', 'compiler', 'owner',
    'primary_diagnostic', 'operation', 'last_completed_command', 'adapter_final_refs',
    'observations', 'maintained_failure', 'unqualified_readback', 'readback_failure',
    'observation', 'queries', 'resolve-canonical', 'resolve-resume', 'require-current',
    'retained_files', 'error', 'record', 'measurement_file'))
PUBLIC_LIST_FIELDS = frozenset((
    'process_events', 'observed_processes', 'process_observation_failures', 'sampled_pids',
    'version', 'capture_observations', 'cases', 'observations', 'initializer_controls',
    'adapter_sites', 'stderr_codes', 'source_refusal_codes', 'stderr_numeric_errors',
    'cleanup_errors'))
PUBLIC_NUMBER_FIELDS = frozenset((
    'original_acceptance_delta', 'member_count', 'bytes', 'original_bytes', 'source_bytes',
    'root_pid', 'pid', 'python_pid', 'child_pid', 'git_pid', 'child_exit', 'git_exit',
    'started_suspended', 'assigned_before_resume', 'root_job_membership_confirmed',
    'complete_memory_scope_valid', 'creation_event_count', 'exit_event_count',
    'sampled_pid_census_complete', 'initial_job_flags', 'terminal_job_flags',
    'terminal_breakaway_allowed', 'baseline_subtracted_bytes', 'harness_included',
    'diagnostic_timeout_seconds', 'cleanup_complete', 'root_exit_observed_ms',
    'completion_port_associated_before_assignment', 'kernel_total_processes',
    'terminal_active_processes', 'kernel_terminated_processes', 'peak_job_committed_bytes',
    'peak_single_process_committed_bytes', 'root_prior_suspend_count', 'elapsed_ms',
    'exit_code', 'exit', 'expected_exit', 'ordinal', 'stdout_bytes', 'stderr_bytes',
    'errno', 'winerror', 'line', 'code', 'stderr_scan_bytes', 'stderr_scan_limit_reached',
    'source_refusal_codes_limited', 'stderr_numeric_errors_limited', 'expected_bytes',
    'captured_bytes', 'read_request_bytes', 'strict_four_way_equal', 'same_api_pairs_equal',
    'selected_cross_api_equal', 'selected_count', 'executed_count', 'skipped_count',
    'ref_count', 'ref_scans_equal', 'architecture_bits', 'in_job', 'currentness_exported_to_other_host',
    'source_and_refs_unchanged', 'automatic_retry', 'cleanup_or_compensation',
    'raw_evidence_uploaded', 'raw_console_uploaded', 'subject_directory_allocated',
    'owner_execution_started', 'maximum_ms', 'maximum_aggregate_job_committed_bytes',
    'st_dev', 'st_ino', 'st_mode', 'st_nlink', 'st_uid', 'st_gid', 'st_size',
    'st_mtime_ns', 'st_ctime_ns', 'st_atime_ns', 'st_birthtime_ns', 'st_file_attributes', 'st_reparse_tag'))
PUBLIC_HASH_FIELDS = frozenset((
    'sha256', 'expected_sha256', 'captured_sha256', 'manifest_sha256',
    'source_manifest_sha256', 'plan_sha256', 'native_capture_sha256', 'native_receiving_sha256',
    'stdout_sha256', 'stderr_sha256', 'source_sha256', 'original_sha256',
    'verify_stdout_sha256', 'require_stdout_sha256', 'refs_before_sha256', 'refs_after_sha256',
    'refs_sha256', 'protected_payloads_sha256', 'image_sha256', 'receipt_sha256'))
PUBLIC_ENUM_FIELDS = frozenset((
    'schema', 'status', 'stage', 'scope', 'measurement_scope', 'classification_scope',
    'authority', 'authority_ceiling', 'caller_profile', 'profile', 'case', 'label',
    'outcome', 'exception', 'exception_type', 'type', 'event', 'reason', 'receiver',
    'platform', 'os_name', 'implementation', 'source_status', 'containment',
    'containment_status', 'metric_admission', 'function', 'kind', 'origin'))
PUBLIC_PRIVATE_FIELDS = frozenset((
    'controller', 'controller_id', 'claim_id', 'run_root_identity', 'pending_run',
    'current_controller_oid', 'first_receipt', 'final_receipt', 'receipt_raw',
    'receipt_token', 'pointer_token', 'invalidation_token', 'token', 'refs',
    'refs_before_queries', 'refs_after_queries', 'current', 'pointer', 'preserved_after',
    'closure', 'command', 'cwd', 'path', 'image', 'sampled_process_images',
    'message', 'detail', 'partial_accounting_error', 'history', 'payload'))


def public_withheld(value):
    raw = canonical(value)
    return {'withheld': True, 'bytes': len(raw), 'sha256': sha(raw),
            'count': len(value) if isinstance(value, (dict, list)) else 1}


def project_public_value(value, field=None, depth=0):
    """Closed field/type/value projection; unknown text and dynamic keys stay private."""
    require(depth <= 32, 'public projection nesting bound exceeded')
    if field in PUBLIC_PRIVATE_FIELDS:
        return public_withheld(value)
    if field in ('process_events', 'observed_processes', 'process_observation_failures', 'sampled_pids'):
        return public_census(value, field)
    if isinstance(value, dict):
        result = {}; omitted = {}
        allowed = (PUBLIC_MAP_FIELDS | PUBLIC_LIST_FIELDS | PUBLIC_NUMBER_FIELDS |
                   PUBLIC_HASH_FIELDS | PUBLIC_ENUM_FIELDS | PUBLIC_PRIVATE_FIELDS |
                   {'source_commit', 'source_tree'})
        for key, item in value.items():
            if key not in allowed:
                omitted[key] = item
            else:
                result[key] = project_public_value(item, key, depth + 1)
        if omitted:
            result['withheld_fields'] = public_withheld(omitted)
        return result
    if isinstance(value, list):
        if field not in PUBLIC_LIST_FIELDS or len(value) > 16384:
            return public_withheld(value)
        return [project_public_value(item, field, depth + 1) for item in value]
    if value is None:
        return None
    if type(value) in (bool, int, float):
        if field in PUBLIC_NUMBER_FIELDS or field in ('sampled_pids', 'version'):
            # canonical() rejects non-finite numbers before public serialization.
            canonical(value)
            return value
        return public_withheld(value)
    if type(value) is str:
        if field in PUBLIC_HASH_FIELDS and re.fullmatch('[0-9a-f]{64}', value):
            return value
        if field == 'source_commit' and value == SOURCE_HEAD:
            return value
        if field == 'source_tree' and value == SOURCE_TREE:
            return value
        if field in (PUBLIC_ENUM_FIELDS | {'cases', 'stderr_codes', 'source_refusal_codes'}) and value in PUBLIC_LITERAL_VALUES:
            return value
    return public_withheld(value)


def public_document(name, raw):
    require(name in set(PUBLIC_FILES) - {'ARTIFACT_MANIFEST.json'}, 'public document name refused')
    value = json.loads(raw)
    require(type(value) is dict, 'public record must be an object')
    # The inherited failure exporter wraps a complete original JSON string.
    # Decode that exact bound record privately and project it recursively.
    if 'original_utf8_json' in value:
        require(type(value['original_utf8_json']) is str, 'original JSON wrapper refused')
        original = value['original_utf8_json'].encode('utf-8')
        require(value.get('original_bytes') == len(original) and value.get('original_sha256') == sha(original),
                'original JSON wrapper binding differs')
        value = {key: item for key, item in value.items() if key != 'original_utf8_json'}
        value['record'] = json.loads(original)
    return {'schema': PUBLIC_SUMMARY_SCHEMA, 'document': name,
            'source_record': {'bytes': len(raw), 'sha256': sha(raw)},
            'observation': project_public_value(value),
            'scope': 'FIXED_PUBLIC_PROJECTION_ONLY; RAW_RECORD_PRIVATE; NO_AUTHORITY_TRANSFER'}


def public_original_path(public, name):
    return public.parent / 'private-public-records' / name


def publish_public_manifest(public):
    public = physical(public)
    present = {path.name for path in public.iterdir()}
    require(present <= set(PUBLIC_FILES) - {'ARTIFACT_MANIFEST.json'}, 'unexpected public artifact')
    for name in sorted(present):
        path = public / name; current = read_json_file(path)
        original_path = public_original_path(public, name)
        if original_path.exists():
            original = read_json_file(original_path)
            projected = canonical(public_document(name, original))
            require(current in (original, projected), 'public/private record collision')
        else:
            original = current
            save(original_path, original)
            require(read_json_file(original_path) == original, 'private original readback differs')
            projected = canonical(public_document(name, original))
        if current != projected:
            temporary = public / (name + '.projection.tmp')
            save(temporary, projected)
            os.replace(temporary, path)
        require(read_json_file(path) == projected, 'projected public readback differs')
    rows = [{'name': name, **identity(public / name)} for name in sorted(present)]
    save(public / 'ARTIFACT_MANIFEST.json', {
        'schema': 'r5.windows-fresh-public-artifact-selection.v1', 'members': rows,
        'selection': 'CLOSED_PUBLIC_PROJECTIONS_ONLY; EXACT_RAW_RECORDS_RETAINED_PRIVATELY'})


def verify_public_projection(public, name, raw):
    if name == 'ARTIFACT_MANIFEST.json':
        value = json.loads(raw)
        require(raw == canonical(value), 'public manifest canonical bytes refused')
        require(type(value) is dict and set(value) == {'schema', 'members', 'selection'}
                and value['schema'] == 'r5.windows-fresh-public-artifact-selection.v1'
                and value['selection'] == 'CLOSED_PUBLIC_PROJECTIONS_ONLY; EXACT_RAW_RECORDS_RETAINED_PRIVATELY',
                'public manifest schema refused')
        require(type(value['members']) is list and len(value['members']) <= len(PUBLIC_FILES) - 1,
                'public manifest member count refused')
        names = set()
        for row in value['members']:
            require(type(row) is dict and set(row) == {'name', 'bytes', 'sha256'}
                    and row['name'] in set(PUBLIC_FILES) - {'ARTIFACT_MANIFEST.json'}
                    and row['name'] not in names and type(row['bytes']) is int
                    and 0 <= row['bytes'] <= 1048576
                    and type(row['sha256']) is str and re.fullmatch('[0-9a-f]{64}', row['sha256']),
                    'public manifest member refused')
            names.add(row['name'])
        return
    original = read_json_file(public_original_path(public, name))
    require(raw == canonical(public_document(name, original)), 'public projection binding differs')


# Embedded in the Windows14 adapter. Observation/export only; no product calls.
DIAGNOSTIC_MAX_BYTES = 8192
REFUSAL_MAX_BYTES = 1024
PUBLIC_MAX_FILE_BYTES = 1048576
PUBLIC_MAX_TOTAL_BYTES = 4194304
CHECKPOINT_PHASES = frozenset((
    'UNOBSERVED', 'CONSTRUCTOR_PREFLIGHT', 'ALLOCATED', 'NEW_SUBJECT_INITIALIZATION',
    'BOOTSTRAP_CAPTURE_METADATA', 'CURRENT_NATIVE_CAPTURE_CONTROLS',
    'ACTUAL_PREDECESSOR_ROTATION', 'FRESH_MANUAL_BOUNDARY', 'MAINTAINED_PREPARE',
    'MAINTAINED_SINGLE_EXECUTE', 'STALE_INITIALIZATION_GUARD_RECEIVING',
    'INDEPENDENT_NATIVE_RECEIVING', 'PUBLISH_SELECTED_NEW_SUBJECT_EVIDENCE'))
CHECKPOINT_COMPLETED = (
    'subject_created', 'bootstrap_metadata', 'baseline_commit', 'pending_claim',
    'initialization_activated', 'first_receipt_verified_and_required', 'native_capture_controls',
    'pending_successor_inspected', 'predecessor_rotated', 'fresh_manual_boundary',
    'maintained_prepared', 'maintained_execute_returned_zero', 'maintained_result_received',
    'stale_initialization_guard', 'native_receiving', 'public_manifest_created')
CHECKPOINT_EXCEPTIONS = frozenset((
    'NONE', 'OTHER_EXCEPTION', 'RuntimeError', 'OSError', 'ValueError', 'TypeError',
    'KeyError', 'AssertionError', 'TimeoutError', 'TimeoutExpired', 'PermissionError',
    'FileNotFoundError', 'FileExistsError', 'MeasurementError', 'QualificationError',
    'MemoryError', 'OverflowError', 'KeyboardInterrupt', 'SystemExit', 'JSONDecodeError'))
CHECKPOINT_NATIVE_STAGES = frozenset((
    'UNOBSERVED', 'MALFORMED_OR_UNKNOWN', 'SOURCE_BINDING', 'ACTUAL_COMPANION_METADATA',
    'COMPLETE', 'CURRENTNESS_BEFORE_NATIVE_SHELL_CONTROLS', 'SELECTED_NATIVE_SHELL_CONTROLS',
    'CURRENT_FOCUSED_SOURCE_DIAGNOSTICS', 'CURRENTNESS_AFTER_NATIVE_SHELL_CONTROLS',
    'INDEPENDENT_MEASUREMENT_READ', 'INDEPENDENT_OWNER_AND_TRANSITION_READBACK',
    'EXACT_CURRENT_WINDOWS_CALLER_AND_RECEIVER'))
CHECKPOINT_NATIVE_STATUSES = frozenset((
    'UNOBSERVED', 'MALFORMED_OR_UNKNOWN', 'FAIL_INCOMPLETE', 'FAILED_RETAINED_NO_RETRY',
    'PASS_NATIVE_CAPTURE_METADATA', 'PASS_NATIVE_CAPTURE_CONTROLS', 'PASS_INDEPENDENT_NATIVE_READBACK'))
CHECKPOINT_FOCUSED_CASES = frozenset((
    'NONE', 'MALFORMED_OR_UNKNOWN', 'installed-dependency-boundary', 'package-contract',
    'copied-install-smoke', 'synthetic-binder-predicates', 'current-and-prior-source-profiles'))
EXPORT_CODES = frozenset((
    'NONE', 'PUBLIC_DIRECTORY_UNAVAILABLE', 'PUBLIC_POPULATION_REFUSED',
    'PUBLIC_FILE_SHAPE_REFUSED', 'PUBLIC_JSON_READ_REFUSED', 'PUBLIC_MANIFEST_SCHEMA_REFUSED',
    'PROJECTION_BINDING_REFUSED', 'PUBLIC_FILE_SIZE_REFUSED', 'PUBLIC_TOTAL_SIZE_REFUSED',
    'PUBLIC_MANIFEST_BINDING_REFUSED', 'PUBLIC_ENCODED_FILE_SIZE_REFUSED',
    'PUBLIC_ENCODED_TOTAL_SIZE_REFUSED', 'PUBLIC_EXPORT_INTERNAL_REFUSED',
    'PUBLIC_OUTPUT_TRANSPORT_REFUSED', 'DIAGNOSTIC_CHECKPOINT_WRITE_REFUSED'))
EXPORT_CHECKPOINTS = frozenset(('NOT_STARTED', 'DIRECTORY', 'POPULATION', 'FILE',
    'PROJECTION', 'MANIFEST', 'ENCODING', 'EMISSION', 'COMPLETE'))


def checkpoint_initial():
    return {'schema': 'r5.windows14.public-diagnostic.v1', 'attempt': 'WINDOWS08_FRESH_SUBJECT',
        'source_commit': SOURCE_HEAD, 'source_tree': SOURCE_TREE, 'authority': 'NONE',
        'scope': 'BOUNDED_OBSERVATIONS_ONLY; NO_CURRENTNESS_TRANSFER_OR_ACCEPTANCE',
        'automatic_retry': False, 'original_acceptance_delta': 0, 'checkpoint_seq': 0,
        'status': 'CHECKPOINT_ONLY_UNOBSERVED', 'phase': 'UNOBSERVED',
        'maximum_ms': 60000, 'maximum_aggregate_job_committed_bytes': 201326592,
        'completed': {name: False for name in CHECKPOINT_COMPLETED},
        'failure': {'exception': 'NONE', 'adapter_sites': [], 'source_refusal_codes': []},
        'command': {'ordinal': 0, 'label': 'NONE', 'exit': None, 'outcome': 'UNOBSERVED'},
        'native': {'status': 'UNOBSERVED', 'stage': 'UNOBSERVED', 'shell_executed': None,
            'focused_executed': None, 'focused_case': 'NONE', 'shell_cleanup_complete': None,
            'focused_cleanup_complete': None},
        'owner': {'runner_dispatch_started': False, 'result_status': 'UNOBSERVED',
            'maintained_failure_status': 'UNOBSERVED',
            'measurement_read': 'UNOBSERVED', 'measurement_bytes': None, 'measurement_sha256': None,
            'status': 'UNOBSERVED', 'root_pid': None, 'started_suspended': None,
            'assigned_before_resume': None, 'complete_memory_scope_valid': None,
            'elapsed_ms': None, 'root_exit_observed_ms': None, 'peak_job_committed_bytes': None,
            'peak_single_process_committed_bytes': None, 'baseline_subtracted_bytes': None,
            'kernel_total_processes': None, 'terminal_active_processes': None,
            'creation_event_count': None, 'exit_event_count': None, 'process_event_count': None,
            'cleanup_complete': None, 'exit_code': None},
        'reader': {'status': 'UNOBSERVED', 'stage': 'UNOBSERVED',
            'caller_observations': None, 'source_and_refs_unchanged': None,
            'unqualified_readback_present': False, 'unqualified_ref_scans_equal': None,
            'resolve_canonical_exit': None, 'resolve_resume_exit': None, 'require_current_exit': None},
        'export': {'state': 'NOT_STARTED', 'code': 'NONE', 'file': 'NONE',
            'checkpoint': 'NOT_STARTED', 'file_bytes': 0, 'total_bytes': 0,
            'encoded_file_bytes': 0, 'encoded_total_bytes': 0, 'files_checked': 0}}


def checkpoint_validate(value):
    template = checkpoint_initial()
    require(type(value) is dict and set(value) == set(template), 'diagnostic top schema refused')
    for key in ('schema', 'attempt', 'source_commit', 'source_tree', 'authority', 'scope',
                'automatic_retry', 'original_acceptance_delta', 'maximum_ms',
                'maximum_aggregate_job_committed_bytes'):
        require(type(value[key]) is type(template[key]) and value[key] == template[key],
                'diagnostic fixed binding refused')
    def integer(item, low=0, high=2**63-1, nullable=False):
        return (nullable and item is None) or (type(item) is int and low <= item <= high)
    def boolean(item): return item is None or type(item) is bool
    def number(item):
        return item is None or (type(item) in (int, float) and math.isfinite(item) and 0 <= item <= 2**53)
    require(integer(value['checkpoint_seq'], high=4096), 'diagnostic sequence refused')
    require(value['phase'] in CHECKPOINT_PHASES and value['status'] in (
        'CHECKPOINT_ONLY_UNOBSERVED', 'RUNNING', 'FAILED_PRESERVED_NO_RETRY', 'ADAPTER_COMPLETED'),
        'diagnostic status or phase refused')
    for name in ('completed', 'failure', 'command', 'native', 'owner', 'reader', 'export'):
        require(type(value[name]) is dict and set(value[name]) == set(template[name]),
                'diagnostic section schema refused')
    require(all(type(v) is bool for v in value['completed'].values()), 'diagnostic milestone refused')
    failure = value['failure']
    require(failure['exception'] in CHECKPOINT_EXCEPTIONS, 'diagnostic exception refused')
    require(type(failure['adapter_sites']) is list and len(failure['adapter_sites']) <= 4,
            'diagnostic traceback bound refused')
    for row in failure['adapter_sites']:
        require(type(row) is dict and set(row) == {'function', 'line'}
                and row['function'] in CHECKPOINT_SITE_FUNCTIONS and integer(row['line'], 1, 20000),
                'diagnostic fixed traceback site refused')
    require(type(failure['source_refusal_codes']) is list and len(failure['source_refusal_codes']) <= 16
            and all(type(code) is str and code in CHECKPOINT_REFUSAL_CODES for code in failure['source_refusal_codes']),
            'diagnostic source code refused')
    command = value['command']
    require(integer(command['ordinal'], high=4096) and command['label'] in CHECKPOINT_COMMAND_LABELS
            and integer(command['exit'], -(2**31), 2**32-1, True)
            and command['outcome'] in ('UNOBSERVED', 'PROCESS_START_PENDING', 'PROCESS_TIMEOUT',
                'PROCESS_START_FAILED', 'COMMAND_INTERRUPTED', 'EXPECTED_EXIT', 'UNEXPECTED_EXIT'),
            'diagnostic command refused')
    native = value['native']
    require(native['status'] in CHECKPOINT_NATIVE_STATUSES and native['stage'] in CHECKPOINT_NATIVE_STAGES
            and integer(native['shell_executed'], 0, 9, True) and integer(native['focused_executed'], 0, 5, True)
            and native['focused_case'] in CHECKPOINT_FOCUSED_CASES
            and boolean(native['shell_cleanup_complete']) and boolean(native['focused_cleanup_complete']),
            'diagnostic native observation refused')
    owner = value['owner']
    require(type(owner['runner_dispatch_started']) is bool
            and owner['result_status'] in ('UNOBSERVED', 'MALFORMED_OR_UNKNOWN',
                'RECORDED_OPERATION_READY_FOR_INDEPENDENT_RECEIVING')
            and owner['maintained_failure_status'] in ('UNOBSERVED', 'MALFORMED_OR_UNKNOWN',
                'OWNER_LAUNCH_ATTEMPTED_UNQUALIFIED', 'NO_OWNER_LAUNCH')
            and owner['measurement_read'] in ('UNOBSERVED', 'READ_BOUND_RECORD', 'READ_REFUSED')
            and owner['status'] in ('UNOBSERVED', 'MALFORMED_OR_UNKNOWN', 'INCOMPLETE_UNADMITTED', 'COMPLETE_UNADMITTED')
            and integer(owner['measurement_bytes'], high=4194304, nullable=True)
            and (owner['measurement_sha256'] is None or (type(owner['measurement_sha256']) is str
                and re.fullmatch('[0-9a-f]{64}', owner['measurement_sha256']))), 'diagnostic owner binding refused')
    for key in ('started_suspended', 'assigned_before_resume', 'complete_memory_scope_valid', 'cleanup_complete'):
        require(boolean(owner[key]), 'diagnostic owner boolean refused')
    for key in ('elapsed_ms', 'root_exit_observed_ms'):
        require(number(owner[key]), 'diagnostic owner duration refused')
    for key in ('peak_job_committed_bytes', 'peak_single_process_committed_bytes', 'baseline_subtracted_bytes'):
        require(integer(owner[key], nullable=True), 'diagnostic owner memory refused')
    for key in ('root_pid', 'kernel_total_processes', 'terminal_active_processes', 'creation_event_count', 'exit_event_count'):
        require(integer(owner[key], high=2**32-1, nullable=True), 'diagnostic owner census refused')
    require(integer(owner['process_event_count'], high=65536, nullable=True)
            and integer(owner['exit_code'], -(2**31), 2**32-1, True), 'diagnostic owner terminal observation refused')
    reader = value['reader']
    require(reader['status'] in CHECKPOINT_NATIVE_STATUSES and reader['stage'] in CHECKPOINT_NATIVE_STAGES
            and integer(reader['caller_observations'], high=3, nullable=True)
            and boolean(reader['source_and_refs_unchanged'])
            and type(reader['unqualified_readback_present']) is bool
            and boolean(reader['unqualified_ref_scans_equal'])
            and all(integer(reader[key], -(2**31), 2**32-1, True) for key in
                    ('resolve_canonical_exit', 'resolve_resume_exit', 'require_current_exit')),
            'diagnostic reader observation refused')
    export = value['export']
    require(export['state'] in ('NOT_STARTED', 'VERIFIED', 'REFUSED') and export['code'] in EXPORT_CODES
            and export['checkpoint'] in EXPORT_CHECKPOINTS and export['file'] in ('NONE', *PUBLIC_FILES)
            and integer(export['files_checked'], high=len(PUBLIC_FILES))
            and all(integer(export[key]) for key in ('file_bytes', 'total_bytes', 'encoded_file_bytes', 'encoded_total_bytes')),
            'diagnostic exporter observation refused')
    raw = canonical(value)
    require(len(raw) <= DIAGNOSTIC_MAX_BYTES, 'diagnostic byte bound refused')
    return raw


def diagnostic_atomic_write(target, raw, *, replace_existing):
    """Commit only this validated record; a failed write leaves the previous file intact.

    Unique exclusive temporary files avoid replaying or deleting an interrupted
    writer's residue. This helper owns only the temporary path it creates.
    """
    import tempfile
    target = Path(target); parent = physical(target.parent)
    descriptor, name = tempfile.mkstemp(prefix=target.name + '.', suffix='.tmp', dir=parent)
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, 'wb') as stream:
            opened = os.fstat(stream.fileno())
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        info = physical(temporary).lstat()
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1
                and (info.st_dev, info.st_ino) == (opened.st_dev, opened.st_ino)
                and temporary.read_bytes() == raw, 'diagnostic atomic temporary readback differs')
        if replace_existing:
            os.replace(temporary, target)
        else:
            # An exclusive hard-link publication cannot replace a concurrent or
            # unreviewed destination. Removing our temporary restores nlink=1.
            os.link(temporary, target)
            temporary.unlink()
    finally:
        # Do not remove stale predecessors, another output, or an owned final file.
        if os.path.lexists(temporary):
            temporary.unlink()


def checkpoint_write(output, value):
    output = physical(output)
    # Validate a copy first; failure must not poison the live diagnostic sequence.
    candidate = dict(value); candidate['checkpoint_seq'] = value['checkpoint_seq'] + 1
    raw = checkpoint_validate(candidate)
    parent = output / 'private-diagnostic'
    parent.mkdir(exist_ok=True); physical(parent)
    target = parent / 'CHECKPOINT.json'
    if os.path.lexists(target):
        info = physical(target).lstat()
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'diagnostic existing file shape refused')
    diagnostic_atomic_write(target, raw, replace_existing=True)
    require(target.read_bytes() == raw, 'diagnostic checkpoint readback differs')
    value['checkpoint_seq'] = candidate['checkpoint_seq']


def checkpoint_read(output):
    target = physical(Path(output) / 'private-diagnostic/CHECKPOINT.json')
    info = target.lstat()
    require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_size <= DIAGNOSTIC_MAX_BYTES,
            'diagnostic checkpoint physical bound refused')
    raw = target.read_bytes(); value = json.loads(raw)
    require(raw == checkpoint_validate(value), 'diagnostic checkpoint exact bytes refused')
    return value


def checkpoint_record(campaign, *, phase=None, milestone=None, command=None, failure=None, completed=False):
    value = campaign.diagnostic
    if phase is not None:
        require(phase in CHECKPOINT_PHASES, 'unknown diagnostic phase'); value['phase'] = phase
    if milestone is not None:
        require(milestone in CHECKPOINT_COMPLETED, 'unknown diagnostic milestone')
        value['completed'][milestone] = True
    if command is not None:
        value['command'] = {key: command.get(key) for key in ('ordinal', 'label', 'exit', 'outcome')}
        if value['command']['label'] not in CHECKPOINT_COMMAND_LABELS:
            value['command']['label'] = 'OTHER_FIXED_OPERATION'
        if command.get('label') == 'maintained-execute': value['owner']['runner_dispatch_started'] = True
    if failure is not None and value['failure']['exception'] == 'NONE':
        name = type(failure).__name__
        value['failure']['exception'] = name if name in CHECKPOINT_EXCEPTIONS else 'OTHER_EXCEPTION'
        sites = []; tb = failure.__traceback__
        while tb is not None:
            if tb.tb_frame.f_code.co_filename == __file__ and tb.tb_frame.f_code.co_name in CHECKPOINT_SITE_FUNCTIONS:
                sites.append({'function': tb.tb_frame.f_code.co_name, 'line': tb.tb_lineno})
            tb = tb.tb_next
        value['failure']['adapter_sites'] = sites[-4:]
        operation = getattr(campaign, 'active_command', None) or {}
        codes = operation.get('source_refusal_codes', [])
        value['failure']['source_refusal_codes'] = [code for code in codes
            if type(code) is str and code in CHECKPOINT_REFUSAL_CODES][:16]
        value['status'] = 'FAILED_PRESERVED_NO_RETRY'
    elif completed:
        value['status'] = 'ADAPTER_COMPLETED'
    elif value['status'] == 'CHECKPOINT_ONLY_UNOBSERVED':
        value['status'] = 'RUNNING'
    checkpoint_write(campaign.out, value)


def checkpoint_observe(campaign, *, persist=True):
    """Read fixed retained observations only. Never query an owner, launch or retry."""
    value = campaign.diagnostic
    def read(relative):
        path = campaign.out / relative
        if not path.exists(): return None
        info = physical(path).lstat()
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_size <= 4194304,
                'diagnostic observation physical bound refused')
        raw = path.read_bytes(); body = json.loads(raw)
        require(type(body) is dict, 'diagnostic observation object required')
        return body, raw
    def enum(item, admitted): return item if type(item) is str and item in admitted else 'MALFORMED_OR_UNKNOWN'
    def count(item, maximum): return item if type(item) is int and 0 <= item <= maximum else None
    def flag(item): return item if type(item) is bool else None
    for relative, target in (('native-metadata/SUMMARY.json', 'native'),
                             ('native-capture/SUMMARY.json', 'native'),
                             ('native-receiving/SUMMARY.json', 'reader')):
        try:
            observed = read(relative)
            if observed is None: continue
            body, _ = observed; row = value[target]
            row['status'] = enum(body.get('status'), CHECKPOINT_NATIVE_STATUSES)
            row['stage'] = enum(body.get('stage'), CHECKPOINT_NATIVE_STAGES)
            if target == 'native':
                shell = body.get('shell_controls', {}); focused = body.get('focused_controls', {})
                if type(shell) is dict:
                    row['shell_executed'] = count(shell.get('executed_count'), 9)
                    job = shell.get('job', {})
                    if type(job) is dict: row['shell_cleanup_complete'] = flag(job.get('cleanup_complete'))
                if type(focused) is dict:
                    row['focused_executed'] = count(focused.get('executed_count'), 5)
                    observations = focused.get('observations', [])
                    if type(observations) is list and observations and type(observations[-1]) is dict:
                        last = observations[-1]
                        row['focused_case'] = enum(last.get('case'), CHECKPOINT_FOCUSED_CASES)
                        job = last.get('job', {})
                        if type(job) is dict: row['focused_cleanup_complete'] = flag(job.get('cleanup_complete'))
            else:
                row['source_and_refs_unchanged'] = flag(body.get('source_and_refs_unchanged'))
                caller = body.get('caller_receiving', {})
                if type(caller) is dict and type(caller.get('observations')) is list:
                    row['caller_observations'] = count(len(caller['observations']), 3)
        except Exception:
            value[target]['status'] = 'MALFORMED_OR_UNKNOWN'
    try:
        result = read('operation/execution/RESULT.json')
        if result is not None:
            status = result[0].get('status')
            value['owner']['result_status'] = status if status == 'RECORDED_OPERATION_READY_FOR_INDEPENDENT_RECEIVING' else 'MALFORMED_OR_UNKNOWN'
    except Exception:
        value['owner']['result_status'] = 'MALFORMED_OR_UNKNOWN'
    try:
        failed = read('operation/execution/FAILURE.json')
        if failed is not None:
            value['owner']['maintained_failure_status'] = enum(failed[0].get('status'),
                ('OWNER_LAUNCH_ATTEMPTED_UNQUALIFIED', 'NO_OWNER_LAUNCH'))
    except Exception:
        value['owner']['maintained_failure_status'] = 'MALFORMED_OR_UNKNOWN'
    try:
        observed = read('operation/execution/unqualified-readback/OBSERVATION.json')
        if observed is not None:
            body, _ = observed; reader = value['reader']; reader['unqualified_readback_present'] = True
            reader['unqualified_ref_scans_equal'] = flag(body.get('ref_scans_equal'))
            queries = body.get('queries', {})
            if type(queries) is dict:
                for key, label in (('resolve_canonical_exit', 'resolve-canonical'),
                                   ('resolve_resume_exit', 'resolve-resume'),
                                   ('require_current_exit', 'require-current')):
                    row = queries.get(label)
                    item = row.get('exit_code') if type(row) is dict else None
                    reader[key] = item if type(item) is int and -(2**31) <= item <= 2**32-1 else None
    except Exception:
        pass  # Absent/malformed unqualified evidence never becomes a positive reader result.
    for relative in ('operation/execution/MEASUREMENT.json', 'operation/execution/operation/measurement.json'):
        try:
            observed = read(relative)
            if observed is None: continue
            body, raw = observed; owner = value['owner']
            owner.update(measurement_read='READ_BOUND_RECORD', measurement_bytes=len(raw), measurement_sha256=sha(raw),
                status=enum(body.get('status'), ('INCOMPLETE_UNADMITTED', 'COMPLETE_UNADMITTED')))
            for key in ('started_suspended', 'assigned_before_resume', 'complete_memory_scope_valid', 'cleanup_complete'):
                owner[key] = flag(body.get(key))
            for key in ('elapsed_ms', 'root_exit_observed_ms'):
                item = body.get(key)
                owner[key] = item if type(item) in (int, float) and math.isfinite(item) and 0 <= item <= 2**53 else None
            for key in ('peak_job_committed_bytes', 'peak_single_process_committed_bytes', 'baseline_subtracted_bytes'):
                owner[key] = count(body.get(key), 2**63-1)
            for key in ('root_pid', 'kernel_total_processes', 'terminal_active_processes', 'creation_event_count', 'exit_event_count'):
                owner[key] = count(body.get(key), 2**32-1)
            events = body.get('process_events')
            owner['process_event_count'] = count(len(events), 65536) if type(events) is list else None
            item = body.get('exit_code')
            owner['exit_code'] = item if type(item) is int and -(2**31) <= item <= 2**32-1 else None
            break
        except Exception:
            value['owner']['measurement_read'] = 'READ_REFUSED'
    if persist:
        checkpoint_write(campaign.out, value)


def public_census(value, field):
    """Lossless typed event/PID/hash transport. No command, image path or text payload."""
    require(type(value) is list, 'public census list required')
    original = public_withheld(value)
    if field == 'process_events':
        require(len(value) <= 65536, 'public event census exceeds unchanged source bound')
        codes = {'ACTIVE_PROCESS_ZERO': 4, 'NEW_PROCESS': 6, 'EXIT_PROCESS': 7, 'ABNORMAL_EXIT_PROCESS': 8}
        payload = bytearray(); counts = {name: 0 for name in codes}
        for row in value:
            require(type(row) is dict and set(row) == {'event', 'pid'}
                    and type(row['event']) is str and row['event'] in codes
                    and type(row['pid']) is int and 0 <= row['pid'] <= 2**32-1, 'public event census schema refused')
            payload.extend(struct.pack('>BI', codes[row['event']], row['pid'])); counts[row['event']] += 1
        encoding = 'U8_WIN32_EVENT_U32BE_PID_V1'
        extra = {'event_counts': counts}
    elif field == 'observed_processes':
        require(len(value) <= 8192, 'public image census exceeds unchanged source bound')
        payload = bytearray()
        for row in value:
            require(type(row) is dict and set(row) == {'pid', 'image', 'image_sha256', 'in_job'}
                    and type(row['pid']) is int and 0 < row['pid'] <= 2**32-1
                    and type(row['image']) is str and type(row['image_sha256']) is str
                    and re.fullmatch('[0-9a-f]{64}', row['image_sha256']) and type(row['in_job']) is bool,
                    'public image census schema refused')
            payload.extend(struct.pack('>I32sB', row['pid'], bytes.fromhex(row['image_sha256']), int(row['in_job'])))
        encoding = 'U32BE_PID_SHA256_32BYTES_U8_MEMBERSHIP_V1'; extra = {}
    elif field == 'process_observation_failures':
        require(len(value) <= 65536, 'public observation failure census bound refused')
        counts = {'PROCESS_ALREADY_GONE_OR_UNOPENABLE': 0, 'IMAGE_UNAVAILABLE': 0}
        for row in value:
            require(type(row) is dict and set(row) == {'pid', 'reason'}
                    and type(row['pid']) is int and 0 < row['pid'] <= 2**32-1
                    and type(row['reason']) is str and row['reason'] in counts, 'public failure census schema refused')
            counts[row['reason']] += 1
        return {'encoding': 'FIXED_REASON_COUNTS_ONLY_V1', 'count': len(value), 'reason_counts': counts,
                'source_record': original, 'scope': 'IMAGE_OBSERVATION_FAILURES; NOT_THE_COMPLETE_JOB_EVENT_CENSUS'}
    elif field == 'sampled_pids':
        require(len(value) <= 8192 and all(type(pid) is int and 0 < pid <= 2**32-1 for pid in value),
                'public sampled PID shape refused')
        return {'count': len(value), 'source_record': original,
                'scope': 'DUPLICATE_OBSERVED_PID_INDEX_ONLY; COMPLETE_EVENT_CENSUS_RETAINED_SEPARATELY'}
    else:
        raise RuntimeError('unknown public census field')
    payload = bytes(payload)
    return {'encoding': encoding, 'count': len(value), 'data_base64': base64.b64encode(payload).decode('ascii'),
            'data_bytes': len(payload), 'data_sha256': sha(payload), 'source_record': original, **extra,
            'scope': 'EXACT_TYPED_PUBLIC_PROCESS_METADATA; NO_PATHS_COMMANDS_OR_QUALIFICATION'}


class PublicExportError(RuntimeError):
    def __init__(self, code, progress):
        require(code in EXPORT_CODES, 'unknown public export refusal code')
        self.code = code; self.progress = dict(progress)
        super().__init__(code)


def public_export_rows(output, progress):
    def gate(ok, code):
        if not ok: raise PublicExportError(code, progress)
    progress['checkpoint'] = 'DIRECTORY'
    try: public = physical(Path(output) / 'public')
    except Exception: raise PublicExportError('PUBLIC_DIRECTORY_UNAVAILABLE', progress) from None
    progress['checkpoint'] = 'POPULATION'
    names = {p.name for p in public.iterdir()}
    gate(names <= set(PUBLIC_FILES) and 'ARTIFACT_MANIFEST.json' in names, 'PUBLIC_POPULATION_REFUSED')
    rows = []
    # Check physical member sizes before the manifest's own per-member cap so a
    # size refusal reports the actual fixed member and its observed size.
    for name in sorted(names - {'ARTIFACT_MANIFEST.json'}) + ['ARTIFACT_MANIFEST.json']:
        progress.update(file=name, file_bytes=0, encoded_file_bytes=0, checkpoint='FILE')
        try:
            info = physical(public / name).lstat(); progress['file_bytes'] = info.st_size
            gate(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, 'PUBLIC_FILE_SHAPE_REFUSED')
        except PublicExportError: raise
        except Exception: raise PublicExportError('PUBLIC_FILE_SHAPE_REFUSED', progress) from None
        gate(info.st_size <= PUBLIC_MAX_FILE_BYTES, 'PUBLIC_FILE_SIZE_REFUSED')
        progress['total_bytes'] += info.st_size
        gate(progress['total_bytes'] <= PUBLIC_MAX_TOTAL_BYTES - DIAGNOSTIC_MAX_BYTES, 'PUBLIC_TOTAL_SIZE_REFUSED')
        try: raw = read_json_file(public / name)
        except Exception: raise PublicExportError('PUBLIC_JSON_READ_REFUSED', progress) from None
        gate(len(raw) == info.st_size, 'PUBLIC_FILE_SHAPE_REFUSED')
        progress['checkpoint'] = 'PROJECTION'
        try: verify_public_projection(public, name, raw)
        except Exception:
            code = 'PUBLIC_MANIFEST_SCHEMA_REFUSED' if name == 'ARTIFACT_MANIFEST.json' else 'PROJECTION_BINDING_REFUSED'
            raise PublicExportError(code, progress) from None
        progress['files_checked'] += 1
        rows.append({'name': name, 'bytes': len(raw), 'sha256': sha(raw), 'utf8_json': raw.decode('utf-8')})
    progress.update(checkpoint='MANIFEST', file='ARTIFACT_MANIFEST.json')
    manifest = json.loads(next(row['utf8_json'] for row in rows if row['name'] == 'ARTIFACT_MANIFEST.json'))
    expected = {row['name']: (row['bytes'], row['sha256']) for row in manifest['members']}
    actual = {row['name']: (row['bytes'], row['sha256']) for row in rows if row['name'] != 'ARTIFACT_MANIFEST.json'}
    gate(expected == actual, 'PUBLIC_MANIFEST_BINDING_REFUSED')
    lines = []
    for row in rows:
        progress.update(checkpoint='ENCODING', file=row['name'])
        line = 'DG18_PUBLIC_JSON ' + json.dumps(row, ensure_ascii=True, separators=(',', ':'))
        length = len(line.encode('ascii')) + 2
        progress['encoded_file_bytes'] = length; progress['encoded_total_bytes'] += length
        gate(length <= PUBLIC_MAX_FILE_BYTES, 'PUBLIC_ENCODED_FILE_SIZE_REFUSED')
        gate(progress['encoded_total_bytes'] <= PUBLIC_MAX_TOTAL_BYTES - DIAGNOSTIC_MAX_BYTES,
             'PUBLIC_ENCODED_TOTAL_SIZE_REFUSED')
        lines.append(line)
    return lines


def emit_public(output):
    """Validate the complete original population before any main evidence output."""
    progress = checkpoint_initial()['export']
    lines = public_export_rows(output, progress)
    for line in lines: print(line)


def public_safe_print(line):
    """A broken output channel must not recursively fail while reporting itself."""
    try:
        print(line)
        return True
    except BaseException:
        return False


def emit_public_retained(output):
    output = physical(output)
    target = output / 'private-diagnostic/CHECKPOINT.json'
    value = checkpoint_read(output) if target.exists() else checkpoint_initial()
    class RetainedObservation:
        pass
    observation = RetainedObservation(); observation.out = output; observation.diagnostic = value
    # Observation collection is independent of checkpoint persistence. A disk
    # refusal cannot mask the main exporter gate or erase the last valid stage.
    checkpoint_observe(observation, persist=False)
    progress = checkpoint_initial()['export']; code = 0; retained = 'UNOBSERVED'
    try:
        lines = public_export_rows(output, progress)
        progress.update(state='VERIFIED', code='NONE', checkpoint='EMISSION')
        value['export'] = dict(progress)
        try:
            checkpoint_write(output, value); retained = 'WRITTEN'
        except BaseException:
            retained = 'REFUSED'
            raise PublicExportError('DIAGNOSTIC_CHECKPOINT_WRITE_REFUSED', progress) from None
        for line in lines:
            if not public_safe_print(line):
                raise PublicExportError('PUBLIC_OUTPUT_TRANSPORT_REFUSED', progress)
        progress['checkpoint'] = 'COMPLETE'
    except PublicExportError as exc:
        progress = exc.progress; progress.update(state='REFUSED', code=exc.code); code = 1
    except BaseException:
        progress.update(state='REFUSED', code='PUBLIC_OUTPUT_TRANSPORT_REFUSED'
            if progress['checkpoint'] == 'EMISSION' else 'PUBLIC_EXPORT_INTERNAL_REFUSED'); code = 1
    value['export'] = dict(progress)
    try:
        checkpoint_write(output, value); retained = 'WRITTEN'
    except BaseException:
        retained = 'REFUSED'; code = 1
        if progress['code'] == 'NONE':
            progress.update(state='REFUSED', code='DIAGNOSTIC_CHECKPOINT_WRITE_REFUSED')
    if code:
        line = 'DG18_PUBLIC_REFUSAL ' + json.dumps({'status': 'UNQUALIFIED_PUBLICATION_REFUSED',
            'authority': 'NONE', 'automatic_retry': False, 'checkpoint_retention': retained,
            **progress}, sort_keys=True, separators=(',', ':'))
        require(len(line.encode('ascii')) + 2 <= REFUSAL_MAX_BYTES, 'public refusal transport bound refused')
        public_safe_print(line)
    return code


def emit_diagnostic(output):
    """Independent bounded export; either the verified artifact or log can retain it.

    A successful return requires the exact immutable artifact. If artifact
    retention refuses, a verified log record is still emitted, but eligibility
    stays false. Log transport failure after artifact retention does not erase
    or disqualify that separately verified artifact.
    """
    output = physical(output); value = checkpoint_read(output); raw = checkpoint_validate(value)
    line = 'DG18_PUBLIC_DIAGNOSTIC ' + json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(',', ':'))
    require(len(line.encode('ascii')) + 2 <= DIAGNOSTIC_MAX_BYTES - REFUSAL_MAX_BYTES,
            'diagnostic log bound refused')
    artifact_retained = False
    try:
        public = output / 'public-diagnostic'; public.mkdir(exist_ok=True); physical(public)
        require({p.name for p in public.iterdir()} <= {'DIAGNOSTIC.json'}, 'diagnostic population refused')
        target = public / 'DIAGNOSTIC.json'
        if os.path.lexists(target):
            info = physical(target).lstat()
            require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and target.read_bytes() == raw,
                    'diagnostic immutable public readback differs')
        else:
            diagnostic_atomic_write(target, raw, replace_existing=False)
        info = physical(target).lstat()
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and target.read_bytes() == raw,
                'diagnostic final public readback differs')
        artifact_retained = True
    except BaseException:
        pass  # The validated record still has an independent bounded log path.
    public_safe_print(line)
    require(artifact_retained, 'diagnostic artifact retention refused')


def validate_diagnostic_artifact(output):
    """Read-only eligibility check with no dependence on stdout or emitter exit.

    Only the exact bounded artifact matching the current canonical checkpoint is
    eligible. This CLI does not create, repair, replace, or emit either record.
    """
    output = physical(output); value = checkpoint_read(output); raw = checkpoint_validate(value)
    line = 'DG18_PUBLIC_DIAGNOSTIC ' + json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(',', ':'))
    require(len(line.encode('ascii')) + 2 <= DIAGNOSTIC_MAX_BYTES - REFUSAL_MAX_BYTES,
            'diagnostic log bound refused')
    public = physical(output / 'public-diagnostic')
    require({p.name for p in public.iterdir()} == {'DIAGNOSTIC.json'}, 'diagnostic population refused')
    target = physical(public / 'DIAGNOSTIC.json'); before = target.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_nlink == 1 and before.st_size == len(raw),
            'diagnostic artifact physical bound refused')
    with target.open('rb') as stream:
        opened = os.fstat(stream.fileno())
        require(stat.S_ISREG(opened.st_mode) and opened.st_nlink == 1 and opened.st_size == len(raw)
                and (opened.st_dev, opened.st_ino) == (before.st_dev, before.st_ino),
                'diagnostic artifact custody refused')
        retained = stream.read(DIAGNOSTIC_MAX_BYTES + 1)
        after = os.fstat(stream.fileno())
    final = physical(target).lstat()
    require(retained == raw and stat.S_ISREG(final.st_mode)
            and after.st_nlink == final.st_nlink == 1 and after.st_size == final.st_size == len(raw)
            and (opened.st_dev, opened.st_ino) == (final.st_dev, final.st_ino),
            'diagnostic artifact exact readback refused')


def preflight_failure(args,exc):
    """Only metadata at this exact owned Actions output; no subject/owner operation."""
    require(os.name=='nt' and os.environ.get('GITHUB_ACTIONS')=='true','no Windows preflight output on another host')
    require(os.environ.get('GITHUB_REPOSITORY')==REPOSITORY and os.environ.get('GITHUB_REF')=='refs/heads/'+BRANCH
        and os.environ.get('GITHUB_EVENT_NAME')=='push' and os.environ.get('GITHUB_RUN_ATTEMPT')=='1','preflight context differs')
    run_id=os.environ.get('GITHUB_RUN_ID','');require(re.fullmatch('[0-9]{1,20}',run_id),'run identity absent')
    parent=physical(os.environ['RUNNER_TEMP']);out=parent/('dg18-iw14-'+run_id+'-1')
    require(Path(args.output).absolute()==out,'preflight output differs')
    if out.exists():
        physical(out);require((out/'ALLOCATION_INTENT.json').is_file(),'preexisting unowned output refused')
    else:out.mkdir(exist_ok=False)
    public=out/'public';public.mkdir(exist_ok=True);physical(public)
    require(not any(public.iterdir()),'preexisting public output refused')
    diagnostic=checkpoint_initial();diagnostic.update(phase='CONSTRUCTOR_PREFLIGHT',status='FAILED_PRESERVED_NO_RETRY')
    diagnostic['failure']['exception']=type(exc).__name__ if type(exc).__name__ in CHECKPOINT_EXCEPTIONS else 'OTHER_EXCEPTION'
    diagnostic['completed']['subject_created']=(out/'subject with space').exists()
    checkpoint_write(out,diagnostic)
    save(public/'FAILURE.json',{'status':'PREFLIGHT_FAILED_NO_OWNER_LAUNCH','stage':'CONSTRUCTOR_PREFLIGHT',
        'exception_type':type(exc).__name__,'source_commit':SOURCE_HEAD,'source_tree':SOURCE_TREE,
        'primary_diagnostic':primary_diagnostic(exc),
        'subject_directory_allocated':(out/'subject with space').exists(),'owner_execution_started':False,
        'automatic_retry':False,'original_acceptance_delta':0,'raw_console_uploaded':False})
    publish_public_manifest(public)

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
        require(sys.implementation.name=='cpython' and sys.version_info[:3]==(3,12,10) and sys.maxsize==2**63-1,'physical CPython 3.12.10 x64 required')
        require(os.environ.get('GITHUB_ACTIONS')=='true' and os.environ.get('GITHUB_REPOSITORY')==REPOSITORY,
                'exact approved repository Actions host required')
        require(os.environ.get('GITHUB_EVENT_NAME')=='push' and os.environ.get('GITHUB_REF')=='refs/heads/'+BRANCH,
                'exact isolated push branch required')
        require(os.environ.get('GITHUB_RUN_ATTEMPT')=='1','workflow reruns refused; no old attempt replay')
        run_id=os.environ.get('GITHUB_RUN_ID','');require(re.fullmatch('[0-9]{1,20}',run_id),'actual workflow run identity missing')
        self.packet=physical(Path(__file__).parent);self.source=physical(args.source)
        self.native_checks=self.packet/'native_checks.py'
        require(identity(self.native_checks)['sha256']==NATIVE_CHECKS_SHA256,'native companion digest differs')
        self.python=physical(args.python);require(self.python.samefile(sys.executable),'selected Python differs from running physical interpreter')
        require(physical(BASH).is_file(),'fixed physical Bash required')
        require(args.git is not None and str(args.git) in DIRECT_GIT_PATHS,
                'explicit allowlisted direct Git selection required')
        GIT=physical(args.git)
        require(str(GIT)==str(args.git) and re.fullmatch('[0-9a-f]{64}',args.git_sha256 or '')
                and identity(GIT)['sha256']==args.git_sha256,
                'held selected direct Git identity differs')
        self.entitlement=(self.packet/'entitlement-reference.txt').read_text().strip()
        require(self.entitlement and self.entitlement!='UNGRANTED' and len(self.entitlement)<=2048
                and '\n' not in self.entitlement and '\r' not in self.entitlement,
                'external owner entitlement reference has not been supplied')
        self.out=physical(Path(args.output).absolute().parent)/Path(args.output).name
        require(not self.out.exists() and not any(self.out.is_relative_to(root) for root in (self.source,self.packet)),
                'unused separated output required; no retry')
        self.repo=self.out/'subject with space';self.raw=self.out/'raw';self.public=self.out/'public';self.tmp=self.repo/'task-tmp'
        self.controller='dg18-iw14-'+run_id
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
        self.diagnostic=checkpoint_initial()
        checkpoint_record(self,phase='ALLOCATED',milestone='subject_created')

    def command(self,argv,label,expected=0,cwd=None,timeout=240):
        argv=list(map(str,argv));began=time.time_ns()
        self.active_command={'ordinal':len(self.commands)+1,'label':label,'expected_exit':expected,
                             'exit':None,'outcome':'PROCESS_START_PENDING'}
        checkpoint_record(self,command=self.active_command)
        try:
            result=subprocess.run(argv,cwd=cwd or self.repo,env=self.env,stdin=subprocess.DEVNULL,
                                  stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
        except BaseException as error:
            self.active_command.update(outcome='PROCESS_TIMEOUT' if isinstance(error,subprocess.TimeoutExpired)
                else 'PROCESS_START_FAILED' if isinstance(error,OSError) else 'COMMAND_INTERRUPTED',
                exception_type=type(error).__name__,errno=getattr(error,'errno',None),winerror=getattr(error,'winerror',None))
            checkpoint_record(self,command=self.active_command)
            raise
        prefix=f'{len(self.commands)+1:03d}-{label}'
        save(self.raw/(prefix+'.stdout'),result.stdout);save(self.raw/(prefix+'.stderr'),result.stderr)
        self.active_command.update(exit=result.returncode,outcome='EXPECTED_EXIT' if result.returncode==expected else 'UNEXPECTED_EXIT',
            elapsed_ms=(time.time_ns()-began)/1e6,stdout_bytes=len(result.stdout),stderr_bytes=len(result.stderr),
            stdout_sha256=sha(result.stdout),stderr_sha256=sha(result.stderr),stderr_codes=stderr_codes(result.stderr))
        self.active_command.update(stderr_observations(result.stderr))
        self.commands.append({'command':argv,'cwd':str(cwd or self.repo),**self.active_command})
        save(self.raw/(prefix+'.json'),self.commands[-1])
        checkpoint_record(self,command=self.active_command)
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

    def native_check(self,action,*,plan_hash=None,current_receipt=None):
        require(identity(self.native_checks)['sha256']==NATIVE_CHECKS_SHA256,'native companion digest differs')
        output=self.out/('native-receiving' if action=='receive' else 'native-'+action)
        argv=[self.python,'-I','-X','utf8','-B',self.native_checks,action,
            '--source',self.source,'--subject',self.repo,'--manifest',self.packet/'SOURCE_MANIFEST.json',
            '--manifest-sha256',identity(self.packet/'SOURCE_MANIFEST.json')['sha256'],
            '--source-head',SOURCE_HEAD,'--source-tree',SOURCE_TREE,'--git',GIT,'--output',output]
        if action=='receive':
            argv.extend(['--operation',self.out/'operation','--controller',self.controller,'--plan-sha256',plan_hash])
        elif action=='capture':
            argv.extend(['--controller',self.controller,'--current-receipt',current_receipt])
        self.command(argv,'native-'+action,timeout=420)
        summary=json.loads(read_json_file(output/'SUMMARY.json'))
        expected={'metadata':'PASS_NATIVE_CAPTURE_METADATA','capture':'PASS_NATIVE_CAPTURE_CONTROLS',
                  'receive':'PASS_INDEPENDENT_NATIVE_READBACK'}[action]
        require(summary['status']==expected,'native companion did not complete its exact scope')
        require(identity(self.native_checks)['sha256']==NATIVE_CHECKS_SHA256,'native companion changed')
        return summary

    def run(self):
        self.stage='NEW_SUBJECT_INITIALIZATION'
        checkpoint_record(self,phase=self.stage)
        shutil.copytree(self.source/'skills',self.repo/'skills')
        for row in self.manifest['members']:
            if row['path'].startswith('skills/'):
                require(identity(self.repo/row['path'])=={'bytes':row['bytes'],'sha256':row['sha256']},'copied runtime differs')
        self.stage='BOOTSTRAP_CAPTURE_METADATA'
        checkpoint_record(self,phase=self.stage)
        metadata=self.native_check('metadata')
        checkpoint_record(self,milestone='bootstrap_metadata')
        self.stage='NEW_SUBJECT_INITIALIZATION'
        checkpoint_record(self,phase=self.stage)
        self.git('-c','init.templateDir=','init','-q','-b','qualification',label='init')
        save(self.repo/'.gitignore',b'.IMPLEMENTAUDIT/\ntask-tmp/\nskills/\n')
        save(self.repo/'TASK.md',('# Actual fresh Windows receiving task\n\nRuntime source '+SOURCE_HEAD+' / '+SOURCE_TREE+
            '\nOne new manual-resume campaign; no old history, native H0, model session, protected retry or acceptance award.\n').encode())
        self.git('add','--','TASK.md','.gitignore',label='add')
        self.git('-c','user.name=R5 Windows receiving','-c','user.email=r5-windows@example.invalid',
            '-c','commit.gpgsign=false','-c','core.hooksPath=NUL','commit','-qm','Define actual fresh Windows receiving task',label='baseline')
        checkpoint_record(self,milestone='baseline_commit')
        head=self.git('rev-parse','HEAD',label='head').decode().strip();tree=self.git('rev-parse','HEAD^{tree}',label='tree').decode().strip()
        relative=self.claim('--controller',self.controller,'Fresh Windows W-FULL receiving',label='claim-pending').decode().strip()
        require(re.fullmatch(r'\.IMPLEMENTAUDIT/runs/[a-z0-9-]+-[A-Za-z0-9]{6}',relative),'unexpected claimed root')
        checkpoint_record(self,milestone='pending_claim')
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
        checkpoint_record(self,milestone='initialization_activated')
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
        checkpoint_record(self,milestone='first_receipt_verified_and_required')
        self.stage='CURRENT_NATIVE_CAPTURE_CONTROLS'
        checkpoint_record(self,phase=self.stage)
        capture=self.native_check('capture',current_receipt=legacy)
        checkpoint_record(self,milestone='native_capture_controls')
        capture['bootstrap_observation']=metadata
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
        checkpoint_record(self,milestone='pending_successor_inspected')
        artifacts['receipt']=self.git('cat-file','blob',legacy.split('@')[1],label='actual-first-receipt-blob')
        save(run/'owner-map.json',{'schema':'implementaudit.rotation-owner-map.v2','owner_map':factory.build_owner_map(bodies,pair,artifacts)})
        self.stage='ACTUAL_PREDECESSOR_ROTATION'
        checkpoint_record(self,phase=self.stage)
        rotation=json.loads(self.claim('--rotate-canonical-state',self.controller,'--owner-map','owner-map.json',label='first-rotation'))
        require(rotation['status']=='ROTATED','real byte-triggered predecessor rotation failed')
        self.claim('--require-current-continuity',self.controller,label='require-migrated-predecessor')
        checkpoint_record(self,milestone='predecessor_rotated')
        self.stage='FRESH_MANUAL_BOUNDARY'
        checkpoint_record(self,phase=self.stage)
        self.claim('--invalidate-continuity',self.controller,'--boundary','manual-resume',
            '--event','new-windows-campaign-'+os.environ['GITHUB_RUN_ID']+'-manual-resume',label='fresh-manual-invalidation')
        checkpoint_record(self,milestone='fresh_manual_boundary')
        self.stage='MAINTAINED_PREPARE'
        checkpoint_record(self,phase=self.stage)
        operation=self.out/'operation'
        prepared=json.loads(self.command([self.python,'-I','-X','utf8','-B',self.runner,'prepare','--source',self.source,
            '--repo',self.repo,'--controller',self.controller,'--source-head',SOURCE_HEAD,'--source-tree',SOURCE_TREE,
            '--bash',BASH,'--python',self.python,'--git',GIT,'--out',operation],'maintained-prepare'))
        self.plan=Path(prepared['plan']);plan_hash=identity(self.plan)['sha256']
        require(prepared['sha256']==plan_hash,'prepared plan digest differs')
        checkpoint_record(self,milestone='maintained_prepared')
        self.stage='MAINTAINED_SINGLE_EXECUTE'
        checkpoint_record(self,phase=self.stage)
        self.command([self.python,'-I','-X','utf8','-B',self.runner,'execute','--plan',self.plan,'--plan-sha256',plan_hash,
            '--entitlement-reference',self.entitlement],'maintained-execute',timeout=600)
        checkpoint_record(self,milestone='maintained_execute_returned_zero')
        result=json.loads((operation/'execution/RESULT.json').read_bytes())
        require(result['status']=='RECORDED_OPERATION_READY_FOR_INDEPENDENT_RECEIVING','maintained operation not qualified for receiving')
        checkpoint_record(self,milestone='maintained_result_received')
        require(verify_source(self.source,self.manifest,self.env)==self.source_before,'source changed after operation')
        self.stage='STALE_INITIALIZATION_GUARD_RECEIVING'
        checkpoint_record(self,phase=self.stage)
        self.refuse_activation(successor_relative,successor_inspect['initialization_token'],'stale-expected-old-initialization',
            'initialization expected-old source/controller/boundary changed')
        current=json.loads((operation/'execution/CURRENT.json').read_bytes())
        require(self.claim('--require-current-continuity',self.controller,label='require-after-stale-initialization-refusal').decode().strip()==current['receipt_token'],
            'stale initialization refusal changed currentness')
        checkpoint_record(self,milestone='stale_initialization_guard')
        self.stage='INDEPENDENT_NATIVE_RECEIVING'
        checkpoint_record(self,phase=self.stage)
        native_receiving=self.native_check('receive',plan_hash=plan_hash)
        checkpoint_record(self,milestone='native_receiving')
        self.stage='PUBLISH_SELECTED_NEW_SUBJECT_EVIDENCE'
        checkpoint_record(self,phase=self.stage)
        save(self.public/'NATIVE_CAPTURE.json',capture)
        save(self.public/'NATIVE_RECEIVING.json',native_receiving)
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
            'native_capture_sha256':identity(self.public/'NATIVE_CAPTURE.json')['sha256'],
            'native_receiving_sha256':identity(self.public/'NATIVE_RECEIVING.json')['sha256'],
            'caller_profile':'composite-20261105-r5-h0-mechanical-template-v1-core',
            'authority_ceiling':result['authority_ceiling'],'original_acceptance_delta':0,
            'measurement_scope':'WHOLE_RESUME_OWNER_JOB; PREPARATION_CONTROL_HARNESS_AND_INDEPENDENT_RECEIVING_OUTSIDE_JOB',
            'maximum_ms':60000,'maximum_aggregate_job_committed_bytes':201326592,'baseline_subtracted_bytes':0})
        self.publish_manifest()
        checkpoint_record(self,milestone='public_manifest_created')
        checkpoint_observe(self)
        checkpoint_record(self,completed=True)
        print(json.dumps({'status':result['status'],'public_manifest_sha256':identity(self.public/'ARTIFACT_MANIFEST.json')['sha256'],
                          'original_acceptance_delta':0},sort_keys=True))

    def publish_manifest(self):
        publish_public_manifest(self.public)
    def failure(self,exc):
        # The maintained runner owns post-attempt reconciliation. Never launch another resume here.
        diagnostic=primary_diagnostic(exc,self)
        try:
            checkpoint_record(self,failure=exc)
            checkpoint_observe(self)
        except Exception:
            pass  # Existing private failure export still runs; checkpoint validation remains fail closed.
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
    parser.add_argument('--git',type=Path);parser.add_argument('--git-sha256')
    parser.add_argument('--output',required=True,type=Path)
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--emit-public',action='store_true');mode.add_argument('--emit-diagnostic',action='store_true');mode.add_argument('--validate-diagnostic-artifact',action='store_true')
    args=parser.parse_args()
    if args.emit_public:
        try:
            code=emit_public_retained(args.output)
        except BaseException:
            public_safe_print('DG18_PUBLIC_REFUSAL {"status":"UNQUALIFIED_PUBLICATION_REFUSED","code":"DIAGNOSTIC_CHECKPOINT_OR_OUTPUT_REFUSED","authority":"NONE","automatic_retry":false}')
            code=1
        raise SystemExit(code)
    if args.emit_diagnostic:
        try:
            emit_diagnostic(args.output)
        except BaseException:
            public_safe_print('DG18_PUBLIC_REFUSAL {"status":"UNQUALIFIED_PUBLICATION_REFUSED","code":"DIAGNOSTIC_RECORD_REFUSED","authority":"NONE","automatic_retry":false}')
            raise SystemExit(1)
        return
    if args.validate_diagnostic_artifact:
        try:
            validate_diagnostic_artifact(args.output)
        except BaseException:
            raise SystemExit(1) from None
        return
    require(args.source is not None and args.python is not None and args.git is not None
            and re.fullmatch('[0-9a-f]{64}',args.git_sha256 or ''),'source, physical Python and bound Git are required')
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
