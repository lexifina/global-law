"""For each old provision the tables leave unaccounted, look for its words in the record at the next edition:
git grep for distinctive phrases of its text across every title. Writes data/unaccounted_trace.tsv."""
import os, re, sys, json, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recod import *

summ = json.load(open(os.path.join(DATA, 'summary.json')))
rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(DATA, 'old_provisions.tsv'), encoding='utf-8')][1:]
out = []
for T, S, s, status, *_ in rows:
    if not status.startswith('unacc'):
        continue
    D = summ[T]['day']
    src = summ[T]['sources'][S]
    old = sections(int(S), src['before_commit'])
    text = blob_text(old[s])
    head = text.split('\n')[0]
    b = body(text)
    sents = sorted({x.strip() for x in re.split(r'(?<=[.;:])\s+|\n', b) if len(x.strip()) > 50},
                   key=lambda x: -len(x))
    phrases = []
    for x in sents[:6]:
        w = re.sub(r'\s+', ' ', x)
        mid = len(w) // 2
        ph = w[max(0, mid - 30): mid + 30]
        ph = ph[ph.find(' ') + 1: ph.rfind(' ')]
        if len(ph) > 30:
            phrases.append(ph)
    ec = src['next_edition']
    hits = {}
    for ph in phrases[:4]:
        res = git('grep', '-l', '-F', ph, ec, '--', 'title-*')
        for l in res.splitlines():
            p = l.split(':', 1)[1]
            if p != f'title-{S}/{s}.md':
                hits[p] = hits.get(p, 0) + 1
    best = sorted(hits.items(), key=lambda x: -x[1])[:3]
    heads = []
    for p, n in best:
        ht = git('show', f'{ec}:{p}').split('\n')[0]
        heads.append(f'{p[:-3]} ({n}/{len(phrases[:4])}): {ht[2:90]}')
    out.append((T, S, s, head[2:100], len(phrases[:4]), ' | '.join(heads)))
    print(T, S, s, '->', ' | '.join(heads)[:200], flush=True)
with open(os.path.join(DATA, 'unaccounted_trace.tsv'), 'w', newline='\n', encoding='utf-8') as f:
    f.write('title\tsrc\tsection\theading\tphrases\tfound_at_next_edition\n')
    for r in out:
        f.write('\t'.join(map(str, r)) + '\n')
