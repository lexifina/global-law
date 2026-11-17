"""Pub 15-T (2020-2026) Annual Percentage Method tables (automated payroll, 2020+ Form W-4) against the statute:
each row of the STANDARD schedule = the year's s1(j) bracket threshold + (s63(c) standard deduction - the Form W-4
adjustment $12,900 MFJ / $8,600 others, Pub 15-T worksheet 1A line 1g), base = tax at the threshold by the s1(j) rates;
the Step 2 checkbox schedule = half the standard deduction and half the bracket widths (halves rounded up to the dollar).
Brackets from indexing/brackets.json and standard deductions from indexing/published.json (both checked against the statute)."""
import os, re, json, subprocess
from fractions import Fraction as F
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
BR = json.load(open(H + '/indexing/brackets.json')); PUB = json.load(open(H + '/indexing/published.json'))
RATES = [0, 10, 12, 22, 24, 32, 35, 37]
def money(s): return F(s.replace('$', '').replace(',', '')) if s else None
STD2021 = {'mfj': 25100, 'single': 12550, 'hoh': 18800}   # Rev. Proc. 2020-45 sec. 3.16 (not captured in published.json)
def expected(y, st, check):
    br = BR[str(y)]['br'][st]
    std = STD2021[st] if y == 2021 else PUB[str(y)][{'mfj': 'std_mfj', 'single': 'std_single', 'hoh': 'std_hoh'}[st]]['v'][-1 if st == 'hoh' else 0]
    if check:
        off = F(std, 2); th = [0] + [F(b, 2) for b in br]
    else:
        off = std - (12900 if st == 'mfj' else 8600); th = [0] + list(br)
    rows = []; base = F(0)
    A = [0] + [off + t for t in th]
    for k in range(8):
        lo = A[k]; hi = A[k + 1] if k < 7 else None
        rows.append((lo, hi, base, RATES[k]))
        if hi is not None: base += F(RATES[k], 100) * (hi - lo)
    return rows
res = {'rows': 0, 'cells': 0, 'off': []}
for y in range(2020, 2027):
    f = H + '/cache/www.irs.gov/pub/irs-prior/p15t--%d.pdf' % y if y < 2026 else H + '/cache/www.irs.gov/pub/irs-pdf/p15t.pdf'
    if not os.path.exists(f): print('missing', y); continue
    t = subprocess.run(['pdftotext', '-layout', f, '-'], capture_output=True, text=True).stdout
    R = r'\$([\d,]+)\s+(?:\$([\d,]+))?\s+\$([\d,.]+)\s+(\d+(?:\.\d+)?)%\s+\$([\d,]+)'
    lines = [l for l in t.splitlines() if len(re.findall(R, l)) == 2]
    blocks = [lines[i: i + 8] for i in range(0, 24, 8)]
    for st, blk in zip(('mfj', 'single', 'hoh'), blocks):
        for side, check in ((0, False), (1, True)):
            exp = expected(y, st, check)
            for k, l in enumerate(blk):
                m = re.findall(R, l)[side]; a, b, c, d, e = money(m[0]), money(m[1]), money(m[2]), int(float(m[3])), money(m[4])
                lo, hi, base, rate = exp[k]
                rd = lambda v: v if v is None or v.denominator == 1 else F(int(v) + 1)    # halves rounded up
                want = (rd(lo), rd(hi), base, rate, rd(lo))
                got = (a, b, c, d, e); res['rows'] += 1; res['cells'] += 5
                for name, g, w in zip('ABCDE', got, want):
                    if g != w and not (name == 'C' and w is not None and abs(g - w) <= F(1, 2)):
                        res['off'].append((y, st, 'checkbox' if check else 'standard', k, name, str(g), str(w)))
print(y, res['rows'], 'rows', res['cells'], 'cells', len(res['off']), 'off')
for o in res['off'][:30]: print(o)
json.dump(res, open(H + '/withholding/p15t_check.json', 'w'), indent=0)
