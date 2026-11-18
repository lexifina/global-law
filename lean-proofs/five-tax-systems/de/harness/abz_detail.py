import json, sys
from collections import Counter
hs=[json.loads(l) for l in open(sys.argv[1])]; L=[json.loads(l) for l in open(sys.argv[2])]; G=[json.loads(l) for l in open(sys.argv[3])]
c=Counter(); ex={}
for h,l,g in zip(hs,L,G):
    us=l['detail']['units']
    lsv=sum(m[k] for u in us for m in u['members'] for k in ('RV','AV','KV','PV')); gsv=g['rv']+g['av']+g['kv']+g['pv']
    if abs(lsv-gsv)>0.05: continue
    t=[]
    dv=sum(u['vorsorgeaufwendungen_10'] for u in us)-g['vorsorge']
    da=sum(u['altersentlastungsbetrag_24a'] for u in us)-g['alte']
    de=sum(u['entlastungsbetragAlleinerziehende_24b'] for u in us)-g['eab']
    ds=sum(u['sonderausgabenOther_10b_10c'] for u in us)-g['sa']
    if dv<-1: t.append('vors<')
    elif dv>0: t.append('vors>')
    if abs(da)>0.005:
        caps=h['interest']+h['dividends']+h['capitalGains']
        t.append('alte'+('-cap' if caps>0 else '')+('<' if da<0 else '>'))
    if abs(de)>0.005: t.append('eab')
    if abs(ds)>0.005: t.append('sa')
    if not t: continue
    k=' '.join(t); c[k]+=1; ex.setdefault(k,[]).append((h['id'],round(dv,2),round(da,2)))
for k,v in c.most_common(): print(v,k,ex[k][:3])
