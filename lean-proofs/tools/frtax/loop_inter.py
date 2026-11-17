"""Loophole hunt, steps 2b-2d: interactions and choice pairs.

  cdhr     the 2025 CDHR (art. 224) against reductions, credits and the scale option (2OP)
  f2       CEHR proration with flat-levy micro income (FINDINGS F2): what M/production charge vs the statute
  divorce  married vs separated parents (box T, shared residence)
  choices  random plausible households (harness/gen.py), every legal toggle the boxes allow
usage: loop_inter.py [parts...]     writes runs/loop/inter_<part>.json
"""
import json, os, sys, random, collections, statistics
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import loop_lib as L

OUT = os.path.expanduser("~/fr/runs/loop")


def both(cases, mcheck=True):
    lo = L.lean(cases)
    m, ko = (L.mlang(cases) if mcheck else ({}, {}))
    return lo, m, ko


def cdhr():
    y = 2025
    cs, meta = [], []
    addons = {"base": {}, "gift7UF_10000": {"7UF": 10000}, "aid7UQ_2000": {"7UQ": 2000},
              "homehelp_12000": {"7DB": 12000}, "childcare_3500": {"7GA": 3500}, "school_lycee": {"7EC": 1},
              "carehome_10000": {"7CD": 10000}, "2OP": {"2OP": 1}, "per_10000": {"6NS": 10000, "APS": 35000, "DPS": 0, "CPS": 0, "BPS": 0}}
    for fam in ("single", "couple"):
        for S in (0, 30000, 100000):
            for D in range(200000, 1500001, 20000):
                for name, extra in addons.items():
                    if fam == "single":
                        b = L.single(y, **{"2DC": D, "2BH": D})
                        if S:
                            b["1AJ"] = S
                    else:
                        b = L.couple(y, **{"2DC": D, "2BH": D})
                        if S:
                            b["1AJ"] = S
                    if name in ("childcare_3500", "school_lycee"):
                        L.kids(b, y, nf=1, ages=(3,) if name == "childcare_3500" else (16,))
                    b.update(extra)
                    cid = f"c{len(cs)}"
                    cs.append((cid, y, b)); meta.append((fam, S, D, name))
    lo = L.lean(cs)
    random.seed(3)
    sample = random.sample(range(len(cs)), 900)
    m, ko = L.mlang([cs[i] for i in sample])
    agree = sum(1 for i in sample if cs[i][0] in m and abs(L.burden(cs[i][2], lo[cs[i][0]]) - L.m_burden(cs[i][2], m[cs[i][0]])) < 0.5)
    comp = sum(1 for i in sample if cs[i][0] in m)
    # index
    B = {}
    for (cid, _, b), k in zip(cs, meta):
        B[k] = (L.burden(b, lo[cid]), lo[cid], b, cid)
    nominal = {"gift7UF_10000": 6600, "aid7UQ_2000": 1500, "homehelp_12000": 6000, "childcare_3500": 1750,
               "school_lycee": 153, "carehome_10000": 2500}
    res = {"m_sample": comp, "m_agree": agree, "by": {}}
    for fam in ("single", "couple"):
        for S in (0, 30000, 100000):
            rows = []
            for D in range(200000, 1500001, 20000):
                base = B[(fam, S, D, "base")]
                row = {"D": D, "cdhr_base": base[1]["CDHR"], "burden": base[0]}
                for name in addons:
                    if name == "base":
                        continue
                    row[name] = base[0] - B[(fam, S, D, name)][0]   # saving
                rows.append(row)
            res["by"][f"{fam}/S{S}"] = rows
    # examples for M/production
    ex = []
    for k in [("single", 30000, 300000, "base"), ("single", 30000, 300000, "homehelp_12000"),
              ("single", 30000, 300000, "gift7UF_10000"), ("single", 30000, 300000, "2OP"),
              ("couple", 30000, 600000, "base"), ("couple", 30000, 600000, "2OP")]:
        ex.append({"key": k, "boxes": B[k][2], "lean": B[k][1], "burden": B[k][0]})
    m2, _ = L.mlang([(f"x{i}", y, e["boxes"]) for i, e in enumerate(ex)])
    for i, e in enumerate(ex):
        e["m"] = m2.get(f"x{i}"); e["m_burden"] = L.m_burden(e["boxes"], e["m"]) if e["m"] else None
    res["examples"] = ex
    return res


