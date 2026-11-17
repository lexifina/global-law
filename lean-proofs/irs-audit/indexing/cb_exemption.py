"""Personal exemption amounts 1990-1996 printed in the Cumulative Bulletins (inflation Rev. Procs, reading-order text)
against s151(d)(4)(A) (1994 edition: $2,000 x the s1(f)(3) cost-of-living adjustment with calendar year 1988 as base;
CPI year = 12 months ending 31 August, s1(f)(4); rounded to the next lowest multiple of $50, s1(f)(6)). CPI-U from
~/docs/data/cpi (BLS), exact fractions."""
import re, glob, os, json
from fractions import Fraction as F
# CPI-U (BLS series CUUR0000SA0) from BLS API v1/v2 JSON responses saved in CPI_DIR
D=os.path.expanduser(os.environ.get('CPI_DIR', '~/docs/data/cpi'))  # BLS API JSON (bls_*.json)
def vint(v):
    d={}
    for r in csv.reader(open(f'{D}/ccpiu_v{v}.csv')):
        if r[0].startswith('obs') or not r[1]: continue
        d[(int(r[0][:4]),int(r[0][5:7]))]=F(r[1])
    return d
def bls(sid):
    d={}
    for fn in glob.glob(f'{D}/bls_*.json'):
        for s in json.load(open(fn))['Results']['series']:
            if s['seriesID']!=sid: continue
            for x in s['data']:
                if x['period']!='M13' and x['value'] not in ('-',''):
                    d[(int(x['year']),int(x['period'][1:]))]=F(x['value'])
    return d
CPI=bls('CUUR0000SA0')
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
def cpiyear(y): return sum(CPI[(y - 1, m)] for m in range(9, 13)) + sum(CPI[(y, m)] for m in range(1, 9))
pub = {}
for f in glob.glob(H + '/src/govinfo/raw/19[89]*_*.txt'):
    t = ' '.join(open(f, errors='replace').read().split())
    for m in re.finditer(r'personal exemption (?:amount )?for (?:tax|taxable) years beginning in (\d{4}) is \$ ?(\d{1,3}(?:, ?\d{3})+|\d+)', t): pub[int(m.group(1))] = (int(m.group(2).replace(',', '').replace(' ', '')), os.path.basename(f))
out = []
for ty, (v, f) in sorted(pub.items()):
    if ty < 1990: continue
    x = 2000 * cpiyear(ty - 1) / cpiyear(1988); want = int(x // 50 * 50)
    out.append(dict(year=ty, printed=v, statute=want, exact=float(x), ok=v == want, src=f))
    print(ty, v, want, round(float(x), 2), 'ok' if v == want else 'DIFF', f)
json.dump(out, open(H + '/indexing/cb_exemption.json', 'w'), indent=0)
