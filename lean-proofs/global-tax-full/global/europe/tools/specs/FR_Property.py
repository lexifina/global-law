S = {'cc': 'FR', 'fam': 'Property', 'families': [], 'doc': "# FR 2025: Property family not reached (grade C)\n\n* 4400 Real-estate transfer and stamp duties (CGI art. 683, 1594 D (DMTO; 1594 D not among the local copies)): tried not read in the P5 pass; would unlock: the act's 2025 rate articles (and the reference region's rate where regional)\n* 4100 Recurrent property tax (CGI art. 1380 ff. (taxe foncière, Paris)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)\n", 'notes': [], 'unsupported': [('!g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate)', '4400 Real-estate transfer and stamp duties: not modelled (grade C: not read in the P5 pass)'), ('!g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate)', '4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)')], 'guards': [], 'taxes': [{'oecd': '4400', 'tax': 'Real-estate transfer and stamp duties', 'statute': 'CGI art. 683, 1594 D (DMTO; 1594 D not among the local copies)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P5 pass', 'unsupported': ["would unlock: the act's 2025 rate articles (and the reference region's rate where regional)"]}, {'oecd': '4100', 'tax': 'Recurrent property tax', 'statute': 'CGI art. 1380 ff. (taxe foncière, Paris)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P5 pass', 'unsupported': ["would unlock: the act and the reference municipality's 2025 rate (registry choice)"]}]}

# ---- pass 3 (R1 Europe, 2026-11-21): taxe foncière sur les propriétés bâties, Paris 2025 ----
S["doc"] = S["doc"].split("\n* 4100")[0].replace("Property family not reached (grade C)", "taxe foncière (4100), Paris") + r'''

## Taxe foncière sur les propriétés bâties, Paris 2025 (pass 3)
Sources (sha256 in `law/SHA256SUMS`, provenance in `law/ARCHIVE_INDEX.tsv`):
* **CGI art. 1380** (Légifrance via the Internet Archive, capture 2025-01-13, `fr/law/cgi_art1380_wb.html`; "Version en
  vigueur depuis le 01 juillet 1979"): "La taxe foncière est établie annuellement sur les propriétés bâties sises en
  France à l'exception de celles qui en sont expressément exonérées".
* **CGI art. 1388** (capture 2024-11-05, `fr/law/cgi_art1388_wb.html`; "Version en vigueur depuis le 11 janvier
  1980"): "La taxe foncière sur les propriétés bâties est établie d'après la valeur locative cadastrale de ces
  propriétés ... et sous déduction de 50 % de son montant".
* **Paris 2025 rates**: DGFiP open data "Fiscalité locale des particuliers" (data.economie.gouv.fr, exercice 2025,
  insee_com 75056 VILLE DE PARIS; `fr/law/dgfip_fiscalite_locale_particuliers_paris.json`, field labels in
  `..._meta.json`): "FB - COMMUNE / TAUX VOTE" 20.5; "FB - TSE / TAUX NET" 0.221; "FB - TSE AUTRES" 0.156;
  "FB - TASA" 0.189; "FB - GEMAPI" 0.143; "FB - TAUX GLOBAL (commune, syndicat de commune, intercommunalité, taxes
  spéciales, GEMAPI)" 21.21; TEOM taux plein 6.21. The Conseil de Paris rate deliberation was not read: grade B.
Base: the valeur locative cadastrale is an annual value (`annualValue`, or `assessed` where only that is given);
without either no charge is made (flagged). Applied to `home` and `realEstate` (bâti); tax rounded down to euros.
'''
S["lean"] = (S.get("lean") or "") + r'''
/-- DGFiP 2025, Paris: taux global TFPB 21,21 % (hundredths of a percent). -/
def tauxGlobalTfbParis2025 : Int := 2121
/-- CGI art. 1388: base = valeur locative cadastrale less 50 %. -/
def baseTfb (vlc : Int) : Int := divR .down (pos vlc) 2
def tfbParis (vlc : Int) : Int := divR .down (baseTfb vlc * tauxGlobalTfbParis2025) 10000
def vlcOf (a : Asset) : Int := if 0 ≤ a.annualValue then a.annualValue else a.assessed
def tfbCharges (as : List Asset) : List Charge :=
  (as.zipIdx.filter fun (a, _) => (a.kind == .home || a.kind == .realEstate) && 0 ≤ vlcOf a).map fun (a, i) =>
    charge .propertyRecurrent "Taxe foncière sur les propriétés bâties (Paris)" (vlcOf a) baseTfb (fun b => divR .down (b * tauxGlobalTfbParis2025) 10000)
      (event := s!"asset {i + 1}") (level := .local)
      (statute := "CGI art. 1380, 1388; Paris 2025 taux global TFPB 21,21 % (DGFiP)")
'''
S["families"] = S.get("families", []) + [("4100 taxe foncière (Paris)", [".propertyRecurrent"], "tfbCharges g.assets")]
S["unsupported"] = [u for u in S["unsupported"] if not u[1].startswith("4100")] + [
  ("g.assets.any (fun a => (a.kind == .home || a.kind == .realEstate) && a.annualValue < 0 && a.assessed < 0)", "4100 taxe foncière: no valeur locative cadastrale (annualValue) given: no charge made"),
  ("g.assets.any (fun a => a.kind == .land)", "4100 taxe foncière sur les propriétés non bâties not modelled"),
  ("g.assets.any (·.kind.isRealEstate)", "4100 taxe foncière: TEOM (6,21 %), frais de gestion (CGI art. 1641), exonérations and dégrèvements not applied")]
S["notes"] = S.get("notes", []) + ["FR 4100: CGI art. 1380, 1388 (Légifrance via Wayback); Paris 2025 taux global TFPB 21,21 % (DGFiP open data)"]
S["guards"] = S.get("guards", []) + [
  "-- VLC 4 000: base 2 000 (art. 1388, 50 %); x 21,21 % = 424,20",
  "baseTfb 4000 == 2000", "tfbParis 4000 == 424", "tfbParis 0 == 0"]
S["taxes"] = [t for t in S["taxes"] if t["oecd"] != "4100"] + [
 {"oecd": "4100", "tax": "Taxe foncière sur les propriétés bâties (Paris)", "statute": "CGI art. 1380, 1388; Paris taux 2025 (commune 20,50 %, taux global 21,21 %)",
  "dated": "CGI art. 1380 in force since 1.7.1979, art. 1388 since 11.1.1980 (Légifrance captures 2025-01-13, 2024-11-05); rates exercice 2025 from DGFiP 'Fiscalité locale des particuliers'",
  "grade": "B", "kernel_parts": ["charge (VLC x 50 % x taux)"],
  "unsupported": ["rates from the DGFiP open-data register (the Conseil de Paris deliberation not read)", "valeur locative cadastrale is an input (asset.annualValue)", "TEOM, frais de gestion (art. 1641), exonérations, TFPNB"]}]
S["lean"] = S["lean"].replace("," + chr(10) + "  ", ", ")

# ---- pass 6 (R1 Europe, 2026-11-21): P5/P6 rows (tools/p6lib.py, tools/p6_rows.py) ----
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6lib.py")).read())
exec(open(__import__("os").path.expanduser("cmp20/global/europe/tools/p6_rows.py")).read())
p6_rows(S)
p6_finish(S)
