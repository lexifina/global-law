import stlink as S, collections, random, sys
from stlink import BO, L
S.init()
random.seed(7)
shards=[p for p in __import__('pop').state_shards()]
random.shuffle(shards)
out=[]
for p in shards[:25]:
    meta={int(x[0]):x for x in L.meta_rows(p[:-9]+'.meta.tsv.gz')}
    st=collections.Counter()
    for n,g in L.decisions(p):
        if not g['cw']: continue
        for c in S.select(n,g,meta.get(n),st):
            r,w=BO.decide(BO.dispositions(g),c[2],True)
            if r is None and w=='no_disposition': out.append(n)
random.shuffle(out)
out=out[:40]
T=L.fetch_texts(out)
for n in out:
    t=T[n][1].replace('\n',' ')
    print('==',n,len(t)); print(t[-330:])
