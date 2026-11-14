"""nj9: every v8e row whose acting court is a NJ court of the post-1948 system and whose target court is a NJ court of
the pre-1948 system (and the reverse), with the round-8 Lean verdict (round8/out/v8e/certs.tsv, classes.tsv).
Reads only the staged data tables and the Lean output; no key.  Usage: python -X utf8 nj_rows.py > rows.tsv"""
import os, sys, csv
C2 = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
S = os.path.join(C2, 'round8', 'stage', 'v8e')
O = os.path.join(C2, 'round8', 'out', 'v8e')
csv.field_size_limit(1 << 30)

OLD = {1094: 'E&A', 1095: 'oldSup', 1206: 'Chancery', 1216: 'Prerogative', 1207: 'OyerTerminer'}
NEW = {1096: 'Sup', 1099: 'AppDiv', 1222: 'ChanDiv', 1224: 'LawDiv', 1227: 'Superior', 1225: 'ProbateDiv',
       1223: 'CrimDiv', 1264: 'TaxCt', 1215: 'Municipal', 1226: 'Resentencing', 1258: 'ChanProbate'}
NJ = set(range(1094, 1101)) | set(range(1206, 1228)) | {1258, 1264}
CUT = 19480915


def rows(name, n):
    with open(os.path.join(S, name), encoding='utf-8', newline='') as f:
        for line in f:
            p = line.rstrip('\r\n').split('\t')
            yield p + [''] * (n - len(p))


court, date = {}, {}
with open(os.path.join(S, 'decisions2.tsv'), encoding='utf-8') as f:
    for line in f:
        p = line.split('\t', 3)
        c = int(p[1]) if p[1] else -1
        if c in NJ:
            court[int(p[0])] = c
            date[int(p[0])] = int(p[2] or 0)


def era(n):
    c, d = court.get(n), date.get(n, 0)
    if c is None:
        return None
    if c in (1094, 1095, 1206, 1216) or d < CUT:
        return 'old'
    return 'new'


def lab(n):
    c = court[n]
    return '%d:%s' % (c, OLD.get(c) or NEW.get(c) or str(c))


verd = {}
with open(os.path.join(O, 'certs.tsv'), encoding='utf-8') as f:
    next(f)
    for line in f:
        p = line.rstrip('\n').split('\t')
        verd[p[1]] = (p[2], p[3])
cls = {}
with open(os.path.join(O, 'classes.tsv'), encoding='utf-8') as f:
    next(f)
    for line in f:
        p = line.rstrip('\n').split('\t')
        cls[p[0]] = p[1] + '/' + p[3]

out = []
# treatments: id, acting, target, date, kind, ...
for p in rows('treatments.tsv', 16):
    a, t = int(p[1]), int(p[2])
    if a in court and t in court and era(a) != era(t):
        out.append(('treatment', p[0], lab(a), date[a], lab(t), date[t], p[4]))
# witness rows: tw:<acting>:<target>:<off>:<witness>  (witness = col 1) -- the witness acts on the target
for p in rows('treatment_witness.tsv', 4):
    k = p[0].split(':')
    w, t, a = int(p[1]), int(k[2]), int(k[1])
    if w in court and t in court and era(w) != era(t):
        out.append(('witness', p[0], lab(w), date[w], lab(t), date[t], 'via ' + (lab(a) if a in court else str(a))))
# history: id, target, acting, date, kind
for p in rows('history.tsv', 13):
    t, a = int(p[1]), int(p[2])
    if a in court and t in court and era(a) != era(t):
        out.append(('history', p[0], lab(a), date[a], lab(t), date[t], p[4]))
w = sys.stdout
w.write('table\tid\tacting\tadate\ttarget\ttdate\tkind\tlean_all\tlean_firm\tclass\n')
for r in sorted(out, key=lambda r: (r[0], r[2], r[4], r[1])):
    key = r[1]
    w.write('\t'.join(map(str, r)) + '\t' + '\t'.join(verd.get(key, ('-', '-'))) + '\t' + cls.get(key, '-') + '\n')
