"""Summarise runs/loop/scan_*.jsonl: notches (one euro that costs more than one euro) by cause, and sustained
abnormal marginal-rate zones (> 60 % over at least 200 €).
usage: loop_scan_report.py   -> runs/loop/scan_report.json (+ printed summary)"""
import json, os, collections

D = os.path.expanduser("~/fr/runs/loop")


def cause(n):
    mv = n["moved"]
    d = n["d_burden_per_euro"]
    if "IMPNET" in mv and mv["IMPNET"][0] >= 61 and mv["IMPNET"][1] == 0:
        return "tax falls under 61 € as income rises (art. 197 C rounding + art. 1657, 1 bis)"
    if "REVKIRE" in mv and (mv["REVKIRE"][1] - mv["REVKIRE"][0]) > 100 and "RNI" not in mv:
        return "art. 157 bis allowance cliff on the total income (art. 197 C)"
    if abs(d) <= 4 and not ("IMPNET" in mv and mv["IMPNET"][0] == 0) and not ("PSNET" in mv and mv["PSNET"][0] == 0):
        return "ordinary / rounding (|Δ| ≤ 4 €)"
    if "PSNET" in mv and mv["PSNET"][0] == 0 and mv["PSNET"][1] >= 61:
        return "social levies 61 € threshold (CSS L136-6, III)"
    if "RNI" in mv and "RNG" in mv and (mv["RNI"][1] - mv["RNI"][0]) - (mv["RNG"][1] - mv["RNG"][0]) > 100:
        return "art. 157 bis allowance cliff"
    if "IMPNET" in mv and mv["IMPNET"][0] <= 0 < mv["IMPNET"][1] and "IAVCR" in mv and mv["IAVCR"][1] >= 61 > mv["IAVCR"][0]:
        return "61 € collection threshold (art. 1657, 1 bis)"
    if "IMPNET" in mv and mv["IMPNET"][0] < 0 and "IAVCR" in mv:
        return "credits vs uncollected tax"
    if "CDHR" in mv:
        return "CDHR"
    if "NBPT" in mv:
        return "parts changed"
    return "other"


def main():
    notches = [json.loads(l) for l in open(f"{D}/scan_notches.jsonl")]
    ivs = [json.loads(l) for l in open(f"{D}/scan_intervals.jsonl")]
    by = collections.defaultdict(list)
    for n in notches:
        by[cause(n)].append(n)
    rep = {"n_notches": len(notches), "n_intervals": len(ivs), "causes": {}}
    for c, ns in sorted(by.items(), key=lambda kv: -len(kv[1])):
        top = max(ns, key=lambda n: n["d_burden_per_euro"])
        neg = min(ns, key=lambda n: n["d_burden_per_euro"])
        years = collections.Counter(n["year"] for n in ns)
        fams = collections.Counter(n["fam"] for n in ns)
        moves = collections.Counter(n["move"] for n in ns)
        rep["causes"][c] = {"n": len(ns), "max_d": top["d_burden_per_euro"], "max_example": top,
                            "min_d": neg["d_burden_per_euro"], "min_example": neg if neg["d_burden_per_euro"] < 0 else None,
                            "years": dict(years), "fams": dict(fams), "moves": dict(moves),
                            "max_by_year": {y: max(n["d_burden_per_euro"] for n in ns if n["year"] == y) for y in years}}
    # merge adjacent flagged intervals of one template (the scan splits them where the step rate crosses 100 %)
    ivs.sort(key=lambda z: (z["tid"], z["x_lo"]))
    merged = []
    for z in ivs:
        if merged and merged[-1]["tid"] == z["tid"] and merged[-1]["x_hi"] == z["x_lo"]:
            m = merged[-1]
            m["x_hi"] = z["x_hi"]; m["sum_db"] += z["sum_db"]; m["rmax"] = max(m["rmax"], z["rmax"])
            m["rmin"] = min(m["rmin"], z["rmin"])
        else:
            merged.append(dict(z))
    for m in merged:
        m["mean_rate"] = m["sum_db"] / (m["x_hi"] - m["x_lo"])
    ivs = merged
    # sustained zones: > 60 % over >= 1 000 €
    zones = [iv for iv in ivs if iv["x_hi"] - iv["x_lo"] >= 1000 and iv["mean_rate"] > 0.6]
    zc = collections.defaultdict(list)
    for z in zones:
        zc[(z["move"], z["bg"] if z["bg"].startswith("E") else "bg:" + z["bg"])].append(z)
    rep["zones"] = []
    for k, zs in sorted(zc.items()):
        best = max(zs, key=lambda z: z["mean_rate"])
        rep["zones"].append({"move": k[0], "bg": k[1], "n": len(zs), "max_mean_rate": round(best["mean_rate"], 4),
                             "example": {kk: best[kk] for kk in ("year", "fam", "bg", "spouse", "move", "x_lo", "x_hi", "mean_rate", "rmax")},
                             "rate_over_100": sum(1 for z in zs if z["mean_rate"] > 1.0)})
    # sustained > 100 %
    over = [iv for iv in ivs if iv["x_hi"] - iv["x_lo"] >= 1000 and iv["mean_rate"] > 1.0]
    rep["sustained_over_100"] = sorted(over, key=lambda z: -z["mean_rate"])[:20]
    json.dump(rep, open(f"{D}/scan_report.json", "w"), indent=1)
    for c, v in rep["causes"].items():
        print(f"{c:50s} n={v['n']:6d} max Δ/€={v['max_d']:8.0f} min={v['min_d']:6.0f} by year {v['max_by_year']}")
    print("zones (>60 % over >=200 €):")
    for z in rep["zones"]:
        print(" ", z["move"], z["bg"], z["n"], z["max_mean_rate"], z["rate_over_100"], z["example"])
    print("sustained >100 %:", len(over))
    for z in rep["sustained_over_100"][:10]:
        print(" ", z)


if __name__ == "__main__":
    main()
