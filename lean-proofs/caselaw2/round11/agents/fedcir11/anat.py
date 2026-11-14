import csv,collections,sys
R=list(csv.DictReader(open('work/pop.tsv',encoding='utf-8'),delimiter='\t',quoting=csv.QUOTE_NONE))
def marked(r): return 'neg:' in r['v10d_status'] or 'unknown:' in r['v10d_status']
def mine(r): return any(x.startswith(('neg','unknown')) and x.endswith('@'+r['acting']) for x in r['v10d_status'].split(';'))
for key in (('520','dist'),('520','cfc'),('520','cit'),('520','cavc'),('655','cit')):
  S=[r for r in R if (r['acourt'],r['tclass'])==key and r['judgment'].split('/')[0] in ('reversed','vacated','modified')]
  A=[r for r in R if (r['acourt'],r['tclass'])==key and r['judgment'].split('/')[0]=='affirmed']
  print(key, 'negjudg pairs',len(S), 'aff pairs', len(A), 'aff-pairs with neg status', sum(marked(r) for r in A))
  for cap in ('2','1','0'):
    T=[r for r in S if r['cap']==cap]; U=[r for r in T if not marked(r)]
    c=collections.Counter(r['r6stage'] for r in U)
    print('  cap',cap,'pairs',len(T),'marked any',len(T)-len(U),'by this',sum(mine(r) for r in T),'unmarked',len(U), c.most_common(7))
