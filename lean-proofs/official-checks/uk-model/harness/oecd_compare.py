"""Compare uktax with the OECD Taxing Wages 2026 decomposition for the UK, 2025 (= tax year 2025-26).
Source: OECD SDMX API, OECD.CTP.TPS,DSD_TAX_WAGES_DECOMP@DF_TW_DECOMP (refs/oecd/gbr_decomp_2025.csv)."""
import csv, json, subprocess, collections
EXE = '/home/lean/cmp/uk/lean/.lake/build/bin/uktax'
rows = list(csv.DictReader(open('/home/lean/cmp/uk/refs/oecd/gbr_decomp_2025.csv', encoding='utf-8-sig')))
cases = collections.defaultdict(dict)
for r in rows:
    if r['UNIT_MEASURE'] != 'XDC' or r['OBS_VALUE'] == '': continue
    cases[(r['HOUSEHOLD_TYPE'], r['INCOME_PRINCIPAL'])][r['MEASURE']] = float(r['OBS_VALUE'])
hs = []
keys = sorted(cases)
for (ht, lev) in keys:
    c = cases[(ht, lev)]
    w = round(c['GRS_EARN'] if 'GRS_EARN' in c else c.get('GWE', 0))
    h = {"id": f"{ht}-{lev}", "year": 2025, "adults": [{"age": 40, "wages": w, "selfEmployment": 0, "pension": 0}],
         "married": False, "children": [], "interest": 0, "dividends": 0, "capitalGains": 0, "rentalIncome": 0,
         "charitable": 0, "pensionContributions": 0}
    if ht.startswith('C_'):
        h["adults"].append({"age": 40, "wages": 0, "selfEmployment": 0, "pension": 0}); h["married"] = True
    if ht.endswith('C2'):
        h["children"] = [{"age": 6}, {"age": 11}]
    hs.append(h)
print('measures available:', sorted(cases[keys[0]].keys()))
inp = '\n'.join(json.dumps(h) for h in hs) + '\n'
out = [json.loads(l) for l in subprocess.run([EXE], input=inp, capture_output=True, text=True, check=True).stdout.splitlines()]
stats = collections.defaultdict(lambda: collections.Counter()); worst = collections.defaultdict(list)
for h, o, k in zip(hs, out, keys):
    c = cases[k]; ht = k[0]
    gwe = c['GWE']; w = h['adults'][0]['wages']
    # the model gets whole pounds: allow the effect of rounding the wage (at most 47 % of the 50p rounding) + 1p
    tol = 0.5 * 0.47 + 0.02
    lean_it = o['incomeTax'] + o['detail']['hicbc']        # OECD's central income tax includes the HICBC?
    pairs = {'income tax (excl. HICBC)': (o['incomeTax'], -c['IT_CG']),
             'income tax incl. HICBC': (lean_it, -c['IT_CG']),
             'employee SSC': (o['employeeSocial'], -c['EESSC']),
             'cash benefits (gross CB)': (o['detail']['childBenefit'], c['CB'])}
    for name, (a, b) in pairs.items():
        ok = abs(a - b) <= tol
        stats[(ht, name)]['ok' if ok else 'bad'] += 1
        if not ok: worst[(ht, name)].append((k[1], round(a, 2), round(b, 2)))
for (ht, name), cnt in sorted(stats.items()):
    w = worst[(ht, name)]
    print(f"{ht} {name:28s} equal {cnt['ok']:3d}/201", ('e.g. ' + str(w[:3])) if w else '')
