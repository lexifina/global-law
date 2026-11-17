"""Withholding rates against the DGFiP production simulator's SAVED answers (no request is sent).

usage: pas_score_saved.py [LEAN_BINARY] [OUT_JSON]

1. Production set: runs/pas/prod_cases.jsonl (323 returns) with the answers in runs/pas/sim_prod.jsonl; M from
   runs/pas/prod/pas_m.jsonl (318 computed, 5 refused).
2. Saved pages: runs/pas/saved_pages.json, the rows matched back to their inputs (131). M is run on them with Mlang
   (local, `cal<year>`) into runs/pas/saved/ the first time; later runs reuse runs/pas/saved/pas_m.jsonl.

Lean is the binary given (default: the current build). Prints the household-rate and individualised-rate scores
and writes the per-return rows to OUT_JSON (default runs/pas/score_saved.json).
"""
import json, os, subprocess, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pas_run as P

H = os.path.expanduser("~/fr")
PD = f"{H}/runs/pas"
LEAN = sys.argv[1] if len(sys.argv) > 1 else P.LEAN
OUT = sys.argv[2] if len(sys.argv) > 2 else f"{PD}/score_saved.json"


def lean_run(cases):
    inp = "".join(f"{c['id']};{c['year']};" + ",".join(f"{k}={v}" for k, v in c["boxes"].items()) + "\n" for c in cases)
    out = subprocess.run([LEAN], input=inp, capture_output=True, text=True).stdout
    res = {}
    for line in out.splitlines():
        p = line.split(";")
        if p[0] != "ERR":
            res[p[0]] = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in p[1:] if "=" in kv}
    return res


eq = P.eq


def score(name, cases, sim, m):
    lean = lean_run(cases)
    st = collections.Counter()
    fam = collections.defaultdict(collections.Counter)
    rows = []
    for c in cases:
        s, lv, mv = sim.get(c["id"], {}), lean.get(c["id"], {}), m.get(c["id"])
        if "TXFOYER" not in s:
            continue
        f = c.get("family", "-")
        st["hh"] += 1
        fam[f]["n"] += 1
        lo = eq(lv.get("TXFOYER"), s["TXFOYER"])
        st["hh Lean = prod"] += lo
        fam[f]["Lean = prod"] += lo
        if mv is not None:
            st["hh M computed"] += 1
            st["hh M = prod"] += eq(mv.get("RASTXFOYER", 0), s["TXFOYER"])
        else:
            st["hh M refused"] += 1
            st["hh M refused, Lean = prod"] += lo
        row = {"id": c["id"], "year": c["year"], "family": f, "prod": s["TXFOYER"], "lean": lv.get("TXFOYER"),
               "lean61": lv.get("TXFOYER61"), "m": None if mv is None else mv.get("RASTXFOYER", 0),
               "PASII": lv.get("PASII"), "INDTAZ": None if mv is None else mv.get("INDTAZ")}
        if not lo:
            row["class"] = P.classify(lv, mv) if mv is not None and "TXFOYER" in lv else "M refused / Lean out of scope"
            st["class: " + row["class"]] += 1
        if "TXDEC1" in s:
            st["ind"] += 1
            st["ind Lean computes"] += "TXDEC1" in lv
            st["ind Lean = prod"] += all(eq(lv.get("TXDEC" + k), s["TXDEC" + k]) for k in "12")
            st["ind Lean S = prod"] += all(eq(lv.get("TXDEC" + k + "S"), s["TXDEC" + k]) for k in "12")
            if mv is not None:
                st["ind M = prod"] += all(eq(mv.get("RASTXDEC" + k, 0), s["TXDEC" + k]) for k in "12")
            row.update(prod_ind=[s["TXDEC1"], s["TXDEC2"]], lean_ind=[lv.get("TXDEC1"), lv.get("TXDEC2")],
                       leanS_ind=[lv.get("TXDEC1S"), lv.get("TXDEC2S")])
        rows.append(row)
    print(f"== {name}")
    for k in sorted(st):
        print(f"  {k}: {st[k]}")
    if any(f != "-" for f in fam):
        print("  by family (household rate, Lean = prod / n):")
        for f in sorted(fam):
            print(f"    {fam[f]['Lean = prod']}/{fam[f]['n']}  {f}")
    return {"stats": dict(st), "families": {f: dict(v) for f, v in fam.items()}, "rows": rows}


def main():
    res = {"lean": LEAN}
    # 1. production set
    cases = [json.loads(l) for l in open(f"{PD}/prod_cases.jsonl")]
    sim = {r["id"]: r["sim"] for r in map(json.loads, open(f"{PD}/sim_prod.jsonl"))}
    m = {}
    for l in open(f"{PD}/prod/pas_m.jsonl"):
        r = json.loads(l)
        m[r.pop("id")] = r
    res["production"] = score("production set (sim_prod.jsonl)", cases, sim, m)
    # 2. saved pages
    pages = [r for r in json.load(open(f"{PD}/saved_pages.json")) if r.get("matched")]
    cases = [{"id": r["id"], "year": r["year"], "boxes": r["boxes"]} for r in pages]
    sim = {r["id"]: r["sim"] for r in pages}
    mfile = f"{PD}/saved/pas_m.jsonl"
    if not os.path.exists(mfile):
        os.makedirs(f"{PD}/saved", exist_ok=True)
        m = P.run_m(cases, f"{PD}/saved/mwork", 12)
        with open(mfile, "w") as f:
            for k, v in m.items():
                f.write(json.dumps({"id": k, **v}) + "\n")
    m = {}
    for l in open(mfile):
        r = json.loads(l)
        m[r.pop("id")] = r
    print(f"saved pages matched: {len(pages)}, by year {dict(collections.Counter(r['year'] for r in pages))}")
    res["saved_pages"] = score("saved production pages (saved_pages.json, matched)", cases, sim, m)
    json.dump(res, open(OUT, "w"), indent=1)


if __name__ == "__main__":
    main()
