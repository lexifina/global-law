import os
import json, sys
from collections import Counter
sys.path.insert(0, os.path.expanduser('~/cmp/de/harness'))
from compare_gettsim import lean_fields, g_fields
hs=[json.loads(l) for l in open(sys.argv[1])]; L=[json.loads(l) for l in open(sys.argv[2])]; G=[json.loads(l) for l in open(sys.argv[3])]
c=Counter(); ex={}
for h,l,g in zip(hs,L,G):
    lf,gf=lean_fields(l),g_fields(g)
    svok=all(abs(lf[k]-gf[k])<=0.011 for k in ['rv','av','kv','pv'])
    if not svok: continue
    de=lf['est']-gf['est']; dz=max(lf['zve'],0)-gf['zve']
    if abs(de)<1e-6 and abs(dz)<1e-6: continue
    t=[]
    if dz!=0: t.append('zve%+d' % (1 if dz>0 else -1) if abs(dz)<=1 else 'zveBIG')
    if any(a['age']>=65 for a in h['adults']): t.append('65+')
    if h['interest']+h['dividends']+h['capitalGains']>0: t.append('cap')
    if h['married'] and len(h['adults'])==2: t.append('joint')
    if any(a['pension']>0 for a in h['adults']): t.append('pens')
    if h['pensionContributions']>0: t.append('basisrente')
    if any(c['age']<25 for c in h['children']): t.append('kids')
    if any(a['selfEmployment']!=0 for a in h['adults']): t.append('self')
    if abs(de)<=1: t.append('est<=1')
    k=' '.join(t); c[k]+=1; ex.setdefault(k,[]).append((h['id'],round(de,2),round(dz,2)))
for k,v in c.most_common(40): print(v,k,ex[k][:3])
