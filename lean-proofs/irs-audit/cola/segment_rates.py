"""Monthly pension segment-rate notices (§430(h)(2), §417(e)): (a) each month's spot segment rates = the average of the
printed corporate bond yield curve over the segment's maturities (0.5-5, 5.5-20, 20.5-60 years); (b) 24-month average
segment rates = the mean of the 24 monthly spot rates printed in the notices; (c) 30-year Treasury permissible range
= 90% (95% before 2008?) to 105% of the weighted average, as printed in the column heading."""
import re, os, glob, json, collections
G = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/src/irs-guidance')
MON = {m: i + 1 for i, m in enumerate(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'])}
spot = {}; avg24 = {}; curves = {}; tre = []; src = {}
for f in sorted(glob.glob(G + '/notice/*/*.md')):
    t = open(f, encoding='utf-8').read()
    if '24-month average segment rates' not in t: continue
    item = re.search(r'^item: "([^"]+)"', t, re.M).group(1)
    lines = t.splitlines(); mode = None; curve = []; cur_month = None
    for i, l in enumerate(lines):
        c = [x.strip() for x in l.split('|')]
        while len(c) > 1 and c[-1] == '': c.pop()
        if l.startswith('Applicable Month | First Segment'): mode = 'avg'; continue
        if l.startswith('Month | First Segment'): mode = 'spot'; continue
        if l.startswith('Maturity | Yield'): mode = 'curve'; continue
        m = re.match(r'(\w+) (\d{4})$', c[0]) if c else None
        if mode in ('avg', 'spot') and m and m.group(1) in MON and len(c) == 4:
            key = (int(m.group(2)), MON[m.group(1)])
            try: vals = [float(x) for x in c[1:]]
            except ValueError: continue
            (avg24 if mode == 'avg' else spot)[key] = vals; src.setdefault(mode + str(key), item)
            if mode == 'spot': cur_month = key
            mode = None if mode == 'avg' else mode
        elif mode == 'curve' and re.match(r'^\d+\.\d \|', l):
            for k in range(0, len(c) - 1, 2):
                try: curve.append((float(c[k]), float(c[k + 1])))
                except ValueError: pass
        rm = re.match(r'(\w+) (\d{4}) \| (\d+\.\d+) \| (\d+\.\d+) to (\d+\.\d+)$', l.strip())
        if rm and rm.group(1) in MON: tre.append((item, rm.group(1), int(rm.group(2)), float(rm.group(3)), float(rm.group(4)), float(rm.group(5)), t[max(0, t.rfind('Permissible Range', 0, t.find(l))): t.find(l)][:60]))
    if curve and cur_month: curves[cur_month] = (item, curve)
a_bad = []; na = 0
for key, (item, cv) in curves.items():
    if key not in spot: continue
    for s, (lo, hi) in enumerate([(0.5, 5.0), (5.5, 20.0), (20.5, 60.0)]):
        ys = [y for mt, y in cv if lo <= mt <= hi]
        if len(ys) < int((hi - lo) * 2) + 1: continue
        na += 1
        mean = sum(ys) / len(ys)
        if abs(mean - spot[key][s]) > 0.0101: a_bad.append((item, key, s + 1, spot[key][s], round(mean, 4)))
b_bad = []; nb = 0
for key, v in avg24.items():
    y, m = key; months = [((y * 12 + m - 2 - k) // 12, (y * 12 + m - 2 - k) % 12 + 1) for k in range(24)]   # the 24 months ending with the month before the applicable month
    if all(mm in spot for mm in months):
        for s in range(3):
            nb += 1; mean = sum(spot[mm][s] for mm in months) / 24
            if abs(mean - v[s]) > 0.0101: b_bad.append((src.get('avg' + str(key)), key, s + 1, v[s], round(mean, 4)))
c_bad = []; nc = 0
for item, mo, y, w, lo, hi, head in tre:
    pm = re.search(r'(\d+)% to (\d+)%', head); 
    if not pm: continue
    nc += 1; plo, phi = int(pm.group(1)), int(pm.group(2))
    if abs(round(w * plo / 100 + 1e-9, 2) - lo) > 0.0101 or abs(round(w * phi / 100 + 1e-9, 2) - hi) > 0.0101: c_bad.append((item, mo, y, w, lo, hi, plo, phi))
res = dict(curve_checks=na, curve_off=a_bad, avg24_checks=nb, avg24_off=b_bad, treasury_checks=nc, treasury_off=c_bad, months_spot=len(spot), curves=len(curves))
json.dump(res, open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/cola/segment_rates.json'), 'w'), indent=1, default=str)
print({k: (len(v) if isinstance(v, list) else v) for k, v in res.items()})
print('A', a_bad[:8]); print('B', b_bad[:8]); print('C', c_bad[:8])
