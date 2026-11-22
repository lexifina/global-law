import TaxKernel.Global2
import R5Common

/-!
# Armenia 2025: VAT (5111) and excise (5121), Tax Code ՀՕ-165-Ն

Source: Global law `armenia/national/acts/code/2016/ՀՕ-165-Ն`, read as in force on 2025-07-01
(`law/gl_vat_excise_2025-07-01.txt`, `law/gl_vat_payers_2025-07-01.txt`; official text arlis.am).
* art. 63(1) (last changed ՀՕ-285-Ն, in force 2025-01-01): "ԱԱՀ-ն հաշվարկվում է 20 տոկոս դրույքաչափով" except the
  exempt (art. 64) and zero-rated (art. 65) supplies.
* art. 59(4)(1): a person is a VAT payer from 1 January if its previous year's turnover "գերազանցել է 115 միլիոն
  դրամը" (one year is seen: this year's turnover is used).
* art. 64(2) exemptions used for the basket: 1)-5) general education, 11) medical care services, 12) medical goods
  (not applied to `medicines`: the item names medical-purpose goods, not medicines generally), 24) newspapers and
  magazines, 44) insurance, 47) banking and financial services.
* art. 85(1): the excise base is the quantity in the natural units of art. 88.
* art. 88(1) table, 2025 column (last changed ՀՕ-452-Ն, in force 2025-07-01): row 2 spirits 4 200 դրամ per litre;
  row 6 beer 150, row 7 grape wine 165 per litre; row 10 tobacco products 17 700 per 1 000 sticks; row 17 petrol
  43 600 and row 18 diesel 14 200 per tonne. art. 88(1) second sentence: rows 1, 2, 3, 10, 14 and 15 at the printed
  rates; every other row times the art. 88(2) coefficient, 1.16 from 1 January 2025.
* art. 88(3): spirits (2208) above 40 % vol: + 7.5 դրամ per litre for each whole point above 40 %.
-/

namespace AmGlobal
open TaxKernel TaxKernel.Global R5Common

/-- art. 63(1): 20 %. -/
def vatStd : Int := 2000
/-- art. 59(4)(1): 115 million դրամ turnover. -/
def vatThreshold : Int := 115000000
/-- art. 88(2): coefficient 1.16 for 2025 (per 100). -/
def coef2025 : Int := 116

def aah : Vat :=
  { name := "Ավելացված արժեքի հարկ (ԱԱՀ)", standard := vatStd, threshold := vatThreshold,
    classOf := fun g => match g with
      | .education | .health | .newspapers | .insurance | .financial => .exempt
      | _ => .standard }

/-- art. 88(1) row 2 and (3): spirits per litre, + 7.5 per whole point above 40 % vol. -/
def spiritsDuty (s : Spend) : Int :=
  let extraTenths : Int := if s.abvBp > 4000 then 75 * ((s.abvBp - 4000) / 100) else 0
  divR .down (s.quantity * (42000 + extraTenths)) 10000

def ratePerLitre (g : Good) : Option (Int × Int × String) :=
  match g with
  | .beer => some (150 * coef2025, 100, "art. 88(1) row 6 (150 per litre) × art. 88(2) 1.16")
  | .wine => some (165 * coef2025, 100, "art. 88(1) row 7 (165 per litre) × art. 88(2) 1.16")
  | .cigarettes => some (17700, 1000, "art. 88(1) row 10 (17 700 per 1 000 sticks, not × coefficient)")
  | _ => none

def exciseDuty (s : Spend) : Option (Int × String) :=
  if s.good == .spirits then some (spiritsDuty s, "art. 88(1) row 2 (4 200 per litre), art. 88(3)")
  else match ratePerLitre s.good with
    | some (n, d, st) => some (divR .down (s.quantity * n) (d * 1000), st)
    | none => none

/-- art. 88(1) rows 17-18 × art. 88(2) 1.16, per tonne (kernel 2.1 `ExciseRule` per mass: the line's `"massG"`; the
code prints no density). The art. 88(7) floor on petrol (excise + VAT per tonne ≥ 135 000 × 1.16) is not applied. -/
def fuel : List ExciseRule :=
  [{ good := .petrol, name := "Ակցիզային հարկ", perKgNum := 43600 * coef2025, perKgDen := 100 * 1000,
     statute := "Tax Code art. 88(1) row 17 (43 600 per tonne) × art. 88(2) 1.16" },
   { good := .diesel, name := "Ակցիզային հարկ", perKgNum := 14200 * coef2025, perKgDen := 100 * 1000,
     statute := "Tax Code art. 88(1) row 18 (14 200 per tonne) × art. 88(2) 1.16" }]

def consumption : Family :=
  { name := "5111 ԱԱՀ, 5121 ակցիզային հարկ", covers := [.vat, .excise],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else
        [aah.basketCharge g.consumption "Tax Code art. 63(1) (20 %), art. 64(2) 1)-5), 11), 24), 44), 47)"])
      ++ (if g.entity == .company && !g.company.sales.isEmpty then
            [aah.businessCharge g.company "Tax Code art. 59(4) (115 M threshold), art. 63"] else [])
      ++ (g.consumption.filterMap fun s => (exciseDuty s).map fun (d, st) =>
            exciseCharge "Ակցիզային հարկ" s d s!"Tax Code {st}")
      ++ exciseRuleCharges fuel g }

def consumptionUnsupported (g : CanonGlobal) : List String :=
  (if (consumptionX g).any (fun (s, x) => (s.good == .petrol || s.good == .diesel) && x.massG < 0) then
    ["excise on petrol/diesel is per tonne (art. 88(1) rows 17-18): give the line's massG (the code prints no density); without it the duty is 0"] else [])
  ++ (if g.consumption.any (·.good == .petrol) then ["art. 88(7) floor on petrol (excise + VAT ≥ 135 000 × 1.16 per tonne) not applied"] else [])
  ++ (if g.consumption.any (·.good == .tobaccoOther) then ["excise on cigars, heated tobacco and liquids (art. 88(1) rows 11-15): units not in the basket; not computed"] else [])
  ++ (if g.consumption.any (·.good == .rent) then ["rent: VAT applies only when the landlord is a VAT payer (art. 59); the basket's rent is taxed at 20 %"] else [])

-- art. 63(1): 20 % inside 12 000 is 2 000
#guard aah.embedded { good := .food, amount := 12000 } == 2000
-- one tonne of petrol: 43 600 × 1.16 = 50 576
#guard (fuel.getD 0 default).dutyOn { good := .petrol, amount := 900000, quantity := 1350000 } { massG := 1000000 } == 50576
#guard aah.embedded { good := .education, amount := 12000 } == 0
-- art. 59(4): at the threshold no VAT, above it output − input
#guard aah.net { turnover := 115000000, sales := [{ good := .other, net := 115000000 }] } == 0
#guard aah.net { turnover := 115000001, sales := [{ good := .other, net := 115000001 }], inputs := [{ good := .other, net := 1000000 }] } == 23000000 - 200000
-- art. 88: 1 litre of 40 % spirits 4 200; of 45 % 4 200 + 5 × 7.5; 1 litre of beer 174; 20 cigarettes 354
#guard spiritsDuty { good := .spirits, amount := 0, quantity := 1000, abvBp := 4000 } == 4200
#guard spiritsDuty { good := .spirits, amount := 0, quantity := 1000, abvBp := 4500 } == 4237
#guard (exciseDuty { good := .beer, amount := 0, quantity := 1000 }).map (·.1) == some 174
#guard (exciseDuty { good := .cigarettes, amount := 0, quantity := 20000 }).map (·.1) == some 354

end AmGlobal
