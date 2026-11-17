"""Four-way: the DGFiP's production simulator as arbiter, against Mlang (published M code), Lean and OpenFisca-France.

usage: sim_compare2.py sim.jsonl cases.jsonl run_dir [openfisca.json] > report.txt
run_dir holds m.jsonl and cal.log from run.py; cases M refused are scored as "refused".
Writes run_dir/sim_verdicts.json (one row per case).
"""
import collections, json, os, re, subprocess, sys

LEAN = os.path.expanduser("~/fr/lean/.lake/build/bin/frtax")
sim = {}
for l in open(sys.argv[1]):
    d = json.loads(l)
    sim[d["id"]] = d["sim"]
cases = {(c := json.loads(l))["id"]: c for l in open(sys.argv[2])}
run = sys.argv[3]
m = {(d := json.loads(l))["id"]: d for l in open(f"{run}/m.jsonl")}
mrej = {}
for block in open(f"{run}/cal.log").read().split("traitement du fichier ")[1:]:
    ko = re.search(r"ATRT000 \| KO \| (\S+)", block)
    if ko:
        mrej[block.split('"')[1][:-4]] = ko.group(1)
of = {}
if len(sys.argv) > 4:
    for yd in json.load(open(sys.argv[4]))["years"].values():
        for r in yd["rows"]:
            of[r["id"]] = dict(r["of"], of_irn=r["of_irn"])

ids = [i for i in cases if i in sim]
inp = "".join(f"{i};{cases[i]['year']};" + ",".join(f"{k}={v}" for k, v in cases[i]["boxes"].items()) + "\n" for i in ids)
lean = {}
for l in subprocess.run([LEAN], input=inp, capture_output=True, text=True).stdout.splitlines():
    p = l.split(";")
    lean[p[0]] = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in p[1:]}


def g(d, k):
    v = d.get(k) if d else None
    return None if v is None else float(v)


def defi(d, rni, rng):
    a, b = g(d, rni), g(d, rng)
    return -b if a == 0 and b is not None and b < 0 else a


def ab(v):
    return None if v is None else abs(v)


def fields(s, mv, lv, ov):
    """simulator figure -> values from M, Lean, OpenFisca (None: that program does not give it)."""
    def tax(irn, ce, cd):  # production's "Impôt sur le revenu net" includes the CEHR and the CDHR
        return None if irn is None else irn + (ce or 0) + (cd or 0)

    def pay(irn, ce, cd, ps):  # M's IRN and Lean's IMPNET already apply the 61 € test (art. 1657, 1 bis);
        t = tax(irn, ce, cd)  # a balance under 12 € is not collected either (art. 1657, 1)
        return None if t is None else (0 if 0 < t < 12 else t) + (ps or 0)

    def sub(a, b):
        return None if a is None else a - (b or 0)
    return {
        "parts": (g(s, "NBPT"), g(mv, "NBPT"), g(lv, "NBPT"), g(ov, "nbptr")),
        "RFR": (g(s, "REVKIRE"), g(mv, "REVKIRE"), g(lv, "REVKIRE"), g(ov, "rfr")),
        # "Revenu net imposable ou déficit à reporter": a deficit is printed as a positive amount
        "taxable income": (g(s, "RNI"), defi(mv, "RNI", "RNG"), defi(lv, "RNI", "RNG"), defi(ov, "rni", "rng")),
        "gross tax": (g(s, "IDRS"), g(mv, "IDRS2"), g(lv, "IDRSCAP"), None),
        "décote": (s.get("IDEC", 0.0), g(mv, "IDEC"), g(lv, "IDEC"), g(ov, "decote")),
        "reductions": (s.get("ITRED", 0.0), g(mv, "ITRED"), g(lv, "ITRED"), None),
        "flat taxes": (s.get("PROP", 0.0), g(mv, "IPROP") or (0.0 if mv else None), g(lv, "PFU"), None),
        # pages from before the label fix lack the CEHR line: scored only where production printed it
        "CEHR": (s.get("CEHR"), g(mv, "CHRAPRES") or (0.0 if mv else None), g(lv, "CHRAPRES"),
                 g(ov, "contribution_exceptionnelle_hauts_revenus")),
        # production prints the net tax before the collection thresholds: M IAN − IRE, Lean IAVCR − CITOT
        "net income tax": (ab(g(s, "IRNET")), ab(tax(sub(g(mv, "IAN"), g(mv, "IRE")), g(mv, "CHRAPRES"), g(mv, "CDHR"))),
                           ab(tax(sub(g(lv, "IAVCR"), g(lv, "CITOT")), g(lv, "CHRAPRES"), g(lv, "CDHR"))),
                           ab(tax(g(ov, "of_irn"), g(ov, "contribution_exceptionnelle_hauts_revenus"),
                                  -(g(ov, "contribution_differentielle_hauts_revenus") or 0)))),
        "amount payable": ((s.get("PAYER") or 0) - (s.get("REMB") or 0) if "PAYER" in s else None,
                           pay(g(mv, "IRN"), g(mv, "CHRAPRES"), g(mv, "CDHR"), g(mv, "PSNET")),
                           pay(g(lv, "IMPNET"), g(lv, "CHRAPRES"), g(lv, "CDHR"), g(lv, "PSNET")), None),
    }


