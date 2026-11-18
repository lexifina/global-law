import json, sys
from collections import Counter
hs=[json.loads(l) for l in open(sys.argv[1])]; L=[json.loads(l) for l in open(sys.argv[2])]; G=[json.loads(l) for l in open(sys.argv[3])]
def lsv(o):
    r=dict(rv=0,av=0,kv=0,pv=0)
    for u in o['detail']['units']:
        for m in u['members']:
            r['rv']+=m['RV']; r['av']+=m['AV']; r['kv']+=m['KV']; r['pv']+=m['PV']
    return r
def tags(h):
    t=set()
    for a in h['adults']:
        w=a['wages']; p=a['pension']; s=a['selfEmployment']
        if w>0 and p>0: t.add('wage+pension')
        if a['age']>=67 and w>6672: t.add('age67+wage')
        if 6672<w<=24000: t.add('midijob')
        if 0<w<=6672: t.add('minijob')
        if s>6420 and w<=6672 and p<=0: t.add('selfMain')
        if p>0 and w==0: t.add('pensionOnly')
        if a['age']<23: t.add('under23')
    if h['children']: t.add('kids%d'%len([c for c in h['children'] if c['age']<25]))
    return t
for f in ['rv','av','kv','pv']:
    c=Counter(); ex={}
    for h,l,g in zip(hs,L,G):
        d=lsv(l)[f]-g[f]
        if abs(d)>0.011:
            k=' '.join(sorted(tags(h))) or 'plain'
            c[k]+=1; ex.setdefault(k,(h['id'],round(d,2)))
    print(f, sum(c.values()))
    for k,v in c.most_common(12): print('   ',v,k,ex[k])
