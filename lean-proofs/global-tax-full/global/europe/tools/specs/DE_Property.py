S = {'cc': 'DE', 'fam': 'Property', 'families': [], 'doc': "# DE 2025: Property family not reached (grade C)\n\n* 4100 Recurrent property tax (Grundsteuergesetz (GrStG 2025, Berlin Hebesatz 470 %)): tried not read in the P5 pass; would unlock: the act and the reference municipality's 2025 rate (registry choice)\n", 'notes': [], 'unsupported': [('!g.purchases.isEmpty || g.assets.any (·.kind.isRealEstate)', '4100 Recurrent property tax: not modelled (grade C: not read in the P5 pass)')], 'guards': [], 'taxes': [{'oecd': '4100', 'tax': 'Recurrent property tax', 'statute': 'Grundsteuergesetz (GrStG 2025, Berlin Hebesatz 470 %)', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'tried': 'not read in the P5 pass', 'unsupported': ["would unlock: the act and the reference municipality's 2025 rate (registry choice)"]}]}

# ---- pass 3 (R1 Europe, 2026-11-21): Grundsteuer B, Berlin 2025 ----
S["doc"] = S["doc"].split("\n* 4100")[0].replace("Property family not reached (grade C)", "Grundsteuer (4100), Berlin") + r'''

## Grundsteuer, Berlin 2025 (pass 3)
Sources (sha256 in `law/SHA256SUMS`, provenance in `law/ARCHIVE_INDEX.tsv`):
* **GrStG** (gesetze-im-internet.de, fetched 2026-11-21: `grstg___13`, `___25`, `___37`): § 37 (1) "Diese Fassung des
  Gesetzes gilt erstmals für die Grundsteuer des Kalenderjahres 2025"; § 13 Steuermessbetrag = "Anwendung eines
  Promillesatzes (Steuermesszahl) auf den Grundsteuerwert"; § 25 (1) the Gemeinde sets the "Hundertsatz des
  Steuermeßbetrags ... (Hebesatz)". No Berlin deviation from §§ 13, 25 in the Fußnoten.
* **BlnGrStMG** vom 27. Juni 2024 (GVBl. 2024, 422; `blngrstmg.pdf`), § 1 (1), "abweichend von § 15 Absatz 1" GrStG:
  "1. ... unbebaute Grundstücke im Sinne des § 246 des Bewertungsgesetzes ... 0,45 Promille, 2. ... bebaute
  Grundstücke im Sinne des § 249 Absatz 1 Nummer 1 bis 4 ... 0,31 Promille, 3. ... § 249 Absatz 1 Nummer 5 bis 8 ...
  0,45 Promille".
* **Haushaltsgesetz 2024/2025 § 4 (2)**, inserted by the Zweites Nachtragshaushaltsgesetz 2024/2025 vom 27.6.2024
  Art. 1 Nr. 3 (GVBl. 2024 S. 433; `gvbl_berlin_2024_nr26.pdf`): "Die Hebesätze für die Grundsteuer werden für das
  Jahr 2025 1. für Betriebe der Land- und Forstwirtschaft auf 0 Prozent 2. für Grundstücke auf 470 Prozent des
  Steuermessbetrages festgesetzt."
* Worked example of the Senatsverwaltung für Finanzen (FAQ Grundsteuer, `faq_grundsteuer_berlin.html`):
  "150.000 € (= Grundsteuerwert) x 0,31/1000 (Messzahl für Wohnen) = 46,50 € (Messbetrag) ... x 470 % = 218,55 €".
Base: the asset's `assessed` value is the Grundsteuerwert (BewG §§ 243 ff., Hauptfeststellung 1.1.2022); without it the
market value stands in. Kinds: `home` and `realEstate` are taken as Wohngrundstücke (§ 249 (1) Nr. 1-4), `land` as
unbebaut (§ 246). Messbetrag kept in cents (rounded down), the tax rounded down to whole euros.
'''
S["lean"] = (S.get("lean") or "") + r'''
/-- HG 2024/2025 § 4 (2) Nr. 2 (2. NHG 24/25): Hebesatz für Grundstücke 2025, percent. -/
def hebesatzBerlin2025 : Int := 470
/-- BlnGrStMG § 1 (1): Steuermesszahl in hundredths of a per mille (31 = 0,31 ‰). -/
def messzahlBerlin : AssetKind → Int
  | .land => 45
  | _ => 31
/-- GrStG § 13: Steuermessbetrag in cents = Grundsteuerwert x Steuermesszahl (rounded down to the cent). -/
def messbetragCent (k : AssetKind) (w : Int) : Int := divR .down (pos w * messzahlBerlin k) 1000
/-- GrStG § 25 (1): Grundsteuer = Steuermessbetrag x Hebesatz (whole euros, rounded down). -/
def grundsteuerBerlin (k : AssetKind) (w : Int) : Int := divR .down (messbetragCent k w * hebesatzBerlin2025) 10000
def grundsteuerCharges (as : List Asset) : List Charge :=
  (as.zipIdx.filter fun (a, _) => a.kind.isRealEstate).map fun (a, i) =>
    charge .propertyRecurrent "Grundsteuer B (Berlin)" a.statutoryValue (fun w => w) (fun w => grundsteuerBerlin a.kind w)
      (event := s!"asset {i + 1}") (level := .local)
      (statute := "GrStG §§ 13, 25, 37 (1); BlnGrStMG § 1 (1); HG 2024/2025 § 4 (2) Nr. 2 (470 %)")
'''
S["families"] = S.get("families", []) + [("4100 Grundsteuer (Berlin)", [".propertyRecurrent"], "grundsteuerCharges g.assets")]
S["unsupported"] = [u for u in S["unsupported"] if not u[1].startswith("4100")] + [
  ("g.assets.any (fun a => a.kind.isRealEstate && a.assessed < 0)", "4100 Grundsteuer: no Grundsteuerwert given (BewG §§ 243 ff. not modelled): the market value stands in"),
  ("g.assets.any (fun a => a.kind == .realEstate)", "4100 Grundsteuer: realEstate taken as Wohngrundstück (0,31 ‰); Geschäftsgrundstücke (§ 249 (1) Nr. 5-8) bear 0,45 ‰; § 15 (2)-(5) GrStG reductions (Förderzusage, Denkmal) not applied")]
