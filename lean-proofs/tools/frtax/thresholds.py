"""Benchmark: thresholds the DGFiP prints in the brochure (Tableau 4: first taxable income at which the cap on
the quotient familial applies; Tableau 6: taxable income from which tax is due; Tableau 7: from which tax of
61 euros or more is due). Each is the smallest taxable income R with a property; found by bisection with the
Lean model and with Mlang (cal) on the same household (R entered as net property income 4BA)."""
import json, os, re, subprocess, sys, tempfile, concurrent.futures as cf

LEAN = os.path.expanduser("~/fr/lean/.lake/build/bin/frtax")
BIN = os.path.expanduser("~/fr/bin")
BR = os.path.expanduser("~/fr/docs/brochure")


def kids(n):
    b = {}
    if n:
        b["0CF"] = n
        for i in range(n):
            b["0F%d" % i] = 2015
    return b


ROWS4 = {
    "T_no": ({"0AC": 1, "0BT": 1}, {2: 1, 2.5: 2, 3.5: 3, 4.5: 4, 5.5: 5}),
    "T_inv": ({"0AC": 1, "0BT": 1, "0AP": 1}, {2.5: 1, 3: 2, 4: 3, 5: 4, 6: 5}),
    "L": ({"0AC": 1, "0AL": 1}, {1.5: 0}),
    "Inv_single": ({"0AC": 1, "0AP": 1}, {1.5: 0}),
    "C_no": ({"0AC": 1}, {1.5: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6}),
    "C_inv": ({"0AC": 1, "0AP": 1}, {2: 1, 2.5: 2, 3.5: 3, 4.5: 4, 5.5: 5}),
    "V_no": ({"0AV": 1}, {2.5: 1, 3: 2, 4: 3, 5: 4, 6: 5}),
    "V_inv": ({"0AV": 1, "0AP": 1}, {3: 1, 3.5: 2, 4.5: 3, 5.5: 4}),
    "M_no": ({"0AM": 1, "0DB": 1980}, {2.5: 1, 3: 2, 4: 3, 5: 4, 6: 5}),
    "M_inv": ({"0AM": 1, "0DB": 1980, "0AP": 1}, {2.5: 0, 3: 1, 3.5: 2, 4.5: 3, 5.5: 4}),
}
ROWS67 = {"seule": ({"0AC": 1}, {1: 0, 1.5: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6}),
          "couple": ({"0AM": 1, "0DB": 1980}, {2.5: 1, 3: 2, 4: 3, 5: 4, 6: 5})}
COLS = [1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5, 5.5, 6]
LABELS4 = [("Sans invalide ou ancien combattant", "T_no"), ("1 invalide ou ancien combattant", "T_inv"),
           ("Parent isolé pendant 5 ans", "L"), ("Invalide ou ancien combattant", "Inv_single"),
           ("Sans invalide ou ancien combattant", "C_no"), ("1 invalide ou ancien combattant", "C_inv"),
           ("Sans invalide ou ancien combattant", "V_no"), ("1 invalide ou ancien combattant", "V_inv"),
           ("Sans invalide ou ancien combattant", "M_no"), ("1 invalide ou ancien combattant", "M_inv")]


def nums(line, after):
    rest = line.split(after, 1)[1] if after in line else line
    vals = re.findall(r"(\d{1,3} \d{3}|–|-)", rest)
    return [int(v.replace(" ", "")) if v[0].isdigit() else None for v in vals]


def parse(ed):
    lines = open("%s/%s/ch/21.txt" % (BR, ed), encoding="utf-8").read().split("\n")
    t4, idx = {}, 0
    for l in lines:
        if idx < len(LABELS4) and LABELS4[idx][0] in l:
            vals = nums(l, LABELS4[idx][0])
            t4[LABELS4[idx][1]] = {c: v for c, v in zip([1.5] + COLS[2:], vals) if v}
            idx += 1
    t67 = {}
    for tab in ("Tableau 6", "Tableau 7"):
        i = next(k for k, l in enumerate(lines) if tab in l)
        seule = next(l for l in lines[i:i + 8] if "personne seule" in l)
        couple = next(l for l in lines[i:i + 8] if "couple" in l)
        t67[tab] = {"seule": {c: v for c, v in zip(COLS, nums(seule, "seule")) if v},
                    "couple": {c: v for c, v in zip(COLS, nums(couple, "pacsé")) if v}}
    return t4, t67


def lean_eval(year, cases):
    inp = "".join("%s;%d;%s\n" % (cid, year, ",".join("%s=%s" % kv for kv in b.items())) for cid, b in cases)
    r = subprocess.run([LEAN], input=inp, capture_output=True, text=True)
    out = {}
    for l in r.stdout.splitlines():
        p = l.split(";")
        out[p[0]] = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in p[1:]}
    return out


