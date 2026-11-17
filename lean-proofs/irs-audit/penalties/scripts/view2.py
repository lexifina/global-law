#!/usr/bin/env python3
"""view2.py <id-or-cite> [chars] [regex]: determination passage (or the first match of regex) + parsed records."""
import json, re, sys, os
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/penalties')
P = json.load(open(H + '/data2/parsed.json'))
k = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 450
o = [x for x in P if x['id'] == k or x.get('cite') == k or x['docket'] == k][0]
t = re.sub(r'\s+', ' ', open(H + '/data2/lay/%s.txt' % o['id'], errors='ignore').read())
pat = sys.argv[3] if len(sys.argv) > 3 else r'(?:Respondent|respondent|Commissioner|IRS|Internal Revenue Service|notice|Notice)[^.]{0,160}?(?:determined|determining|asserted)'
m = re.search(pat, t, re.I if len(sys.argv) > 3 else 0); s = m.start() if m else 0
print('##', o.get('cite'), o['docket'], o['type'], o['decision'], o['status'], o.get('mode'))
print('  recs', [(r['year'], r.get('deficiency'), r.get('pen')) for r in o['recs']][:6])
print('  ' + t[max(0, s - 40):s + n])
