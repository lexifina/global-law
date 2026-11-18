"""uktax vs OECD Taxing Wages 2026 (UK, 2025): income tax and employee SSC bracketed by the model at the wage rounded
down and up to whole pounds; child benefit net of HICBC compared with OECD 'cash benefits'."""
import csv, json, subprocess, collections, math
EXE = '/home/lean/cmp/uk/lean/.lake/build/bin/uktax'
rows = list(csv.DictReader(open('/home/lean/cmp/uk/refs/oecd/gbr_decomp_2025.csv', encoding='utf-8-sig')))
cases = collections.defaultdict(dict)
for r in rows:
    if r['UNIT_MEASURE'] == 'XDC' and r['OBS_VALUE'] != '':
        cases[(r['HOUSEHOLD_TYPE'], r['INCOME_PRINCIPAL'])][r['MEASURE']] = float(r['OBS_VALUE'])
keys = sorted(cases)
def hh(ht, w, tag):
    h = {"id": f"{ht}-{tag}", "year": 2025, "adults": [{"age": 40, "wages": w, "selfEmployment": 0, "pension": 0}],
         "married": False, "children": [], "interest": 0, "dividends": 0, "capitalGains": 0, "rentalIncome": 0,
         "charitable": 0, "pensionContributions": 0}
    if ht.startswith('C_'):
        h["adults"].append({"age": 40, "wages": 0, "selfEmployment": 0, "pension": 0}); h["married"] = True
    if ht.endswith('C2'): h["children"] = [{"age": 6}, {"age": 11}]
    return h
hs = []
for (ht, lev) in keys:
    g = cases[(ht, lev)]['GWE']
    hs += [hh(ht, math.floor(g), 'lo'), hh(ht, math.ceil(g), 'hi')]
inp = '\n'.join(json.dumps(h) for h in hs) + '\n'
out = [json.loads(l) for l in subprocess.run([EXE], input=inp, capture_output=True, text=True, check=True).stdout.splitlines()]
res = collections.Counter(); cbdiff = collections.defaultdict(list)
for i, k in enumerate(keys):
    c = cases[k]; lo, hi = out[2 * i], out[2 * i + 1]
    for name, f, ov in (('income tax', lambda o: o['incomeTax'], -c['IT_CG']), ('employee SSC', lambda o: o['employeeSocial'], -c['EESSC'])):
        a, b = sorted((f(lo), f(hi)))
        res[(k[0], name, a - 0.02 <= ov <= b + 0.02)] += 1
    if k[0].endswith('C2'):
        cbdiff[k[0]].append((int(k[1][2:]), round(c['CB'], 2), lo['benefits'], hi['benefits']))
for (ht, name, ok), n in sorted(res.items()):
    print(ht, name, 'within bracket' if ok else 'OUTSIDE', n)
for ht, lst in cbdiff.items():
    lst.sort()
    uc = [x for x in lst if x[1] > 2257.8]
    full = [x for x in lst if abs(x[1] - 2257.79) < 0.01]
    band = [x for x in lst if 0 < x[1] < 2257.78]
    zero = [x for x in lst if x[1] == 0]
    print(ht, f"UC (OECD > CB): AW{uc[0][0]}-AW{uc[-1][0]} ({len(uc)})" if uc else "no UC",
          f"| full CB: {len(full)} (OECD 2257.79 vs Lean {full[0][2] if full else ''})",
          f"| HICBC band: {len(band)}, max |OECD-Lean| {max(abs(x[1]-x[2]) for x in band):.2f}" if band else '',
          f"| nil: {len(zero)}, Lean nil there: {sum(1 for x in zero if x[2]==0 and x[3]==0)}")
