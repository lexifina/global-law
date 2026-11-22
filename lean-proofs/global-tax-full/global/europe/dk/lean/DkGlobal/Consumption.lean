import DkGlobal.Pit

/-!
# DK 2025: Merværdiafgift (moms) (5111); excises not modelled in this pass

Source: Bekendtgørelse af lov om merværdiafgift (momsloven), LBK nr 209 af 27/02/2024, retsinformation.dk ELI XML (official; status Valid through 2025), `dk/law/momsl_lbk2024_209.xml`; sha256 in `law/SHA256SUMS`.
* § 33: "Afgiften udgør 25 pct. af afgiftsgrundlaget."
* § 48, stk. 1: registration not required "når de samlede afgiftspligtige leverancer ikke overstiger 50.000 kr. årligt"

## FT review (2026-11-21, third pass): passenger transport
Same LBK nr 209 af 27/02/2024 (`dk/law/momsl_lbk2024_209.txt`). **§ 13, stk. 1**: "Følgende varer og ydelser er
fritaget for afgift: ... 15) Personbefordring. Fritagelsen omfatter dog ikke anden erhvervsmæssig passagerkørsel med bus
end rutekørsel." The household's `transport` is read as exempt passenger transport (non-scheduled commercial bus
excepted, listed).


## 5121 Excise duties (alcohol, tobacco, motor and heating fuel) (gap pass, grade B)
Source: European Commission, Taxes in Europe Database (TEDB), DK excise records for the situation on 1 July 2025 (tobacco 4067, alcohol 4065, energy 4066; data supplied by the member state; REST service of the TEDB web application, read 2026-11-21, held as `dk/law/tedb_*.json`).
* TEDB DK manufactured tobacco (1.7.2025): 1935.4 DKK per 1 000 cigarettes + 1.0 % of the retail selling price
* TEDB DK beer (1.7.2025): 48.74 DKK per hl and % vol (= per litre of pure alcohol)
* TEDB DK still wine (1.7.2025): 1126 DKK per hl of product
* TEDB DK ethyl alcohol (1.7.2025): 15000 DKK per hl of pure alcohol
-/

namespace DkGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Merværdiafgift (moms)", standard := 2500, threshold := 50000,
    classOf := fun gd => match gd with
      | .health | .education | .financial | .insurance | .rent | .transport => .exempt
      | _ => .standard }

def vatStatute : String := "Momsloven (LBK nr 209 af 27/02/2024) § 33 (25 pct.); § 13 (fritagelser); § 48, stk. 1 (50.000 kr.)"

def excise : Excise :=
  { rates := [
      { good := .cigarettes, name := "Excise duty on cigarettes", perUnitNum := 9677, perUnitDen := 5000, adValoremBp := 100, statute := "TEDB DK manufactured tobacco (1.7.2025): 1935.4 DKK per 1 000 cigarettes + 1.0 % of the retail selling price" },
      { good := .beer, name := "Excise duty on beer", perUnitNum := 2437, perUnitDen := 50, onPureAlcohol := true, statute := "TEDB DK beer (1.7.2025): 48.74 DKK per hl and % vol (= per litre of pure alcohol)" },
      { good := .wine, name := "Excise duty on still wine", perUnitNum := 563, perUnitDen := 50, statute := "TEDB DK still wine (1.7.2025): 1126 DKK per hl of product" },
      { good := .spirits, name := "Excise duty on ethyl alcohol", perUnitNum := 150, onPureAlcohol := true, statute := "TEDB DK ethyl alcohol (1.7.2025): 15000 DKK per hl of pure alcohol" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Merværdiafgift (moms)", covers := [.vat, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption }]

def absent : List Absent :=
  []

def notes : List String := ["DK 5111: LBK nr 209 af 27/02/2024 (in force 2024-03-04, Valid at fetch)", "DK 5121 gap pass: Excise duties (alcohol, tobacco, motor and heating fuel) (B, TEDB situation on 1.7.2025)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance) then ["exempt supplies taken from the act's structure (EU/EEA standard exemptions), not quoted item by item"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Mineralolieafgiftsloven, tobaksafgiftsloven, øl- og vinafgiftsloven, spiritusafgiftsloven) not modelled in this pass"] else [])
  ++ (if g.consumption.any (fun s => s.good == .transport) then ["transport exempt (§ 13, stk. 1, nr. 15); non-scheduled commercial bus travel is taxable at 25 % (not separated)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .heatingOil) then ["5121 DK: excise on petrol, diesel, heatingOil not charged: the 2025 rate changed during the year and the purchase is undated (grade C)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .electricity || s.good == .gas || s.good == .tobaccoOther) then ["5121 DK: excise on electricity, natural gas and tobacco other than cigarettes not modelled (gap pass)"] else [])

#guard vat.embedded { good := .clothing, amount := 12500 } == 2500
#guard vat.net { turnover := 50000, sales := [{ good := .other, net := 50000 }] } == 0
#guard vat.embedded { good := .transport, amount := 125 } == 0
#guard excise.duty { good := .cigarettes, amount := 5000, quantity := 1000000 } == 1985
#guard excise.duty { good := .beer, amount := 300, quantity := 100000, abvBp := 500 } == 243
#guard excise.duty { good := .wine, amount := 800, quantity := 100000, abvBp := 1200 } == 1126
#guard excise.duty { good := .spirits, amount := 2000, quantity := 100000, abvBp := 4000 } == 6000

end DkGlobal.Consumption
