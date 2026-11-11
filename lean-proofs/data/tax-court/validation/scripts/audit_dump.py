import json,glob,os,sys,collections
B=r'C:\Users\alany\Documents\tax-formalization-data\taxcourt\encoded'
keys=collections.Counter(); keycases=collections.defaultdict(set)
def walk(o,p,cid):
    if isinstance(o,dict):
        for k,v in o.items():
            keys[p+k]+=1; keycases[p+k].add(cid); walk(v,p+k+'.',cid)
    elif isinstance(o,list):
        for x in o: walk(x,p,cid)
for f in sorted(glob.glob(B+r'\*.case.json')):
    cid=os.path.basename(f)[:-10]
    d=json.load(open(f,encoding='utf-8'))
    for yr in (d if isinstance(d,list) else [d]):
        for sec in ('facts','asFiled'):
            if sec in yr: walk(yr[sec],sec+'.',cid)
        for k in yr:
            if k not in ('facts','asFiled'): keys['TOP.'+k]+=1; keycases['TOP.'+k].add(cid)
for k,n in sorted(keys.items()):
    print(n,k, sorted(keycases[k])[:6] if n<8 else '')
