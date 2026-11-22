import TaxKernel.Global2
import R5Common

/-!
# United Arab Emirates 2025: VAT (5111); excise tax (5121)

Sources: Executive Regulation of Federal Decree-Law No. 8 of 2017 on VAT (Cabinet Decision No. 52 of 2017 as amended
by Cabinet Decisions 46/2020 … 100/2024, 100/2025 (from 29 Sep 2025) and 149/2026 (from 1 Oct 2026)), FTA
consolidation `law/vat_fdl8_2017_consol_2026-09.pdf` ("not an official translation"; the articles used carry no 2025
or 2026 amendment note):
* art. 1: "Standard rate: The Tax rate specified in Article 3 of the Decree-Law." The Decree-Law itself was not
  reached (uaelegislation.gov.ae answered HTML, government.ae refused); its 5 % rate is from the official news agency
  WAM ("President issues VAT Decree-Law", 2017): **grade B**.
* art. 7(1): "The Mandatory Registration Threshold shall be AED 375,000".
* art. 40 zero-rating of education services; art. 41 zero-rating of healthcare services; art. 42 financial services
  (exempt, except fee-based ones); art. 43 exemption of residential buildings (rent); art. 45 exemption of local
  passenger transport.
* Excise: Cabinet Decision No. 52 of 2019 and its amendments, MOF consolidation "as published by the Ministry of
  Finance" of 18 Sep 2025 (to CD 99/2025, effective 9 Sep 2025, which amended art. 3 only), archived on the FTA site
  2025-10-13 (`law/cd52_2019_amended_20250918.pdf`): art. 12 "Tobacco and tobacco products 100% … Carbonated drinks
  50% Energy drinks 100% Sweetened drinks 50%"; art. 13 excise price = the higher of the FTA standard price list
  and the retail sales price less tax (the list floor is not applied). Rate on the price before excise and VAT.
-/

namespace AeGlobal
open TaxKernel TaxKernel.Global R5Common

def vat : Vat :=
  { name := "Value Added Tax", standard := 500, threshold := 375000,
    classOf := fun g => match g with
      | .education | .health => .zero
      | .financial | .rent | .transport => .exempt
      | _ => .standard }

def drink (sub : String) (bp : Int) (what : String) : ExciseRule :=
  { good := .nonAlcoholic, sub, name := "Excise Tax", adValoremBp := bp, valueBase := .beforeTax, vatBp := 500,
    statute := s!"Cabinet Decision 52/2019 (as amended to 99/2025) art. 12: {what}" }

def excise : List ExciseRule :=
  [drink "softDrinks" 5000 "carbonated drinks 50 %", drink "sweetenedDrinks" 5000 "sweetened drinks 50 %",
   drink "energyDrinks" 10000 "energy drinks 100 %",
   { good := .cigarettes, name := "Excise Tax", adValoremBp := 10000, valueBase := .beforeTax, vatBp := 500,
     statute := "Cabinet Decision 52/2019 art. 3, 12: tobacco and tobacco products 100 %" },
   { good := .tobaccoOther, name := "Excise Tax", adValoremBp := 10000, valueBase := .beforeTax, vatBp := 500,
     statute := "Cabinet Decision 52/2019 art. 3, 12: tobacco and tobacco products 100 %" }]

def consumption : Family :=
  { name := "5111 VAT, 5121 excise tax", covers := [.vat, .excise],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else
        [vat.basketCharge g.consumption "FDL 8/2017 art. 3 (5 %, via WAM); Exec. Reg. art. 40, 41 (zero), 42, 43, 45 (exempt)"])
      ++ (if g.entity == .company && !g.company.sales.isEmpty then
            [vat.businessCharge g.company "Exec. Reg. art. 7(1) (AED 375,000), art. 55 (apportionment)"] else [])
      ++ exciseRuleCharges excise g }

def consumptionUnsupported (g : CanonGlobal) : List String :=
  (if g.consumption.any (·.good == .medicines) then ["medicines: zero-rating of designated medicines (Cabinet list) not read; taxed at 5 %"] else [])
  ++ (if g.consumption.any (·.good == .insurance) then ["insurance: life insurance exempt (art. 42), other insurance taxed: all taxed at 5 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .cigarettes || s.good == .tobaccoOther) then
    ["tobacco excise: the FTA standard price list floor (CD 52/2019 art. 13) not applied"] else [])
  ++ (if (consumptionX g).any (fun (s, x) => s.good == .nonAlcoholic && x.sub == "") then
    ["nonAlcoholic lines without sub (softDrinks/sweetenedDrinks/energyDrinks): no excise applied"] else [])

#guard vat.embedded { good := .food, amount := 10500 } == 500
#guard vat.embedded { good := .education, amount := 10500 } == 0
#guard vat.net { turnover := 375000, sales := [{ good := .other, net := 375000 }] } == 0
-- a zero-rated supplier recovers its input tax (pro rata counts zero-rated supplies as taxable)
#guard vat.net { turnover := 1000000, sales := [{ good := .education, net := 1000000 }], inputs := [{ good := .other, net := 200000 }] } == -10000

-- 100 % on the price before excise and VAT: 210 = 100 + 100 + 5 % VAT
#guard (excise.getD 2 default).dutyOn { good := .nonAlcoholic, amount := 210 } { sub := "energyDrinks" } == 100
#guard (excise.getD 0 default).dutyOn { good := .nonAlcoholic, amount := 1575 } { sub := "softDrinks" } == 500

end AeGlobal
