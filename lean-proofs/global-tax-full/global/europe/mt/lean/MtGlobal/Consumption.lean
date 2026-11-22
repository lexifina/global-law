import MtGlobal.Pit

/-!
# MT 2025: Value Added Tax (5111); excises not modelled in this pass

Source: Value Added Tax Act, Cap. 406, legislation.mt consolidated PDF (official; it lists amendments up to Act III of 2026 and Legal Notices of 2026, so the 2025 wording is read through an unchanged rate structure), `mt/law/cap406.pdf`; sha256 in `law/SHA256SUMS`.
* art. 19: tax "at the rate of eighteen per cent of the taxable value of the supply"
* Eighth Schedule: "The letting of or the provision of accommodation in any premises ... 7%"; "2. The supply of electricity. 5%"

## FT review (2026-11-21, second pass): Fifth Schedule exemptions (ftd_ec_tedb_vat_2025 dev failures)
Same consolidation (`mt/law/cap406.pdf`, `cap406.txt`), Fifth Schedule:
* **Part One "Exemptions with credit"** (art. 2 "exempt with credit supply": no tax charged, input tax deductible):
  item 9 "The supply of food for human consumption, excluding food supplied in the course of catering."; item 10 "The
  supply of pharmaceutical goods."; item 11 "The supply of: (a) transport by scheduled bus service consisting of trips
  on scheduled routes; (b) scheduled inter-island sea transport of passengers ...; (e) scheduled passenger transport
  services by means of public lift". The household's `transport` is read as scheduled public passenger transport.
* **Part Two "Exemptions without credit"**, item 15 "The supply of water services by a public authority." (the
  household's `water` is the public supply): no tax charged on the supply.


## 5121 Excise duties (alcohol, tobacco, motor and heating fuel) (gap pass, grade B)
Source: European Commission, Taxes in Europe Database (TEDB), MT excise records for the situation on 1 July 2025 (tobacco 4134, alcohol 4131, energy 4133; data supplied by the member state; REST service of the TEDB web application, read 2026-11-21, held as `mt/law/tedb_*.json`).
* TEDB MT manufactured tobacco (1.7.2025): 107 EUR per 1 000 cigarettes + 23.4 % of the retail selling price, at least 165 EUR per 1 000
* TEDB MT beer (1.7.2025): 4.6 EUR per hl and % vol (= per litre of pure alcohol)
* TEDB MT still wine (1.7.2025): 20.5 EUR per hl of product
* TEDB MT ethyl alcohol (1.7.2025): 1360 EUR per hl of pure alcohol
* TEDB MT energy products (1.7.2025): unleaded petrol 359 EUR per 1 000 l
* TEDB MT energy products (1.7.2025): gas oil used as propellant 330 EUR per 1 000 l
* TEDB MT energy products (1.7.2025): gas oil used as heating fuel (non-business use) 172.09 EUR per 1 000 l
-/

namespace MtGlobal.Consumption
open TaxKernel TaxKernel.Global

def vat : Vat :=
  { name := "Value Added Tax", standard := 1800, reduced := 700, superReduced := 500, threshold := 0,
    classOf := fun gd => match gd with
      | .hotels => .reduced
      | .electricity => .superReduced
      | .food | .medicines | .transport => .zero
      | .water => .exempt
      | _ => .standard }

def vatStatute : String := "VAT Act (Cap. 406) art. 19 (18 %); Eighth Schedule (7 % accommodation, 5 % electricity ...); Fifth Schedule Part One items 9-11 (food, pharmaceutical goods, scheduled passenger transport: exempt with credit), Part Two item 15 (water by a public authority: exempt)"

def excise : Excise :=
  { rates := [
      { good := .cigarettes, name := "Excise duty on cigarettes", perUnitNum := 107, perUnitDen := 1000, adValoremBp := 2340, minNum := 33, minDen := 200, statute := "TEDB MT manufactured tobacco (1.7.2025): 107 EUR per 1 000 cigarettes + 23.4 % of the retail selling price, at least 165 EUR per 1 000" },
      { good := .beer, name := "Excise duty on beer", perUnitNum := 23, perUnitDen := 5, onPureAlcohol := true, statute := "TEDB MT beer (1.7.2025): 4.6 EUR per hl and % vol (= per litre of pure alcohol)" },
      { good := .wine, name := "Excise duty on still wine", perUnitNum := 41, perUnitDen := 200, statute := "TEDB MT still wine (1.7.2025): 20.5 EUR per hl of product" },
      { good := .spirits, name := "Excise duty on ethyl alcohol", perUnitNum := 68, perUnitDen := 5, onPureAlcohol := true, statute := "TEDB MT ethyl alcohol (1.7.2025): 1360 EUR per hl of pure alcohol" },
      { good := .petrol, name := "Excise duty on unleaded petrol", perUnitNum := 359, perUnitDen := 1000, statute := "TEDB MT energy products (1.7.2025): unleaded petrol 359 EUR per 1 000 l" },
      { good := .diesel, name := "Excise duty on gas oil used as propellant", perUnitNum := 33, perUnitDen := 100, statute := "TEDB MT energy products (1.7.2025): gas oil used as propellant 330 EUR per 1 000 l" },
      { good := .heatingOil, name := "Excise duty on gas oil used as heating fuel (non-business use)", perUnitNum := 17209, perUnitDen := 100000, statute := "TEDB MT energy products (1.7.2025): gas oil used as heating fuel (non-business use) 172.09 EUR per 1 000 l" }] }

set_option linter.unusedVariables false in
def families : List Family :=
  [{ name := "5111 Value Added Tax", covers := [.vat, .excise],
     run := fun args g prev =>
       (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption vatStatute])
       ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company vatStatute] else [])
       ++ excise.charges g.consumption }]

