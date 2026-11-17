import json, os, re, sys
sys.path.insert(0, os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/indexing'))
from docs import DOCS
from extract import text, norm
T = json.load(open('tables.json'))
res = {}
for y, d in sorted(T.items()):
    y = int(y)
    if y not in DOCS or not d['sched']: continue
    t = ' '.join(norm(text(p)[0]) for p in DOCS[y])
    miss = []; n = 0
    for st, rows in d['sched'].items():
        for o, b, r in rows[1:]:
            n += 1
            if '$%s' % format(o, ',') not in t and format(o, ',') not in t: miss.append((st, o))
    res[y] = (n, miss)
    print(y, n, 'thresholds;', len(miss), 'not found in', DOCS[y], miss[:6])
json.dump(res, open('thresholds_vs_revproc.json', 'w'))
