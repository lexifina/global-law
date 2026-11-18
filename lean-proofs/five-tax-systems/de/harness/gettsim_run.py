#!/usr/bin/env python3
"""Run GETTSIM (1.3.x) on canonical households and print one JSON line per household.

gettsim_run.py households.jsonl > gettsim.jsonl

Mapping (the same assumptions as the Lean model, EXAMPLE.md):
* a married couple is jointly assessed; household-level amounts are split equally between two adults;
* children get both adults as parents; a single adult is entered as both parents of each child, so that she has two
  Kinderfreibeträge and the whole Kindergeld counts in the Günstigerprüfung (GETTSIM's documented way, see
  kinderfreibetrag.py "Users should overwrite this function if there are single parents ...");
* children 18-24 are "in_ausbildung"; the statutory pension is entered directly (`einnahmen__renten__gesetzliche_m`)
  with `jahr_renteneintritt` = the year the person turned 65 (at most 2025);
* pension contributions go to `beitrag_private_rentenversicherung_m` (Basisrente);
* nobody is privately insured; donations are not modelled by GETTSIM (the generator sets them to 0).
"""
import json, sys
import numpy as np
import gettsim
from gettsim import InputData, MainTarget, TTTargets

POLICY_DATE = "2025-07-01"

TARGETS = [
    "einkommensteuer__betrag_y_sn",
    "einkommensteuer__betrag_mit_kinderfreibetrag_y_sn",
    "einkommensteuer__betrag_ohne_kinderfreibetrag_y_sn",
    "einkommensteuer__zu_versteuerndes_einkommen_y_sn",
    "einkommensteuer__kinderfreibetrag_günstiger_sn",
    "einkommensteuer__abgeltungssteuer__betrag_y_sn",
    "einkommensteuer__einkünfte__gesamtbetrag_der_einkünfte_y_sn",
    "einkommensteuer__abzüge__vorsorgeaufwendungen_y_sn",
    "einkommensteuer__abzüge__betrag_y_sn",
    "einkommensteuer__gesamteinkommen_y_sn",
    "solidaritätszuschlag__betrag_y_sn",
    "kindergeld__betrag_m",
    "sozialversicherung__rente__beitrag__betrag_versicherter_m",
    "sozialversicherung__kranken__beitrag__betrag_versicherter_m",
    "sozialversicherung__pflege__beitrag__betrag_versicherter_m",
    "sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_m",
    "sn_id",
    "einkommensteuer__abzüge__altersfreibetrag_y",
    "einkommensteuer__abzüge__alleinerziehend_betrag_y",
    "einkommensteuer__abzüge__sonderausgaben_y_sn",
]

def tree_of(qnames):
    t = {}
    for q in qnames:
        parts = q.split("__")
        d = t
        for p in parts[:-1]:
            d = d.setdefault(p, {})
        d[parts[-1]] = None
    return t

