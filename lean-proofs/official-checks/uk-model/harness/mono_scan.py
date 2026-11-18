"""Empirical monotonicity of the full household model: raise one income by d pounds and see whether the household's
income tax (contract incomeTax: liability less relief at source), the s. 23 liability alone, and income tax + CGT
fall. usage: python3 -I mono_scan.py households.jsonl [--literal]"""
import json, subprocess, sys, collections, copy
EXE = '/home/lean/cmp/uk/lean/.lake/build/bin/uktax'
flags = [a for a in sys.argv[2:] if a.startswith('--')]
hs = [json.loads(l) for l in open(sys.argv[1])]
fields = [('adults', 0, 'wages'), ('adults', 0, 'selfEmployment'), ('adults', 0, 'pension'), ('adults', 1, 'wages'),
          ('', None, 'interest'), ('', None, 'dividends'), ('', None, 'rentalIncome'), ('', None, 'capitalGains')]
deltas = [1, 100, 2000]
variants = []
for h in hs:
    for (grp, k, f) in fields:
        if grp == 'adults' and k >= len(h['adults']): continue
        for d in deltas:
            g = copy.deepcopy(h)
            if grp: g['adults'][k][f] = g['adults'][k].get(f, 0) + d
            else: g[f] = g.get(f, 0) + d
            g['id'] = f"{h['id']}|{f}{k if k is not None else ''}|+{d}"
            variants.append(g)
def run(items):
    inp = '\n'.join(json.dumps(x) for x in items) + '\n'
    out = subprocess.run([EXE] + flags, input=inp, capture_output=True, text=True, check=True).stdout
    return {json.loads(l)['id']: json.loads(l) for l in out.splitlines() if l.strip()}
base = run(hs); var = run(variants)
measures = {
  'incomeTax': lambda o: o['incomeTax'],
  'liability': lambda o: o['detail']['liabilityITA2007s23'],
  'liability+CGT': lambda o: o['detail']['liabilityITA2007s23'] + o['surtaxes'].get('capitalGainsTax', 0),
}
falls = collections.defaultdict(list)
for vid, vo in var.items():
    bid = vid.split('|')[0]; bo = base[bid]
    for m, fn in measures.items():
        dlt = fn(vo) - fn(bo)
        if dlt < -0.005: falls[m].append((round(dlt, 2), vid))
print(f"{len(hs)} households, {len(var)} perturbations, flags {flags}")
for m in measures:
    fl = sorted(falls[m])
    by = collections.Counter(v.split('|')[1] for _, v in fl)
    print(f"  {m}: falls {len(fl)}; by field {dict(by)}; worst {fl[:3]}")
