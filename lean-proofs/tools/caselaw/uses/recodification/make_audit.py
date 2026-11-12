"""Audit samples (fixed seed).
  audit/totality_sample.tsv : 36 old provisions (6 per title), our status/images next to the raw table rows that
                              cover them, for a by-hand check of the table reading.
  audit/content_packet.txt  : 24 mapped pairs that lose an amount, percent or date (stratified by title), with the
                              old words and the new words, for a reader to judge.
"""
import os, sys, random, json, csv, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recod import *

random.seed(20261112)
A = os.path.join(BASE, 'audit')
os.makedirs(A, exist_ok=True)
summ = json.load(open(os.path.join(DATA, 'summary.json')))
olds = list(csv.DictReader(open(os.path.join(DATA, 'old_provisions.tsv'), encoding='utf-8'), delimiter='\t'))
raw = [l.rstrip('\n').split('\t') for l in open(os.path.join(DATA, 'dispo_rows.tsv'), encoding='utf-8')]
by_t = collections.defaultdict(list)
for r in olds:
    by_t[r['title']].append(r)
with open(os.path.join(A, 'totality_sample.tsv'), 'w', newline='\n', encoding='utf-8') as f:
    f.write('title\tsrc\tsection\tstatus\treason\timages\traw_rows_naming_it\n')
    for t in sorted(by_t):
        for r in random.sample(by_t[t], 6):
            s = r['section']
            hits = [f'{x[3]} => {x[4]}' for x in raw if x[0] == t and
                    re.match(rf'^(\d+ U\.S\.C\. )?{re.escape(s)}(\b|\(| |,)', x[3])]
            f.write('\t'.join([t, r['src'], s, r['status'], r['reason'][:80], r['images'][:80], ' || '.join(hits)[:400]]) + '\n')
pairs = list(csv.DictReader(open(os.path.join(DATA, 'pairs.tsv'), encoding='utf-8'), delimiter='\t'))
flag = [p for p in pairs if any(x.split(':')[0] in ('amount', 'percent', 'date') for x in p['lost'].split())]
quota = {'36': 4, '40': 6, '41': 5, '51': 4, '54': 5}
pick = []
for t, q in quota.items():
    c = [p for p in flag if p['title'] == t]
    pick += random.sample(c, min(q, len(c)))
with open(os.path.join(A, 'content_packet.txt'), 'w', newline='\n', encoding='utf-8') as f:
    for i, p in enumerate(pick, 1):
        T, S, s = p['title'], int(p['src']), p['section']
        src = summ[T]['sources'][str(S)]
        ot = blob_text(sections(S, src['before_commit'])[s])
        edday = max(summ[T]['new_title_day'], min(v['next_edition_day'] or 99999999 for v in summ[T]['sources'].values()))
        nt = ''
        for img in p['images'].split():
            tt, sec = img.split(':', 1)
            tr = in_force(int(tt), commit_on(int(tt), edday))
            if sec in tr:
                nt += blob_text(tr[sec]) + '\n'
        f.write(f'===== CASE {i}: old {S} U.S.C. {s} (in force the day before {summ[T]["law"]}, {summ[T]["day"]}) '
                f'-> {p["images"]}\nFLAGGED AS LOST: {p["lost"]}\n----- OLD TEXT -----\n{ot[:6000]}\n'
                f'----- NEW TEXT (first edition after) -----\n{nt[:6000]}\n\n')
print(len(pick), 'content cases;', sum(len(v) and 6 for v in by_t.values()), 'totality rows')
