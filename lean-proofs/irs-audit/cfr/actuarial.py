"""Actuarial tables printed in 26 CFR 20.2031-7(d)(6) and 25.2512-5(d)(6): Table B (term-certain remainder factors),
Table J (beginning-of-interval annuity adjustment) and Table K (end-of-interval), and the 2010CM life table."""
import re, os, json
C = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/src/cfr')
out = {}
for f in ['title-26-part-0020/sec-2031-0007.md', 'title-26-part-0025/sec-2512-0005.md']:
    L = open(C + '/' + f, encoding='utf-8').read().splitlines()
    B = []; JK = {'J': [], 'K': []}; lx = {}; cur = None; rates = None
    for line in L:
        if line.startswith('Table B'): cur = 'B'; continue
        if line.startswith('Table J'): cur = 'J'; continue
        if line.startswith('Table K'): cur = 'K'; continue
        if 'Table 4 to Paragraph (d)(7)(ii)' in line or line.startswith('Age x |'): cur = 'L'; continue
        if line.startswith('(7)') or line.startswith('(e)'): cur = None if cur != 'L' else cur
        c = [x.strip() for x in line.split('|')]
        if cur == 'B':
            if c[0].endswith('%') and all(x.endswith('%') for x in c): rates = [int(round(float(x[:-1]) * 10)) for x in c]; continue
            if rates and c[0].isdigit() and len(c) == len(rates) + 1:
                for r, v in zip(rates, c[1:]): B.append((r, int(c[0]), int(v.replace('.', '').lstrip('0') or '0')))
        elif cur in ('J', 'K'):
            if re.match(r'^\d+\.\d$', c[0]) and len(c) == 6:
                JK[cur].append((int(round(float(c[0]) * 10)), [int(x.replace('.', '')) for x in c[1:]]))
        elif cur == 'L':
            for k in range(0, len(c) - 1, 2):
                if c[k].isdigit(): lx[int(c[k])] = c[k + 1].replace(',', '')
    out[f] = dict(B=B, J=JK['J'], K=JK['K'], lx=lx)
    print(f, 'B', len(B), 'J', len(JK['J']), 'K', len(JK['K']), 'lx', len(lx))
json.dump(out, open(os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/cfr/actuarial.json'), 'w'))
