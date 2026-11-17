"""Steps 3b/3c: returns in the 2042 box format through Catala, Mlang and Lean, on the ground they share.

usage: catala_compare.py cases.jsonl|irj-dir[,irj-dir...] outdir [years=2022,2023] [limit]

For each return of income 2022 or 2023:
  full       the return as generated: parts (NBPT) from Catala, M and Lean (Lean only when the return is inside its
             scope; M may refuse);
  projected  the return reduced to the boxes Catala's interface reads (salaries, pensions, annuities, BIC, BNC,
             family boxes, birth years): revenu brut global from Catala (sum of its three category scopes, less
             professional deficits), M (RBG1) and Lean (RNG: no charges are left, so RNG = RBG), and the category nets
             against M (salaries/pensions/annuities TSPR; BIC BIN + BICNPF; BNC BNN + BNCIF).
Writes outdir/rows.jsonl (every program's figures) and outdir/summary.json.
"""
import collections, json, os, sys, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from catala_lib import run_catala, run_lean, run_m, mget, load_irj
from of_calc_tests import in_lean_scope


def load(spec, years, limit):
    cases = []
    for part in spec.split(","):
        if os.path.isdir(part):
            for y in years:
                for p in sorted(glob.glob(f"{part}/in{y}/*.irj")):
                    cases.append(load_irj(p))
        else:
            for l in open(part):
                c = json.loads(l)
                if "boxes" in c and c.get("year") in years:
                    cases.append({"id": c["id"], "year": c["year"], "boxes": c["boxes"]})
    cases = [c for c in cases if c["year"] in years]
    return cases[:limit] if limit else cases


def eq(a, b, tol=0.5):
    return a is not None and b is not None and abs(a - b) <= tol


def main():
    spec, outdir = sys.argv[1], sys.argv[2]
    years = [int(y) for y in (sys.argv[3] if len(sys.argv) > 3 else "2022,2023").split(",")]
    limit = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    os.makedirs(outdir, exist_ok=True)
    cases = load(spec, years, limit)
    print("returns", len(cases), collections.Counter(c["year"] for c in cases), flush=True)
    cat_full = run_catala(cases)
    proj = []
    for c in cases:
        ign = set((cat_full.get(c["id"], {}).get("IGNORED") or "").split(",")) - {""}
        proj.append({"id": c["id"], "year": c["year"], "boxes": {k: v for k, v in c["boxes"].items() if k not in ign},
                     "dropped": sorted(ign)})
    cat_proj = run_catala(proj)
    m_full, m_proj = {}, {}
    for y in years:
        m_full.update(run_m(y, [c for c in cases if c["year"] == y]))
        m_proj.update(run_m(y, [c for c in proj if c["year"] == y]))
    lean_full = run_lean([c for c in cases if in_lean_scope(c["boxes"])])
    lean_proj = run_lean([c for c in proj if in_lean_scope(c["boxes"])])
    stats = collections.Counter()
    with open(f"{outdir}/rows.jsonl", "w") as f:
        for c, p in zip(cases, proj):
            i = c["id"]
            cf, cp, mf, mp = cat_full.get(i, {}), cat_proj.get(i, {}), m_full.get(i), m_proj.get(i)
            lf, lp = lean_full.get(i), lean_proj.get(i)
            row = {"id": i, "year": c["year"], "boxes": c["boxes"], "dropped": p["dropped"],
                   "catala": cf, "catala_proj": cp, "m": mf, "m_proj": mp, "lean": lf, "lean_proj": lp}
            f.write(json.dumps(row) + "\n")
            stats["n"] += 1
            stats["in_catala_scope"] += not p["dropped"]
            stats["catala_err"] += "ERR" in cf
            stats["m_refused_full"] += mf is None or "_refused" in mf
            stats["m_refused_proj"] += mp is None or "_refused" in mp
            stats["lean_scope_full"] += lf is not None
            stats["lean_scope_proj"] += lp is not None
            # parts on the full return
            cn, mn, ln = cf.get("NBPT"), mget(mf, "NBPT"), (lf or {}).get("NBPT")
            if cn is not None and mn is not None:
                stats["nbpt_cm_n"] += 1
                stats["nbpt_cm_eq"] += eq(cn, mn, 0.01)
            if cn is not None and ln is not None:
                stats["nbpt_cl_n"] += 1
                stats["nbpt_cl_eq"] += eq(cn, ln, 0.01)
            if mn is not None and ln is not None:
                stats["nbpt_lm_n"] += 1
                stats["nbpt_lm_eq"] += eq(mn, ln, 0.01)
            # revenu brut global on the projected return
            cr, mr, lr = cp.get("RBG"), mget(mp, "RBG1"), (lp or {}).get("RNG")
            if cr is not None and mr is not None:
                stats["rbg_cm_n"] += 1
                stats["rbg_cm_eq"] += eq(cr, mr)
                # category nets
                ts_c = cp["TS_RBG"] - cp["TS_DEF"]
                stats["ts_cm_eq"] += eq(ts_c, mget(mp, "TSPR"))
                bic_c = cp["BIC_RBG"] - cp["BIC_DEFPRO"]
                stats["bic_cm_eq"] += eq(bic_c, mget(mp, "BIN") + mget(mp, "BICNPF")) if mget(mp, "BIN") is not None else 0
                bnc_c = cp["BNC_RBG"] - cp["BNC_DEFPRO"]
                stats["bnc_cm_eq"] += eq(bnc_c, mget(mp, "BNN") + mget(mp, "BNCIF")) if mget(mp, "BNN") is not None else 0
            if cr is not None and lr is not None:
                stats["rbg_cl_n"] += 1
                stats["rbg_cl_eq"] += eq(cr, lr)
            if mr is not None and lr is not None:
                stats["rbg_lm_n"] += 1
                stats["rbg_lm_eq"] += eq(mr, lr)
    json.dump(dict(stats), open(f"{outdir}/summary.json", "w"), indent=1)
    print(json.dumps(dict(stats), indent=1))


if __name__ == "__main__":
    main()
