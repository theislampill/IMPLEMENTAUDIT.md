import hashlib,json,pathlib,sys
manifest=json.loads(pathlib.Path(sys.argv[2]).read_bytes())
root=pathlib.Path(sys.argv[3])
rows=[]
for member in manifest['members']:
 raw=(root/member['path']).read_bytes()
 observed=hashlib.sha256(raw).hexdigest()
 if len(raw)!=member['bytes'] or observed!=member['sha256']:
  raise SystemExit('source identity differs')
 rows.append(member['path']+'\t'+str(len(raw))+'\t'+observed)
inventory=('\n'.join(rows)+'\n').encode()
if sys.argv[1]=='inventory':
 sys.stdout.buffer.write(inventory)
elif sys.argv[1]=='consume':
 supplied=sys.stdin.buffer.read()
 if supplied!=inventory:
  raise SystemExit('received inventory differs from actual source')
 sys.stdout.write(json.dumps({'consumed_members':len(rows),'inventory_sha256':hashlib.sha256(supplied).hexdigest(),'source_commit':manifest['commit']},sort_keys=True)+'\n')
else:
 raise SystemExit('unsupported operation')
