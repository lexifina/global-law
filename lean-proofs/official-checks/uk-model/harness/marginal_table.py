"""Effective marginal rates from the Lean model: one employee, k children (0-4), rest of UK / Scotland, wages
£0-£200,000 in £100 steps. Burden = incomeTax + employeeSocial - benefits (child benefit net of HICBC)."""
import json, subprocess, csv
EXE = '/home/lean/cmp/uk/lean/.lake/build/bin/uktax'
hs = []
for region in ('ruk', 'scotland'):
    for k in range(5):
        for w in range(0, 200001, 100):
            h = {"id": f"{region}|{k}|{w}", "year": 2025, "adults": [{"age": 40, "wages": w}], "married": False,
                 "children": [{"age": 5}] * k}
            if region == 'scotland': h["region"] = "scotland"
            hs.append(h)
out = subprocess.run([EXE], input='\n'.join(json.dumps(h) for h in hs) + '\n', capture_output=True, text=True, check=True).stdout
res = {}
for l in out.splitlines():
    o = json.loads(l); region, k, w = o['id'].split('|')
    res[(region, int(k), int(w))] = o['incomeTax'] + o['employeeSocial'] - o['benefits']
with open('/home/lean/cmp/uk/runs/marginal_rates.csv', 'w', newline='') as f:
    wr = csv.writer(f); wr.writerow(['region', 'children', 'wages', 'burden', 'marginal_rate_next_100'])
    for (region, k, w), b in sorted(res.items()):
        nxt = res.get((region, k, w + 100))
        wr.writerow([region, k, w, round(b, 2), '' if nxt is None else round((nxt - b) / 100, 4)])
# summary: highest marginal rate over a £100 step, and where
for region in ('ruk', 'scotland'):
    for k in range(5):
        rates = [((res[(region, k, w + 100)] - res[(region, k, w)]) / 100, w) for w in range(0, 200000, 100)]
        mx = max(rates)
        top = sorted(set(w for r, w in rates if r >= mx[0] - 1e-9))
        avg_hicbc = (res[(region, k, 80000)] - res[(region, k, 60000)]) / 20000
        avg_taper = (res[(region, k, 125100)] - res[(region, k, 100000)]) / 25100
        print(f"{region:8s} k={k}: max £100-step rate {mx[0]:.4f} at wages {top[:3]}...; avg 60-80k {avg_hicbc:.4f}; avg 100-125.1k {avg_taper:.4f}")