def f2():
    cs, meta = [], []
    for y in (2020, 2021, 2022, 2023, 2024, 2025):
        for fam in ("single", "couple"):
            for S in (300000, 400000, 600000, 1000000, 2000000):
                if fam == "couple":
                    S *= 2
                for box in ("5TE", "5TB"):
                    for X in (0, 1000, 10000, 30000, 50000, 77700):
                        b = L.single(y, **{"1AJ": S}) if fam == "single" else L.couple(y, **{"1AJ": S // 2, "1BJ": S // 2})
                        if X:
                            b[box] = X
                        cs.append((f"f{len(cs)}", y, b)); meta.append((y, fam, S, box, X))
    lo = L.lean(cs)
    m, ko = L.mlang(cs)
    rows = []
    for (cid, y, b), k in zip(cs, meta):
        if cid not in m:
            continue
        l, mm = lo[cid], m[cid]
        rows.append({"year": k[0], "fam": k[1], "S": k[2], "box": k[3], "X": k[4],
                     "lean_cehr": l["CHRAPRES"], "m_cehr": mm.get("CHRAPRES"), "lean_cdhr": l["CDHR"], "m_cdhr": mm.get("CDHR"),
                     "lean_burden": L.burden(b, l), "m_burden": L.m_burden(b, mm),
                     "rfr": l["REVKIRE"], "m_rfr": mm.get("REVKIRE"), "lean_irn": l["IMPNET"], "m_irn": mm.get("IRN")})
    return {"rows": rows, "refused": dict(collections.Counter(ko.values()))}


def divorce():
    cs, meta = [], []
    for y in (2024, 2025):
        for nk in (1, 2, 3):
            for a in range(10000, 200001, 5000):
                for b_ in range(0, a + 1, 5000):
                    C = L.kids(L.couple(y, **{"1AJ": a, **({"1BJ": b_} if b_ else {})}), y, nf=nk)
                    def p(inc, **kw):
                        d = {"0AD": 1, "0DA": 1980, **kw}
                        if inc:
                            d["1AJ"] = inc
                        return d
                    opts = {"married": [C],
                            "shared_T": [L.kids(p(a, **{"0BT": 1}), y, nh=nk), L.kids(p(b_, **{"0BT": 1}), y, nh=nk)],
                            "all_with_a_T": [L.kids(p(a, **{"0BT": 1}), y, nf=nk), p(b_)],
                            "all_with_b_T": [p(a), L.kids(p(b_, **{"0BT": 1}), y, nf=nk)]}
                    for o, rets in opts.items():
                        for j, r in enumerate(rets):
                            cs.append((f"d{len(cs)}", y, r)); meta.append((y, nk, a, b_, o, j))
    lo = L.lean(cs)
    tot = collections.defaultdict(float)
    for (cid, _, b), k in zip(cs, meta):
        tot[k[:5]] += L.burden(b, lo[cid])
    res = {}
    for y in (2024, 2025):
        for nk in (1, 2, 3):
            best = []
            for a in range(10000, 200001, 5000):
                for b_ in range(0, a + 1, 5000):
                    mar = tot[(y, nk, a, b_, "married")]
                    sep = {o: tot[(y, nk, a, b_, o)] for o in ("shared_T", "all_with_a_T", "all_with_b_T")}
                    o = min(sep, key=sep.get)
                    best.append((mar - sep[o], a, b_, o))
            best.sort(reverse=True)
            res[f"{y}/kids{nk}"] = {"max_separation_saving": best[:3], "n_sep_better": sum(1 for x in best if x[0] > 0),
                                    "n": len(best), "at": [x for x in best if (x[1], x[2]) in ((40000, 20000), (60000, 30000), (100000, 50000), (200000, 0))]}
    # M on the 2025, 2-children examples
    sel = [(cid, y, b) for (cid, y, b), k in zip(cs, meta) if k[0] == 2025 and k[1] == 2 and (k[2], k[3]) in ((60000, 30000), (100000, 50000))]
    m, ko = L.mlang(sel)
    res["m_check"] = {cid: [L.burden(b, lo[cid]), L.m_burden(b, m[cid]) if cid in m else ko.get(cid)] for cid, y, b in sel}
    return res


def choices(n=60000):
    import gen
    random.seed(11)
    hh = [gen.household(i, random.choice([2020, 2021, 2022, 2023, 2024, 2025])) for i in range(n)]
    cs, meta = [], []
    for h in hh:
        y, b = h["year"], h["boxes"]
        cs.append((h["id"] + "_d", y, b)); meta.append((h["id"], "default", 0))
        inv = any(k in b for k in ("2DC", "2TR", "2TS", "3VG", "2FU"))
        if inv:
            t = dict(b)
            if "2OP" in t:
                del t["2OP"]
            else:
                t["2OP"] = 1
            cs.append((h["id"] + "_op", y, t)); meta.append((h["id"], "toggle_2OP", 0))
        for w in ("A", "B"):
            if f"1{w}K" in b:
                t = dict(b); del t[f"1{w}K"]
                cs.append((h["id"] + f"_k{w}", y, t)); meta.append((h["id"], f"drop_1{w}K", 0))
        if b.get("0DJ", 0) > 0:
            t = dict(b); t["0DJ"] -= 1
            k = t["0DJ"]
            t.pop(f"0J{k}", None)
            if t["0DJ"] == 0:
                del t["0DJ"]
            att = {2020: 5959, 2021: 6042, 2022: 6368, 2023: 6674, 2024: 6794, 2025: 6855}[y]
            t["6EL"] = t.get("6EL", 0) + att
            if "7EF" in t:
                t["7EF"] -= 1
                if t["7EF"] <= 0:
                    del t["7EF"]
            single_parent = not ("0AM" in t or "0AO" in t)
            if single_parent and not (t.get("0CF") or t.get("0CH") or t.get("0DJ")):
                t.pop("0BT", None); t["0AL"] = 1
            cs.append((h["id"] + "_al", y, t)); meta.append((h["id"], "child_to_alimony", 0))
            cs.append((h["id"] + "_alc", y, L.single(y, born=y - 20, **{"1AO": att}))); meta.append((h["id"], "child_to_alimony", 1))
        for vl, mi in (("5TA", "5KO"), ("5TB", "5KP"), ("5TE", "5HQ")):
            if vl in b or mi in b:
                t = dict(b)
                if vl in b:
                    t[mi] = t.get(mi, 0) + t.pop(vl)
                    lab = "vl_to_micro"
                else:
                    t[vl] = t.pop(mi)
                    lab = "micro_to_vl"
                cs.append((h["id"] + "_" + vl, y, t)); meta.append((h["id"], lab, 0))
        if "0AM" in b or "0AO" in b:   # year of marriage / PACS: separate returns (art. 6, 5)
            s1 = {"0AC": 1, "0DA": b["0DA"]}; s2 = {"0AC": 1, "0DA": b.get("0DB", 1980)}
            # declarant 2's own boxes move to a return of their own; joint items (investment, property, charges,
            # gifts, children) stay with declarant 1 (no box T: they lived as a couple)
            M2 = {"1BJ": "1AJ", "1BP": "1AP", "1BA": "1AA", "1HB": "1GB", "1BF": "1AF", "1BG": "1AG", "1BS": "1AS",
                  "1BZ": "1AZ", "1BO": "1AO", "1BL": "1AL", "1BM": "1AM", "1BK": "1AK", "1HH": "1GH", "1BD": "1AD",
                  "1BV": "1AV", "5LO": "5KO", "5LP": "5KP", "5IQ": "5HQ", "5UA": "5TA", "5UB": "5TB", "5UE": "5TE",
                  "5LC": "5KC", "5RC": "5QC", "5IC": "5HC", "5OD": "5ND", "6NT": "6NS", "6RT": "6RS", "APT": "APS",
                  "DPT": "DPS", "CPT": "CPS", "BPT": "BPS", "7AE": "7AC", "0AF": "0AP"}
            for k, v in b.items():
                if k in ("0AM", "0AO", "0DA", "0DB", "6QR", "0AS"):
                    continue
                if k in M2:
                    s2[M2[k]] = v
                else:
                    s1[k] = v
            cs.append((h["id"] + "_s1", y, s1)); meta.append((h["id"], "separate_returns", 0))
            cs.append((h["id"] + "_s2", y, s2)); meta.append((h["id"], "separate_returns", 1))
    lo = L.lean(cs)
    tot = collections.defaultdict(float)
    ok = collections.defaultdict(lambda: True)
    for (cid, y, b), (hid, opt, j) in zip(cs, meta):
        if cid not in lo:
            ok[(hid, opt)] = False
            continue
        tot[(hid, opt)] += L.burden(b, lo[cid])
    gains = collections.defaultdict(list)
    for (hid, opt), v in tot.items():
        if opt == "default" or not ok[(hid, opt)]:
            continue
        gains[opt].append((tot[(hid, "default")] - v, hid))
    res = {}
    for opt, g in gains.items():
        vals = sorted(x for x, _ in g)
        pos = [x for x in vals if x > 0]
        res[opt] = {"n": len(vals), "n_better": len(pos), "share_better": round(len(pos) / len(vals), 4),
                    "median_gain_if_better": statistics.median(pos) if pos else 0,
                    "p90_gain_if_better": pos[int(0.9 * len(pos))] if pos else 0, "max_gain": vals[-1],
                    "median_cost_if_worse": statistics.median([-x for x in vals if x < 0]) if any(x < 0 for x in vals) else 0,
                    "top": sorted(g, reverse=True)[:3]}
    return res


PARTS = {"cdhr": cdhr, "f2": f2, "divorce": divorce, "choices": choices}
if __name__ == "__main__":
    for p in sys.argv[1:] or list(PARTS):
        r = PARTS[p]()
        json.dump(r, open(f"{OUT}/inter_{p}.json", "w"), indent=1, default=str)
        print(p, "done", flush=True)
