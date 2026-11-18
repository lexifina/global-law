"""Show a household and one perturbation side by side (per-person key lines). usage: perturb_show.py file id field k d [flags]"""
import json, subprocess, sys, copy
EXE = '/home/lean/cmp/uk/lean/.lake/build/bin/uktax'
f, hid, field, k, d = sys.argv[1:6]; flags = sys.argv[6:]
h = next(json.loads(l) for l in open(f) if json.loads(l)['id'] == hid)
g = copy.deepcopy(h)
if k == '-': g[field] = g.get(field, 0) + int(d)
else: g['adults'][int(k)][field] = g['adults'][int(k)].get(field, 0) + int(d)
print('IN', json.dumps(h))
out = subprocess.run([EXE] + flags, input=json.dumps(h) + '\n' + json.dumps(g) + '\n', capture_output=True, text=True).stdout.splitlines()
for tag, l in zip(['base', f'+{d} {field}'], out):
    o = json.loads(l); dd = o['detail']
    print(f"== {tag}: incomeTax {o['incomeTax']} liab {dd['liabilityITA2007s23']} CGT {o['surtaxes'].get('capitalGainsTax',0)} election {dd['election']}")
    for p in dd['persons']:
        c = {kk: v for kk, v in p['charged'].items() if v}
        print('   ', {kk: p[kk] for kk in ['step3Income','basicRateLimit','bandsExtendedForPension','taxAtStep5','marriageAllowanceReduction','giftAidCharge','liability','capitalGainsTax','cgtTaxableGains']}, c)
