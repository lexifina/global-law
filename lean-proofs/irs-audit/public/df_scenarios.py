"""Direct File scenario snapshots that carry computed values (/taxableIncome, /tentativeTaxFromTaxableIncome): tax recomputed
by the Tax Table rule (s1(j) brackets of the year, midpoint of the $50 row under $100,000; exact over) for 2023 and 2024."""
import json, glob, os
from fractions import Fraction as F
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit')); BR = json.load(open(H + '/indexing/brackets.json'))
R = [10, 12, 22, 24, 32, 35, 37]
def tax(y, st, ti):
    br = BR[str(y)]['br'][st]; x = F(ti)
    if ti < 100000: x = F(int(ti) // 50 * 50 + 25) if ti >= 5 else (F(ti // 5 * 5 + F(5, 2)) if ti > 0 else F(0))
    t = F(0); lo = 0
    for r, hi in zip(R, br + [10**12]):
        if x > lo: t += F(r, 100) * (min(x, hi) - lo)
        lo = hi
    return int(t + F(1, 2)) if ti < 100000 else t
ST = {'single': 'single', 'marriedFilingJointly': 'mfj', 'headOfHousehold': 'hoh', 'marriedFilingSeparately': 'mfs', 'qualifiedSurvivingSpouse': 'mfj'}
for f in glob.glob(H + '/src/irs-public/direct-file/**/scenarios/**/*.json', recursive=True):
    d = json.load(open(f)); d = d.get('facts', d)
    if '/taxableIncome' not in d or '/tentativeTaxFromTaxableIncome' not in d: continue
    fsv = d.get('/filingStatus', {}).get('value'); fsv = fsv.get('value', fsv) if isinstance(fsv, dict) else fsv
    fsv = (fsv[0] if isinstance(fsv, list) else fsv); ti = d['/taxableIncome']['value']; tt = d['/tentativeTaxFromTaxableIncome']['value']
    st = ST.get(str(fsv), 'single')
    print(os.path.basename(f), fsv, ti, tt, {y: float(tax(y, st, ti)) for y in (2023, 2024)})
