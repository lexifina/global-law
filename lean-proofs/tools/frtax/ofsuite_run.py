"""Step 3: run the converted OpenFisca-France tests through Mlang (cal<year>) and the Lean model, and score every
program (OpenFisca itself included) against each test's stated value.

usage: ofsuite_run.py cases.jsonl results.jsonl > scoreboard.txt
A figure is equal when within max(test margin, 1 €) (M and Lean round to the euro, OpenFisca does not);
parts must match to 0.01.
"""
import collections, json, os, re, subprocess, sys, tempfile
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from of_calc_tests import in_lean_scope

LEAN = os.path.expanduser("~/fr/lean/.lake/build/bin/frtax")
BIN = os.path.expanduser("~/fr/bin")
OUT = {  # same table as ofsuite_convert.OUT (kept here so this script does not need OpenFisca)
    "nbptr": ("NBPT", "NBPT", None), "rni": ("RNI", "RNI", None), "rbg": ("RBG1", None, None),
    "rfr": ("REVKIRE", "REVKIRE", None), "ir_plaf_qf": ("IDRS3", "IDRS", None),
    "decote_gain_fiscal": ("IDEC", "IDEC", None), "ip_net": ("IDRS4", "IDRS4", None),
    "iaidrdi": ("IAD11", "IAIDRDI", None), "reductions": ("ITRED_NET", "ITRED", None), "iai": ("IAN_REP", "IAVCR", None),
    "impot_revenu_restant_a_payer": ("IRN_TOT", "IMPNET_TOT", "neg"),
    "contribution_exceptionnelle_hauts_revenus": ("CHRAPRES", "CHRAPRES", "abs"),
    "prelevement_forfaitaire_unique_ir": (None, None, "abs"), "ir_taux_marginal": ("TXMARJ", None, "pct"),
}
MVARS = sorted({m for m, _, _ in OUT.values() if m and m.isupper() and "_" not in m} | {"IDRS2", "IRE", "IINET", "RNG", "IDRS", "CITOT", "IAVIM",
                                                  "PSNET", "CDHR", "TXMOYIMP", "ITRED", "IAN", "IRN", "AVFISCOPTER", "IPREP", "CHRAPRES"})


def run_m(year, cases):
    cal = f"{BIN}/cal{year}"
    d = tempfile.mkdtemp(prefix="ofsuite_")
    os.makedirs(d + "/o")
    files, names = [], {}
    for k, (cid, boxes) in enumerate(cases):
        n = f"c{k}"
        names[n] = cid
        body = ["#NOM", n, "#ENTREES-PRIMITIF", "REGCO/1", f"ANREV/{year}"] + [f"{b}/{v}" for b, v in boxes.items()]
        body += ["#CONTROLES-PRIMITIF", "#RESULTATS-PRIMITIF", "#ENTREES-CORRECTIF", "#CONTROLES-CORRECTIF",
                 "#RESULTATS-CORRECTIF", "##"]
        open(f"{d}/{n}.irj", "w").write("\n".join(body) + "\n")
        files.append(f"{d}/{n}.irj")
    r = subprocess.run([cal, "-completion", "-m", "p", "-a", str(year), "-dst", d + "/o"] + files,
                       capture_output=True, text=True)
    ko = {}
    for block in r.stdout.split("traitement du fichier ")[1:]:
        m = re.search(r"ATRT000 \| KO \| (\S+)", block)
        if m:
            ko[block.split('"')[1].rsplit("/", 1)[-1][:-4]] = m.group(1)
    out = {}
    for n, cid in names.items():
        p = f"{d}/o/{n}.irj"
        vals = {}
        if os.path.exists(p) and n not in ko:
            for line in open(p):
                if "/" in line:
                    k, v = line.strip().split("/", 1)
                    if k in MVARS and k not in vals:
                        try:
                            vals[k] = float(v)
                        except ValueError:
                            pass
        if not vals.get("NBPT"):
            vals = {"_refused": ko.get(n, "no parts")}
        if "_refused" not in vals:
            g = lambda k: vals.get(k, 0.0)
            # M figures defined as OpenFisca defines them: reductions net of the global-cap clawback (art. 200-0 A),
            # tax before credits with recaptured reductions (8TF, IPREP) added, amount payable with CEHR and CDHR
            vals["ITRED_NET"] = g("ITRED") - g("AVFISCOPTER")
            vals["IAN_REP"] = g("IAN") + g("IPREP")
            vals["IRN_TOT"] = g("IRN") + g("CHRAPRES") + g("CDHR")
        out[cid] = vals
    return out


def run_lean(year, cases):
    inp = "".join(f"{cid};{year};" + ",".join(f"{k}={v}" for k, v in b.items()) + "\n" for cid, b in cases)
    r = subprocess.run([LEAN], input=inp, capture_output=True, text=True)
    out = {}
    for l in r.stdout.splitlines():
        p = l.split(";")
        if p[0] != "ERR":
            d = {kv.split("=")[0]: float(kv.split("=")[1]) for kv in p[1:] if "=" in kv}
            d["IAIDRDI"] = max(0.0, d["IDRS4"] - d["ITRED"])
            d["IMPNET_TOT"] = d["IMPNET"] + d.get("CHRAPRES", 0) + d.get("CDHR", 0)
            out[p[0]] = d
    return out


