import HrGlobal.Pit
import TaxKernel.Global2

/-!
# HR 2025: Porez na dodanu vrijednost (5111); excises not modelled in this pass

Source: Narodne novine (official gazette): Zakon o izmjenama i dopunama Zakona o PDV-u NN 39/2022 (čl. 38 as replaced), NN 35/2024, NN 152/2024 (`hr/law/nn2022_39_478_pdv.html`, `nn2024_35_539_pdv.html`, `nn2024_152_2508_pdv.html`); no consolidated official text; sha256 in `law/SHA256SUMS`.
* čl. 38 (1): "PDV se obračunava i plaća po stopi od 25%." (2): "po sniženoj stopi od 5% na isporuke ...: a) sve vrste kruha, b) sve vrste mlijeka ..., c) knjige ..., d) lijekove ..., j) jestiva ulja i masti ..., l) ... svježeg ili rashlađenog mesa ..., o) ... svježe ili rashlađene ribe ..., r) ... svježeg ili rashlađenog povrća ..., s) ... svježeg i suhog voća ..., t) ... svježih jaja"
* čl. 38 (3): "po sniženoj stopi od 13% ...: a) usluge smještaja ..., b) novine i časopise ..., e) isporuku vode ..., f) isporuku električne energije ..., g) isporuku prirodnog plina i grijanja ..., l) pripremanje i usluživanje jela i slastica u ugostiteljskom objektu"
* čl. 90 (1) (NN 152/2024): "čiji godišnji promet u tuzemstvu nije bio veći od 60.000,00 eura oslobođen je plaćanja PDV-a"

## FT review (2026-11-21, third pass): natural gas
**Zakon o izmjeni Zakona o PDV-u, NN 52/2025** (`hr/law/nn2025_52_673.html`, in force 30.3.2025), čl. 1: "u članku 38.
stavku 4. riječi: »31. ožujka 2025.« zamjenjuju se riječima: »31. ožujka 2026.«. U stavku 5. riječi: »31. ožujka 2025.«
zamjenjuju se riječima: »31. ožujka 2026.«." Čl. 38 st. 4 (NN 39/2022 wording, extended by NN 35/2024 and NN 52/2025):
"na isporuke prirodnog plina, uključujući naknade vezane uz tu isporuku ... PDV se obračunava i plaća po sniženoj stopi
od 5%". So natural gas bears 5 % for the whole of 2025 (the model gave the `gas` line the standard 25 %).


## 5121 Excise duties (alcohol, tobacco, motor and heating fuel) (gap pass, grade B)
Source: European Commission, Taxes in Europe Database (TEDB), HR excise records for the situation on 1 July 2025 (tobacco 4044, alcohol 4042, energy 4043; data supplied by the member state; REST service of the TEDB web application, read 2026-11-21, held as `hr/law/tedb_*.json`).
* TEDB HR beer (1.7.2025): 5.31 EUR per hl and % vol (= per litre of pure alcohol)
* TEDB HR still wine (1.7.2025): 0 EUR per hl of product
* TEDB HR ethyl alcohol (1.7.2025): 796.34 EUR per hl of pure alcohol
* TEDB HR energy products (1.7.2025): unleaded petrol 512.31 EUR per 1 000 l
* TEDB HR energy products (1.7.2025): gas oil used as propellant 406.13 EUR per 1 000 l
* TEDB HR energy products (1.7.2025): gas oil used as heating fuel (non-business use) 56.14 EUR per 1 000 l


## 5121 Trošarina na cigarete (stope od 1.7.2025.) (gap pass 2) (gap pass, grade B)
Source: EC TEDB tax 4044 (Excise duty on manufactured tobacco), situations 1.1 and 1.7.2025 (`tools/in_gap/tedb/tax_HR_4044_*.json`).
* Zakon o trošarinama; TEDB HR 4044 at 1.1.2025: 53,10 EUR / 1 000 + 34 %, minimum 117,87 EUR
* Zakon o trošarinama; TEDB HR 4044 at 1.7.2025 (rates for cigarettes applicable as from 01/07/2025): 56,10 EUR / 1 000 + 34 %, minimum 124,20 EUR
-/

namespace HrGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Porez na dodanu vrijednost", standard := 2500, reduced := 1300, superReduced := 500, threshold := 60000,
    classOf := fun gd => match gd with
      | .health | .education | .financial | .insurance | .rent => .exempt
      | .food | .books | .medicines | .gas => .superReduced
      | .hotels | .newspapers | .water | .electricity | .restaurants => .reduced
      | _ => .standard }

def vatStatute : String := "Zakon o PDV-u čl. 38 st. 1-3 (25 %, 5 %, 13 %; NN 39/22), st. 4-5 (NN 35/24: to 31.3.2025); čl. 90 st. 1 (60.000,00 eura; NN 152/24)"

