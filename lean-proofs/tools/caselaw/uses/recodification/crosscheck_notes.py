"""A second official source for titles 51 and 54: when a restatement repeals a section of another title, the Code
keeps a placeholder there ("Repealed. Pub. L. 113-287 ... See sections 100101(a), 100301 ... of Title 54"). The record
holds these placeholders. Compare the sections each names with the disposition table's images.
Writes data/crosscheck_notes.tsv."""
import os, re, sys, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recod import *

summ = json.load(open(os.path.join(DATA, 'summary.json')))
rows = [l.rstrip('\n').split('\t') for l in open(os.path.join(DATA, 'old_provisions.tsv'), encoding='utf-8')][1:]
out, stats = [], collections.Counter()
for T, S, s, status, reason, images, *_ in rows:
    if T not in ('51', '54') or S == T:
        continue
    src = summ[T]['sources'][S]
    ph = sections(int(S), src['next_edition']).get(s)
    if not ph:
        stats[(T, 'no placeholder')] += 1
        continue
    txt = blob_text(ph)
    head = txt.split('\n')[0]
    if not PLACEHOLDER.match(txt):
        stats[(T, 'still in force')] += 1
        continue
    law = summ[T]['law'].replace('-', '–')
    if law not in head:
        stats[(T, 'placeholder for another law')] += 1
        continue
    note = re.sub(r'\s+', ' ', txt)
    named = set()
    # titles 51 and 54 number every section with five or six digits; nothing else in a placeholder does
    # (Statutes at Large pages and public law numbers are shorter)
    body_ = note.split('\n', 1)[-1] if '\n' in note else note[len(head):]
    if f'Title {T}' in body_:
        named |= set(re.findall(r'(?<![\d–-])(\d{5,6}[a-z]?)(?![\d–-])', body_))
        for a, b in re.findall(r'\b(\d{5,6}) (?:to|through) (\d{5,6})\b', body_):
            named |= {str(i) for i in range(int(a), int(b) + 1)}
    tab = {i.split(':', 1)[1] for i in images.split() if i.startswith(T + ':')}
    if not named and not tab:
        verdict = 'both name none'
    elif named == tab:
        verdict = 'agree'
    elif not named:
        verdict = 'note names none'
    elif not tab:
        verdict = 'table names none'
    elif named & tab:
        verdict = 'overlap'
    else:
        verdict = 'disagree'
    stats[(T, verdict)] += 1
    out.append((T, S, s, status, ' '.join(sorted(tab, key=skey)), ' '.join(sorted(named, key=skey)), verdict,
                note[:300]))
with open(os.path.join(DATA, 'crosscheck_notes.tsv'), 'w', newline='\n', encoding='utf-8') as f:
    f.write('title\tsrc\tsection\tstatus\ttable_images\tnote_sections\tverdict\tplaceholder\n')
    for r in out:
        f.write('\t'.join(r) + '\n')
for k, v in sorted(stats.items()):
    print(k, v)
