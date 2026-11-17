"""EUROMOD (JRC; model J2.0+, FR country model, CC BY 4.0 rules; engine EUPL-1.2 via the `euromod` Python connector on
.NET 8, run on Linux through pythonnet/coreclr): its income-tax policy tin_fr checked against Lean's scale-table mode.

EUROMOD works on survey-style person records (gross monthly incomes; it computes contributions, the 10 % allowance,
etc. itself), not on 2042 boxes, so returns cannot be mapped one to one. What is tested instead is the tax computation
proper: for every fiscal unit of the FR training data (2,397 synthetic households shipped with the model) run systems
FR_2021 .. FR_2025, take EUROMOD's own taxable income il_rniy (x 12), its number of parts tinqt_s and family situation,
and compare its tax after the QF cap and the décote (tingt_s x 12, before reductions) with Lean's `tableTax` for that
situation, parts and taxable income (harness/bareme_all.py's T mode), for the matching income year.
EUROMOD system FR_Y carries the scale of income year Y-1 (FR_2024: décote 873, the income-2023 figure).

usage: DOTNET_ROOT=... PYTHONNET_RUNTIME=coreclr refs/impl/euromod/venv/bin/python impl_euromod.py
writes runs/impl/euromod/{rows.jsonl,report.txt}
"""
import collections, json, math, os, subprocess, sys, time
import pandas as pd

FR = os.path.expanduser("~/fr")
M = f"{FR}/refs/impl/euromod/m/EUROMOD_RELEASES_J2.0+"
LEAN = f"{FR}/lean/.lake/build/bin/frtax"
OUT = f"{FR}/runs/impl/euromod"
os.makedirs(OUT, exist_ok=True)
r = lambda x: math.floor(x + 0.5)


def main():
    from euromod import Model
    mod = Model(M)
    fr = mod.countries["FR"]
    data = pd.read_csv(M + "/Input/FR_training_data.txt", sep="\t")
    rows, timing = [], {}
    for sy in range(2021, 2026):
        t0 = time.time()
        o = fr.systems[f"FR_{sy}"].run(data, "FR_training_data").outputs[0]
        timing[sy] = time.time() - t0
        head = "tu_fiscalunit_fr_HeadID"
        for hid, g in o.groupby(head):
            h = g[g.idperson == hid]
            if h.empty:
                continue
            h = h.iloc[0]
            kids = int(g["tu_fiscalunit_fr_IsDepChild"].sum())
            adults = len(g) - kids
            sit = 4 if adults >= 2 else (3 if h.dms == 5 and kids else (2 if kids else 0))
            rni = 12 * float(g["il_rniy"].sum())  # income lists are per person; SchedCalc sums Base over the unit
            rows.append({"id": f"e{sy}_{int(hid)}", "system": sy, "year": sy - 1, "sit": sit, "kids": kids,
                         "dms": int(h.dms), "parts": float(h.tinqt_s), "rni": rni,
                         "tax": 12 * float(g["tingt_s"].sum()), "decote": 12 * float(g["sin02_s"].sum()) if "sin02_s" in g else 0.0,
                         "cap": 12 * float(g["tintalm_s"].sum()) if "tintalm_s" in g else 0.0, "capy": 12 * float(g["il_capy"].sum())})
    inp = "".join(f"T;{x['id']};{x['year']};{x['sit']};{int(round(x['parts'] * 4))};{max(0, r(x['rni']))}\n" for x in rows)
    lean = {}
    for l in subprocess.run([LEAN], input=inp, capture_output=True, text=True).stdout.splitlines():
        p = l.split(";")
        lean[p[0]] = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in p[1:] if "=" in kv}
    st = collections.Counter()
    with open(f"{OUT}/rows.jsonl", "w") as f:
        for x in rows:
            x["lean_tax"] = lean.get(x["id"], {}).get("TAX")
            if x["lean_tax"] is None:
                st["no Lean answer (situation/parts combination)"] += 1
            else:
                d = r(x["tax"]) - x["lean_tax"]
                x["gap"] = d
                pos = x["rni"] > 0
                st[(x["system"], "n")] += 1
                st[(x["system"], "eq")] += d == 0
                st[(x["system"], "le2")] += abs(d) <= 2
                st[(x["system"], "taxed_n")] += x["lean_tax"] > 0 or x["tax"] > 0.5
                st[(x["system"], "taxed_eq")] += (x["lean_tax"] > 0 or x["tax"] > 0.5) and d == 0
            f.write(json.dumps(x) + "\n")
    rep = [f"EUROMOD J2.0+ FR training data ({data.idhh.nunique()} households), engine seconds per system "
           + ", ".join(f"FR_{k}: {v:.1f}" for k, v in timing.items())]
    for sy in range(2021, 2026):
        rep.append(f"  FR_{sy} (income {sy - 1}): fiscal units {st[(sy, 'n')]}; tax after cap and décote = Lean tableTax "
                   f"{st[(sy, 'eq')]} ({100 * st[(sy, 'eq')] / max(1, st[(sy, 'n')]):.1f} %), within 2 EUR {st[(sy, 'le2')]}; "
                   f"units with tax > 0: {st[(sy, 'taxed_eq')]}/{st[(sy, 'taxed_n')]} equal")
    rep.append(f"  {st['no Lean answer (situation/parts combination)']} units without a Lean answer")
    open(f"{OUT}/report.txt", "w").write("\n".join(rep) + "\n")
    print("\n".join(rep))


if __name__ == "__main__":
    main()
