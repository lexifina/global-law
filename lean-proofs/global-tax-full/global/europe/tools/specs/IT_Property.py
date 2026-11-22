S = {'cc': 'IT', 'fam': 'Property', 'families': [], 'doc': "# IT 2025: Property family not reached (grade C)\n\n* 4400 Real-estate transfer and stamp duties (DPR 131/1986 Tariffa art. 1 (registro 9 %, 2 % prima casa)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)\n* 4100 Recurrent property tax (IMU (L. 160/2019 art. 1 c. 738 ff., Roma)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)\n", 'notes': [], 'unsupported': [('!g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate)', '4400 Real-estate transfer and stamp duties: not modelled (grade C: not read in the P5 pass)'), ('!g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate)', '4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)')], 'guards': [], 'taxes': [{'oecd': '4400', 'tax': 'Real-estate transfer and stamp duties', 'statute': 'DPR 131/1986 Tariffa art. 1 (registro 9 %, 2 % prima casa)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P5 pass', 'unsupported': ["would unlock: the act's 2025 rate articles (and the reference region's rate where regional)"]}, {'oecd': '4100', 'tax': 'Recurrent property tax', 'statute': 'IMU (L. 160/2019 art. 1 c. 738 ff., Roma)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P5 pass', 'unsupported': ["would unlock: the act and the reference municipality's 2025 rate (registry choice)"]}]}

# ---- pass 3 (R1 Europe, 2026-11-21): IMU, Roma 2025 ----
S["doc"] = S["doc"].split("\n* 4100")[0].replace("Property family not reached (grade C)", "IMU (4100), Roma") + r'''

## IMU, Roma 2025 (pass 3)
Sources (sha256 in `law/SHA256SUMS`, provenance in `law/ARCHIVE_INDEX.tsv`):
* **L. 27 dicembre 2019 n. 160, art. 1** (normattiva, vigente al 2025-07-01, commi 701-800:
  `it/law/l160_2019_art1_c701-800_vig20250701.html`): c. 740 "Il possesso dell'abitazione principale o assimilata
  ... non costituisce presupposto dell'imposta, salvo che si tratti di un'unità abitativa classificata nelle
  categorie catastali A/1, A/8 o A/9"; c. 745 base = "rendite risultanti in catasto, vigenti al 1° gennaio dell'anno
  di imposizione, rivalutate del 5 per cento ... i seguenti moltiplicatori: a) 160 per i fabbricati classificati nel
  gruppo catastale A e nelle categorie catastali C/2, C/6 e C/7, con esclusione della categoria catastale A/10 ...
  e) 65 per i fabbricati classificati nel gruppo catastale D"; c. 746 aree fabbricabili at the "valore venale in
  comune commercio"; c. 754 "aliquota di base è pari allo 0,86 per cento e i comuni ... possono aumentarla sino
  all'1,06 per cento"; c. 755 a further "0,08 per cento" where the commune kept the TASI maggiorazione.
* **Roma Capitale, Deliberazione dell'Assemblea Capitolina n. 182 del 19-12-2024**, Prospetto aliquote IMU 2025
  (MEF Dipartimento delle Finanze, Regolamenti e aliquote, anno 2025, cc H501, published 24-01-2025:
  `it/law/roma_imu_2025_delibera182.pdf`): "Abitazione principale di categoria catastale A/1, A/8 e A/9 e relative
  pertinenze 0,6%"; "Fabbricati appartenenti al gruppo catastale D (esclusa la categoria catastale D/10) 1,06%";
  "Aree fabbricabili 1,14%"; "Altri fabbricati (fabbricati diversi dall'abitazione principale e dai fabbricati
  appartenenti al gruppo catastale D) 1,14%"; "Terreni agricoli 1,06%".
Base: `home` is the abitazione principale (c. 740: not taxed; A/1, A/8, A/9 flagged); `realEstate` an "altro
fabbricato" of gruppo A (moltiplicatore 160, 1,14 %) on its rendita catastale (`annualValue`), or, without it, on
its `assessed` IMU value, else its market value; `land` an area fabbricabile at its market value (c. 746), 1,14 %.
Tax rounded down to whole euros.
'''
S["lean"] = (S.get("lean") or "") + r'''
/-- Delibera AC 182/2024 (prospetto 2025): altri fabbricati and aree fabbricabili 1,14 % (bp). -/
def aliquotaAltriRoma : Int := 114
/-- L. 160/2019 art. 1 c. 745: rendita rivalutata del 5 % x 160 (gruppo A); in euros, rounded down. -/
def valoreImu (rendita : Int) : Int := divR .down (pos rendita * 105 * 160) 100
/-- The IMU value of a building: from the rendita where given, else the assessed value, else market value. -/
def baseImu (a : Asset) : Int :=
  if a.kind == .land then pos a.value
  else if 0 ≤ a.annualValue then valoreImu a.annualValue else a.statutoryValue
def imuRoma (base : Int) : Int := divR .down (pos base * aliquotaAltriRoma) 10000
def imuCharges (as : List Asset) : List Charge :=
  (as.zipIdx.filter fun (a, _) => a.kind == .realEstate || a.kind == .land).map fun (a, i) =>
    charge .propertyRecurrent "IMU (Roma)" (baseImu a) (fun v => v) (fun v => imuRoma v)
      (event := s!"asset {i + 1}") (level := .local)
      (statute := "L. 160/2019 art. 1 c. 740, 745, 746, 754, 755; Delibera Assemblea Capitolina n. 182/2024 (1,14 %)")
'''
S["families"] = S.get("families", []) + [("4100 IMU (Roma)", [".propertyRecurrent"], "imuCharges g.assets")]
S["unsupported"] = [u for u in S["unsupported"] if not u[1].startswith("4100")] + [
  ("g.assets.any (fun a => a.kind == .home)", "4100 IMU: the abitazione principale is taken as not A/1, A/8, A/9 (c. 740, no tax); luxury categories (0,6 %, EUR 200 detrazione c. 749) need the category"),
  ("g.assets.any (fun a => a.kind == .realEstate && a.annualValue < 0)", "4100 IMU: no rendita catastale (annualValue) given: the assessed or market value stands in for the c. 745 value"),
  ("g.assets.any (fun a => a.kind == .realEstate)", "4100 IMU: realEstate taken as gruppo A (160, 1,14 %); gruppo D (65, 1,06 %), A/10, C/1 and the reduced Roma rates (canone concordato, comodato) not applied")]
