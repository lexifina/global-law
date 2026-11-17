"""Benchmark: worked examples printed in the DGFiP brochure pratique (editions 2025 and 2026), encoded as returns
with the answer the brochure gives. Each is run through the Lean model and Mlang (cal)."""
import json, os, subprocess, sys, tempfile

LEAN = os.path.expanduser("~/fr/lean/.lake/build/bin/frtax")
BIN = os.path.expanduser("~/fr/bin")


def kids(prefix, n, born=2015):
    return {f"{prefix}{i}": born for i in range(n)}


EX = []
for ed, year, b1 in (("2025", 2024, 11497), ("2026", 2025, 11600)):
    EX += [
        dict(id=f"parts-375-{ed}", ed=ed, year=year, src="ch. Situation du foyer, EXEMPLES (1)",
             boxes={"0AM": 1, "0DA": 1980, "0DB": 1980, "0CF": 2, **kids("0F", 2), "0CH": 1, "0CI": 1, **kids("0H", 1)},
             expect={"NBPT": 3.75}),
        dict(id=f"parts-275-{ed}", ed=ed, year=year, src="ch. Situation du foyer, EXEMPLES (2)",
             boxes={"0AC": 1, "0DA": 1980, "0BT": 1, "0CH": 3, "0CI": 1, **kids("0H", 3)},
             expect={"NBPT": 2.75}),
        dict(id=f"bareme-54000-{ed}", ed=ed, year=year, src="ch. Calcul de l'impôt, Tableau de calcul, EXEMPLE",
             boxes={"0AM": 1, "0DA": 1980, "0DB": 1980, "0CF": 2, **kids("0F", 2), "4BA": 54000},
             expect={"IDRS": 2146 if year == 2024 else 2112}),
        dict(id=f"decote-2140-{ed}", ed=ed, year=year, src="ch. Calcul de l'impôt, Décote, EXEMPLE",
             boxes={"0AM": 1, "0DA": 1980, "0DB": 1980, "4BA": 42448 if year == 2024 else 42654},
             expect={"IDRS": 2140, "IDEC": 502 if year == 2024 else 515, "IDRS4": 1638 if year == 2024 else 1625}),
        dict(id=f"syndicats-{ed}", ed=ed, year=year, src="ch. RICI 2042, cotisations syndicales, EXEMPLE",
             boxes={"0AC": 1, "0DA": 1980, "1AJ": 27000, "7AC": 300},
             expect={"CITOT": 178}),
        dict(id=f"per-couple-{ed}", ed=ed, year=year, src="ch. Charges à déduire, épargne retraite, couple (sans mutualisation)",
             boxes={"0AM": 1, "0DA": 1980, "0DB": 1980, "1AJ": 40000, "6NS": 1500,
                    "APS": 1399 if year == 2024 else 1637, "DPS": 1200, "CPS": 0, "BPS": 0,
                    "6NT": 5200, "APT": 4399 if year == 2024 else 4637, "DPT": 0, "CPT": 0, "BPT": 0},
             expect={"RNG": 36000 - 1500 - (4399 if year == 2024 else 4637)}),
        dict(id=f"per-couple-mutualise-{ed}", ed=ed, year=year, src="ch. Charges à déduire, épargne retraite, couple (mutualisation)",
             boxes={"0AM": 1, "0DA": 1980, "0DB": 1980, "1AJ": 40000, "6NS": 1500, "6QR": 1,
                    "APS": 1399 if year == 2024 else 1637, "DPS": 1200, "CPS": 0, "BPS": 0,
                    "6NT": 5200, "APT": 4399 if year == 2024 else 4637, "DPT": 0, "CPT": 0, "BPT": 0},
             expect={"RNG": 36000 - 6700}),
    ]
MVAR = {"NBPT": "NBPT", "IDRS": "IDRS", "IDEC": "IDEC", "IDRS4": "IDRS4", "CITOT": "IRE", "RNG": "RNG"}


def run_m(e):
    d = tempfile.mkdtemp()
    os.makedirs(d + "/o")
    p = d + "/x.irj"
    body = ["#NOM", e["id"], "#ENTREES-PRIMITIF", "REGCO/1"] + [f"{k}/{v}" for k, v in e["boxes"].items()]
    body += ["#CONTROLES-PRIMITIF", "#RESULTATS-PRIMITIF", "#ENTREES-CORRECTIF", "#CONTROLES-CORRECTIF",
             "#RESULTATS-CORRECTIF", "##"]
    open(p, "w").write("\n".join(body) + "\n")
    r = subprocess.run([f"{BIN}/cal{e['year']}", "-completion", "-m", "p", "-a", str(e["year"]), "-dst", d + "/o", p],
                       capture_output=True, text=True)
    out = {}
    if os.path.exists(d + "/o/x.irj"):
        sec = None
        for line in open(d + "/o/x.irj"):
            if line.startswith("#"):
                sec = line.strip(); continue
            if sec == "#RESULTATS-PRIMITIF" and "/" in line:
                k, v = line.strip().split("/", 1)
                out[k] = float(v)
    else:
        out["_rejected"] = r.stdout[-200:]
    return out


def run_lean(e):
    line = f"{e['id']};{e['year']};" + ",".join(f"{k}={v}" for k, v in e["boxes"].items()) + "\n"
    r = subprocess.run([LEAN], input=line, capture_output=True, text=True)
    return {kv.split("=")[0]: float(kv.split("=")[1]) for kv in r.stdout.strip().split(";")[1:]}


rows = []
okl = okm = tot = 0
for e in EX:
    m, l = run_m(e), run_lean(e)
    for f, want in e["expect"].items():
        lv, mv = l.get(f), m.get(MVAR[f])
        tot += 1
        okl += lv == want
        okm += mv == want
        rows.append(dict(id=e["id"], src=e["src"], field=f, brochure=want, lean=lv, m=mv, m_rejected=m.get("_rejected")))
        print(f"{e['id']:28s} {f:6s} brochure {want:>8} lean {lv!s:>8} M {mv!s:>8}")
print(f"worked examples: {tot} answers; Lean {okl}/{tot}; Mlang {okm}/{tot}")
json.dump(rows, open(sys.argv[1], "w"))
