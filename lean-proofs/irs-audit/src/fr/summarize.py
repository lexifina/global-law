"""IRS Federal Register correction notices (244; 151 with text): what they correct (calibration: errors the IRS itself
fixed), and whether any touches a finding (sections 20.2031-7, 1.664-4, 151, 152, 2631, 1274, 6621, 7520)."""
import os, re, json, glob, collections
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit')); idx = json.load(open(H + '/src/fr/corrections.json'))
c = collections.Counter(); hits = []
for d in idx:
    c['type_' + str(d.get('type'))] += 1; c['year_' + d['publication_date'][:4]] += 0
    f = H + '/src/fr/text/%s.txt' % d['document_number']
    if not os.path.exists(f): continue
    t = ' '.join(open(f, errors='replace').read().split()); c['with_text'] += 1
    if re.search(r'\$\s?[\d,]{3,}|\d+(\.\d+)? percent|\d\.\d+%', t): c['mentions_amount_or_rate'] += 1
    if re.search(r'(?i)table', t): c['mentions_table'] += 1
    for s in ('20.2031-7', '1.664-4', '25.2512-5', '1.7520', '20.7520', '1.1274', '301.6621'):
        if s in t: hits.append((d['document_number'], d['publication_date'], s, d['title'][:90]))
print(dict((k, v) for k, v in c.items() if not k.startswith('year_')))
print(collections.Counter(d['publication_date'][:3] + '0s' for d in idx))
for h in hits: print(h)
json.dump(dict(summary=c, hits=hits), open(H + '/src/fr/summary.json', 'w'), indent=0)
