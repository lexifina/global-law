import TaxKernel.Global2
import R5Common

/-!
# Georgia 2025: VAT (დღგ, 5111) and excise (აქციზი, 5121), Tax Code of Georgia (2010)

Source: Global law `georgia/national/acts/code/2010/3591`, as in force on 2025-07-01 (`law/gl_vat_excise_2025-07-01.txt`,
`law/gl_excise_alcohol_2025-07-01.txt`, `law/gl_vat_exempt_2025-07-01.txt`; official text matsne.gov.ge).
* art. 166 (last changed №7204-Iს, in force 2020-10-05): "დღგ-ის განაკვეთია 18 პროცენტი".
* art. 165(1) (in force 2023-04-18): registration when supplies in any continuous 12 calendar months exceed
  "100 000 ლარი".
* art. 171(1) exemptions without credit used for the basket: ა) financial operations/services; ვ) goods of HS 4901,
  4902, 4904 (books, newspapers, music); ლ) urban and intra-district passenger transport at regulated tariffs. The
  items of art. 171(2) are not in the record read (only its heading line): medical and education are taxed here.
* art. 188(1) (last changed №134-Iმს-XIმპ, in force 2025-01-01): HS 2402 20 cigarettes 1.9 ლარი per 20 sticks;
  art. 188(1¹) ა): plus "საცალო სარეალიზაციო ფასის 30 პროცენტი" (30 % of the retail price).
  Petrol (2710 12) 500 and diesel 400 ლარი per tonne.
* art. 188¹(1) (last changed №1935-რს, 23.12.2017): beer 0.12 ლარი per litre per 1 % vol; other fermented drinks
  above 5 % vol 5 ლარი per litre; spirits (2208 with more than 1.2 % vol, except the codes of row 7) 22.5 ლარი per
  litre of pure alcohol. Grape wine (2204) is outside the article's definitions: no excise.
-/

namespace GeGlobal
open TaxKernel TaxKernel.Global R5Common

def vatStd : Int := 1800
def vatThreshold : Int := 100000

def dgg : Vat :=
  { name := "დამატებული ღირებულების გადასახადი (დღგ)", standard := vatStd, threshold := vatThreshold,
    classOf := fun g => match g with
      | .financial | .books | .newspapers | .transport => .exempt
      | _ => .standard }

def aqcizi : Excise :=
  { rates := [
      { good := .beer, name := "აქციზი", perUnitNum := 12, onPureAlcohol := true,
        statute := "Tax Code art. 188¹(1) row 1 (0.12 ლარი per litre per 1 % vol)" },
      { good := .spirits, name := "აქციზი", perUnitNum := 225, perUnitDen := 10, onPureAlcohol := true,
        statute := "Tax Code art. 188¹(1) row 5 (22.5 ლარი per litre of pure alcohol)" },
      { good := .cigarettes, name := "აქციზი", perUnitNum := 19, perUnitDen := 200, adValoremBp := 3000,
        statute := "Tax Code art. 188(1) HS 2402 20 (1.9 ლარი per 20) + art. 188(1¹) ა) (30 % of the retail price)" }] }

/-- art. 188(1): petrol 500, diesel 400 ლარი per tonne (kernel 2.1 `ExciseRule` per mass: the line's `"massG"`; the
code prints no density). -/
def fuel : List ExciseRule :=
  [{ good := .petrol, name := "აქციზი", perKgNum := 500, perKgDen := 1000, statute := "Tax Code art. 188(1) (2710 12: 500 ლარი per tonne)" },
   { good := .diesel, name := "აქციზი", perKgNum := 400, perKgDen := 1000, statute := "Tax Code art. 188(1) (diesel: 400 ლარი per tonne)" }]

def consumption : Family :=
  { name := "5111 დღგ, 5121 აქციზი", covers := [.vat, .excise],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else
        [dgg.basketCharge g.consumption "Tax Code art. 166 (18 %), art. 171(1) ა), ვ), ლ)"])
      ++ (if g.entity == .company && !g.company.sales.isEmpty then
            [dgg.businessCharge g.company "Tax Code art. 165(1) (100 000 ლარი), art. 166, art. 177 (proportional credit)"] else [])
      ++ aqcizi.charges g.consumption
      ++ exciseRuleCharges fuel g }

def consumptionUnsupported (g : CanonGlobal) : List String :=
  (if (consumptionX g).any (fun (s, x) => (s.good == .petrol || s.good == .diesel) && x.massG < 0) then
    ["excise on petrol (500) and diesel (400 ლარი per tonne, art. 188(1)): give the line's massG (no statutory density); without it the duty is 0"] else [])
  ++ (if g.consumption.any (fun s => s.good == .health || s.good == .education || s.good == .medicines) then
    ["VAT exemptions of art. 171(2) (not in the record read): health, education and medicines taxed at 18 %"] else [])
  ++ (if g.consumption.any (·.good == .spirits) then ["spirits of the row-7 codes (2208 20, 2208 60, …) are 15 ლარი per litre of pure alcohol; all spirits taken at 22.5"] else [])

#guard dgg.embedded { good := .food, amount := 11800 } == 1800
#guard dgg.embedded { good := .financial, amount := 11800 } == 0
#guard dgg.net { turnover := 100000, sales := [{ good := .other, net := 100000 }] } == 0
-- beer: 10 litres at 5 % = 0.5 l of pure alcohol × 12 = 6 ლარი
#guard aqcizi.duty { good := .beer, amount := 30, quantity := 10000, abvBp := 500 } == 6
-- spirits: 2 litres at 40 % = 0.8 l pure × 22.5 = 18
#guard aqcizi.duty { good := .spirits, amount := 60, quantity := 2000, abvBp := 4000 } == 18
-- 200 cigarettes costing 80 ლარი: 10 × 1.9 + 30 % × 80 = 43
#guard aqcizi.duty { good := .cigarettes, amount := 80, quantity := 200000 } == 43

#guard (fuel.getD 1 default).dutyOn { good := .diesel, amount := 3000, quantity := 1190000 } { massG := 1000000 } == 400

end GeGlobal