def absent : List Absent :=
  []

def notes : List String := ["MT 5111: legislation.mt consolidation (to 2026)", "MT 5111 Value Added Tax: back to B (pass 17, 2025 text read)", "MT 5121 gap pass: Excise duties (alcohol, tobacco, motor and heating fuel) (B, TEDB situation on 1.7.2025)"]

set_option linter.unusedVariables false in
def unsupported (args : List String) (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .books || s.good == .newspapers || s.good == .transport || s.good == .restaurants) then ["books (5 %), newspapers and restaurant rates not read item by item: taken at 18 %; transport read as scheduled passenger transport (Fifth Schedule Part One item 11; taxis and other transport are taxable)"] else [])
  ++ (if g.entity == .company then ["small undertaking exemption (art. 11) not read: no threshold applied"] else [])
  ++ (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .cigarettes || s.good == .beer || s.good == .wine || s.good == .spirits) then ["excise (Excise Duty Act (Cap. 382)) not modelled in this pass"] else [])
  ++ (if g.consumption.any (fun s => s.good == .electricity || s.good == .gas || s.good == .tobaccoOther) then ["5121 MT: excise on electricity, natural gas and tobacco other than cigarettes not modelled (gap pass)"] else [])

#guard vat.embedded { good := .clothing, amount := 11800 } == 1800
#guard vat.embedded { good := .hotels, amount := 10700 } == 700
#guard vat.embedded { good := .electricity, amount := 10500 } == 500
#guard vat.embedded { good := .food, amount := 11800 } == 0
#guard vat.embedded { good := .medicines, amount := 11800 } == 0
#guard vat.embedded { good := .transport, amount := 11800 } == 0
#guard vat.embedded { good := .water, amount := 11800 } == 0
#guard vat.embedded { good := .other, amount := 11800 } == 1800
#guard excise.duty { good := .cigarettes, amount := 5000, quantity := 1000000 } == 1277
#guard excise.duty { good := .beer, amount := 300, quantity := 100000, abvBp := 500 } == 23
#guard excise.duty { good := .wine, amount := 800, quantity := 100000, abvBp := 1200 } == 20
#guard excise.duty { good := .spirits, amount := 2000, quantity := 100000, abvBp := 4000 } == 544
#guard excise.duty { good := .petrol, amount := 1700, quantity := 1000000 } == 359
#guard excise.duty { good := .diesel, amount := 1600, quantity := 1000000 } == 330
#guard excise.duty { good := .heatingOil, amount := 1000, quantity := 1000000 } == 172

end MtGlobal.Consumption
