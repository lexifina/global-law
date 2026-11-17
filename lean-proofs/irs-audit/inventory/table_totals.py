"""Arithmetic of printed tables in IRB items: (1) a column headed "Total" equals the sum of the other numeric cells of
its row; (2) a row labelled "Total" equals the sum of the rows above it in the same block; (3) APA reports: cumulative
executed through year Y-1 + executed in Y = cumulative through Y."""
import re, glob, os, json, collections
G = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/src/irs-guidance')
def num(x):
    x = x.replace(',', '').replace('$', '').strip()
    return int(x) if re.fullmatch(r'\d+', x) else None
c1 = c2 = c3 = 0; bad = []
for f in sorted(glob.glob(G + '/*/*/*.md')):
    if f.split('/')[-3] not in ('announcement', 'notice', 'rev-proc', 'rev-rul'): continue
    t = open(f, encoding='utf-8').read(); item = re.search(r'^item: "([^"]+)"', t, re.M).group(1)
    header = None; block = []
    for line in t.splitlines():
        if '|' not in line:
            if line.strip(): header = None; block = []
            continue
        c = [x.strip() for x in line.split('|')]
        if c[-1].lower() == 'total' and all(num(x) is None for x in c): header = c; block = []; continue
        if header and len(c) == len(header):
            vals = [num(x) for x in c[1:]]
            if all(v is not None for v in vals) and len(vals) >= 3:
                c1 += 1
                if sum(vals[:-1]) != vals[-1]: bad.append(('rowsum', item, c[0][:40], vals))
        if re.match(r'(?i)^total\b', c[0]) and block and not re.search(r'\d{4}\s*[–-]', c[0]):
            rows = [r for r in block if len(r) == len(c)]
            for j in range(1, len(c)):
                tot = num(c[j]); vals = [num(r[j]) for r in rows]
                if tot is None or len(vals) < 2 or any(v is None for v in vals): continue
                c2 += 1
                if sum(vals) != tot: bad.append(('colsum', item, c[0][:40], j, tot, sum(vals)))
            block = []
        elif any(num(x) is not None for x in c[1:]): block.append(c)
    m1 = re.search(r'Total Executed 1991[–-](\d{4}) \|([^\n]*)\n+Total Executed in (\d{4}) \|([^\n]*)\n+Total Executed 1991[–-](\d{4}) \|([^\n]*)', t)
    if m1:
        a = [num(x) for x in m1.group(2).split('|')]; b = [num(x) for x in m1.group(4).split('|')]; s = [num(x) for x in m1.group(6).split('|')]
        for x, y, z in zip(a, b, s):
            if None in (x, y, z): continue
            c3 += 1
            if x + y != z: bad.append(('cumulative', item, x, y, z))
print('row totals', c1, 'column totals', c2, 'APA cumulative', c3, 'mismatches', len(bad))
for b in bad[:30]: print(b)
json.dump(dict(row=c1, col=c2, apa=c3, bad=bad), open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/inventory/table_totals.json'), 'w'), indent=1)
