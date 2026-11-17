#!/usr/bin/env python3
"""Tables for RUN2.md -> data2/stats2.md (markdown) and data2/stats2.json."""
import json, os, collections
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/penalties'); D2 = H + '/data2'
INV = json.load(open(D2 + '/inventory.json'))
P = json.load(open(D2 + '/parsed.json'))
RM = json.load(open(D2 + '/rowmeta.json'))
F = json.load(open(D2 + '/flags.json'))
T = json.load(open(D2 + '/tags.json'))
FIN = json.load(open(D2 + '/final.json')) if os.path.exists(D2 + '/final.json') else {}
out = []; S = {}
def tab(head, rows):
    out.append('| ' + ' | '.join(head) + ' |'); out.append('|' + '---|' * len(head))
    for r in rows: out.append('| ' + ' | '.join(str(x) for x in r) + ' |')
    out.append('')
def pct(a, b): return '%.1f%%' % (100.0 * a / b) if b else '-'

INSCOPE = {'acc', '6651a1', '6651a2', '6651f', 'c1'}
labs = collections.defaultdict(list)
for rid, m in RM.items():
    for k, v in m['labels']:
        if k in INSCOPE: labs[m['id']].append(v)
bucket = {}
for f in F: bucket.setdefault(f['id'], set()).add(f['bucket'][:2])
def oclass(i):
    L = labs.get(i)
    if not L: return None
    if any(v.startswith('FLAG') or v.startswith('CHECK') for v in L): return 'flag ' + min(bucket.get(i, {'B?'}))
    if all(v.startswith('agrees') for v in L): return 'agrees'
    return 'consistent'
Pd = [o for o in P if not o['status'].startswith('duplicate')]
TYPES = ['MOP', 'SOP', 'TCOP', 'OST']
FIG = {'parsed', 'unparsed', 'penalty amount not stated'}
# 1. inventory
out.append('### Inventory by type'); rows = []
for t in TYPES + ['all']:
    sel = [o for o in Pd if t == 'all' or o['type'] == t]
    rows.append([t, len(sel), sum(o['status'] != 'not fetched' for o in sel), sum(o['status'] in FIG for o in sel),
                 sum(o['status'] == 'parsed' for o in sel), sum(1 for o in sel if oclass(o['id']))])
tab(['Type', 'Opinions (deduplicated)', 'Fetched', 'With notice figures', 'Parsed', 'Checked by Lean'], rows)
S['inventory_type'] = rows
out.append('### Inventory by filing year'); rows = []
for y in sorted({o['year_filed'] for o in Pd}):
    sel = [o for o in Pd if o['year_filed'] == y]
    c = collections.Counter(o['type'] for o in sel)
    rows.append([y, len(sel), ' / '.join(str(c.get(t, 0)) for t in TYPES), sum(o['status'] != 'not fetched' for o in sel),
                 sum(o['status'] == 'parsed' for o in sel), sum(1 for o in sel if oclass(o['id']))])
tab(['Year', 'Opinions', 'MOP / SOP / TCOP / OST', 'Fetched', 'Parsed', 'Checked'], rows)
S['inventory_year'] = rows
out.append('### Status of every opinion'); c = collections.Counter(o['status'] for o in P)
tab(['Status', 'Opinions'], c.most_common()); S['status'] = c.most_common()
# 2. opinion classes
oc = collections.Counter(oclass(o['id']) for o in Pd if oclass(o['id']))
n = sum(oc.values()); S['classes'] = dict(oc)
out.append('### Opinion-level classes (automatic, before hand verification), %d opinions' % n)
tab(['Class', 'Opinions', 'Share'], [[k, v, pct(v, n)] for k, v in sorted(oc.items())])
# 3. year-record labels
c = collections.Counter((k, v) for m in RM.values() for k, v in m['labels'])
out.append('### Year-record labels (Lean)'); tab(['Check', 'Label', 'Rows'], [[k, v, x] for (k, v), x in sorted(c.items())])
S['labels'] = [[k, v, x] for (k, v), x in sorted(c.items())]
# 4. year-level rates
out.append('### Year-level rates (checked opinions by filing year)'); rows = []; yr = {}
for y in sorted({o['year_filed'] for o in Pd}):
    cl = [oclass(o['id']) for o in Pd if o['year_filed'] == y and oclass(o['id'])]
    if not cl: continue
    k = len(cl); a = cl.count('agrees'); s = cl.count('consistent'); f = k - a - s
    big = sum(1 for x in cl if x and x.startswith('flag') and x[-2:] in ('B3', 'B6', 'B7', 'B4', 'B5'))
    rows.append([y, k, pct(a, k), pct(s, k), pct(f, k), pct(big, k)]); yr[y] = (k, a, s, f)
