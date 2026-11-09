"""Pure exact public overlay/tree/request construction. No provider writes."""
import hashlib
import compose as C

def oid(kind,raw):return hashlib.sha1(kind.encode()+b' '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
def git_tree(leaves):
 root={}
 for name,row in leaves.items():
  parts=name.split('/');node=root
  for part in parts[:-1]:node=node.setdefault(part,{})
  C.need(parts[-1] not in node,'TREE_FILE_ALIAS');node[parts[-1]]=(row['mode'],row['git_blob'])
 def tree(node):
  entries=[]
  for name,value in node.items():
   directory=type(value) is dict;mode,sha=('40000',tree(value)) if directory else value
   entries.append((name.encode()+ (b'/' if directory else b''),mode.encode()+b' '+name.encode()+b'\0'+bytes.fromhex(sha)))
  return oid('tree',b''.join(body for _,body in sorted(entries)))
 return tree(root)

def build(out):
 prefix='tree/';public={name[len(prefix):]:body for name,body in out.items() if name.startswith(prefix)}
 manifest=C.parse(out['tree/'+C.W.CORE+'/SOURCE_MANIFEST.json'])
 C.need(manifest['schema']=='dg16.inner-owner.cumulative-source-candidate.v1' and manifest['commit']==C.SOURCE and manifest['tree']==C.TREE and manifest['parent_commit']=='ea61b498d6cffd4747966e7dd716abd3b3cffc1f' and manifest['file_count']==1759 and manifest['total_bytes']==166407881,'ACTUAL_BASE_MANIFEST')
 base={r['path']:r for r in manifest['members']};C.need(len(base)==1759 and sum(r['bytes'] for r in base.values())==166407881 and git_tree(base)==C.TREE,'ACTUAL_COMPLETE_BASE_TREE')
 leaves={n:dict(r) for n,r in base.items()};request=[];reused=[];blobs={r['git_blob']:r for r in base.values()}
 for name,raw in sorted(public.items()):
  pin=oid('blob',raw);row=dict(path=name,mode='100644',git_blob=pin,**C.desc(raw));leaves[name]=row
  item=dict(path=name,mode='100644',type='blob')
  if pin in blobs:
   original=blobs[pin];C.need(C.desc(raw)=={k:original[k] for k in ('bytes','sha256')},'SOURCE_BLOB_REUSE_BODY')
   item['sha']=pin;reused.append(dict(path=name,actual_source_path=original['path'],git_blob=pin,**C.desc(raw)))
  else:item['content']=raw.decode('utf8')
  request.append(item)
 expected=git_tree(leaves);selection=C.parse(out['SELECTION.json'])
 return {'CreateTree.json':C.encode(dict(base_tree=C.TREE,tree=request)),
  'CreateCommit.json':C.encode(dict(message='Bind reviewed fixed-root G1 and two-stage G3 composition',tree=expected,parents=[C.SOURCE])),
  'EXPECTED_PUBLIC_TREE.json':C.encode(dict(schema='dg16.final-host-expected-public-tree.v1',authority='NONE',source_commit=C.SOURCE,source_tree=C.TREE,expected_tree=expected,branch=selection['branch'],members=[leaves[n] for n in sorted(leaves)],file_count=len(leaves),total_bytes=sum(r['bytes'] for r in leaves.values()),original_awards=[])),
  'PUBLICATION_RECONSTRUCTION.json':C.encode(dict(schema='dg16.final-host-publication-reconstruction.v1',authority='NONE',actual_provider_mutation=False,base_files=1759,public_overlay_files=len(public),expected_tree=expected,source_blob_reuse=reused,inline_files=len(request)-len(reused),sole_parent=C.SOURCE,fresh_ref_and_actual_tree_receiving='ROOT_REQUIRED',original_awards=[]))}
