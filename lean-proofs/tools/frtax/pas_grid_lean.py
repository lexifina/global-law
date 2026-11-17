"""Default grids: the Lean model (G lines) against the statute dataset data/pas_grids.jsonl, cell by cell: for each
grid and bracket, the base at the lower bound (that bracket's rate) and one euro below (the bracket before), and
the top. Also probes M's dependants' grid (RASTXPAC7) at the 2026 mainland bounds 8 739 and 8 789 through a
dependant's BNC profit (monthly base = arr(arr(profit x 1.11) / 12), art. 204 H, III, 1, d, last paragraph).
Writes runs/pas/grid_lean.json."""
import json, os, subprocess, tempfile, re
H = os.path.expanduser("~/fr")
LEAN = f"{H}/lean/.lake/build/bin/frtax"
grids = [json.loads(l) for l in open(f"{H}/data/pas_grids.jsonl")]
probes = []
for g in grids:
    lo, rates = g["lower_bounds"], g["rates"]
    probes.append((g["rate_year"], g["zone"], 0, rates[0]))
    for k, b in enumerate(lo):
        probes.append((g["rate_year"], g["zone"], b, rates[k + 1]))
        probes.append((g["rate_year"], g["zone"], b - 1, rates[k]))
    probes.append((g["rate_year"], g["zone"], 10 ** 7, rates[-1]))
inp = "".join(f"G;g{i};{y};{z};{b}\n" for i, (y, z, b, _) in enumerate(probes))
out = subprocess.run([LEAN], input=inp, capture_output=True, text=True).stdout.splitlines()
got = {l.split(";")[0]: float(l.split("GRID=")[1]) for l in out if "GRID=" in l}
bad = [dict(rate_year=y, zone=z, base=b, statute=r, lean=got.get(f"g{i}")) for i, (y, z, b, r) in enumerate(probes)
       if got.get(f"g{i}") is None or abs(got[f"g{i}"] - r) > 1e-9]
res = {"probes": len(probes), "equal": len(probes) - len(bad), "diffs": bad}
print(f"Lean grids vs statute: {res['equal']}/{res['probes']} probes equal")

# M's dependants' grid, income 2025 (rate year 2026), through a dependant's BNC profit (box 5SC)
mres = []
for prof in (94000, 94550, 94595, 94640, 95000, 95100):
    d = tempfile.mkdtemp(); os.makedirs(d + "/o")
    body = ["#NOM", "X", "#ENTREES-PRIMITIF", "REGCO/1", "ANREV/2025", "0AM/1", "0DA/1980", "0DB/1980", "0CF/1", "0F0/2008",
            "1AJ/40000", "1BJ/30000", f"5SC/{prof}", "#CONTROLES-PRIMITIF", "#RESULTATS-PRIMITIF", "#ENTREES-CORRECTIF",
            "#CONTROLES-CORRECTIF", "#RESULTATS-CORRECTIF", "##"]
    open(d + "/x.irj", "w").write("\n".join(body) + "\n")
    r = subprocess.run([f"{H}/bin/cal2025", "-completion", "-m", "p", "-a", "2025", "-dst", d + "/o", d + "/x.irj"],
                       capture_output=True, text=True)
    vals = {}
    if os.path.exists(d + "/o/x.irj"):
        for line in open(d + "/o/x.irj"):
            k = line.split("/")[0]
            if k in ("REVMENSPAC7", "RASTXPAC7", "RASTXPAC", "RASBNCPN", "RASPACA", "NBPT") and k not in vals:
                vals[k] = float(line.split("/")[1])
    ko = re.findall(r"KO \| (\S+)", r.stdout)
    base = vals.get("REVMENSPAC7")
    lean = None
    if base is not None:
        o = subprocess.run([LEAN], input=f"G;x;2026;metropole;{int(base)}\n", capture_output=True, text=True).stdout
        lean = float(o.split("GRID=")[1])
    mres.append({"5SC": prof, "M": vals, "M_refused": ko, "lean_grid_at_M_base": lean})
    print("  dependant BNC", prof, vals, ko, "Lean grid at that base:", lean)
res["m_dependant_probe"] = mres
json.dump(res, open(f"{H}/runs/pas/grid_lean.json", "w"), indent=1)
