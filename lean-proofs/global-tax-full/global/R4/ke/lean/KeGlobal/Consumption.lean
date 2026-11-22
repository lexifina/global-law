import R4Common

/-!
# Kenya 2025: VAT (5111) and excise duty (5121)

Sources (Kenya Law consolidations at 2025-07-01, archived by the registry):
* **VAT Act No. 35 of 2013** (`global/registry/afm_data/fetch/KE/ke_vat2.html.txt`): s. 5 (2) "The rate of tax shall
  be— (a) in the case of a zero-rated supply, zero per cent; … (b) in any other case, sixteen per cent of the taxable
  value". First Schedule (exempt supplies): medicaments (heading 3003-3004), "Supply by way of sale, renting, leasing,
  hiring, letting of land or residential premises", "financial services", "Insurance and reinsurance services",
  "Transportation of passengers by any means of conveyance excluding international air transport", unprocessed milk,
  eggs and vegetables. Second Schedule (zero-rated): "27. Liquefied Petroleum Gas" (Act No. 4 of 2023, s. 38).
* **Excise Duty Act No. 23 of 2015**, First Schedule (`…/KE/ke_exc.html.txt`): "Beer, Cider, … of alcoholic strength
  not exceeding 6% KSh. 22.50 per centilitre of pure alcohol"; "Wines including fortified wines … KSh. 22.50 per
  centilitre of pure alcohol"; "Spirits of undenatured ethyl alcohol; spirits liqueurs and other spirituous beverages of
  alcoholic strength exceeding 6% KSh. 10 per centilitre of pure alcohol" (as printed); "Cigarette with filters …
  KSh. 4,100 per mille"; "Bottled or similarly packaged waters and other non-alcoholic beverages, not including fruit
  or vegetable juices. Shs. 6.41 per litre"; "2710.12.20 Motor Spirit (gasoline) premium per 1000 litres @ 20degC
  21,953.02"; "2710.19.31 Gas oil (automotive …) per 1000 litres @ 20degC 11,370.99". Specific rates only: no base
  question.
-/

namespace KeGlobal
open TaxKernel TaxKernel.Global

def vatK : Vat :=
  { name := "Value Added Tax", standard := 1600,
    classOf := fun gd => match gd with
      | .gas => .zero
      | .medicines | .rent | .financial | .insurance | .transport => .exempt
      | _ => .standard }

def vat : Family := R4.vatFamily vatK "VAT Act 2013 s. 5 (2) (16 %); First Schedule (exempt), Second Schedule para 27 (LPG zero-rated)"

def excises : List R4.Exc :=
  [ { good := .beer, name := "Excise duty (beer)", perUnitNum := 2250, onPureAlcohol := true, maxAbvBp := 600,
      statute := "Excise Duty Act First Schedule (KSh 22.50 per cl of pure alcohol)" },
    { good := .wine, name := "Excise duty (wines)", perUnitNum := 2250, onPureAlcohol := true,
      statute := "Excise Duty Act First Schedule (KSh 22.50 per cl of pure alcohol)" },
    { good := .spirits, name := "Excise duty (spirits)", perUnitNum := 1000, onPureAlcohol := true, minAbvBp := 600,
      statute := "Excise Duty Act First Schedule (KSh 10 per cl of pure alcohol, as printed)" },
    { good := .nonAlcoholic, name := "Excise duty (waters and non-alcoholic beverages)", perUnitNum := 641, perUnitDen := 100,
      statute := "Excise Duty Act First Schedule (Shs 6.41 per litre)" },
    { good := .cigarettes, name := "Excise duty (cigarettes)", perUnitNum := 4100, perUnitDen := 1000,
      statute := "Excise Duty Act First Schedule (KSh 4,100 per mille)" },
    { good := .petrol, name := "Excise duty (motor spirit)", perUnitNum := 2195302, perUnitDen := 100000,
      statute := "Excise Duty Act First Schedule 2710.12.20 (21,953.02 per 1000 l, premium)" },
    { good := .diesel, name := "Excise duty (gas oil)", perUnitNum := 1137099, perUnitDen := 100000,
      statute := "Excise Duty Act First Schedule 2710.19.31 (11,370.99 per 1000 l)" } ]

def excise : Family := R4.exciseFamily "excise duty (Excise Duty Act 2015, First Schedule)" excises

def consumptionNotes (g : CanonGlobal) : List String :=
  (if g.consumption.any (·.good == .food) then
     ["VAT Act First and Second Schedules: unprocessed milk, eggs, vegetables and other listed foods are exempt or zero-rated; the food line is taxed at 16 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .education || s.good == .health) then
     ["VAT Act First Schedule Part II: educational and medical services not located in the archived text: taxed at 16 %"] else [])
  ++ (if g.consumption.any (fun s => s.good == .beer && s.abvBp > 600) then ["beer above 6 % vol: excise line not mapped"] else [])
  ++ (if !g.consumption.isEmpty then ["Railway Development Levy, Import Declaration Fee, Road Maintenance Levy: not modelled"] else [])

-- 1 litre of 5 % beer = 5 cl of pure alcohol: KSh 112.50
#guard (R4.exciseCharges excises [{ good := .beer, amount := 300, quantity := 1000, abvBp := 500 }]).map (·.due) == [112]
-- 20 cigarettes: KSh 82
#guard (R4.exciseCharges excises [{ good := .cigarettes, amount := 350, quantity := 20000 }]).map (·.due) == [82]
-- 1 000 litres of premium petrol: KSh 21 953
#guard (R4.exciseCharges excises [{ good := .petrol, amount := 0, quantity := 1000000 }]).map (·.due) == [21953]
#guard vatK.embedded { good := .other, amount := 11600 } == 1600
#guard vatK.embedded { good := .rent, amount := 11600 } == 0

end KeGlobal
