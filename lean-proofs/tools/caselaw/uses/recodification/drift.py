"""Later drift, from the record: law commits after a restatement that touch an old location it emptied (a section it
repealed or moved), where the path is not a section of the new title. Writes data/drift_record.tsv."""
import os, sys, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recod import *

summ = json.load(open(os.path.join(DATA, 'summary.json')))
rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(DATA, 'old_provisions.tsv'), encoding='utf-8')][1:]
gone = collections.defaultdict(set)  # (T, S) -> old sections the restatement emptied
for T, S, s, status, reason, images, ok, vanished, n in rows:
    if status in ('kept',) or (status == 'mapped' and vanished == '0'):
        continue
    gone[(int(T), int(S))].add(s)
out = []
for (T, S), secs in sorted(gone.items()):
    D = summ[str(T)]['day']
    new_secs = None
    for c, d, a, sub in title_log(S):
        if d <= D or 'edition' in a:
            continue
        for l in git('show', '--format=', '--name-status', c, '--', f'title-{S}/').splitlines():
            st, p = l.split('\t')[:2]
            sec = p.split('/', 1)[1][:-3]
            if sec not in secs:
                continue
            if S == T:
                # the same number may now be a new section: only count it if the record had no new section there
                if sec in in_force(T, commit_on(T, D)) and sec not in in_force(S, summ[str(T)]['sources'][str(S)]['before_commit']):
                    continue
            txt = git('show', f'{c}:{p}') if st != 'D' else ''
            out.append((T, S, sec, d, a, st, txt.split('\n')[0][2:140] if txt else '(deleted)'))
with open(os.path.join(DATA, 'drift_record.tsv'), 'w', newline='\n', encoding='utf-8') as f:
    f.write('title\tsrc\tsection\tday\tlaw\tchange\theading_after\n')
    for r in out:
        f.write('\t'.join(map(str, r)) + '\n')
print(len(out), 'law changes to emptied old locations')
for r in out[:40]:
    print(r)
