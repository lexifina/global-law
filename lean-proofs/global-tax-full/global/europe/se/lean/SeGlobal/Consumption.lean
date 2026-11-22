import SeGlobal.Pit
import TaxKernel.Global2

/-!
# Sweden 2025: mervärdesskatt (5111); excises not read

Source: mervärdesskattelag (2023:200), Riksdagen text of SFS 2023:200 (`se/law/ml2023.html`, current text
"Ändrad: t.o.m. SFS 2026:1025" with the amendment notes; sha256 in `law/SHA256SUMS`): grade B (the 2025 wording is
read through the amendment notes; 2026 changes are marked "Lag (2026:119)").
* **9 kap.**: "Normalskattesats - 25 procent"; "Reducerad skattesats - 12 procent": food ("sådana livsmedel som avses i
  artikel 2 i EU:s livsmedelsförordning", except water and "spritdrycker, vin och starköl"), "rumsuthyrning i
  hotellrörelse", "restaurang- och cateringtjänster"; 6 % for books, newspapers and passenger transport.
* **18 kap.** exemption for small businesses whose turnover "inte överstiger 120 000 kronor under kalenderåret".


## 5121 Excise duties (alcohol, tobacco, motor and heating fuel) (gap pass, grade B)
Source: European Commission, Taxes in Europe Database (TEDB), SE excise records for the situation on 1 July 2025 (tobacco 4110, alcohol 4107, energy 4109; data supplied by the member state; REST service of the TEDB web application, read 2026-11-21, held as `se/law/tedb_*.json`).
* TEDB SE manufactured tobacco (1.7.2025): 2060 SEK per 1 000 cigarettes + 1.0 % of the retail selling price
* TEDB SE beer (1.7.2025): 228 SEK per hl and % vol (= per litre of pure alcohol)
* TEDB SE still wine (1.7.2025): 2958 SEK per hl of product
* TEDB SE ethyl alcohol (1.7.2025): 52697 SEK per hl of pure alcohol


## 5121 Energiskatt och koldioxidskatt på bensin, diesel och eldningsolja (ny tabell från 1.7.2025) (gap pass 2) (gap pass, grade B)
Source: Regeringskansliet, SFS-registret (rkrattsbaser.gov.se/sfsr?bet=1994:1776, fetched 2026-11-22, `se/law/sfsr_1994_1776.html`): SFS 2024:1144 amends 2 kap. 1 §, in force 2025-07-01 (the only 2025 change to 2 kap. 1 §); figures from the TEDB SE 4109 at 1.1 and 1.7.2025.
* LSE 1994:1776 2 kap. 1 § (TEDB SE 4109 at 1.1.2025: 5 110 SEK / m³)
* LSE 2 kap. 1 § in the wording of SFS 2024:1144 (ikraft 2025-07-01; TEDB at 1.7.2025: 4 790 SEK / m³)
* LSE 2 kap. 1 § (TEDB at 1.1.2025: 4 281 SEK / m³)
* LSE 2 kap. 1 § as SFS 2024:1144 (TEDB at 1.7.2025: 3 961 SEK / m³)
* LSE 2 kap. 1 § (TEDB at 1.1.2025: 4 280 SEK / m³)
* LSE 2 kap. 1 § as SFS 2024:1144 (TEDB at 1.7.2025: 3 960 SEK / m³)
-/

namespace SeGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Mervärdesskatt", standard := 2500, reduced := 1200, superReduced := 600, threshold := 120000,
    classOf := fun gd => match gd with
      | .food | .nonAlcoholic | .hotels | .restaurants => .reduced
      | .books | .newspapers | .transport => .superReduced
      | .health | .education | .financial | .insurance | .rent => .exempt
      | _ => .standard }

def vatStatute : String := "ML (2023:200) 9 kap. (25 %, 12 %, 6 %); 10 kap. (undantag); 18 kap. (120 000 kronor)"

def excise : Excise :=
  { rates := [
      { good := .cigarettes, name := "Excise duty on cigarettes", perUnitNum := 103, perUnitDen := 50, adValoremBp := 100, statute := "TEDB SE manufactured tobacco (1.7.2025): 2060 SEK per 1 000 cigarettes + 1.0 % of the retail selling price" },
      { good := .beer, name := "Excise duty on beer", perUnitNum := 228, onPureAlcohol := true, statute := "TEDB SE beer (1.7.2025): 228 SEK per hl and % vol (= per litre of pure alcohol)" },
      { good := .wine, name := "Excise duty on still wine", perUnitNum := 1479, perUnitDen := 50, statute := "TEDB SE still wine (1.7.2025): 2958 SEK per hl of product" },
      { good := .spirits, name := "Excise duty on ethyl alcohol", perUnitNum := 52697, perUnitDen := 100, onPureAlcohol := true, statute := "TEDB SE ethyl alcohol (1.7.2025): 52697 SEK per hl of pure alcohol" }] }

