"""Parse every year's Tax Table and Tax Rate Schedules (Form 1040 instructions) into tables.json."""
import re, os, json, glob
C = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/cache/www.irs.gov/pub/irs-prior')
SRC = {y: ('%s/i1040tt--%d.txt' % (C, y), 'https://www.irs.gov/pub/irs-prior/i1040tt--%d.pdf' % y) for y in range(1997, 2025)}
SRC[1995] = ('%s/i1040--1995.txt' % C, 'https://www.irs.gov/pub/irs-prior/i1040--1995.pdf')
SRC[1996] = ('%s/i1040--1996.txt' % C, 'https://www.irs.gov/pub/irs-prior/i1040--1996.pdf')
SRC[2025] = (os.path.expanduser('~/docs/irs/i1040tt.txt'), 'https://www.irs.gov/pub/irs-prior/i1040tt--2025.pdf')
num = r'(\d{1,3}(?:,\d{3})*)'
ROW = re.compile(r'\s+'.join([num] * 6))
SROW = re.compile(r'^\s*\$?([\d,]+)\s+(?:\$?([\d,]+)\s+)?(?:\$?([\d,]+\.\d\d|[\d,]+)\s*\+\s*)?(\d+(?:\.\d+)?)\s*%\s+(?:of the excess over\s+)?\$?([\d,]+)\s*$')
def toi(s): return int(s.replace(',', ''))
out = {}
for y, (f, url) in sorted(SRC.items()):
    if not os.path.exists(f): print(y, 'missing'); continue
    lines = open(f, encoding='utf-8', errors='replace').read().splitlines()
    grid = {0: 5, 5: 15, 15: 25}
    for a in range(25, 3000, 25): grid[a] = a + 25
    for a in range(3000, 100000, 50): grid[a] = a + 50
    rows = {}
    for line in lines:
        toks = re.findall(num, line)
        vals = [toi(x) for x in toks]
        for i in range(len(vals) - 5):
            v = vals[i:i + 6]
            if grid.get(v[0]) == v[1] and v[0] not in rows and all(0 <= t <= v[1] * 0.4 + 1 for t in v[2:]) and v[2] >= 0.09 * v[0] - 1 and v[3] <= v[2] <= v[4] and v[5] <= v[2]:
                rows[v[0]] = v
    # schedules: from the Tax Table booklet, else from the year's Form 1040 instructions
    slines = lines
    if not any(re.match(r'\s*Schedule (X|Y-1|Y-2|Z)\s*[—-]', l) for l in lines):
        for alt in ('%s/i1040--%d.txt' % (C, y), '%s/i1040gi--%d.txt' % (C, y)):
            if os.path.exists(alt): slines = open(alt, encoding='utf-8', errors='replace').read().splitlines(); break
    sched = {}; cur = None
    for line in slines:
        mh = re.match(r'\s*Schedule (X|Y-1|Y-2|Z)\s*[—-]', line)
        if mh: cur = mh.group(1); sched.setdefault(cur, []); continue
        if cur:
            ms = SROW.match(line)
            if ms:
                over = toi(ms.group(1)); rate = ms.group(4); base = ms.group(3); ov2 = toi(ms.group(5))
                if over == ov2 and (not sched[cur] or over > sched[cur][-1][0]):
                    sched[cur].append([over, base.replace(',', '') if base else '0', rate])
    srt = sorted(rows.values())
    gaps = sorted(set(grid) - set(rows))
    out[y] = dict(src=url, rows=srt, sched=sched, gaps=gaps, first=srt[0][0] if srt else None, last=srt[-1][1] if srt else None)
    print(y, len(srt), 'rows; first', out[y]['first'], 'last', out[y]['last'], 'gaps', len(gaps), gaps[:4], {k: len(v) for k, v in sched.items()})
json.dump(out, open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/tables/tables.json'), 'w'))