tab(['Year', 'Checked', 'Agree (exact rate)', 'Within the rate', 'Flagged (any)', 'Flagged excluding rounding/40% label'], rows)
S['year_rates'] = rows
out.append('### By decade'); rows = []
for d0 in (1990, 2000, 2010, 2020):
    v = [yr[y] for y in yr if d0 <= y < d0 + 10] or [(0, 0, 0, 0)]
    k, a, s, f = (sum(x[i] for x in v) for i in range(4))
    rows.append(['%ds' % d0, k, pct(a, k), pct(s, k), pct(f, k)])
tab(['Decade', 'Checked', 'Agree', 'Within', 'Flagged'], rows); S['decades'] = rows
# 5. flag buckets
c = collections.Counter(f['bucket'] for f in F); ob = collections.Counter(min(v) for v in bucket.values())
out.append('### Flag buckets'); tab(['Bucket', 'Rows', 'Opinions (lowest bucket)'], [[k, v, ob.get(k[:2], 0)] for k, v in sorted(c.items())])
# 6. 6751(b)
out.append('### Section 6751(b) (phrase tags) by filing period'); rows = []
for a, b in ((1995, 2006), (2007, 2016), (2017, 2020), (2021, 2026)):
    sel = [o for o in Pd if a <= o['year_filed'] <= b and o['status'] != 'not fetched']
    tg = collections.Counter((T.get(o['id']) or {}).get('6751b', 'not mentioned') for o in sel)
    rows.append(['%d-%d' % (a, b), len(sel), tg.get('mentioned only', 0) + tg.get('IRS met (phrase)', 0) + tg.get('IRS failed (phrase)', 0) + tg.get('both phrases', 0),
                 tg.get('IRS met (phrase)', 0), tg.get('IRS failed (phrase)', 0), tg.get('both phrases', 0)])
tab(['Filed', 'Opinions', 'Mention 6751(b)', 'IRS met (phrase)', 'IRS failed (phrase)', 'Both phrases'], rows); S['6751b'] = rows
# 7. court outcome on 6662
oc2 = collections.Counter((T.get(o['id']) or {}).get('acc_outcome') for o in Pd if o['status'] == 'parsed' and any(r.get('pen') and any(k.startswith('6662') for k in r['pen']) for r in o['recs']))
out.append('### Court outcome on the accuracy-related penalty (phrase match)'); tab(['Outcome', 'Opinions'], oc2.most_common())
# 8. final decisions
if FIN:
    c = collections.Counter(); comp = collections.Counter(); ex = []
    for i, v in FIN.items():
        oc_ = v['outcomes']
        c['targets'] += 1
        if v['docket_status'] != 'ok': c['no public docket record'] += 1; continue
        if not oc_: c['no decision entry on the docket'] += 1
        if any(x.endswith('fetched') for x in oc_): c['decision document fetched'] += 1
        elif any('private' in x for x in oc_): c['decision private (stipulated / computation)'] += 1
        elif any('no file' in x for x in oc_): c['decision entered, no file attached (paper era)'] += 1
        if v.get('final'): c['final figures parsed'] += 1
        o = next((x for x in P if x['id'] == i), None)
        if v.get('final') and o:
            for r in o['recs']:
                if not r.get('pen'): continue
                fy = v['final'].get(str(r['year']))
                if not fy: continue
                for k, a in r['pen'].items():
                    kk = {'6662': '6662(a)', '6663(a)': '6663'}.get(k, k)
                    if kk not in ('6662(a)', '6663', '6662(h)', '6651(a)(1)', '6651(a)(2)'): continue
                    if kk not in fy: comp['%s: not stated in decision' % kk] += 1; continue
                    b = fy[kk]
                    lab = 'same as notice' if abs(b - a) <= 1 else 'zero' if b == 0 else 'reduced' if b < a else 'increased'
                    comp['%s: %s' % (kk, lab)] += 1
                    if lab == 'increased': ex.append((v.get('cite'), v['docket'], r['year'], kk, a, b))
    out.append('### Final decisions (targets: parsed Rule 155 opinions and every flagged opinion)')
    tab(['Docket outcome', 'Opinions'], sorted(c.items()))
    tab(['Notice vs entered decision', 'Year-penalties'], sorted(comp.items()))
    S['final'] = dict(c); S['final_comp'] = dict(comp); S['final_increased'] = ex
    if os.path.exists(D2 + '/classified_final.tsv'):
        cf = collections.Counter(l.rstrip('\n').split('\t')[3] for l in open(D2 + '/classified_final.tsv'))
        tab(['Lean label on the entered figures', 'Rows'], cf.most_common()); S['final_labels'] = cf.most_common()
json.dump(S, open(D2 + '/stats2.json', 'w'), indent=0)
open(D2 + '/stats2.md', 'w').write('\n'.join(out) + '\n')
print('\n'.join(out)[:200])
