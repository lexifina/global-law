"""Benchmark: the DGFiP's printed scale ("Barème de l'impôt", brochure pratique, chapter "Calcul de l'impôt").

For each edition (2025 = income 2024, 2026 = income 2025) parse every printed cell (situation, parts, taxable
income, tax after the cap and the décote), then:
  * Lean: the household path when a household reaches that situation and number of parts with nothing else
    (field IDRS4), and `tableTax` for every cell;
  * Mlang (cal): the same households (M variable IDRS4, "droits simples avant reductions"), with the taxable
    income entered as net property income (4BA), which no allowance touches.
usage: brochure_tables.py out.json
"""
import json, os, re, subprocess, sys, tempfile, collections

BR = os.path.expanduser("~/fr/docs/brochure")
LEAN = os.path.expanduser("~/fr/lean/.lake/build/bin/frtax")
BIN = os.path.expanduser("~/fr/bin")
SECTIONS = [  # header regex -> situation code
    (re.compile(r"ÉLEVÉ SEULES pendant au moins 5 ans \(case L\)"), 1),
    (re.compile(r"^PERSONNES SEULES\."), 0),
    (re.compile(r"^CÉLIBATAIRES OU DIVORCÉS élevant seuls"), 2),
    (re.compile(r"^VEUFS ayant au moins un enfant"), 3),
    (re.compile(r"^MARIÉS OU PACSÉS\s*$"), 4),
]

def parse(path):
    lines = open(path, encoding="utf-8", errors="replace").read().split("\n")
    start = next(i for i, l in enumerate(lines) if "BARÈME DE L’IMPÔT" in l)
    end = next((i for i, l in enumerate(lines) if "FICHE FACULTATIVE" in l), len(lines))
    sit, cols, cells = None, None, []
    for l in lines[start:end]:
        for rx, code in SECTIONS:
            if rx.search(l.strip()) or rx.search(l):
                sit, cols = code, ([1.5] if code == 1 else None)
        if sit is None:
            continue
        toks = l.split()
        if cols is None or (len(toks) >= 4 and all(re.fullmatch(r"\d(,\d+)?", t) for t in toks)):
            if len(toks) >= 4 and all(re.fullmatch(r"\d(,\d+)?", t) for t in toks):
                vals = [float(t.replace(",", ".")) for t in toks]
                half = len(vals) // 2 if len(vals) % 2 == 0 and vals[:len(vals)//2] == vals[len(vals)//2:] else len(vals)
                cols = vals[:half]
            continue
        nums = []
        for t in reversed(toks):
            if re.fullmatch(r"\d+", t):
                nums.append(int(t))
            else:
                break
        nums.reverse()
        k = len(cols) + 1
        if len(nums) < k or len(nums) % k:
            continue
        for g in range(0, len(nums), k):
            inc, taxes = nums[g], nums[g + 1:g + k]
            for c, t in zip(cols, taxes):
                cells.append({"sit": sit, "parts": c, "income": inc, "tax": t})
    return cells

def household(sit, parts):
    """Boxes giving exactly this situation and number of parts with no other effect, or None."""
    q = int(round(parts * 4))
    if sit == 1:
        return {"0AC": 1, "0DA": 1966, "0AL": 1} if q == 6 else None
    if sit == 4:
        base = {"0AM": 1, "0DA": 1980, "0DB": 1980}
        kids = {8: 0, 10: 1, 12: 2, 16: 3, 20: 4}.get(q)
    elif sit == 0:
        base = {"0AC": 1, "0DA": 1980}
        kids = {4: 0, 6: 1, 8: 2, 12: 3, 16: 4, 20: 5}.get(q)
    elif sit == 2:
        base = {"0AC": 1, "0DA": 1980, "0BT": 1}
        kids = {8: 1, 10: 2, 14: 3, 18: 4, 22: 5}.get(q)
    elif sit == 3:
        base = {"0AV": 1, "0DA": 1980}
        kids = {10: 1, 12: 2, 16: 3, 20: 4}.get(q)
    else:
        return None
    if kids is None:
        return None
    b = dict(base)
    if kids:
        b["0CF"] = kids
        for i in range(kids):
            b[f"0F{i}"] = 2015
    return b

