import AdGlobal.Pit

/-!
# AD 2025: Consumption family not reached (grade C)

* 5111 VAT (Llei 11/2012 de l'impost general indirecte (IGI)): tried bopa.ad not fetched; 1.x law folder holds only IRPF articles; Global law (the 1.x source) not used (coordinator, 2026-11-21); would unlock: the IGI law consolidated as in force 2025 (bopa.ad)
* 5121 Excise duties (Llei de l'impost especial sobre ...): tried not reached in the P1 pass; would unlock: the excise act's 2025 rate articles


## 5111 Impost general indirecte (pass 9, grade B)
Source: Llei 11/2012, del 21 de juny, de l'impost general indirecte, BOPA núm. 33 (18.7.2012), consellgeneral.ad (`ad/law/llei11_2012.pdf`).
* art. 57: "El tipus de gravamen general és d'un 4,5%"; art. 58: reduced 1 % on food and non-alcoholic drinks, water, books, newspapers and magazines, private lessons
* art. 59: super-reduced 0 % on hospital and health care by public or conventioned providers, social assistance, education by authorised bodies, sport; art. 60: increased 9,5 % on banking and financial services
* grade B: the 2012 text is read; later amendments (for instance a 2,5 % special rate) are not


## 5111 IGI: 2025 text read, back to A, three classes corrected (gap pass, grade C)
Source: BOPA; read from lexifina/andorra-law `lleis/2012-011, 2014-010, 2017-003, 2019-003, 2022-017, 2022-041, 2025-005` (commit c0fc158, 6327902, bf9a6cb, fa9fc9d, 7e01567, f4a9261, f246318, in force 2013-2025).
* art. 57: "El tipus de gravamen general és d'un 4,5%"
* art. 58 (Llei 10/2014): 1 % for food, non-alcoholic drinks, water, books and newspapers
* art. 59 (Llei 3/2019): 0 % for health and hospital care, social care, education, residential rent and medicines reimbursed by the CASS
* art. 60 bis (Llei 3/2017): "El tipus de gravamen especial és del 2,5%" (passenger transport, private cultural services, art)
* art. 60: 9,5 % on banking and financial services
* Corrections: residential rent was charged 4,5 % (now 0 %), passenger transport 4,5 % (now 2,5 %), medicines 4,5 % (now 0 %)


## 5121 Impostos especials (alcohol, carburants) (gap pass, grade B)
Source: BOPA; read from lexifina/andorra-law `lleis/2008-027, lleis/2021-019` (commit ddf225c, 274d010, in force 22.1.2009 / 11.8.2021).
* art. 20: "25 euros per hectolitre d'alcohol pur" for beer, wine and spirits alike
* art. 28 (Llei 19/2021): petrol RON 95-98 0,407584 EUR per litre, gas oil 0,247035, heating gas oil 0,027176, plus the CO2 element (30 EUR per tonne: 0,0648 petrol, 0,0765 gas oil)
* cigarettes: an excise of 0,02 EUR per pack (art. 12, Llei 1/2022) and a consumption tax under Llei 11/2024 of 3,012439 or 5,020732 EUR per pack depending on the regime of origin: not modelled
-/

namespace AdGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Impost general indirecte", standard := 450, reduced := 100, reduced2 := 950, superReduced := 250, threshold := 0,
    classOf := fun gd => match gd with
      | .food | .nonAlcoholic | .water | .books | .newspapers => .reduced
      | .health | .education | .rent | .medicines => .zero
      | .financial => .reduced2
      | .transport => .superReduced
      | _ => .standard }

def vatStatute : String := "Llei 11/2012 de l'impost general indirecte art. 57 (4,5 %), 58 (1 %), 59 (0 %), 60 (9,5 %)"

def excise : Excise :=
  { rates := [
      { good := .spirits, name := "Impost sobre l'alcohol", perUnitNum := 25, perUnitDen := 100, onPureAlcohol := true, statute := "Llei 27/2008 art. 20: 25 euros per hectolitre d'alcohol pur" },
      { good := .beer, name := "Impost sobre l'alcohol (cervesa)", perUnitNum := 25, perUnitDen := 100, onPureAlcohol := true, statute := "Llei 27/2008 art. 20: 25 euros per hectolitre d'alcohol pur" },
      { good := .wine, name := "Impost sobre l'alcohol (vi)", perUnitNum := 25, perUnitDen := 100, onPureAlcohol := true, statute := "Llei 27/2008 art. 20: 25 euros per hectolitre d'alcohol pur" },
      { good := .petrol, name := "Impost sobre els carburants (gasolina 95-98)", perUnitNum := 472384, perUnitDen := 1000000, statute := "Llei 27/2008 art. 28 (redacció Llei 19/2021 art. 6): 0,407584 + element CO2 0,0648 euros per litre" },
      { good := .diesel, name := "Impost sobre els carburants (gasoil)", perUnitNum := 323535, perUnitDen := 1000000, statute := "Llei 27/2008 art. 28 (redacció Llei 19/2021): 0,247035 + element CO2 0,0765 euros per litre" },
      { good := .heatingOil, name := "Impost sobre els carburants (gasoil de calefacció)", perUnitNum := 103676, perUnitDen := 1000000, statute := "Llei 27/2008 art. 28 (redacció Llei 19/2021): 0,027176 + element CO2 0,0765 euros per litre" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Impost general indirecte (pass 9)", covers := [.vat, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption }]

def absent : List Absent :=
  []

def notes : List String := ["AD 5111 pass 9: BOPA 33/2012 (original text; later amendments not read) (grade B)", "AD gap pass: 5111 IGI: 2025 text read, back to A, three classes corrected", "AD 5121 gap pass: Impostos especials (alcohol, carburants) (B, law as enacted with the amending laws found in the repository (Llei 19/2021, Llei 1/2022) applied; no consolidated text, later amendments not excluded (grade B))"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .health || s.good == .education) then ["health and education taken at 0 % (art. 59: only when supplied by public, conventioned or authorised providers)"] else [])
  ++ (if g.entity == .company then ["no registration threshold applied (not read)"] else [])
  ++ (if g.consumption.any (fun s => s.good == .cigarettes || s.good == .tobaccoOther) then ["5121 AD tobacco not modelled (Llei 11/2024 consumption tax by regime of origin)"] else [])

#guard vat.embedded { good := .clothing, amount := 10450 } == 450
#guard vat.embedded { good := .food, amount := 10100 } == 100
#guard vat.embedded { good := .financial, amount := 10950 } == 950
#guard vat.embedded { good := .health, amount := 10000 } == 0
#guard vat.embedded { good := .transport, amount := 10250 } == 250
#guard vat.embedded { good := .rent, amount := 10000 } == 0
#guard excise.duty { good := .spirits, amount := 2000, quantity := 100000, abvBp := 4000 } == 10
#guard excise.duty { good := .beer, amount := 300, quantity := 100000, abvBp := 500 } == 1
#guard excise.duty { good := .wine, amount := 800, quantity := 100000, abvBp := 1200 } == 3
#guard excise.duty { good := .petrol, amount := 1700, quantity := 1000000 } == 472
#guard excise.duty { good := .diesel, amount := 1600, quantity := 1000000 } == 323
#guard excise.duty { good := .heatingOil, amount := 1000, quantity := 1000000 } == 103

end AdGlobal.Consumption
