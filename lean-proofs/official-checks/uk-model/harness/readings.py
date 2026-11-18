"""How often, and by how much, other readings change income tax + CGT (vs the default model)."""
import json, subprocess, sys
EXE = '/home/lean/cmp/uk/lean/.lake/build/bin/uktax'
def run(flags, f):
    out = subprocess.run([EXE] + flags + [f], capture_output=True, text=True, check=True).stdout
    return [json.loads(l) for l in out.splitlines() if l.strip()]
tot = lambda o: o['detail']['liabilityITA2007s23'] + o['surtaxes'].get('capitalGainsTax', 0)
for f in sys.argv[1:]:
    base = run([], f)
    for name, fl in (('s12B(8) literal', ['--psa-literal']), ('s192(4) words (main rates only)', ['--ras-literal']),
                     ('s192(4) unconditional (CG21204/PE)', ['--ras-unconditional'])):
        alt = run(fl, f)
        d = [(round(tot(x) - tot(y), 2), x['id']) for x, y in zip(alt, base) if abs(tot(x) - tot(y)) > 0.005]
        print(f"{f.split('/')[-1]:16s} {name:38s} changed {len(d):4d}/{len(base)}" + (f"  min {min(d)}  max {max(d)}" if d else ''))
