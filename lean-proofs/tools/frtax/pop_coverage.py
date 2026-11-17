"""Coverage of the published national data by the Lean model: which declared amounts and which reductions/credits
it reads, and how much of the published totals the rest represents.
usage: pop_coverage.py year  -> data/pop/coverage_<year>.json and printed tables"""
import json, os, sys
year = int(sys.argv[1])
H = os.path.expanduser("~/fr")
T = json.load(open(f"{H}/data/pop/targets_{year}.json"))
probe = json.load(open(f"{H}/data/pop/lean_boxes_{year}.json"))
lit = set(open(f"{H}/runs/pop/lean_boxes.txt").read().split())
SITU = {"0AC", "0AD", "0AV", "0AM", "0AO"}
modelled = {k for k, v in probe.items() if v} | (lit & set(probe)) | SITU | {"1CK", "1DK"}
# boxes that carry no taxable amount of their own (payments on account, informational, IFI, management codes)
INFO_PREFIX = ("8HV", "8HW", "8HX", "8IV", "8IW", "8IX", "8JV", "8KV", "8LV", "8MV", "9", "0", "R", "Z", "B")
INFO = {"2CK", "2BH", "2CG", "2DF", "2UU", "8UT", "3WG", "3WM", "3SG", "4BZ", "8TT", "8UU", "8VL"}
# declared income, by family: these are the published amounts that feed the tax base
INCOME = lambda k: k[0] in "12345" or k in ("8TK", "8TM", "8TV")

rows = []
for k, t in T["boxes"].items():
    if k in INFO or k.startswith(INFO_PREFIX):
        continue
    if t["n"] == t["amount"]:          # tick boxes
        continue
    rows.append({"box": k, "label": t["label"], "n": t["n"], "amount": t["amount"], "modelled": k in modelled,
                 "income": INCOME(k)})
inc = [r for r in rows if r["income"]]
tot = sum(r["amount"] for r in inc)
mod = sum(r["amount"] for r in inc if r["modelled"])
res = {"year": year, "income_boxes": len(inc), "income_amount": tot, "income_amount_modelled": mod,
       "income_boxes_modelled": sum(1 for r in inc if r["modelled"])}
fams = {}
for r in inc:
    f = r["box"][0] if r["box"][0] in "12345" else "8"
    a = fams.setdefault(f, [0.0, 0.0])
    a[0] += r["amount"]; a[1] += r["amount"] if r["modelled"] else 0
res["by_section"] = fams
res["top_unmodelled_income"] = sorted([r for r in inc if not r["modelled"]], key=lambda r: -r["amount"])[:30]
res["top_unmodelled_other"] = sorted([r for r in rows if not r["income"] and not r["modelled"]], key=lambda r: -r["amount"])[:25]
# reductions and credits: the DGFiP tables by device (hors PFO)
MOD_CI = {"CI EMPLOI SALARIE A DOMICILE", "CI FRAIS DE GARDE JEUNES ENFANTS", "CI COTISATIONS SYNDICALES",
          "CI IMPOT PAYE A L'ETRANGER SUR RCM, PLUS-VALUES ET AUTRES REVENUS"}
MOD_RI = {"DONS AUX OEUVRES", "DONS\xa0: PERSONNES EN DIFFICULTE", "DONS : PERSONNES EN DIFFICULTE", "ENFANTS SCOLARISES",
          "DEPENSES D'ACCUEIL DANS UN ETABLISSEMENT POUR PERSONNES DEPENDANTES", "DONS SAUVEGARDE DU PATRIMOINE RELIGIEUX",
          "DONS AIDE AUX VICTIME DE MAYOTTE"}
rici = {}
for kind, modset in (("CI", MOD_CI), ("RI", MOD_RI)):
    items = [(n, v.get("montants", 0.0), v.get("nombres", 0.0)) for n, v in T["ci_ri"].get(kind, {}).items()
             if "PRELEVEMENT FORFAITAIRE VERSE" not in n]
    rici[kind] = {"total": sum(a for _, a, _ in items), "modelled": sum(a for n, a, _ in items if n in modset),
                  "unmodelled_top": sorted([(n, a, c) for n, a, c in items if n not in modset], key=lambda x: -x[1])[:10]}
res["rici"] = rici
json.dump(res, open(f"{H}/data/pop/coverage_{year}.json", "w"), indent=1, ensure_ascii=False)
print(f"income {year}: {res['income_boxes_modelled']}/{res['income_boxes']} income boxes modelled; amount "
      f"{mod / 1e9:,.1f} of {tot / 1e9:,.1f} bn EUR ({100 * mod / tot:.1f} %)")
for f, (a, m) in sorted(fams.items()):
    print(f"  section {f}: {m / 1e9:,.1f} / {a / 1e9:,.1f} bn ({100 * m / max(a, 1):.1f} %)")
print("top unmodelled income boxes:")
for r in res["top_unmodelled_income"][:20]:
    print(f"  {r['box']} {r['n']:>10,.0f} {r['amount'] / 1e6:>10,.0f} M  {r['label'][:80]}")
for k, v in rici.items():
    print(f"{k}: modelled devices {v['modelled'] / 1e9:.2f} of {v['total'] / 1e9:.2f} bn ({100 * v['modelled'] / v['total']:.1f} %)")
    for n, a, c in v["unmodelled_top"][:8]:
        print(f"    {a / 1e6:>8,.0f} M  {c:>9,.0f}  {n}")
