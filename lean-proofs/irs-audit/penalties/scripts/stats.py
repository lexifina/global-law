#!/usr/bin/env python3
"""Coverage and results tables for RUN1.md, from parsed.json, classified.tsv, flags.json and the hand-written
verdicts in data/verdicts.json ({cite: {"class": ..., "note": ...}})."""
import os, re, json, collections
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/penalties')
S = json.load(open(H + '/cache/sample.json'))
P = json.load(open(H + '/data/parsed.json'))
V = json.load(open(H + '/data/verdicts.json')) if os.path.exists(H + '/data/verdicts.json') else {}
cls = collections.defaultdict(list)
for l in open(H + '/data/classified.tsv'):
    rid, y, k, v = l.rstrip('\n').split('\t'); cls[rid.split('#')[0]].append((rid, int(y), k, v))
out = {}
out['docket_entries_sampled'] = len(S)
out['pdfs_fetched'] = len(os.listdir(H + '/cache/pdf'))
out['unique_opinions'] = len(P)
out['by_type'] = dict(collections.Counter({'MOP': 'memorandum', 'SOP': 'summary', 'TCOP': 'T.C. (division)'}.get(o.get('type'), '?') for o in P))
out['filing_years'] = '%s-%s' % (min(o['filed'][:4] for o in P if o.get('filed')), max(o['filed'][:4] for o in P if o.get('filed')))
out['parse_status'] = dict(collections.Counter(o['status'] if o['status'] != 'unparsed' else 'unparsed (figures in prose the parser could not align)' for o in P))
with_rows = [o for o in P if o['id'] in cls]
out['opinions_with_checked_rows'] = len(with_rows)
out['year_records_checked'] = len({r for o in with_rows for (r, *_ ) in cls[o['id']]})
fam = collections.Counter(); famop = collections.defaultdict(set)
for oid, lst in cls.items():
    for rid, y, k, v in lst:
        fam[(k, v)] += 1
out['checks'] = {'%s | %s' % kv: n for kv, n in sorted(fam.items())}
# opinion-level classes
opc = collections.Counter(); per_decade = collections.defaultdict(collections.Counter)
for o in with_rows:
    labels = [v for (_, _, k, v) in cls[o['id']] if k != 'other']
    if not labels:
        c = 'only out-of-scope sections (pre-1990 regime)'
    elif any(v.startswith(('FLAG', 'CHECK')) for v in labels):
        c = V.get(str(o.get('cite')), {}).get('class', 'FLAG not yet verified')
    elif all(v.startswith('agrees') for v in labels if not v.startswith('not checkable')):
        c = 'agrees with Lean (exact statutory rate on the deficiency)'
    elif all(v.startswith(('agrees', 'consistent', 'not checkable')) for v in labels):
        c = 'consistent with Lean (within the statutory rate; base is part of the deficiency)'
    else:
        c = 'other'
    opc[c] += 1
    per_decade[o['filed'][:3] + '0s'][c] += 1
out['opinion_classes'] = dict(opc.most_common())
out['opinion_classes_by_filing_decade'] = {k: dict(v) for k, v in sorted(per_decade.items())}
# row-level for 6662 family
acc = collections.Counter(v.split(':')[0] + ':' + v.split(':')[1][:30] for o in with_rows for (_, _, k, v) in cls[o['id']] if k == 'acc')
out['acc_rows'] = dict(acc)
co = json.load(open(H + '/data/court_outcome.json'))
out['court_outcome_6662'] = dict(collections.Counter(co.values()))
json.dump(out, open(H + '/data/stats.json', 'w'), indent=1)
print(json.dumps(out, indent=1))
