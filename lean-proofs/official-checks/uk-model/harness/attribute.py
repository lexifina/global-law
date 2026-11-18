"""Attribute each statute-vs-PolicyEngine difference to the PolicyEngine convention that removes it.
usage: python3 -I attribute.py base   (needs base.jsonl, base.pe.jsonl; runs uktax variants)"""
import json, subprocess, sys, collections
base = sys.argv[1]
EXE = '/home/lean/cmp/uk/lean/.lake/build/bin/uktax'
ins = [json.loads(l) for l in open(base + '.jsonl')]
pe = [json.loads(l) for l in open(base + '.pe.jsonl')]
def run(flags):
    out = subprocess.run([EXE] + flags + [base + '.jsonl'], capture_output=True, text=True, check=True).stdout
    return [json.loads(l) for l in out.splitlines() if l.strip()]
def vals(lo, po):
    P = po['persons']
    pv = (sum(p['income_tax_before_winter_fuel_payment_charge'] - p['CB_HITC'] - p['personal_pension_contributions_tax'] for p in P),
          sum(p['capital_gains_tax'] for p in P), sum(p['national_insurance'] for p in P), sum(p['CB_HITC'] for p in P))
    lv = (lo['incomeTax'], lo['surtaxes'].get('capitalGainsTax', 0), lo['employeeSocial'], lo['detail']['hicbc'])
    return all(abs(a - b) <= 1.0 for a, b in zip(lv, pv)), [round(a - b, 2) for a, b in zip(lv, pv)]
variants = {'statute': [], 'ras': ['--pe-ras'], 'ma': ['--pe-ma'], 'giftaid': ['--pe-ga'], 'cgt': ['--pe-cgt'],
            'mca': ['--pe-mca'], 'all': ['--pe']}
res = {k: run(v) for k, v in variants.items()}
singles = ['ras', 'ma', 'giftaid', 'cgt', 'mca']
cat = collections.Counter(); amounts = collections.defaultdict(list); unexplained = []
import itertools
for i, (h, po) in enumerate(zip(ins, pe)):
    ok, d = vals(res['statute'][i], po)
    if ok: cat['equal'] += 1; continue
    found = None
    for k in singles:
        if vals(res[k][i], po)[0]: found = k; break
    if found is None:
        # pairs of conventions
        for a, b in itertools.combinations(singles, 2):
            r2 = run_pair = None
        found = 'several' if vals(res['all'][i], po)[0] else 'UNEXPLAINED'
    cat[found] += 1
    amounts[found].append(d[0] + d[1])
    if found == 'UNEXPLAINED': unexplained.append((h['id'], d))
print(json.dumps({'n': len(ins), 'categories': cat}, indent=1))
for k, v in amounts.items():
    print(k, 'count', len(v), 'mean diff (Lean - PE, income tax + CGT)', round(sum(v) / len(v), 2), 'min', min(v), 'max', max(v))
for u in unexplained[:20]: print('UNEXPLAINED', u)
