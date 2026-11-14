"""Residual check for the Journals not re-extracted: tokens with an 'f' that occur rarely and become a frequent word of
the whole held Journal vocabulary when one 'f' is read as 'fi' or 'fl'. python -I residual_lig.py <txt> ... (first
args = texts to check, marked by a leading '+'; the rest build the vocabulary too)"""
import sys, re, collections
LIG = {'ﬀ': 'ff', 'ﬁ': 'fi', 'ﬂ': 'fl', 'ﬃ': 'ffi', 'ﬄ': 'ffl'}
voc = collections.Counter(); per = {}
for a in sys.argv[1:]:
    p = a.lstrip('+'); s = open(p, encoding='utf-8').read()
    for k, v in LIG.items(): s = s.replace(k, v)
    s = s.replace('­\n', '')
    c = collections.Counter(re.findall(r'[A-Za-z]+', s)); voc.update(c)
    if a.startswith('+'): per[p] = c
for p, c in per.items():
    hits = []
    for t, n in c.items():
        if 'f' not in t or voc[t] > 3: continue
        cands = set()
        for i, ch in enumerate(t):
            if ch == 'f':
                for ins in ('i', 'l'):
                    w = t[:i+1] + ins + t[i+1:]
                    if voc[w] >= 5: cands.add(w)
        if len(cands) == 1: hits.append((t, cands.pop(), n))
    print(p.rsplit('/',1)[-1], len(hits), sum(h[2] for h in hits), hits[:15])