MV = ["IDRS4", "IDRS", "IDRS2", "PLAFQF", "NBPT"]


def m_eval(year, cases):
    d = tempfile.mkdtemp()
    os.makedirs(d + "/in"); os.makedirs(d + "/out")
    files = []
    for cid, b in cases:
        p = "%s/in/%s.irj" % (d, cid)
        body = ["#NOM", cid, "#ENTREES-PRIMITIF", "REGCO/1"] + ["%s/%s" % kv for kv in b.items()]
        body += ["#CONTROLES-PRIMITIF", "#RESULTATS-PRIMITIF", "#ENTREES-CORRECTIF", "#CONTROLES-CORRECTIF",
                 "#RESULTATS-CORRECTIF", "##"]
        open(p, "w").write("\n".join(body) + "\n")
        files.append(p)
    chunks = [files[i:i + 40] for i in range(0, len(files), 40)]
    cal = "%s/cal%d" % (BIN, year)
    with cf.ThreadPoolExecutor(30) as ex:
        list(ex.map(lambda ch: subprocess.run([cal, "-completion", "-m", "p", "-a", str(year), "-dst", d + "/out"] + ch,
                                              capture_output=True), chunks))
    out = {}
    for cid, _ in cases:
        p = "%s/out/%s.irj" % (d, cid)
        v = {}
        if os.path.exists(p):
            sec = None
            for line in open(p):
                if line.startswith("#"):
                    sec = line.strip()
                    continue
                if sec == "#RESULTATS-PRIMITIF":
                    k = line.split("/")[0]
                    if k in MV:
                        v[k] = float(line.split("/")[1])
        out[cid] = v
    return out


def bisect(year, specs, pred_lean, pred_m, lo=0, hi=400000):
    res = {}
    for who, ev, pred in (("lean", lean_eval, pred_lean), ("m", m_eval, pred_m)):
        L = {k: lo for k in specs}
        H = {k: hi for k in specs}
        while any(L[k] < H[k] for k in specs):
            mids = {k: (L[k] + H[k]) // 2 for k in specs if L[k] < H[k]}
            keys = list(mids)
            out = ev(year, [("c%d" % i, dict(specs[k], **{"4BA": mids[k]})) for i, k in enumerate(keys)])
            for i, k in enumerate(keys):
                if pred(out.get("c%d" % i, {})):
                    H[k] = mids[k]
                else:
                    L[k] = mids[k] + 1
        for k in specs:
            res.setdefault(k, {})[who] = L[k] if L[k] < hi else None
    return res


def main():
    report = {}
    for ed, year in (("2025", 2024), ("2026", 2025)):
        t4, t67 = parse(ed)
        specs = {}
        for row, (base, m) in ROWS4.items():
            for parts, n in m.items():
                b = dict(base)
                b["0DA"] = 1966 if row == "L" else 1980
                b.update(kids(n))
                specs[(row, parts)] = b
        rA = bisect(year, specs, lambda o: o.get("IDRSCAP", 0) > o.get("IDRSFULL", 0),
                    lambda o: o.get("PLAFQF", 0) == 1)
        rB = bisect(year, specs, lambda o: o.get("IDRS", 0) > o.get("IDRSFULL", 0),
                    lambda o: o.get("PLAFQF", 0) == 1 and o.get("IDRS2", 0) - o.get("IDRS", 0) < 1000)
        rows = []
        for (row, parts) in specs:
            rows.append({"table": 4, "row": row, "parts": parts, "printed": t4.get(row, {}).get(parts),
                         "lean_A": rA[(row, parts)]["lean"], "m_A": rA[(row, parts)]["m"],
                         "lean_B": rB[(row, parts)]["lean"], "m_B": rB[(row, parts)]["m"]})
        for tab, thr in (("Tableau 6", 1), ("Tableau 7", 61)):
            specs = {}
            for row, (base, m) in ROWS67.items():
                for parts, n in m.items():
                    b = dict(base)
                    b["0DA"] = 1980
                    b.update(kids(n))
                    specs[(row, parts)] = b
            r = bisect(year, specs, lambda o, t=thr: o.get("IDRS4", 0) >= t, lambda o, t=thr: o.get("IDRS4", 0) >= t)
            for (row, parts) in specs:
                rows.append({"table": int(tab[-1]), "row": row, "parts": parts,
                             "printed": t67[tab][row].get(parts), "lean": r[(row, parts)]["lean"],
                             "m": r[(row, parts)]["m"]})
        report[ed] = rows
        print("== edition %s (income %d)" % (ed, year))
        for x in rows:
            print("  ", x)
    json.dump(report, open(sys.argv[1], "w"), default=str)


if __name__ == "__main__":
    main()