def run_m(year, cases):
    d = tempfile.mkdtemp()
    os.makedirs(f"{d}/in"); os.makedirs(f"{d}/out")
    files = []
    for cid, boxes in cases:
        p = f"{d}/in/{cid}.irj"
        body = ["#NOM", cid, "#ENTREES-PRIMITIF", "REGCO/1"] + [f"{k}/{v}" for k, v in boxes.items()]
        body += ["#CONTROLES-PRIMITIF", "#RESULTATS-PRIMITIF", "#ENTREES-CORRECTIF", "#CONTROLES-CORRECTIF",
                 "#RESULTATS-CORRECTIF", "##"]
        open(p, "w").write("\n".join(body) + "\n")
        files.append(p)
    import concurrent.futures as cf
    chunks = [files[i:i + 200] for i in range(0, len(files), 200)]
    def go(ch):
        subprocess.run([f"{BIN}/cal{year}", "-completion", "-m", "p", "-a", str(year), "-dst", f"{d}/out"] + ch,
                       capture_output=True)
    with cf.ThreadPoolExecutor(30) as ex:
        list(ex.map(go, chunks))
    out = {}
    for cid, _ in cases:
        p = f"{d}/out/{cid}.irj"
        if os.path.exists(p):
            sec = None
            for line in open(p):
                if line.startswith("#"):
                    sec = line.strip(); continue
                if sec == "#RESULTATS-PRIMITIF" and line.startswith("IDRS4/"):
                    out[cid] = float(line.split("/")[1])
    return out

def run_lean(lines):
    r = subprocess.run([LEAN], input="".join(lines), capture_output=True, text=True)
    res = {}
    for l in r.stdout.splitlines():
        parts = l.split(";")
        res[parts[0]] = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in parts[1:] if "=" in kv}
    return res

def main():
    result = {}
    for ed, year in [("2025", 2024), ("2026", 2025)]:
        cells = parse(f"{BR}/{ed}/ch/21.txt")
        for i, c in enumerate(cells):
            c["id"] = f"b{ed}_{i}"
            c["boxes"] = household(c["sit"], c["parts"])
        lt = run_lean([f"T;{c['id']};{year};{c['sit']};{int(round(c['parts']*4))};{c['income']}\n" for c in cells])
        hh = [c for c in cells if c["boxes"] is not None]
        cases = [(c["id"], {**c["boxes"], "4BA": c["income"]}) for c in hh]
        lh = run_lean([f"{cid};{year};" + ",".join(f"{k}={v}" for k, v in b.items()) + "\n" for cid, b in cases])
        mm = run_m(year, cases)
        for c in cells:
            c["lean_table"] = lt.get(c["id"], {}).get("TAX")
            if c["boxes"] is not None:
                c["lean_household"] = lh.get(c["id"], {}).get("IDRS4")
                c["m"] = mm.get(c["id"])
        result[ed] = cells
        n = len(cells); nh = len(hh)
        ok_lt = sum(1 for c in cells if c["lean_table"] == c["tax"])
        ok_lh = sum(1 for c in hh if c["lean_household"] == c["tax"])
        ok_m = sum(1 for c in hh if c["m"] == c["tax"])
        print(f"edition {ed} (income {year}): {n} printed cells; Lean tableTax {ok_lt}/{n}; "
              f"household cells {nh}: Lean {ok_lh}/{nh}, Mlang {ok_m}/{nh}")
        bysit = collections.Counter((c["sit"], c["parts"]) for c in cells)
        print("   cells per (situation, parts):", dict(sorted(bysit.items())))
        bad = [c for c in cells if c["lean_table"] != c["tax"] or (c["boxes"] and (c.get("m") != c["tax"] or c.get("lean_household") != c["tax"]))]
        for c in bad[:25]:
            print("   DIFF", {k: c.get(k) for k in ("sit", "parts", "income", "tax", "lean_table", "lean_household", "m")})
    json.dump(result, open(sys.argv[1], "w"))

if __name__ == "__main__":
    main()