S["notes"] = S.get("notes", []) + ["IT 4100: IMU L. 160/2019 vigente 2025-07-01; Roma prospetto aliquote 2025 (Delibera AC 182/2024)"]
S["guards"] = S.get("guards", []) + [
  "-- rendita 1 000: 1 000 x 1,05 x 160 = 168 000; x 1,14 % = 1 915,20",
  "valoreImu 1000 == 168000", "imuRoma (valoreImu 1000) == 1915",
  "-- area fabbricabile 100 000 (valore venale): 1 140",
  "imuRoma 100000 == 1140", "imuRoma 0 == 0"]
S["taxes"] = [t for t in S["taxes"] if t["oecd"] != "4100"] + [
 {"oecd": "4100", "tax": "Imposta municipale propria (IMU, Roma)", "statute": "L. 27 dicembre 2019 n. 160 art. 1 c. 740, 745, 746, 754, 755; Deliberazione Assemblea Capitolina n. 182 del 19.12.2024 (prospetto aliquote 2025)",
  "dated": "normattiva vigente al 2025-07-01; prospetto aliquote anno 2025 published by the MEF on 24.1.2025",
  "grade": "A", "kernel_parts": ["charge (rendita x 1,05 x moltiplicatore x aliquota)"],
  "unsupported": ["catastal category not in the input: realEstate taken as gruppo A, home as non-luxury abitazione principale", "rendita catastale is an input (asset.annualValue)", "reduced Roma rates and agevolazioni (c. 760 canone concordato 75 %, comodato 50 %)", "terreni agricoli"]}]
S["lean"] = S["lean"].replace("," + chr(10) + "  ", ", ")

# ---- pass 6 (R1 Europe, 2026-11-21): P5/P6 rows (tools/p6lib.py, tools/p6_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6_rows.py")).read())
p6_rows(S)
p6_finish(S)
