"""The per-title table: results/per_title.tsv (and printed)."""
import os, sys, csv, json, re, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from recod import DATA, BASE, RESTATEMENTS

R = os.path.join(BASE, 'results')
summ = json.load(open(os.path.join(DATA, 'summary.json')))
olds = list(csv.DictReader(open(os.path.join(DATA, 'old_provisions.tsv'), encoding='utf-8'), delimiter='\t'))
pairs = list(csv.DictReader(open(os.path.join(DATA, 'pairs.tsv'), encoding='utf-8'), delimiter='\t'))
apps = list(csv.DictReader(open(os.path.join(DATA, 'app_rows.tsv'), encoding='utf-8'), delimiter='\t'))
drift = list(csv.DictReader(open(os.path.join(DATA, 'drift_notes.tsv'), encoding='utf-8'), delimiter='\t'))
cites = list(csv.DictReader(open(os.path.join(DATA, 'cites_old.tsv'), encoding='utf-8'), delimiter='\t'))
unrel = list(csv.DictReader(open(os.path.join(DATA, 'vanished_unrelated.tsv'), encoding='utf-8'), delimiter='\t'))
lean = {}
for l in open(os.path.join(R, 'lean_run.txt'), encoding='utf-8'):
    m = re.match(r'(explained )?(\w+)(\.ed)?\.tsv: .*images not in force (\d+); total (\w+); sound (\w+)', l)
    if m:
        lean[(m.group(2), bool(m.group(3)), bool(m.group(1)))] = (int(m.group(4)), m.group(5), m.group(6))
rows = []
for T, law, D in RESTATEMENTS:
    t = str(T)
    st = collections.Counter(r['status'] for r in olds if r['title'] == t)
    ps = [p for p in pairs if p['title'] == t]
    lost_any = sum(1 for p in ps if p['lost'].strip())
    lost_hi = sum(1 for p in ps if any(x.split(':')[0] in ('amount', 'percent', 'date') for x in p['lost'].split()))
    app = [a for a in apps if a['title'] == t]
    rows.append({
        'title': T, 'law': law, 'in_force': D,
        'old_provisions': sum(st.values()),
        'mapped': st['mapped'] + st['transferred'] + st['kept'],
        'of_which_transferred_by_credits': st['transferred'], 'of_which_kept_in_place': st['kept'],
        'kept_as_note': st['note'], 'omitted_with_reason': st['omitted'],
        'explained_only_by_code_notes': st['prior_note'] + st['other_law'],
        'unaccounted': st['unaccounted'] + st['unaccounted_still_printed'],
        'appendix_rows_not_in_record': len(app),
        'images_not_in_force_on_day': lean.get((t, False, False), ('',))[0],
        'images_not_in_force_at_edition': lean.get((t, True, False), ('',))[0],
        'pairs_compared': len(ps), 'pairs_losing_a_number': lost_any, 'pairs_losing_amount_percent_or_date': lost_hi,
        'median_word_coverage': sorted(float(p['word_coverage']) for p in ps)[len(ps) // 2] if ps else '',
        'drift_notes_2024': sum(1 for d in drift if d['title'] == t),
        'vanished_same_edition_unrelated': sum(1 for u in unrel if u['title'] == t),
        'later_cites_to_old_numbers_translatable': sum(1 for c in cites if c['title'] == t and c['kind'] == 'translatable'),
        'later_cites_to_old_numbers_omitted': sum(1 for c in cites if c['title'] == t and c['kind'].startswith('omitted')),
    })
with open(os.path.join(R, 'per_title.tsv'), 'w', newline='\n', encoding='utf-8') as f:
    f.write('\t'.join(rows[0]) + '\n')
    for r in rows:
        f.write('\t'.join(str(v) for v in r.values()) + '\n')
for k in rows[0]:
    print(f'{k:42s}', '\t'.join(str(r[k]) for r in rows))
print('totals: old', sum(r['old_provisions'] for r in rows), 'mapped', sum(r['mapped'] for r in rows),
      'omitted', sum(r['omitted_with_reason'] for r in rows), 'note', sum(r['kept_as_note'] for r in rows),
      'unaccounted', sum(r['unaccounted'] for r in rows))
