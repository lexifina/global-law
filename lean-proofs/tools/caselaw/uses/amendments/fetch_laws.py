import sys, csv, collections
sys.path.insert(0, 'tools')
import fetch
laws = set()
for r in csv.reader(open('../../usc/versions.tsv', encoding='utf-8'), delimiter='\t'):
    if r[2] == 'law': laws.add(r[3])
lo = int(sys.argv[1]); hi = int(sys.argv[2])
got = miss = 0
for lab in sorted(laws):
    c, n = (int(x) for x in lab.replace('Pub. L. ', '').split('-'))
    if not (lo <= c <= hi): continue
    m = fetch.fetch(fetch.plaw_mods(c, n))
    x = fetch.fetch(fetch.plaw_uslm(c, n))
    if x is None: miss += 1
    else: got += 1
print('uslm got', got, 'missing', miss, flush=True)
