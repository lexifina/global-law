S = {'cc': 'AT', 'fam': 'Property', 'doc': '# AT 2025: transfer duties on purchases (4400); recurrent property tax not modelled\n\nSource: Grunderwerbsteuergesetz 1987, RIS Fassung vom 01.07.2025 (`at/law/grestg_2025-07-01.html`); sha256 in `law/SHA256SUMS`.\n* § 7 (1) Z 3: "3,5%" of the consideration for other (entgeltliche) acquisitions\n* § 7 (1) Z 2 lit. a: unentgeltliche Erwerbe "für die ersten 250 000 Euro 0,5%, für die nächsten 150 000 Euro 2%, darüber hinaus 3,5% des Grundstückswertes" (not used for purchases)\n', 'lean': 'def d0 : TransferDuty :=\n  { name := "Grunderwerbsteuer",\n    sched := Schedule.flat 350,\n    kinds := [.home, .realEstate, .land] }', 'families': [('4400 transfer duties', ['.transactions'], 'd0.charges g.purchases "GrEStG 1987 § 7 (1) Z 3 (3,5 %)"')], 'notes': ['AT 4400: RIS Fassung vom 01.07.2025'], 'unsupported': [('!g.purchases.isEmpty', 'Eintragungsgebühr (GGG TP 9 lit. b Z 1, 1,1 %) not modelled; family and gratuitous transfers (§ 7 (1) Z 2) are not purchases'), ('g.assets.any (·.kind.isRealEstate)', 'recurrent property tax (4100) not modelled')], 'guards': ['d0.amount { kind := .home, price := 200000 } == 7000', 'd0.amount { kind := .home, price := 2000000 } == 70000'], 'taxes': [{'oecd': '4400', 'tax': 'Grunderwerbsteuer', 'statute': 'GrEStG 1987 § 7 (1) Z 3 (3,5 %)', 'dated': 'RIS Fassung vom 01.07.2025', 'grade': 'A', 'kernel_parts': ['TransferDuty'], 'unsupported': ['Eintragungsgebühr (GGG TP 9 lit. b Z 1, 1,1 %) not modelled; family and gratuitous transfers (§ 7 (1) Z 2) are not purchases']}, {'oecd': '4100', 'tax': 'Recurrent property tax', 'statute': 'local', 'grade': 'C', 'status': 'unsupported', 'kernel_parts': [], 'unsupported': ["the default municipality's act and rate not read in the P5 pass; would unlock: the property-tax act and the reference municipality's rate (registry choice)"]}]}

