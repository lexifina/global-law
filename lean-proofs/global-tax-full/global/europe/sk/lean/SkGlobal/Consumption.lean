import SkGlobal.Pit

/-!
# Slovakia 2025: daň z pridanej hodnoty (5111), spotrebná daň z minerálneho oleja (5121)

Sources: Slov-Lex (official), static consolidations in force from 1 January 2025: zákon 222/2004 Z. z. o DPH
(`sk/law/dph_20250101.html`), zákon 98/2004 Z. z. o spotrebnej dani z minerálneho oleja
(`sk/law/akciza_mineral_20250101.html`); sha256 in `law/SHA256SUMS`.
* **§ 27 (1)**: "Základná sadzba dane na tovary a služby je 23 % zo základu dane"; (2) "Znížená sadzba dane 19 %" for
  goods in príloha č. 7 bod 1 and services in príloha č. 7a bod 1; (3) "Znížená sadzba dane 5 %" for príloha č. 7 body
  2 a 3, príloha č. 7a bod 2. The annexes are not in the consolidation file read: the reduced classes are not assigned.
* **§ 4 (1)**: registration when turnover "presiahla 50 000 eur".
* **Zákon 98/2004 § 7 (1)**: "a) motorový benzín ... 2710 12 41, 2710 12 45, 2710 12 49 514 eur/1 000 l"; "d) plynový
  olej ... 368 eur/1 000 l".

## FT review (2026-11-21, third pass): heating oil
Slov-Lex znenie od 1. 1. 2025 (`sk/law/akciza_mineral_20250101.txt`; the rate section is printed there as **§ 6 (1)**,
the model's citations say § 7 (1)): "d) plynový olej kódu kombinovanej nomenklatúry 2710 19 43, 2710 19 46,
2710 19 47, 2710 19 48, 2710 20 11, 2710 20 16 a 2710 20 19 368 eur/1 000 l"; "e) vykurovací olej kódu kombinovanej
nomenklatúry 2710 19 62, 2710 19 66, 2710 19 67, 2710 20 32, 2710 20 38 a 2710 20 90 111,50 eura/1 000 kg". Gas oil
used as "palivo" (fuel for producing heat, § 3 (5)) has no rate of its own and no exemption (§ 10 (1) lists none for
heating; § 15 refunds only to tax warehouses and licensed user undertakings). The household's `heatingOil` (light
heating oil, gas oil by the kernel's reading) therefore bears the d) rate; heavy fuel oils of the e) codes (per kg) are
listed, not computed.


## 5121 Spotrebné dane z tabaku, liehu, piva, vína (gap pass, grade B)
Source: European Commission, Taxes in Europe Database (TEDB), SK excise records for the situation on 1 July 2025 (tobacco 4149, alcohol 4147; data supplied by the member state; REST service of the TEDB web application, read 2026-11-21, held as `sk/law/tedb_*.json`).
* TEDB SK manufactured tobacco (1.7.2025): 91.3 EUR per 1 000 cigarettes + 25.0 % of the retail selling price, at least 148 EUR per 1 000
* TEDB SK beer (1.7.2025): 3.587 EUR per hl and % vol (= per litre of pure alcohol)
* TEDB SK still wine (1.7.2025): 0 EUR per hl of product
* TEDB SK ethyl alcohol (1.7.2025): 1490.4 EUR per hl of pure alcohol
-/

namespace SkGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Daň z pridanej hodnoty", standard := 2300, reduced := 1900, superReduced := 500, threshold := 50000,
    classOf := fun gd => match gd with
      | _ => .standard }

def vatStatute : String := "zákon 222/2004 Z. z. § 27 (1) 23 %, (2) 19 %, (3) 5 %; § 4 (1) (50 000 eur)"

def excise : Excise :=
  { rates := [
      { good := .petrol, name := "Spotrebná daň z minerálneho oleja (benzín)", perUnitNum := 514, perUnitDen := 1000, statute := "zákon 98/2004 Z. z. § 7 (1) a): 514 eur / 1 000 l" },
      { good := .diesel, name := "Spotrebná daň z minerálneho oleja (plynový olej)", perUnitNum := 368, perUnitDen := 1000, statute := "zákon 98/2004 Z. z. § 7 (1) d): 368 eur / 1 000 l" },
      { good := .heatingOil, name := "Spotrebná daň z minerálneho oleja (plynový olej na vykurovanie)", perUnitNum := 368, perUnitDen := 1000, statute := "zákon 98/2004 Z. z. § 6 (1) d) (znenie od 1. 1. 2025): 368 eur / 1 000 l plynového oleja; no heating rate or exemption for gas oil" },
      { good := .cigarettes, name := "Excise duty on cigarettes", perUnitNum := 913, perUnitDen := 10000, adValoremBp := 2500, minNum := 37, minDen := 250, statute := "TEDB SK manufactured tobacco (1.7.2025): 91.3 EUR per 1 000 cigarettes + 25.0 % of the retail selling price, at least 148 EUR per 1 000" },
      { good := .beer, name := "Excise duty on beer", perUnitNum := 3587, perUnitDen := 1000, onPureAlcohol := true, statute := "TEDB SK beer (1.7.2025): 3.587 EUR per hl and % vol (= per litre of pure alcohol)" },
      { good := .wine, name := "Excise duty on still wine", statute := "TEDB SK still wine (1.7.2025): 0 EUR per hl of product" },
      { good := .spirits, name := "Excise duty on ethyl alcohol", perUnitNum := 1863, perUnitDen := 125, onPureAlcohol := true, statute := "TEDB SK ethyl alcohol (1.7.2025): 1490.4 EUR per hl of pure alcohol" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 DPH, 5121 SDMO", covers := [.vat, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption }]

def absent : List Absent :=
  []

def notes : List String := ["SK 5111/5121: Slov-Lex consolidations from 2025-01-01", "SK 5121 gap pass: Spotrebné dane z tabaku, liehu, piva, vína (B, TEDB situation on 1.7.2025)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if !g.consumption.isEmpty then ["every basket line at 23 %: the 19 % and 5 % annexes (príloha č. 7, 7a) and the exemptions (§§ 28-42) not read"] else [])
  ++ (if g.consumption.any (fun s => s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["tobacco and alcohol duties (zákony 106/2004, 530/2011) not reached (Slov-Lex static file 404)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .heatingOil) then ["heating oil read as gas oil (§ 6 (1) d), 368 eur / 1 000 l); a vykurovací olej of the e) codes (2710 19 62-67 ...) bears 111,50 eur / 1 000 kg instead (per kg: not computed)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .electricity || s.good == .gas || s.good == .tobaccoOther) then ["5121 SK: excise on electricity, natural gas and tobacco other than cigarettes not modelled (gap pass)"] else [])

#guard vat.embedded { good := .clothing, amount := 123 } == 23
#guard vat.net { turnover := 50000, sales := [{ good := .other, net := 50000 }] } == 0
#guard excise.duty { good := .petrol, amount := 1700, quantity := 1000000 } == 514
#guard excise.duty { good := .diesel, amount := 1600, quantity := 1000000 } == 368
#guard excise.duty { good := .heatingOil, amount := 1000, quantity := 1000000 } == 368
#guard excise.duty { good := .cigarettes, amount := 5000, quantity := 1000000 } == 1341
#guard excise.duty { good := .beer, amount := 300, quantity := 100000, abvBp := 500 } == 17
#guard excise.duty { good := .wine, amount := 800, quantity := 100000, abvBp := 1200 } == 0
#guard excise.duty { good := .spirits, amount := 2000, quantity := 100000, abvBp := 4000 } == 596

end SkGlobal.Consumption
