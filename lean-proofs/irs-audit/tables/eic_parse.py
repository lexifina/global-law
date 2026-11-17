"""EIC Table (Form 1040 instructions) 2009-2024 against the year's Rev. Proc. parameters and the statutory rates."""
import re, os, json, sys, io, contextlib
sys.path.insert(0, os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/indexing'))
with contextlib.redirect_stdout(io.StringIO()):
    from docs import DOCS
    from extract import text, norm
C = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/cache/www.irs.gov/pub/irs-prior')
def toi(s): return int(s.replace(',', ''))
cell = r'(\d{1,3}(?:,\d{3})*|\*+)'; num = r'(\d{1,3}(?:,\d{3})*)'
ROW = re.compile(r'\s+'.join([num, num] + [cell] * 8))
def params(ty):
    docs = list(DOCS[ty])
    if ty == 2021: docs.append('rev-proc/2021/2021-023.md')
    if ty == 2009: docs.append('rev-proc/2009/2009-021.md')
    res = {}
    for p in docs:
        t = norm(text(p)[0])
        for m in re.finditer(r'Earned Income Amount \|? ?\$([\d,]+) \|? ?\$([\d,]+) \|? ?\$([\d,]+) \|? ?\$([\d,]+)', t):
            seg = t[m.start(): m.start() + 900]
            def row(lbl):
                mm = re.search(re.escape(lbl) + r'[^$]{0,80}?\$([\d,]+) \|? ?\$([\d,]+) \|? ?\$([\d,]+) \|? ?\$([\d,]+)', seg)
                return [toi(x) for x in mm.groups()] if mm else None
            mx = row('Maximum Amount of Credit')
            if not mx:
                mm = re.match(r'[^$]*?\$([\d,]+) \$([\d,]+) \$([\d,]+) \$([\d,]+)', t[m.end(): m.end() + 80])
                mx = [toi(x) for x in mm.groups()] if mm else None
            r = dict(eia=[toi(x) for x in m.groups()], mx=mx,
                     thr_s=row('Threshold Phaseout Amount (Single') or row('Threshold Phaseout Amount (All other'),
                     co_s=row('Completed Phaseout Amount (Single') or row('Completed Phaseout Amount (All other'),
                     thr_j=row('Threshold Phaseout Amount (Married'), co_j=row('Completed Phaseout Amount (Married'))
            if all(r.values()): res = r   # the last complete table in the last document wins
    return res
out = {}
for ty in range(2009, 2025):
    f = ('%s/i1040--%d.raw.txt' % (C, ty) if ty <= 2011 else '%s/i1040--%d.txt' % (C, ty)) if ty <= 2013 else '%s/i1040gi--%d.txt' % (C, ty)
    t = open(f, errors='replace').read()
    i = t.find('Earned Income Credit (EIC) Table'); body = t[i:] if i >= 0 else t
    rows = {}
    for line in body.splitlines():
        for m in ROW.finditer(line):
            g = m.groups(); lo, hi = toi(g[0]), toi(g[1])
            if hi - lo in (49, 50) and (lo % 50 == 0 or lo == 1) and lo not in rows:
                rows[lo] = (hi, [None if c.startswith('*') else toi(c) for c in g[2:]])
    p = params(ty)
    if p:
        top = max(p['co_j']); mxx = max(p['mx'])
        rows = {lo: r for lo, r in rows.items() if lo < top and all(v is None or v <= mxx for v in r[1])}
    out[ty] = dict(rows=sorted([lo, hi, v] for lo, (hi, v) in rows.items()), params=p, src=f.split('/')[-1])
    print(ty, len(rows), 'rows', p.get('eia'), p.get('mx'), p.get('thr_s'), p.get('thr_j'), p.get('co_s'))
json.dump(out, open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/tables/eic.json'), 'w'))
