"""Announcements (and APA reports): table rows labelled "Total" against the sum of the rows above them."""
import re, glob, os, json
G = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/src/irs-guidance')
def num(x):
    x = x.replace(',', '').replace('$', '').strip()
    return int(x) if re.fullmatch(r'\d+', x) else None
checks = 0; bad = []
for f in sorted(glob.glob(G + '/announcement/*/*.md')):
    item = re.search(r'^item: "([^"]+)"', open(f).read(400), re.M).group(1)
    block = []
    for line in open(f, encoding='utf-8').read().splitlines() + ['']:
        if '|' not in line:
            block = []; continue
        c = [x.strip() for x in line.split('|')]
        if re.match(r'(?i)^(grand )?total', c[0]):
            rows = [r for r in block if len(r) == len(c)]
            if len(rows) >= 2:
                for j in range(1, len(c)):
                    tot = num(c[j]); vals = [num(r[j]) for r in rows]
                    if tot is None or any(v is None for v in vals): continue
                    checks += 1
                    if sum(vals) != tot: bad.append((item, os.path.relpath(f, G), c[0][:30], j, tot, sum(vals), len(vals)))
            block = []
        else:
            if any(num(x) is not None for x in c[1:]): block.append(c)
            else: block = []
print('total-row checks', checks, 'mismatches', len(bad))
for b in bad[:40]: print(b)
json.dump(dict(checks=checks, bad=bad), open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/inventory/announcement_totals.json'), 'w'), indent=1)
