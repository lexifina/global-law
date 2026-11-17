"""AFR tables reprinted in the Cumulative Bulletins 1996-2008 vs the IRB editions (afr/afr.json): every cell of
table 1 (14-row tables, same row order) and table 2, and the s382/s42 figures. A difference is either a CB correction of
an IRB misprint or a reprint error (or OCR); each is looked up by hand."""
import json, os
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
irb = {(r['year'], r['month']): r for r in json.load(open(H + '/afr/afr.json'))}
cb = json.load(open(H + '/afr/afr_cb_late.json'))
n = 0; diffs = []
for r in cb:
    k = (r['year'], r['month']); i = irb.get(k)
    if not i: continue
    for t in ('table1', 'table2'):
        a, b = r[t], i[t]
        if len(a) != len(b): continue
        for ri, (ra, rb) in enumerate(zip(a, b)):
            for ci, (x, y) in enumerate(zip(ra, rb)):
                n += 1
                if float(x) != float(y): diffs.append((k, t, ri, ci, 'CB', x, 'IRB', y, i['item']))
    for f in ('adj_lt', 'lihtc70', 'lihtc30'):
        if r.get(f) and i.get(f):
            n += 1
            if float(r[f]) != float(i[f]): diffs.append((k, f, 'CB', r[f], 'IRB', i[f], i['item']))
print(n, 'cells compared', len(diffs), 'differ'); [print(d) for d in diffs[:30]]
json.dump(dict(compared=n, diffs=diffs), open(H + '/afr/cb_vs_irb.json', 'w'), indent=0)
