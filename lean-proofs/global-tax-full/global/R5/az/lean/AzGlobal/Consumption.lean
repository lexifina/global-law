import TaxKernel.Global
import R5Common

/-!
# Azerbaijan 2025: VAT (ƏDV, 5111) and excise (aksiz, 5121), Tax Code (Vergi Məcəlləsi, 2000)

Source: Global law `azerbaijan/national/acts/mecelle/2000/46948`, as in force on 2025-07-01
(`law/gl_vat_excise_2025-07-01.txt`; official text e-qanun.az).
* art. 173.1 (unchanged since 2001): "ƏDV-nin dərəcəsi hər vergi tutulan əməliyyatın … dəyərinin 18 faizidir".
* art. 155.1 (last changed Qanun 1033-VIQD, in force 2024-01-01): registration when taxable operations in any
  consecutive 12 months exceed "200.000 manatdan artıq".
* art. 164.1 (last changed Qanun 192-VIIQD, in force 2025-06-17) exemptions used for the basket: 164.1.2 financial
  services ("maliyyə … xidmətlərinin göstərilməsi"); 164.1.8 media products and books. Partial exemptions not applied
  to whole basket classes: 164.1.12 metro, 164.1.13 pre-school education, 164.1.27 wheat flour and bread,
  164.1.51-1 medical services in teaching hospitals.
* art. 175.4: input VAT in proportion to taxable turnover in total turnover (pro rata).
* art. 190.3 (last changed Qanun 1033-VIQD, in force 2024-01-01): 190.3.1-190.3.3 spirits 4,8 manat per litre;
  190.3.4-190.3.5 wine and sparkling wine 0,2; 190.3.6 beer 0,4; 190.3.8 cigarettes 45,5 manat per 1 000.
  190.3-1: the excise is the rate times the actual volume (quantity).
-/

namespace AzGlobal
open TaxKernel TaxKernel.Global R5Common

def vatStd : Int := 1800
def vatThreshold : Int := 200000

def edv : Vat :=
  { name := "Əlavə dəyər vergisi (ƏDV)", standard := vatStd, threshold := vatThreshold,
    classOf := fun g => match g with
      | .financial | .books | .newspapers => .exempt
      | _ => .standard }

def aksiz : Excise :=
  { rates := [
      perUnit .spirits "Aksiz" 48 10 "Tax Code art. 190.3.1-190.3.3 (4,8 manat per litre)",
      perUnit .wine "Aksiz" 2 10 "Tax Code art. 190.3.5 (0,2 manat per litre)",
      perUnit .beer "Aksiz" 4 10 "Tax Code art. 190.3.6 (0,4 manat per litre)",
      perUnit .cigarettes "Aksiz" 455 10000 "Tax Code art. 190.3.8 (45,5 manat per 1 000)"] }

def consumption : Family :=
  { name := "5111 ƏDV, 5121 aksiz", covers := [.vat, .excise],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else
        [edv.basketCharge g.consumption "Tax Code art. 173.1 (18 %), art. 164.1.2, 164.1.8"])
      ++ (if g.entity == .company && !g.company.sales.isEmpty then
            [edv.businessCharge g.company "Tax Code art. 155.1 (200 000 manat), art. 173.1, art. 175.4 (pro rata)"] else [])
      ++ aksiz.charges g.consumption }

def consumptionUnsupported (g : CanonGlobal) : List String :=
  (if g.consumption.any (fun s => s.good == .petrol || s.good == .diesel || s.good == .heatingOil) then
    ["excise on petroleum products (art. 190.1.6): rates not printed in art. 190.3 (set by the executive); not computed"] else [])
  ++ (if g.consumption.any (·.good == .tobaccoOther) then ["excise on cigars, e-liquids, heated tobacco (art. 190.3.7, 190.3.11-190.3.16): units not in the basket"] else [])
  ++ (if g.consumption.any (fun s => s.good == .food || s.good == .education || s.good == .health || s.good == .transport) then
    ["partial VAT exemptions not applied to whole basket classes: bread and wheat flour (164.1.27), pre-school education (164.1.13), metro (164.1.12), teaching-hospital care (164.1.51-1)"] else [])

#guard edv.embedded { good := .food, amount := 11800 } == 1800
#guard edv.embedded { good := .financial, amount := 11800 } == 0
#guard edv.net { turnover := 200000, sales := [{ good := .other, net := 200000 }] } == 0
#guard edv.net { turnover := 200001, sales := [{ good := .other, net := 200001 }] } == 36000
#guard aksiz.duty { good := .spirits, amount := 0, quantity := 500 } == 2
#guard aksiz.duty { good := .cigarettes, amount := 0, quantity := 20000 } == 0
#guard aksiz.duty { good := .cigarettes, amount := 0, quantity := 2000000 } == 91

end AzGlobal