def build(households):
    rows = []      # one dict per person
    owner = []     # (household index, role)
    pid = 0
    for hi, h in enumerate(households):
        adults = h["adults"]
        n = len(adults)
        ids = list(range(pid, pid + n))
        married = bool(h.get("married")) and n == 2
        kids = h.get("children", [])
        elig = sum(1 for k in kids if k["age"] < 25)
        cap = h.get("interest", 0) + h.get("dividends", 0) + h.get("capitalGains", 0)
        for j, a in enumerate(adults):
            age = int(a.get("age", 40))
            pension = a.get("pension", 0)
            se = a.get("selfEmployment", 0)
            wages = a.get("wages", 0)
            rows.append({
                "p_id": ids[j], "hh_id": hi, "alter": age, "geburtsjahr": 2025 - age, "geburtsmonat": 1,
                "familie__p_id_ehepartner": ids[1 - j] if married else -1,
                "familie__p_id_elternteil_1": -1, "familie__p_id_elternteil_2": -1,
                "familie__alleinerziehend": (n == 1 and any(k["age"] < 25 for k in kids)),
                "einkommensteuer__gemeinsam_veranlagt": married,
                "einnahmen__bruttolohn_m": wages / 12.0,
                "einnahmen__kapitalerträge_y": cap / n,
                "einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_y": float(se),
                "einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_y": h.get("rentalIncome", 0) / n,
                "einkommensteuer__einkünfte__ist_hauptberuflich_selbstständig": bool(se > 6420 and wages <= 6672 and pension <= 0),
                "einkommensteuer__abzüge__beitrag_private_rentenversicherung_m": h.get("pensionContributions", 0) / n / 12.0,
                "sozialversicherung__pflege__beitrag__hat_kinder": len(kids) > 0,
                "sozialversicherung__rente__bezieht_rente": pension > 0,
                "sozialversicherung__rente__jahr_renteneintritt": min(2025, 2025 - age + 65),
                "einnahmen__renten__gesetzliche_m": pension / 12.0,
                "kindergeld__in_ausbildung": False, "kindergeld__p_id_empfänger": -1,
                "arbeitsstunden_w": 40.0 if wages > 0 else 0.0,
                # single parent: both Freibeträge and the whole Kindergeld (overriding GETTSIM's per-parent count,
                # as its kinderfreibetrag.py asks users to do), without entering the child twice as her child
                "einkommensteuer__anzahl_kinderfreibeträge": (2 if n == 1 else 1) * elig,
                "einkommensteuer__relevantes_kindergeld_m": 255.0 * elig / (1 if n == 1 else 2),
            })
            owner.append((hi, "adult"))
        pid += n
        for k in kids:
            age = int(k["age"])
            rows.append({
                "p_id": pid, "hh_id": hi, "alter": age, "geburtsjahr": 2025 - age, "geburtsmonat": 1,
                "familie__p_id_ehepartner": -1,
                "familie__p_id_elternteil_1": ids[0], "familie__p_id_elternteil_2": ids[1] if n == 2 else -1,
                "familie__alleinerziehend": False, "einkommensteuer__gemeinsam_veranlagt": False,
                "einnahmen__bruttolohn_m": 0.0, "einnahmen__kapitalerträge_y": 0.0,
                "einkommensteuer__einkünfte__aus_selbstständiger_arbeit__betrag_y": 0.0,
                "einkommensteuer__einkünfte__aus_vermietung_und_verpachtung__betrag_y": 0.0,
                "einkommensteuer__einkünfte__ist_hauptberuflich_selbstständig": False,
                "einkommensteuer__abzüge__beitrag_private_rentenversicherung_m": 0.0,
                "sozialversicherung__pflege__beitrag__hat_kinder": False,
                "sozialversicherung__rente__bezieht_rente": False,
                "sozialversicherung__rente__jahr_renteneintritt": 2025,
                "einnahmen__renten__gesetzliche_m": 0.0,
                "kindergeld__in_ausbildung": 18 <= age < 25, "kindergeld__p_id_empfänger": ids[0],
                "arbeitsstunden_w": 0.0,
                "einkommensteuer__anzahl_kinderfreibeträge": 0, "einkommensteuer__relevantes_kindergeld_m": 0.0,
            })
            owner.append((hi, "child"))
            pid += 1
    return rows, owner