/-- Energiskatt och koldioxidskatt på bensin, diesel och eldningsolja (ny tabell från 1.7.2025) (gap pass 2; kernel 2.1 `ExciseRule` date windows). -/
def gxDated0 : ExciseRule :=
  { good := .petrol,   name := "Energi- och koldioxidskatt (bensin, miljöklass 1)",   perUnitNum := 5110,   perUnitDen := 1000,   validTo := "2025-07-01",   statute := "LSE 1994:1776 2 kap. 1 § (TEDB SE 4109 at 1.1.2025: 5 110 SEK / m³)" }
def gxDated1 : ExciseRule :=
  { good := .petrol,   name := "Energi- och koldioxidskatt (bensin, miljöklass 1)",   perUnitNum := 4790,   perUnitDen := 1000,   validFrom := "2025-07-01",   statute := "LSE 2 kap. 1 § in the wording of SFS 2024:1144 (ikraft 2025-07-01; TEDB at 1.7.2025: 4 790 SEK / m³)" }
def gxDated2 : ExciseRule :=
  { good := .diesel,   name := "Energi- och koldioxidskatt (dieselbränsle, miljöklass 1)",   perUnitNum := 4281,   perUnitDen := 1000,   validTo := "2025-07-01",   statute := "LSE 2 kap. 1 § (TEDB at 1.1.2025: 4 281 SEK / m³)" }
def gxDated3 : ExciseRule :=
  { good := .diesel,   name := "Energi- och koldioxidskatt (dieselbränsle, miljöklass 1)",   perUnitNum := 3961,   perUnitDen := 1000,   validFrom := "2025-07-01",   statute := "LSE 2 kap. 1 § as SFS 2024:1144 (TEDB at 1.7.2025: 3 961 SEK / m³)" }
def gxDated4 : ExciseRule :=
  { good := .heatingOil,   name := "Energi- och koldioxidskatt (eldningsolja)",   perUnitNum := 4280,   perUnitDen := 1000,   validTo := "2025-07-01",   statute := "LSE 2 kap. 1 § (TEDB at 1.1.2025: 4 280 SEK / m³)" }
def gxDated5 : ExciseRule :=
  { good := .heatingOil,   name := "Energi- och koldioxidskatt (eldningsolja)",   perUnitNum := 3960,   perUnitDen := 1000,   validFrom := "2025-07-01",   statute := "LSE 2 kap. 1 § as SFS 2024:1144 (TEDB at 1.7.2025: 3 960 SEK / m³)" }

def gxDatedRules : List ExciseRule := [gxDated0, gxDated1, gxDated2, gxDated3, gxDated4, gxDated5]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 mervärdesskatt", covers := [.vat, .excise, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption
       ++ exciseRuleCharges gxDatedRules g }]

def absent : List Absent :=
  []

def notes : List String := ["SE 5111: ML 2023:200, current text with amendment notes", "SE 5121 gap pass: Excise duties (alcohol, tobacco, motor and heating fuel) (B, TEDB situation on 1.7.2025)", "SE 5121 gap pass 2: Energiskatt och koldioxidskatt på bensin, diesel och eldningsolja (ny tabell från 1.7.2025) (B, change on 1.7.2025)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["energy tax, tobacco and alcohol taxes (LSE 1994:1776, LTS 1994:1563, LAS 2022:155) not read"] else [])
  ++ (if g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent) then ["exemptions (10 kap.) taken from the act's structure, not quoted"] else [])
  ++ (if g.consumption.any (fun s => s.good == .electricity || s.good == .gas || s.good == .tobaccoOther) then ["5121 SE: excise on electricity, natural gas and tobacco other than cigarettes not modelled (gap pass)"] else [])

#guard vat.embedded { good := .clothing, amount := 125 } == 25
#guard vat.embedded { good := .food, amount := 112 } == 12
#guard vat.embedded { good := .books, amount := 106 } == 6
#guard vat.net { turnover := 120000, sales := [{ good := .other, net := 120000 }] } == 0
#guard excise.duty { good := .cigarettes, amount := 5000, quantity := 1000000 } == 2110
#guard excise.duty { good := .beer, amount := 300, quantity := 100000, abvBp := 500 } == 1140
#guard excise.duty { good := .wine, amount := 800, quantity := 100000, abvBp := 1200 } == 2958
#guard excise.duty { good := .spirits, amount := 2000, quantity := 100000, abvBp := 4000 } == 21078
#guard gxDated0.dutyOn { good := .petrol, amount := 1700, quantity := 1000000 } {} == 5110
#guard gxDated1.dutyOn { good := .petrol, amount := 1700, quantity := 1000000 } {} == 4790
#guard gxDated2.dutyOn { good := .diesel, amount := 1700, quantity := 1000000 } {} == 4281
#guard gxDated3.dutyOn { good := .diesel, amount := 1700, quantity := 1000000 } {} == 3961
#guard gxDated4.dutyOn { good := .heatingOil, amount := 1700, quantity := 1000000 } {} == 4280
#guard gxDated5.dutyOn { good := .heatingOil, amount := 1700, quantity := 1000000 } {} == 3960
#guard gxDated0.windowDays 2025 + gxDated1.windowDays 2025 == 365
#guard gxDated2.windowDays 2025 + gxDated3.windowDays 2025 == 365
#guard gxDated4.windowDays 2025 + gxDated5.windowDays 2025 == 365

end SeGlobal.Consumption
