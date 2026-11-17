"""Head to head: run one other implementation on every benchmark, restricted to its scope, and score it against
the printed/stated figures, Lean and M (IMPLEMENTATIONS.md).

usage: impl_score.py <adapter module, e.g. impl_publicodes> [benchmarks: bareme,examples,random,bound,sim]
Writes runs/impl/<KEY>/<benchmark>.json (summary, timing) and <benchmark>_dis.jsonl (every disagreement).
"""
import importlib, json, os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import impl_common as C


def scope(ad, c):
    return ad.in_scope(c["boxes"], c["year"]) if getattr(ad, "SCOPE_BY_YEAR", False) else ad.in_scope(c["boxes"])


def main():
    ad = importlib.import_module(sys.argv[1])
    which = (sys.argv[2] if len(sys.argv) > 2 else "bareme,examples,random,bound,sim").split(",")
    out_dir = f"{C.FR}/runs/impl/{ad.KEY}"
    os.makedirs(out_dir, exist_ok=True)
    report = [f"== {ad.NAME} ({time.strftime('%Y-%m-%d %H:%M')})"]
    for bench in which:
        t0 = time.time()
        if bench == "bareme":
            allc = C.bareme_cases()
            cases = [c for c in allc if c["boxes"] is not None and c["year"] in ad.YEARS and scope(ad, c)]
            refs, fields = ("expected",), ["IDRS4"]
            note = f"{len(allc)} printed cells, {sum(c['boxes'] is not None for c in allc)} with a household"
        elif bench == "examples":
            allc = C.example_cases()
            cases = [c for c in allc if c["year"] in ad.YEARS and scope(ad, c)
                     and any(f in c["expected"] for f in ad.FIELDS)]
            lean = C.run_lean(cases)
            m, ko = C.run_m(cases)
            for c in cases:
                c["lean"], c["m"] = lean.get(c["id"]), m.get(c["id"])
            refs, fields = ("expected", "lean", "m"), ad.FIELDS
            note = f"{len(allc)} examples with boxes and figures for 2020-2025"
        elif bench == "random":
            allc = C.random_cases("final") + C.random_cases("old")
            allc = [c for c in allc if c["year"] in ad.YEARS]
            C.fill_boxes(allc)
            cases = [c for c in allc if scope(ad, c)]
            refs, fields = ("lean", "m"), ad.FIELDS
            note = f"{len(allc)} random returns accepted by M in the implementation's years"
        elif bench == "bound":
            allc = [c for c in C.bound_cases() if c["year"] in ad.YEARS]
            cases = [c for c in allc if scope(ad, c)]
            lean = C.run_lean(cases)
            m, ko = C.run_m(cases)
            for c in cases:
                c["lean"], c["m"] = lean.get(c["id"]), m.get(c["id"])
            refs, fields = ("lean", "m"), ad.FIELDS
            note = f"{len(allc)} statutory-edge returns"
        elif bench == "sim":
            allc = [c for c in C.sim_cases() if c["year"] in ad.YEARS]
            cases = [c for c in allc if scope(ad, c)]
            refused = [c for c in cases if c["expected"] is None]
            cases = [c for c in cases if c["expected"] is not None]
            lean = C.run_lean(cases)
            m, ko = C.run_m(cases)
            for c in cases:
                c["lean"], c["m"] = lean.get(c["id"]), m.get(c["id"])
            refs, fields = ("expected", "lean", "m"), ad.FIELDS
            note = (f"{len(allc)} saved production answers in the implementation's years "
                    f"({len(refused)} in scope that production refused, left out)")
        else:
            raise SystemExit("unknown benchmark " + bench)
        t1 = time.time()
        res, us = ad.run(cases) if cases else ({}, 0.0)
        t2 = time.time()
        rows = [{**c, "impl": res.get(c["id"], {})} for c in cases]
        missing = sum(1 for r in rows if not r["impl"] or r["impl"].get("_error"))
        s, dis = C.score(rows, fields, refs)
        per_hh = (us / len(cases)) if cases else 0
        summ = {"benchmark": bench, "note": note, "in_scope": len(cases), "pool": len(allc), "no_answer": missing,
                "summary": s, "engine_us_per_household": per_hh, "wall_s": t2 - t1, "prep_s": t1 - t0}
        json.dump(summ, open(f"{out_dir}/{bench}.json", "w"), indent=1)
        with open(f"{out_dir}/{bench}_dis.jsonl", "w") as f:
            for d in dis:
                f.write(json.dumps(d, ensure_ascii=False) + "\n")
        with open(f"{out_dir}/{bench}_rows.jsonl", "w") as f:
            for r in rows:
                f.write(json.dumps({k: r.get(k) for k in ("id", "year", "boxes", "impl", "lean", "m", "expected")},
                                   ensure_ascii=False) + "\n")
        report.append(f"[{bench}] {note}; in scope {len(cases)}; no answer {missing}; "
                      f"engine {per_hh:.0f} us/household; wall {t2 - t1:.1f}s")
        report.append(C.fmt_summary(ad.KEY, s, fields))
        print("\n".join(report[-2:]), flush=True)
    open(f"{out_dir}/report.txt", "a").write("\n".join(report) + "\n")


if __name__ == "__main__":
    main()
