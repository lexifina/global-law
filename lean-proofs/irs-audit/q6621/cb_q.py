"""Quarterly section 6621 rulings in the Cumulative Bulletins 1986-1995 (reading-order text): the federal short-term rate
'determined during the month of M Y is N percent' and the overpayment / underpayment rates for the next quarter.
-> q6621/q_cb.json; then a Lean run (lean/q6621/RunCB.lean) with the AFR rows from afr/afr_cb.json + afr/afr.json."""
import re, os, glob, json, collections
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
MON = ['january','february','march','april','may','june','july','august','september','october','november','december']
out = []; seen = set()
for f in sorted(glob.glob(H + '/src/govinfo/raw/19[89]*_*.txt')):
    yv = int(os.path.basename(f)[:4])
    if not 1986 <= yv <= 1995: continue
    t = open(f, errors='replace').read(); t = re.sub(r'-\s*\n\s*', '', t); t = re.sub(r'\s+', ' ', t)
    for m in re.finditer(r'federal short-term rate (?:based on daily compounding )?determined during the month of (\w+),? (19\d\d),? is (\d+) percent\.? (.{0,400})', t):
        mon = m.group(1).lower()
        if mon not in MON: continue
        rest = m.group(4)
        o = re.search(r'overpayment rate of (\d+) percent', rest); u = re.search(r'underpayment rate of (\d+) percent', rest)
        qb = re.search(r'calendar quarter beginning (\w+) 1,? (19\d\d)', rest)
        if not (o and u and qb) or qb.group(1).lower() not in MON: continue
        key = (int(m.group(2)), MON.index(mon) + 1)
        if key in seen: continue
        seen.add(key)
        rr = re.findall(r'Rev\. Rul\. (\d\d-\d+)', t[max(0, m.start() - 2500): m.start()])
        out.append(dict(item='Rev. Rul. ' + rr[-1] if rr else 'C.B. %d (%s %s)' % (yv, mon, m.group(2)), fst_month=list(key),
                        quarter=[int(qb.group(2)), MON.index(qb.group(1).lower()) + 1], fst=m.group(3), over=o.group(1), under=u.group(1), tables=[]))
json.dump(out, open(H + '/q6621/q_cb.json', 'w'), indent=0)
print(len(out), 'quarterly rulings', sorted(tuple(r['quarter']) for r in out))
# Lean: reuse lean/q6621/Run.lean with the CB data
def bp(x): a, _, b = x.partition('.'); return int(a or 0) * 100 + int((b + '00')[:2])
rows = {}
for src in ('afr/afr_cb.json', 'afr/afr.json'):
    for r in json.load(open(H + '/' + src)):
        lab = r.get('labels') or [('short', 100)]
        if r['table1'] and (lab[0] == ['short', 100] or lab[0] == ('short', 100)) and (r['year'], r['month']) not in rows:
            try: rows[(r['year'], r['month'])] = [bp(v) for v in r['table1'][0]]
            except Exception: pass
R = open(H + '/lean/q6621/Run.lean').read()
a = R.index('def afrShort'); b = R.index(']', R.index(':= [', a)) + 1
R = R[:a] + 'def afrShort : List (Nat × Nat × Row) := [' + ','.join('\n  (%d, %d, ⟨%d, %d, %d, %d⟩)' % (y, m, *v) for (y, m), v in sorted(rows.items())) + '\n]' + R[b:]
a = R.index('def qrs'); b = R.index('\n]', a) + 2
recs = ['  { item := "%s", fy := %d, fm := %d, qy := %d, qm := %d, fst := %d, over := some %d, overCorp := none, under := some %d, over10k := none, large := none }' % (
    r['item'], r['fst_month'][0], r['fst_month'][1], r['quarter'][0], r['quarter'][1], 10 * int(r['fst']), 10 * int(r['over']), 10 * int(r['under'])) for r in out]
R = R[:a] + 'def qrs : List QR := [\n' + ',\n'.join(recs) + '\n]' + R[b:]
R = '\n'.join(l for l in R.split('\n') if not re.match(r'def tab[0-9]', l))
a = R.index('def tables'); b = R.index('\n', a)
R = R[:a] + 'def tables : List FTable := []' + R[b:]
open(H + '/lean/q6621/RunCB.lean', 'w').write(R)