# ---- pass 3 (R1 Europe, 2026-11-21): Grundsteuer B, Wien ----
S["doc"] = S["doc"].replace("; recurrent property tax not modelled", "; Grundsteuer (4100), Wien") + r'''

## Grundsteuer, Wien (pass 3)
Sources (sha256 in `law/SHA256SUMS`):
* **GrStG 1955**, RIS Fassung vom 01.07.2025 (`at/law/grstg1955_2025-07-01.html`): § 18 (1) Steuermeßbetrag =
  "Anwendung der Steuermesszahl (§ 19) auf den Einheitswert ... auf volle Cent abzurunden oder aufzurunden";
  § 19 Z 2 "bei Grundstücken ... allgemein 2 vom Tausend; diese Steuermeßzahl ermäßigt sich a) bei
  Einfamilienhäusern für die ersten angefangenen oder vollen 3 650 Euro des Einheitswertes auf 0.5 vom Tausend, für
  die folgenden angefangenen oder vollen 7 300 Euro des Einheitswertes auf 1 vom Tausend, b) bei Mietwohngrundstücken
  und bei gemischtgenutzten Grundstücken für die ersten ... 3 650 Euro ... auf 1 vom Tausend, für die folgenden ...
  3 650 Euro ... auf 1.5 vom Tausend, c) bei den übrigen Grundstücken für die ersten ... 3 650 Euro ... auf 1 vom
  Tausend"; § 27 (1) "Der Jahresbetrag der Steuer ist nach einem Hundertsatz (Hebesatz) des Steuermeßbetrages ... zu
  berechnen ... von der Gemeinde festgesetzt".
* **Verordnung des Gemeinderats, mit der der Hebesatz der Grundsteuer festgesetzt wird** (ABl. der Stadt Wien
  1994/07, RIS Gemeinderecht GEMRE_WI_90101_F440_000, current, fetched 2026-11-21;
  `at/law/wien_hebesatz_grundsteuer_F440.html`): Art. I "Der Hebesatz der Grundsteuer beträgt 500 vH."; Art. II in
  force from 1. Jänner 1994 (no later amendment in RIS).
Base: the asset's `assessed` value is the Einheitswert (BewG 1955); without it the market value stands in (the
Einheitswert is far below market value). Kinds: `home` = Einfamilienhaus (lit. a), `realEstate` = Mietwohngrundstück
(lit. b), `land` = übrige Grundstücke (lit. c). Messbetrag rounded half up to the cent; tax rounded down to euros.
'''
S["lean"] = (S.get("lean") or "") + r'''
/-- Verordnung des Gemeinderats (ABl. 1994/07) Art. I: Hebesatz 500 vH. -/
def hebesatzWien : Int := 500
/-- GrStG 1955 § 19 Z 2 lit. a-c, rates in bp (5 = 0,5 vom Tausend). -/
def messzahlWien : AssetKind → Schedule
  | .home => ⟨[⟨0, 5⟩, ⟨3650, 10⟩, ⟨10950, 20⟩]⟩
  | .realEstate => ⟨[⟨0, 10⟩, ⟨3650, 15⟩, ⟨7300, 20⟩]⟩
  | _ => ⟨[⟨0, 10⟩, ⟨3650, 20⟩]⟩
/-- GrStG 1955 § 18 (1): Steuermeßbetrag in cents, rounded half up. -/
def messbetragCentWien (k : AssetKind) (ew : Int) : Int := divR .halfUp ((messzahlWien k).ticks (pos ew) * 100) BP
/-- GrStG 1955 § 27 (1): Jahresbetrag = Steuermeßbetrag x Hebesatz (whole euros, rounded down). -/
def grundsteuerWien (k : AssetKind) (ew : Int) : Int := divR .down (messbetragCentWien k ew * hebesatzWien) 10000
def grundsteuerCharges (as : List Asset) : List Charge :=
  (as.zipIdx.filter fun (a, _) => a.kind.isRealEstate).map fun (a, i) =>
    charge .propertyRecurrent "Grundsteuer (Wien)" a.statutoryValue (fun w => w) (fun w => grundsteuerWien a.kind w)
      (event := s!"asset {i + 1}") (level := .local)
      (statute := "GrStG 1955 §§ 18 (1), 19 Z 2, 27 (1); Verordnung des Gemeinderats ABl. 1994/07 Art. I (500 vH)")
'''
S["families"] = S.get("families", []) + [("4100 Grundsteuer (Wien)", [".propertyRecurrent"], "grundsteuerCharges g.assets")]
S["unsupported"] = [u for u in S["unsupported"] if "4100" not in u[1]] + [
  ("g.assets.any (fun a => a.kind.isRealEstate && a.assessed < 0)", "4100 Grundsteuer: no Einheitswert given (BewG 1955 not modelled): the market value stands in"),
  ("g.assets.any (fun a => a.kind == .realEstate)", "4100 Grundsteuer: realEstate taken as Mietwohngrundstück (§ 19 Z 2 lit. b); Geschäftsgrundstücke fall under lit. c; exemptions (§ 2) and land- und forstwirtschaftliche Betriebe not modelled")]
S["notes"] = S.get("notes", []) + ["AT 4100: GrStG 1955 RIS Fassung vom 01.07.2025; Wien Hebesatz 500 vH (ABl. 1994/07)"]
S["guards"] = S.get("guards", []) + [
  "-- Einfamilienhaus, Einheitswert 20 000: 3 650 x 0,5 + 7 300 x 1 + 9 050 x 2 per mille = 27,23 Messbetrag (27,225 half up); x 500 % = 136,15",
  "messbetragCentWien .home 20000 == 2723",
  "grundsteuerWien .home 20000 == 136",
  "-- Mietwohngrundstück 3 650: 3,65; x 500 % = 18,25",
  "grundsteuerWien .realEstate 3650 == 18",
  "-- 3 650 x 1 + 3 650 x 1,5 + 2 700 x 2 per mille = 14,525 -> 14,53", "messbetragCentWien .realEstate 10000 == 1453",
  "messbetragCentWien .land 10000 == 1635",
  "grundsteuerWien .land 0 == 0"]
S["taxes"] = [t for t in S["taxes"] if t["oecd"] != "4100"] + [
 {"oecd": "4100", "tax": "Grundsteuer (Wien)", "statute": "GrStG 1955 §§ 18 (1), 19 Z 2 lit. a-c, 27 (1); Verordnung des Gemeinderats, mit der der Hebesatz der Grundsteuer festgesetzt wird (ABl. 1994/07) Art. I",
  "dated": "GrStG 1955 RIS Fassung vom 01.07.2025; Hebesatz 500 vH in force from 1.1.1994 (RIS Gemeinderecht, current)",
  "grade": "A", "kernel_parts": ["charge (Einheitswert x Messzahl schedule x Hebesatz)", "Schedule"],
  "unsupported": ["Einheitswert (BewG 1955) is an input (asset.assessed)", "realEstate taken as Mietwohngrundstück", "exemptions (§ 2), Baurecht (§ 18 (2)), land- und forstwirtschaftliche Betriebe (Grundsteuer A)"]}]
S["lean"] = S["lean"].replace("," + chr(10) + "  ", ", ")

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
