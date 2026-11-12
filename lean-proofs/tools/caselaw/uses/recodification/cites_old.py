"""Bonus: decisions in usc/cites that cite an old location after the restatement took effect, which the mapping can
translate. A cite counts when its title and section are an old provision that the restatement emptied (mapped,
transferred or omitted), it was decided on or after the restatement day, and the number is not also a section of the
same title in force afterwards (old 36 U.S.C. 101 and new 36 U.S.C. 101 are different laws; such cites are counted
apart as ambiguous). The citation extractor does not read "46 U.S.C. App." cites, so 46 App. is not covered.
Writes data/cites_old.tsv and prints the counts."""
import os, sys, glob, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recod import *

summ = json.load(open(os.path.join(DATA, 'summary.json')))
rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(DATA, 'old_provisions.tsv'), encoding='utf-8')][1:]
old = {}
for T, S, s, status, reason, images, ok, vanished, n in rows:
    if status in ('kept',) or vanished == '0':
        continue
    old[(int(S), s)] = (int(T), status, images, reason)
# the sections of each source title in force after the restatement (to spot reused or colliding numbers)
after = {}
for T, v in summ.items():
    for S, x in v['sources'].items():
        after[int(S)] = set(in_force(int(S), commit_on(int(S), 20261103)))
by_src_day = {}
for (S, s), (T, *_ ) in old.items():
    by_src_day[S] = min(by_src_day.get(S, 99999999), summ[str(T)]['day'])
cites = glob.glob(os.path.join(BASE, '..', '..', 'usc', 'cites', '*.usc.tsv'))
out = []
stats = collections.Counter()
for fn in cites:
    court = os.path.basename(fn)[:-8]
    for l in open(fn, encoding='utf-8'):
        f = l.rstrip('\n').split('\t')
        if len(f) < 7 or not f[2].isdigit():
            continue
        S, s, d = int(f[2]), f[3], int(f[1])
        k = (S, s)
        if k not in old:
            continue
        T, status, images, reason = old[k]
        D = summ[str(T)]['day']
        if d < D:
            continue
        reused = s in after.get(S, set())
        kind = 'ambiguous (number in force again)' if reused else (
            'translatable' if images else 'omitted (' + (reason[:40] or status) + ')')
        stats[(T, kind)] += 1
        out.append((T, court, f[0], d, S, s, f[4], kind, images, f[6]))
with open(os.path.join(DATA, 'cites_old.tsv'), 'w', newline='\n', encoding='utf-8') as fo:
    fo.write('title\tcourt\tnode\tdecided\tsrc_title\tsection\tsubsection\tkind\timages\traw\n')
    for r in out:
        fo.write('\t'.join(map(str, r)) + '\n')
for k, v in sorted(stats.items()):
    print(k, v)
print('decisions:', len({(r[1], r[2]) for r in out if r[7] == 'translatable'}))