S["notes"] = S.get("notes", []) + ["DE 4100: Berlin Grundsteuer 2025 (BlnGrStMG § 1; HG 2024/2025 § 4 (2), GVBl. 2024 S. 433)"]
S["guards"] = S.get("guards", []) + [
  "-- the Senatsverwaltung's example: 150 000 x 0,31 per mille = 46,50 EUR Messbetrag; x 470 % = 218,55 EUR",
  "messbetragCent .home 150000 == 4650",
  "grundsteuerBerlin .home 150000 == 218",
  "grundsteuerBerlin .land 100000 == 211",
  "grundsteuerBerlin .home 0 == 0"]
S["taxes"] = [t for t in S["taxes"] if t["oecd"] != "4100"] + [
 {"oecd": "4100", "tax": "Grundsteuer B (Berlin)", "statute": "GrStG §§ 13, 25, 37 (1); BlnGrStMG vom 27.6.2024 § 1 (1); Haushaltsgesetz 2024/2025 § 4 (2) (2. NHG 24/25 Art. 1 Nr. 3)",
  "dated": "GrStG in the 2025 version (§ 37 (1): erstmals 2025); BlnGrStMG GVBl. 2024, 422; Hebesatz 470 % 'für das Jahr 2025' (GVBl. 2024 S. 433)",
  "grade": "A", "kernel_parts": ["charge (two-stage: Grundsteuerwert x Messzahl x Hebesatz)"],
  "unsupported": ["Grundsteuerwert valuation (BewG §§ 243 ff.) is an input (asset.assessed)", "Geschäftsgrundstücke 0,45 ‰ need the use; realEstate taken as residential", "GrStG § 15 (2)-(5) reductions", "Grundsteuer A (0 % in 2025)"]}]
S["lean"] = S["lean"].replace("," + chr(10) + "  ", ", ")
