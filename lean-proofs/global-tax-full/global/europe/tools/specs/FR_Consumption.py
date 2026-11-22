S = dict(cc="FR", fam="Consumption", family_name="5111 TVA",
doc=r'''# France 2025: taxe sur la valeur ajoutée (5111); excises (CIBS) not reached

Sources: the CGI article copies kept by the French 1.x model (`fr/law/y2025/<article>.md`, each with a `.md.src`
naming the version's start date and the amending act; Légifrance itself is blocked from the build server and a second machine).
* **CGI art. 278**: "Le taux normal de la taxe sur la valeur ajoutée est fixé à 20 %" (version from 2014-01-01).
* **art. 278-0 bis**: 5,5 % "A. – Les livraisons portant sur : 1° Les denrées alimentaires destinées à la consommation
  humaine" (except confectionery, chocolate, margarine, caviar, "Les boissons alcooliques"); books.
* **art. 279**: 10 %: "a. ... la fourniture d'un hébergement dans le cadre du secteur hôtelier", restaurant meals
  (m), passenger transport (b quater).
* **art. 281 octies**: "2,10 % pour les livraisons portant sur les préparations magistrales, médicaments ... " (version
  2022-01-01); **art. 278 quater**: other medicines 10 %.
* **art. 293 B I** (version 2025-03-01, Loi n° 2025-127): franchise when the prior-year turnover does not exceed
  "85 000" (services: "37 500"), current year "93 500" / "41 250".
* Exemptions: art. 261 (medical care 4 1°, education 4 4°), 261 C (financial and insurance), 261 D (unfurnished
  residential letting).
Dating: the copies of arts. 278-0 bis and 279 are the versions from 2026-03-01 (Loi n° 2026-103); the 2025 versions
are not in the folder. Their rates (5,5 % and 10 %) are the 2025 rates but the item lists are read in the 2026
wording: grade B.
''',
vat=dict(name="Taxe sur la valeur ajoutée", standard=2000, reduced=1000, reduced2=550, superReduced=210, threshold=85000,
  statute="CGI art. 278 (20 %), 279 (10 %), 278-0 bis (5,5 %), 281 octies (2,1 %), 293 B (franchise 85 000 €); art. 261, 261 C, 261 D (exonérations)",
  classes={"food": "reduced2", "nonAlcoholic": "reduced2", "water": "reduced2", "books": "reduced2",
           "hotels": "reduced", "restaurants": "reduced", "transport": "reduced", "medicines": "superReduced",
           "health": "exempt", "education": "exempt", "financial": "exempt", "insurance": "exempt", "rent": "exempt"}),
notes=["FR 5111: CGI copies of the 1.x model (fr/law/y2025)"],
unsupported=[("g.consumption.any (fun s => s.good == .medicines)", "medicines at 2,1 % (reimbursable, art. 281 octies); non-reimbursable medicines are 10 % (art. 278 quater)"),
  ("g.consumption.any (fun s => s.good == .newspapers)", "press (2,1 %, art. 298 septies) not read: taken at 20 %"),
  ("g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .tobaccoOther || s.good == .beer || s.good == .wine || s.good == .spirits || s.good == .electricity || s.good == .gas)", "accises (code des impositions sur les biens et services) not reached: Légifrance blocked, CIBS not in the local copies")],
guards=["vat.embedded { good := .clothing, amount := 120 } == 20",
        "vat.embedded { good := .food, amount := 1055 } == 55",
        "vat.embedded { good := .restaurants, amount := 110 } == 10",
        "vat.embedded { good := .medicines, amount := 1021 } == 21",
        "vat.net { turnover := 85000, sales := [{ good := .other, net := 85000 }] } == 0",
        "vat.net { turnover := 85001, sales := [{ good := .other, net := 85001 }] } == 17000"],
taxes=[{"oecd": "5111", "tax": "Taxe sur la valeur ajoutée", "statute": "CGI art. 278, 278-0 bis, 278 quater, 279, 281 octies, 293 B", "dated": "CGI copies: 293 B version 2025-03-01; 278-0 bis and 279 read in their 2026-03-01 versions", "grade": "B", "kernel_parts": ["Vat"], "unsupported": ["2025 versions of arts. 278-0 bis, 279 not in the folder", "press 2,1 %", "current-year franchise limit 93 500 €"]},
 {"oecd": "5121", "tax": "Accises (énergies, tabacs, alcools)", "statute": "Code des impositions sur les biens et services (CIBS) L. 312-35, L. 313-19, L. 314-24 (titles from the code's structure)", "grade": "C", "status": "unsupported", "kernel_parts": [], "unsupported": ["Légifrance blocked from the build server and a second machine; CIBS not among the 1.x model's copies; would unlock: Wayback captures of the CIBS articles (LEGIARTI ids needed)"]}])

# ---- pass 3 (R1 Europe, 2026-11-21): excise sources searched again (still C) ----
for _t in S["taxes"]:
    if _t["oecd"] == "5121":
        _t["tried"] = ("CIBS Livre III via Wayback (captures 2024-12-04 and 2025-01-26, fr/law/cibs_livre3_wb*.html): L. 312-35 "
          "(LF 2024 art. 94, in force 2025) gives the carburant tariffs only per MWh (gazoles 59,40, essences 76,826 EUR/MWh); "
          "L. 312-25 leaves the per-litre conversion (energy content) to an arrêté; L. 314-24 tobacco table is the LF 2023 version; "
          "alcohol tariffs are the 2022 amounts before indexation. douane.gouv.fr professional pages (energie, alcools, tabac) hold no "
          "tariff tables (only Presentation-accise-fiscalite-pe.pdf, no amounts); Légifrance JORF returns 403 and its search is not reachable")
        _t["unsupported"] = ["would unlock: the JORF arrêté converting the L. 312-35 EUR/MWh tariffs into EUR/hl and the arrêtés publishing the 2025 indexed alcohol and tobacco tariffs (JORFTEXT ids, then Wayback), or the BOD circular on the 2025 tariffs"]

# ---- pass 16 (R1 Europe, 2026-11-21): year-in-force audit (tools/p16_rows.py, tools/yif16_rows.json) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p10_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p11_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p12_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p13_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p14_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p15_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p16_rows.py")).read())
p16_rows(S)
p6_finish(S)

# ---- gap pass (R1 Europe, 2026-11-21): gap-closing pass (tools/pgap_rows.py, tools/gap_rows.json) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p8_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p9_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p10_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p11_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p12_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p13_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p14_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p15_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p16_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p17_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p18_rows.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/pgap_rows.py")).read())
pgap_rows(S)
p6_finish(S)