def main():
    households = [json.loads(l) for l in open(sys.argv[1]) if l.strip()]
    rows, owner = build(households)
    # the inputs GETTSIM asks for; everything we do not set is 0 / False / -1
    tmpl = gettsim.main(main_target=MainTarget.templates.input_data_dtypes.tree, policy_date_str=POLICY_DATE,
                        tt_targets=TTTargets(tree=tree_of(TARGETS)))
    flat = {}
    def walk(d, pre=""):
        for k, v in d.items():
            if isinstance(v, dict): walk(v, pre + k + "__")
            else: flat[pre + k] = str(v)
    walk(tmpl)
    cols = {}
    keys = set(flat) | set(rows[0].keys())
    for q in sorted(keys):
        vals = [r.get(q) for r in rows]
        dtype = flat.get(q, "")
        if all(v is not None for v in vals):
            cols[q] = np.array(vals)
        elif "Bool" in dtype:
            cols[q] = np.array([bool(v) if v is not None else False for v in vals])
        elif "Int" in dtype:
            cols[q] = np.array([int(v) if v is not None else (-1 if q.endswith("p_id") or "p_id_" in q else 0) for v in vals])
        else:
            cols[q] = np.array([float(v) if v is not None else 0.0 for v in vals])
    res = gettsim.main(main_target=MainTarget.results.df_with_nested_columns, policy_date_str=POLICY_DATE,
                       input_data=InputData.qname(cols), tt_targets=TTTargets(tree=tree_of(TARGETS)))
    df = res
    flatcols = {"__".join([c for c in col if isinstance(c, str) and c]): col for col in df.columns}
    def col(q):
        return df[flatcols[q]].to_numpy()
    sn = col("sn_id")
    out = [dict(id=h["id"], snSeen=set(), est=0.0, estMitKFB=0.0, estOhneKFB=0.0, zve=0.0, kfbGuenstiger=[],
                abgeltung=0.0, gde=0.0, vorsorge=0.0, abzuege=0.0, gesamteinkommen=0.0, soli=0.0, kindergeld=0.0,
                rv=0.0, kv=0.0, pv=0.0, av=0.0, alte=0.0, eab=0.0, sa=0.0) for h in households]
    V = {q: col(q) for q in TARGETS}
    for i, (hi, role) in enumerate(owner):
        o = out[hi]
        o["kindergeld"] += 12 * V["kindergeld__betrag_m"][i]
        if role != "adult":
            continue
        o["rv"] += 12 * V["sozialversicherung__rente__beitrag__betrag_versicherter_m"][i]
        o["kv"] += 12 * V["sozialversicherung__kranken__beitrag__betrag_versicherter_m"][i]
        o["pv"] += 12 * V["sozialversicherung__pflege__beitrag__betrag_versicherter_m"][i]
        o["av"] += 12 * V["sozialversicherung__arbeitslosen__beitrag__betrag_versicherter_m"][i]
        o["alte"] += V["einkommensteuer__abzüge__altersfreibetrag_y"][i]
        o["eab"] += V["einkommensteuer__abzüge__alleinerziehend_betrag_y"][i]
        if sn[i] in o["snSeen"]:
            continue
        o["snSeen"].add(sn[i])
        o["est"] += V["einkommensteuer__betrag_y_sn"][i]
        o["estMitKFB"] += V["einkommensteuer__betrag_mit_kinderfreibetrag_y_sn"][i]
        o["estOhneKFB"] += V["einkommensteuer__betrag_ohne_kinderfreibetrag_y_sn"][i]
        o["zve"] += V["einkommensteuer__zu_versteuerndes_einkommen_y_sn"][i]
        o["kfbGuenstiger"].append(bool(V["einkommensteuer__kinderfreibetrag_günstiger_sn"][i]))
        o["abgeltung"] += V["einkommensteuer__abgeltungssteuer__betrag_y_sn"][i]
        o["gde"] += V["einkommensteuer__einkünfte__gesamtbetrag_der_einkünfte_y_sn"][i]
        o["vorsorge"] += V["einkommensteuer__abzüge__vorsorgeaufwendungen_y_sn"][i]
        o["abzuege"] += V["einkommensteuer__abzüge__betrag_y_sn"][i]
        o["gesamteinkommen"] += V["einkommensteuer__gesamteinkommen_y_sn"][i]
        o["soli"] += V["solidaritätszuschlag__betrag_y_sn"][i]
        o["sa"] += V["einkommensteuer__abzüge__sonderausgaben_y_sn"][i]
    for o in out:
        o.pop("snSeen")
        for k, v in list(o.items()):
            if isinstance(v, (float, np.floating)):
                o[k] = round(float(v), 4)
        print(json.dumps(o, ensure_ascii=False))

if __name__ == "__main__":
    main()