WHO = ("M", "Lean", "OpenFisca")
tot = collections.defaultdict(collections.Counter)
bytag = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
verdicts = []
for i in ids:
    c, s = cases[i], sim[i]
    tag = c.get("tag", "")
    mv, lv, ov = m.get(i), lean.get(i), of.get(i)
    prod_refused = "_error" in s
    row = {"id": i, "year": c["year"], "tag": tag, "boxes": c["boxes"], "sim": s,
           "m_refused": mrej.get(i) if mv is None else None}
    if prod_refused:
        row["verdict"] = {"production": "refused", "M": "refused" if mv is None else "computed",
                          "Lean": "computed", "OpenFisca": "computed" if ov else "n/a"}
        tot["refusals"]["production refused; M refused" if mv is None else "production refused; M computed"] += 1
        verdicts.append(row)
        continue
    if mv is None:
        tot["refusals"]["production computed; M refused"] += 1
    allok = {w: True for w in WHO}
    have = {w: False for w in WHO}
    diffs = {}
    for name, (sv, *vals) in fields(s, mv, lv, ov).items():
        if sv is None:
            continue
        for w, v in zip(WHO, vals):
            if v is None:
                if w == "M" and mv is None:
                    allok[w] = False
                continue
            have[w] = True
            ok = abs(sv - v) < 0.5
            tot[name][w + "_ok"] += ok
            tot[name][w + "_n"] += 1
            allok[w] &= ok
            if not ok:
                diffs.setdefault(name, {"production": sv})[w] = v
    row["diffs"] = diffs
    row["verdict"] = {w: ("refused" if w == "M" and mv is None else
                          "n/a" if not have[w] else "equal" if allok[w] else "differs") for w in WHO}
    for w in WHO:
        tot["every figure"][f"{w}_{row['verdict'][w]}"] += 1
        bytag[tag.split(" ")[0] if tag.startswith(("M refuses", "edge")) else tag][w][row["verdict"][w]] += 1
    verdicts.append(row)

n = len(ids)
print(f"cases answered by the simulator: {n}")
for k, v in tot["refusals"].items():
    print(f"  {k}: {v}")
print("every figure equal to production (cases each program computed):")
for w in WHO:
    e = tot["every figure"]
    print(f"  {w:10s} equal {e[w + '_equal']}  differs {e[w + '_differs']}  refused {e[w + '_refused']}  n/a {e[w + '_n/a']}")
print("by figure (equal / compared):")
for name, cnt in tot.items():
    if name in ("refusals", "every figure"):
        continue
    print(f"  {name:16s} " + "  ".join(f"{w} {cnt[w + '_ok']}/{cnt[w + '_n']}" for w in WHO if cnt[w + "_n"]))
print("by case family (verdicts):")
for tag in sorted(bytag):
    print(f"  {tag:34s} " + " | ".join(f"{w}: " + ", ".join(f"{k} {v}" for k, v in sorted(bytag[tag][w].items()))
                                        for w in WHO))
json.dump(verdicts, open(f"{run}/sim_verdicts.json", "w"), indent=0, ensure_ascii=False)
