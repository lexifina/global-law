"""Published national targets for the population study (income 2023, 2024) -> data/pop/targets_<year>.json.
Sources (raw files under data/pop/raw, provenance in POPULATION.md):
  IRCOM national.xls (data.gouv.fr), ir-declarations-2042-nat.csv (data.economie.gouv.fr),
  DGFiP Statistiques n°32 / n°41 (impots.gouv.fr), IR tables nid_25518/25519/25520/25535/25536 (impots.gouv.fr)."""
import csv, json, os, re, sys
import xlrd, openpyxl
R = os.path.expanduser("~/fr/data/pop/raw")
IRCOM = {2023: "ircom-2024-revenus-2023/ircom_2024_revenus_2023/national/national.xls",
         2024: "ircom-2025-revenus-2024/ircom_2025_revenus_2024/national/national.xls"}

def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

def ircom(year):
    s = xlrd.open_workbook(f"{R}/{IRCOM[year]}").sheet_by_index(0)
    br = []
    for r in range(7, s.nrows):
        lab = str(s.cell_value(r, 1)).strip()
        if not lab or lab.startswith("Plus de 100 000"):
            continue
        vals = [num(s.cell_value(r, c)) for c in range(2, 11)]
        d = dict(zip(["n", "rfr_k", "tax_k", "n_taxed", "rfr_taxed_k", "n_sal", "sal_k", "n_pen", "pen_k"], vals))
        if lab == "Total":
            tot = d; continue
        if lab.startswith("Dont non"):
            dinr = d; continue
        if lab.startswith("*") or lab.startswith("n.c"):
            continue
        nums = [int(x.replace(" ", "")) for x in re.findall(r"\d[\d ]*", lab)]
        lo = 0 if nums[0] == 0 else nums[0] - 1
        hi = nums[1] if len(nums) > 1 else None
        d.update(label=lab, lo=lo, hi=hi)
        br.append(d)
    return {"brackets": br, "total": tot, "nonresidents": dinr}

def boxes(year):
    out = {}
    for r in csv.DictReader(open(f"{R}/ir-declarations-2042-nat.csv", encoding="utf-8-sig"), delimiter=";"):
        if r["annee"] == str(year):
            out[r["nom"]] = {"label": r["libelle"], "n": float(r["nombre"]), "amount": float(r["montant"])}
    return out

def sheet_rows(path, name):
    ws = openpyxl.load_workbook(path, data_only=True)[name]
    return [[v for v in row] for row in ws.iter_rows(values_only=True)]

def ci_ri(year):
    res = {}
    for kind, f in (("CI", "nid_25535_ir_ci_deciles_rfr_par_part.xlsx"), ("RI", "nid_25536_ir_ri_deciles_rfr_par_part.xlsx")):
        for what in ("nombres", "montants"):
            rows = sheet_rows(f"{R}/tables/{f}", f"{year} {what}")
            hdr = next(r for r in rows if r[0] and str(r[0]).startswith("Numéro"))
            tot = next(r for r in rows if r[0] and str(r[0]).strip().startswith("Total"))
            # the header says "en milliers" but the totals are in units (5 145 997 households, 6 507 342 253 EUR)
            unit_line = " ".join(str(x) for x in rows[0] + rows[1] if x)
            for name, v in zip(hdr[3:], tot[3:]):
                if name is None or num(v) is None:
                    continue
                res.setdefault(kind, {}).setdefault(str(name).strip(), {})[what] = num(v)
            res.setdefault("units", {})[f"{kind} {what}"] = unit_line[:200]
    return res

def marginal(year):
    rows = sheet_rows(f"{R}/tables/nid_25519_ir_taux_marginal.xlsx", str(year))
    out = []
    for r in rows:
        if r[1] is not None and num(r[1]) is not None and r[0] and ("rieur" in str(r[0])):
            out.append({"label": str(r[0]), "rate": round(num(r[1]), 2), "n_k": num(r[2]), "tax_M": num(r[4])})
        if r[0] == "TOTAL":
            vals = [num(x) for x in r[1:] if num(x) is not None]
            out.append({"label": "TOTAL", "n_k": vals[0], "tax_M": vals[2]})
    return out

def deciles(year):
    rows = sheet_rows(f"{R}/tables/nid_25518_ir_deciles_rfr_par_part.xlsx", f"a{year}")
    return [[x for x in r if x is not None] for r in rows if any(x is not None for x in r)]

BULLETIN = {  # national aggregates printed by DGFiP Statistiques (euros, households)
    2024: {"source": "DGFiP Statistiques n°41 (Nov 2025), 3e émission, provisional",
           "households": 41.5e6, "households_taxed": 19.6e6, "net_tax": 92e9,
           "tax_scale_before_rici": 98843486993, "tax_flat_hors_bareme": 10.32e9, "cehr": 1.98e9,
           "rici": 19525419691, "rici_n": 12829185.9, "ci": 9769885423, "ci_n": 8627410.88,
           "ri": 9753672745, "ri_n": 7532859.81, "ci_restituted": 2e9},
    2023: {"source": "DGFiP Statistiques n°32 (Apr 2025), data at February 2025",
           "households": 41.2e6, "households_taxed": 18.7e6, "net_tax": 83.5e9,
           "tax_scale_before_rici": 91772030093, "tax_flat_hors_bareme": 7602575235, "cehr": 1400481119,
           "rici": 17.8e9, "rici_n": 12.4e6, "ci": 9.0e9, "ci_n": 8.3e6, "ri": 8.7e9, "ri_n": 7.2e6},
}

if __name__ == "__main__":
    for year in (2023, 2024):
        t = {"year": year, "ircom": ircom(year), "boxes": boxes(year), "bulletin": BULLETIN[year],
             "ci_ri": ci_ri(year), "marginal": marginal(year), "deciles_raw": deciles(year)}
        json.dump(t, open(os.path.expanduser(f"~/fr/data/pop/targets_{year}.json"), "w"), ensure_ascii=False, indent=1)
        i = t["ircom"]
        print(year, "IRCOM households", i["total"]["n"], "tax k€", i["total"]["tax_k"], "taxed", i["total"]["n_taxed"],
              "brackets", len(i["brackets"]), "boxes", len(t["boxes"]), "TMI", t["marginal"][-1])
        print("  CI units:", t["ci_ri"]["units"])
        for k in ("CI", "RI"):
            print(" ", k, {n: v for n, v in list(t["ci_ri"][k].items())[:8]})