def program_value(name, who, got):
    mk, lk, how = OUT[name]
    key = mk if who == "M" else lk
    if key is None or got is None or "_refused" in got:
        return None
    v = got.get(key)
    if v is None:
        return 0.0 if who == "M" else None  # M omits variables that are zero
    return v


def stated_as_program(name, want):
    how = OUT[name][2]
    if how == "neg":
        return -want
    if how == "abs":
        return abs(want)
    if how == "pct":
        return round(want * 100, 4)
    return want


def ok(name, a, b, margin):
    if a is None or b is None:
        return None
    if name == "nbptr":
        return abs(a - b) < 0.01
    return abs(a - b) <= max(margin or 0, 1.0) + 1e-6


def main():
    cases = [json.loads(l) for l in open(sys.argv[1])]
    byyear = collections.defaultdict(list)
    for c in cases:
        byyear[c["year"]].append(c)
    for year, cs in sorted(byyear.items()):
        m = run_m(year, [(c["id"], c["boxes"]) for c in cs])
        lin = [(c["id"], c["boxes"]) for c in cs if year >= 2020 and in_lean_scope(c["boxes"])]
        l = run_lean(year, lin) if lin else {}
        for c in cs:
            c["m"] = m.get(c["id"])
            c["lean"] = l.get(c["id"])
            c["lean_scope"] = year >= 2020 and in_lean_scope(c["boxes"])
            c["lean_out_boxes"] = sorted(k for k in c["boxes"] if not in_lean_scope({k: 1}))
    tab = collections.defaultdict(collections.Counter)
    for c in cases:
        figs = {}
        for name, want in c["expected"].items():
            sw = stated_as_program(name, want)
            mv = program_value(name, "M", c["m"])
            lv = program_value(name, "Lean", c["lean"]) if c["lean"] else None
            ov = c["of"].get(name)
            figs[name] = {"stated": want, "stated_as_M": sw, "OpenFisca": ov,
                          "M": mv, "Lean": lv,
                          "ok_OpenFisca": ok(name, ov, want, c["margin"]), "ok_M": ok(name, mv, sw, c["margin"]),
                          "ok_Lean": ok(name, lv, sw, c["margin"])}
        c["figures"] = figs
        verdict = {}
        for who in ("OpenFisca", "M", "Lean"):
            oks = [f[f"ok_{who}"] for f in figs.values() if f[f"ok_{who}"] is not None]
            if who == "M" and c["m"] and "_refused" in c["m"]:
                verdict[who] = "refused"
            elif who == "Lean" and not c["lean_scope"]:
                verdict[who] = "out of scope" if c["year"] >= 2020 else "n/a (year)"
            elif not oks:
                verdict[who] = "no comparable figure"
            else:
                verdict[who] = "equal" if all(oks) else "differs"
        c["verdict"] = verdict
        band = "2019 (supplement)" if c["year"] == 2019 else "2020-2025"
        for who, v in verdict.items():
            tab[(band, who)][v] += 1
            tab[(band, who)]["tests"] += 1
    with open(sys.argv[2], "w") as f:
        for c in cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print("scoreboard: tests per program (a test is equal when every comparable stated figure is reproduced)")
    for key in sorted(tab):
        print(f"  {key[0]:18s} {key[1]:10s} " + "  ".join(f"{k} {v}" for k, v in sorted(tab[key].items())))
    print("\nfigures by output variable (equal/compared): ")
    fv = collections.defaultdict(collections.Counter)
    for c in cases:
        if c["year"] < 2020:
            continue
        for name, f in c["figures"].items():
            for who in ("OpenFisca", "M", "Lean"):
                if f[f"ok_{who}"] is not None:
                    fv[name][who + "_n"] += 1
                    fv[name][who + "_ok"] += f[f"ok_{who}"]
    for name, cnt in fv.items():
        print(f"  {name:42s} " + "  ".join(f"{w} {cnt[w + '_ok']}/{cnt[w + '_n']}" for w in ("OpenFisca", "M", "Lean")))
    print("\ntests where a program differs from the stated value or M differs from Lean (2020-2025, then 2019):")
    for c in sorted(cases, key=lambda c: (c["year"] < 2020, c["id"])):
        v = c["verdict"]
        mlean = any(f["M"] is not None and f["Lean"] is not None and abs(f["M"] - f["Lean"]) > 0.5
                    for f in c["figures"].values())
        if "differs" in v.values() or v["M"] == "refused" or mlean:
            bad = {n: {k: f[k] for k in ("stated", "OpenFisca", "M", "Lean")} for n, f in c["figures"].items()
                   if any(f[f"ok_{w}"] is False for w in ("OpenFisca", "M", "Lean"))
                   or (f["M"] is not None and f["Lean"] is not None and abs(f["M"] - f["Lean"]) > 0.5)}
            print(f"  {c['id']} {c['year']} {c['tier']} {v} {c['m'].get('_refused', '') if c['m'] else ''}")
            print(f"      boxes {c['boxes']}")
            print(f"      {bad}")


if __name__ == "__main__":
    main()