def excise : Excise :=
  { rates := [
      { good := .beer, name := "Excise duty on beer", perUnitNum := 531, perUnitDen := 100, onPureAlcohol := true, statute := "TEDB HR beer (1.7.2025): 5.31 EUR per hl and % vol (= per litre of pure alcohol)" },
      { good := .wine, name := "Excise duty on still wine", statute := "TEDB HR still wine (1.7.2025): 0 EUR per hl of product" },
      { good := .spirits, name := "Excise duty on ethyl alcohol", perUnitNum := 39817, perUnitDen := 5000, onPureAlcohol := true, statute := "TEDB HR ethyl alcohol (1.7.2025): 796.34 EUR per hl of pure alcohol" },
      { good := .petrol, name := "Excise duty on unleaded petrol", perUnitNum := 51231, perUnitDen := 100000, statute := "TEDB HR energy products (1.7.2025): unleaded petrol 512.31 EUR per 1 000 l" },
      { good := .diesel, name := "Excise duty on gas oil used as propellant", perUnitNum := 40613, perUnitDen := 100000, statute := "TEDB HR energy products (1.7.2025): gas oil used as propellant 406.13 EUR per 1 000 l" },
      { good := .heatingOil, name := "Excise duty on gas oil used as heating fuel (non-business use)", perUnitNum := 2807, perUnitDen := 50000, statute := "TEDB HR energy products (1.7.2025): gas oil used as heating fuel (non-business use) 56.14 EUR per 1 000 l" }] }

/-- Trošarina na cigarete (stope od 1.7.2025.) (gap pass 2; kernel 2.1 `ExciseRule` date windows). -/
def gxDated0 : ExciseRule :=
  { good := .cigarettes,   name := "Trošarina na cigarete",   perUnitNum := 5310,   perUnitDen := 100000,   adValoremBp := 3400,   minNum := 11787,   minDen := 100000,   validTo := "2025-07-01",   statute := "Zakon o trošarinama; TEDB HR 4044 at 1.1.2025: 53,10 EUR / 1 000 + 34 %, minimum 117,87 EUR" }
def gxDated1 : ExciseRule :=
  { good := .cigarettes,   name := "Trošarina na cigarete",   perUnitNum := 5610,   perUnitDen := 100000,   adValoremBp := 3400,   minNum := 12420,   minDen := 100000,   validFrom := "2025-07-01",   statute := "Zakon o trošarinama; TEDB HR 4044 at 1.7.2025 (rates for cigarettes applicable as from 01/07/2025): 56,10 EUR / 1 000 + 34 %, minimum 124,20 EUR" }

def gxDatedRules : List ExciseRule := [gxDated0, gxDated1]

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Porez na dodanu vrijednost", covers := [.vat, .excise, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption
       ++ exciseRuleCharges gxDatedRules g }]

def absent : List Absent :=
  []

def notes : List String := ["HR 5111: NN 39/2022 as amended by NN 113/2022, 35/2024, 152/2024 (in force 1.1.2025)", "HR 5121 gap pass: Excise duties (alcohol, tobacco, motor and heating fuel) (B, TEDB situation on 1.7.2025)", "HR 5121 gap pass 2: Trošarina na cigarete (stope od 1.7.2025.) (B, change on 1.7.2025 as stated by the TEDB record)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .rent || s.good == .financial || s.good == .insurance) then ["exempt supplies taken from the act's structure (EU/EEA standard exemptions), not quoted item by item"] else [])
  ++ (if g.consumption.any (fun s => s.good == .food) then ["food at 5 %: the staples of čl. 38 (2) (bread, milk, oils, fresh meat, fish, fruit, vegetables, eggs, baby food); other processed food is 25 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .heatingOil) then ["district heating at 5 % (st. 5, to 31.3.2026 by NN 52/2025): not a household category here"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Zakon o trošarinama (not read)) not modelled in this pass"] else [])
  ++ (if g.consumption.any (fun s => s.good == .electricity || s.good == .gas || s.good == .tobaccoOther) then ["5121 HR: excise on electricity, natural gas and tobacco other than cigarettes not modelled (gap pass)"] else [])

#guard vat.embedded { good := .clothing, amount := 12500 } == 2500
#guard vat.embedded { good := .hotels, amount := 11300 } == 1300
#guard vat.embedded { good := .food, amount := 10500 } == 500
#guard vat.net { turnover := 60000, sales := [{ good := .other, net := 60000 }] } == 0
#guard vat.embedded { good := .gas, amount := 105 } == 5
#guard excise.duty { good := .beer, amount := 300, quantity := 100000, abvBp := 500 } == 26
#guard excise.duty { good := .wine, amount := 800, quantity := 100000, abvBp := 1200 } == 0
#guard excise.duty { good := .spirits, amount := 2000, quantity := 100000, abvBp := 4000 } == 318
#guard excise.duty { good := .petrol, amount := 1700, quantity := 1000000 } == 512
#guard excise.duty { good := .diesel, amount := 1600, quantity := 1000000 } == 406
#guard excise.duty { good := .heatingOil, amount := 1000, quantity := 1000000 } == 56
#guard gxDated0.dutyOn { good := .cigarettes, amount := 5000, quantity := 1000000 } {} == 1753
#guard gxDated1.dutyOn { good := .cigarettes, amount := 5000, quantity := 1000000 } {} == 1756
#guard gxDated0.windowDays 2025 + gxDated1.windowDays 2025 == 365

end HrGlobal.Consumption
