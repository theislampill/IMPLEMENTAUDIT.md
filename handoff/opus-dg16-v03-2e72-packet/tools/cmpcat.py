import json,sys
a=json.load(open(sys.argv[1])); b=json.load(open('cat-3c22642a.json')); p=json.load(open('cat-d2f04874.json'))
for k in b:
  if a.get(k)!=b[k]: print('DIFF',k)
bl={l['sha256']:l for l in b['literals']}; al={l['sha256']:l for l in a['literals']}; pl={l['sha256']:l for l in p['literals']}
pf={f['id']:f['path'] for f in p['files']}
n=0
for h in pl:
  if al.get(h)!=bl.get(h):
    n+=1
    if n<6: print('P',[(pf[r[0]],r[1],r[2]) for r in pl[h]['references']],'\n A',al.get(h,{}).get('references'),'\n B',bl.get(h,{}).get('references'))
print('lits differ',n)
at={t['sha256']:t for t in a['tests']}; bt={t['sha256']:t for t in b['tests']}
print('tests',len(set(at)^set(bt)), sum(1 for h in at if h in bt and at[h]!=bt[h]))
x=[h for h in at if h in bt and at[h]!=bt[h]][:2]; print([(at[h],bt[h]) for h in x])
