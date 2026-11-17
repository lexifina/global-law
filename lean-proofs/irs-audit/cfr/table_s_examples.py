import re, json, os
from fractions import Fraction as F
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
A = json.load(open(H + '/cfr/actuarial.json'))['title-26-part-0020/sec-2031-0007.md']
lx = {int(k): F(v) for k, v in A['lx'].items()}
L = open(H + '/src/cfr/title-26-part-0020/sec-2031-0007.md').read().splitlines()
rate = None; rows = []
for line in L:
    m = re.search(r'Interest at (\d+\.\d) Percent', line)
    if m: rate = F(m.group(1)) / 100; continue
    c = [x.strip() for x in line.split('|')]
    if rate and len(c) == 4 and c[0].isdigit() and len(c[2]) == 7 and int(c[0]) < 111 and '.' in c[1] and float(c[3]) < 1:
        rows.append((int(c[0]), rate, c[1], c[2], c[3]))
    if line.startswith('Factors from Table B') or line.startswith('Factors From Table K'): rate = None
def rem(x, i):
    v = 1 / (1 + i); s = F(0)
    for t in range(0, 110 - x):
        s += v ** (t + 1) * (lx[x + t] - lx[x + t + 1])
    return s / lx[x] * (1 + i / 2)   # Figure 2 of 20.2031-7(d)(2)(ii)(B) (an image in the eCFR text): mid-year (1 + i/2) factor
bad = 0
for x, i, a, le, r in rows:
    R = rem(x, i); A_ = (1 - R) / i
    ok = abs(R - F(r)) <= F(1, 200000) and abs((1 - R) - F(le)) <= F(1, 200000) and abs(A_ - F(a)) <= F(1, 20000)
    bad += not ok
    print(x, float(i), 'printed', a, le, r, '| computed %.4f %.5f %.5f' % (float(A_), float(1 - R), float(R)), 'ok' if ok else 'DIFF')
print('rows', len(rows), 'bad', bad)
