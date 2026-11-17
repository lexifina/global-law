"""§7702(f)(11)(C): average of the annual mid-term AFRs effective at the beginning of each month of the 60-month
period, as printed in Table 7 of the January AFR rulings 2020-2025, recomputed from the monthly rulings."""
import json, os
from fractions import Fraction as F
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
d = {(r['year'], r['month']): r for r in json.load(open(H + '/afr/afr.json')) if len(r['table1']) >= 5}
pub = {2019: '2.00', 2020: '1.82', 2021: '1.72', 2022: '1.85', 2023: '2.12', 2024: '2.53'}
for y, p in pub.items():
    ms = [(yy, m) for yy in range(y - 4, y + 1) for m in range(1, 13)]
    have = [F(d[k]['table1'][4][0]) for k in ms if k in d]
    miss = [k for k in ms if k not in d]
    avg = sum(have) / len(have)
    print(y, 'printed', p, 'recomputed %.4f' % float(avg), 'from', len(have), 'months; missing', miss, 'match' if abs(avg - F(p)) <= F(5, 1000) else 'DIFF')
