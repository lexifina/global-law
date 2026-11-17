"""Classify OpenFisca-France disagreements with M by cause."""
import json, sys, collections
o = json.load(open(sys.argv[1]))
cases = {json.loads(l)["id"]: json.loads(l) for l in open(sys.argv[2])}
AGE = {2024: (2796, 1398), 2025: (2822, 1411)}
for y, Y in o["years"].items():
    year = int(y)
    causes = collections.Counter(); n = Y["n"]; bad = 0
    for r in Y["rows"]:
        ch = r["checks"]; b = cases[r["id"]]["boxes"]
        badf = [f for f, (of, m, l) in ch.items() if of is None or abs(of - m) >= 0.5]
        if not badf:
            continue
        bad += 1
        couple = "0AM" in b or "0AO" in b
        old = lambda k: b.get(k, 9999) <= year - 65
        d_rni = (ch["RNI"][0] or 0) - ch["RNI"][1]
        d_rfr = (ch["REVKIRE"][0] or 0) - ch["REVKIRE"][1]
        c = []
        if couple and old("0DA") and old("0DB") and round(d_rni) in AGE[year]:
            c.append("157bis-not-doubled")
        if any(k in b for k in ("1GH", "1HH")) and d_rfr < -0.5 and "RNI" not in badf:
            c.append("rfr-without-overtime")
        if all(abs((ch[f][0] or 0) - ch[f][1]) < 2 for f in badf):
            c.append("rounding-under-2-euros")
        causes[tuple(c) if c else ("other",)] += 1
    print(year, "n", n, "OpenFisca all-equal", n - bad, "(%.1f%%)" % (100 * (n - bad) / n), "| causes:", dict(causes.most_common()))
