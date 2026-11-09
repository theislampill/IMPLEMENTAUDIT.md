"""Packaging byte/privacy readback only; never imports or executes staged code."""
from pathlib import Path
import ast, hashlib, json, re

P=Path(__file__).resolve().parent
sha=lambda raw:hashlib.sha256(raw).hexdigest()
index=json.loads((P/'SOURCE_INDEX.json').read_bytes())
private=json.loads((P/'PRIVATE_DEPENDENCIES.json').read_bytes())
key=re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----[\r\n]+[A-Za-z0-9+/=]{32,}')
objects={};marker_only=[]
for row in index['members']:
    relative=row['archive_path'].removeprefix('recovery/sol/')
    assert relative.startswith('objects/') and '..' not in Path(relative).parts
    file=P/relative;raw=file.read_bytes()
    assert len(raw)==row['bytes'] and sha(raw)==row['sha256']
    assert not key.search(raw),'PRIVATE_KEY_MATERIAL'
    if file.suffix=='.py':
        # Inspect literal values, without compiling/importing/executing code.
        for n in ast.walk(ast.parse(raw)):
            if isinstance(n,ast.Constant) and isinstance(n.value,(str,bytes)):
                value=n.value.encode() if isinstance(n.value,str) else n.value
                assert not key.search(value),'EMBEDDED_PRIVATE_KEY_LITERAL'
    if b'-----BEGIN PRIVATE KEY-----' in raw or b'-----BEGIN RSA PRIVATE KEY-----' in raw:
        assert row['sha256']=='8abaec881996c34f79ccb83616e59b4a601504e137d1165b64dc1430823e6dba'
        marker_only.append(row['logical_path'])
    objects[row['sha256']]=file
assert not ({r['sha256'] for r in private['dependencies']} & set(objects)), 'PRIVATE_ROLE_BODY'
for file in P.rglob('*'):
    if file.is_file():
        assert file.suffix.lower() not in {'.cms','.pem','.key','.jsonl','.log','.zip','.deb','.tar','.xz','.pyc'}
checks=dict(schema='dg16.sol-public-component-packaging-checks.v1',object_hash_readback='ALL_MATCH',
    private_dependency_body_hash_matches=0,actual_private_key_blocks_or_literals=0,
    public_guard_marker_only=marker_only,
    marker_note='Initial lexical marker check stopped on the unchanged public carrier key-format guard. No key material was found; guard bytes were preserved.',
    raw_stdout_stderr='Omitted from fixture projections; original receipt hashes retained',
    validation_scope='Packaging only: explicit allowlist, byte/hash readback, structural private-key check and forbidden body/extension checks. No engineering tests, operator execution or provider effect.',
    original_or_hosted_runs=0,source_engineering_after_stop=0,Pro_receipt='NOT_CLAIMED')
(P/'PACKAGING_CHECKS.json').write_text(json.dumps(checks,indent=2)+'\n')
files=[]
for file in sorted(P.rglob('*')):
    if file.is_file() and file.name not in {'SCOPED_MANIFEST.json','MANIFEST_SHA256.txt'}:
        raw=file.read_bytes();rel=file.relative_to(P).as_posix()
        files.append(dict(path=rel,archive_path='recovery/sol/'+rel,bytes=len(raw),sha256=sha(raw)))
manifest=dict(schema='dg16.sol-public-component-scoped-manifest.v1',scope='ALLOWLISTED_PUBLIC_SOURCE_AND_SCOPED_RECEIPTS_ONLY',
    logical_source_members=len(index['members']),unique_source_objects=len(objects),private_role_input_bodies=0,
    raw_logs_or_tool_histories=0,live_or_encrypted_payloads=0,original_or_hosted_operations_during_packaging=0,
    source_engineering_after_owner_stop=0,Pro_receipt='NOT_CLAIMED_HUMAN_LAUNCH_REQUIRED',files=files)
raw=(json.dumps(manifest,indent=2)+'\n').encode();(P/'SCOPED_MANIFEST.json').write_bytes(raw)
(P/'MANIFEST_SHA256.txt').write_text(sha(raw)+'  SCOPED_MANIFEST.json\n')
print(json.dumps(dict(manifest_sha256=sha(raw),files=len(files),logical_members=len(index['members']),
    unique_objects=len(objects),bytes=sum(r['bytes'] for r in files),private_dependency_metadata_rows=len(private['dependencies']),
    external_public_roles=len(index['external_public_dependencies']),engineering_or_provider_operations=0)))
