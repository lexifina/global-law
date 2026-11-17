"""SOI Historical Table 23 (personal exemptions, lowest/highest bracket) 1996-2018 against the verified amounts:
exemption (single, married = 2x, dependent) vs Rev. Proc. amounts (indexing/published.json, 1998-2017); lowest and
highest bracket thresholds (married joint) vs the Form 1040 rate schedules parsed by tables/parse_tables.py (tables/tables.json) or
indexing/brackets.json (2018)."""
import os, sys, re, json
sys.path.insert(0, os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit') + '/pylib')); import xlrd
H = os.path.expanduser(os.environ.get('IRS_AUDIT', '~/irs-audit'))
P = json.load(open(H + '/indexing/published.json')); B = json.load(open(H + '/indexing/brackets.json'))
sh = xlrd.open_workbook(H + '/cache/www.irs.gov/pub/irs-soi/histab23.xls').sheet_by_index(0)
def num(x):
    s = re.sub(r'\[[^\]]*\]', '', str(x)).replace(',', '').strip()
    try: return float(s)
    except ValueError: return None
res = {'checked': 0, 'off': []}
for r in range(sh.nrows):
    v = sh.row_values(r); m = re.match(r'(\d{4})(\.0)?$', str(v[0]).strip())
    if not m: continue
    y = m.group(1)
    if int(y) < 1996: continue
    single, married, dep, lo_rate, lo_ti, hi_rate, hi_ti = [num(x) for x in v[1:8]]
    pe = P.get(y, {}).get('pers_exempt', {}).get('v')
    if pe and single is not None:
        for name, got, want in (('single', single, pe[0]), ('married', married, 2 * pe[0]), ('dependent', dep, pe[0])):
            res['checked'] += 1
            if got != want: res['off'].append((y, name, got, want))
    if y in B:
        for name, got, want in (('lowest bracket mfj', lo_ti, B[y]['br']['mfj'][0]), ('highest bracket mfj', hi_ti, B[y]['br']['mfj'][-1])):
            res['checked'] += 1
            if got != want: res['off'].append((y, name, got, want))
print(res['checked'], 'checked', res['off'])
json.dump(res, open(H + '/soi/histab23_check.json', 'w'))
# lowest and highest bracket thresholds (married filing jointly, schedule Y-1) 1996-2017 vs the Form 1040 schedules
T = json.load(open(H + '/tables/tables.json'))
for r in range(sh.nrows):
    v = sh.row_values(r); m = re.match(r'(\d{4})(\.0)?$', str(v[0]).strip())
    if not m or not (1996 <= int(m.group(1)) <= 2017): continue
    y = m.group(1); s = T.get(y, {}).get('sched', {}).get('Y-1')
    if not s: continue
    lo_ti, hi_ti = num(v[5]), num(v[7]); lo_r, hi_r = num(v[4]), num(v[6])
    for name, got, want in (('lowest bracket top mfj', lo_ti, s[1][0]), ('highest bracket floor mfj', hi_ti, s[-1][0]), ('lowest rate', lo_r, float(s[0][2])), ('highest rate', hi_r, float(s[-1][2]))):
        res['checked'] += 1
        if got != want: res['off'].append((y, name, got, want))
print(res['checked'], 'checked incl. brackets', res['off'])
json.dump(res, open(H + '/soi/histab23_check.json', 'w'))
