"""Sample ~30 misses of a scored build and print, for each, the overruling decision's text around its mention of X.

    python -X utf8 disagree_sample.py <label> <n> > work/disagree_<label>.txt
"""
import collections, hashlib, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); B = os.path.dirname(HERE)
sys.path.insert(0, HERE); import link as L
label, n = sys.argv[1], int(sys.argv[2])
cases = [l.rstrip('\n').split('\t') for l in open(os.path.join(B, 'results', label + '.cases.tsv'), encoding='utf-8')]
hdr, cases = cases[0], cases[1:]
key = {}
for l in open(os.path.join(B, 'key.tsv'), encoding='utf-8'):
    p = l.rstrip('\n').split('\t'); key[p[0]] = p
idx = {}
for l in open(os.path.join(B, 'work', 'old_index.tsv'), encoding='utf-8'):
    p = l.rstrip('\n').split('\t'); idx.setdefault(p[1], p)
miss = [c for c in cases if c[8] != 'hit' or (c[14] == '0')]
by_t = collections.defaultdict(list)
for c in miss:
    by_t[c[5].split(',')[0]].append(c)
pick = []
quota = {'georgia1922': 12, 'greenleaf1838': 6, 'desty1874': 5, 'benjamin1893': 4, 'labatt1860': 3}
for t, cs in by_t.items():
    cs.sort(key=lambda c: hashlib.sha1(('d:' + c[0]).encode()).hexdigest())
    pick += cs[:quota.get(t, 3)]
extra = [c for c in cases if c[8] == 'other_actor' or c[14] == '0']
for c in extra:
    if c not in pick: pick.append(c)
ys = {}
for c in pick:
    for y in c[6].split(','):
        p = idx[y]; ys[int(y)] = {'node': int(y), 'repo': p[3], 'path': p[7]}
T = L.fetch_texts(list(ys.values()))
for c in pick:
    x = idx[c[0]]
    r0 = key[c[15].split(',')[0]]
    print('=' * 100)
    print('X', c[0], x[6], '|', x[5], '|', x[2], '| tables', c[5], '| outcome', c[8], '| model', c[11][:200], c[12][:150])
    print('  table row:', r0[1], 'leaf', r0[2], '|', r0[6], '|', r0[26][:150])
    for y in c[6].split(','):
        p = idx[y]; t = T.get(int(y), '')
        print('  Y', y, p[6], '|', p[5], '|', p[2], '| len', len(t))
        xr = {'node': int(c[0]), 'cite': x[6], 'name': x[5]}
        spots = []
        forms = set()
        for k in [x[0]]:
            v, tk, pg = k.split(' ')
            for m in re.finditer(r'(?<!\d)' + v + r'\s+[A-Z][A-Za-z.&\'’ ]{0,25}?,?\s+' + pg + r'(?!\d)', t):
                spots.append(m.start())
        toks = [w for w in re.findall(r'[A-Za-z]{4,}', x[5]) if w.lower() not in L.STOP]
        for w in toks[:2]:
            for m in re.finditer(r'\b' + re.escape(w) + r'\b', t):
                spots.append(m.start())
        spots = sorted(set(spots))[:3]
        for s in spots:
            print('    ...' + t[max(0, s - 350):s + 450].replace('\n', ' ') + '...')
        if not spots:
            print('    (no mention found) ' + t[:300].replace('\n', ' '))
