import TaxKernel.Global2
import R5Common

/-!
# Saudi Arabia 2025: VAT (5111); excise not computed (5121)

Source: VAT Law (Royal Decree M/113, 2/11/1438H), laws.boe.gov.sa as archived on 2025-05-07
(`law/vat_2025.html`, `law/ARCHIVE_INDEX.tsv`), art. 2: "تطبق الضريبة بنسبة أساسية قدرها (15%) من قيمة التوريد أو
الاستيراد، مالم يرد نص الإعفاء أو فرض نسبة الصفر". The Law leaves the exempt and zero-rated supplies and the
registration threshold to the Implementing Regulations ("تحدد اللائحة التوريدات المعفاة من الضريبة، والتوريدات الخاضعة
للضريبة بنسبة الصفر"). Implementing Regulations (Board resolution 3839, 1438H, as amended to resolution 2-7-21,
1443H; ZATCA English text archived 2025-04-20, `law/zatca/vat_regs_en_2025.pdf`): Chapter Five exempts financial
services (margin-based, `financial`) and the lease or licence of residential real estate (`rent`); Chapter Six
zero-rates qualifying medicines and medical goods (`medicines`). Insurance other than life insurance stays taxable
(`insurance` at 15 %, life cover not split out). The business registration threshold is not applied. Excise Tax Law (Royal Decree M/86): text not reached (no GUID found in the boe listing): not computed.
-/

namespace SaGlobal
open TaxKernel TaxKernel.Global R5Common

def vat : Vat :=
  { name := "ضريبة القيمة المضافة", standard := 1500,
    classOf := fun g => match g with
      | .financial | .rent => .exempt
      | .medicines => .zero
      | _ => .standard }

def drink (sub : String) (bp : Int) (what : String) : ExciseRule :=
  { good := .nonAlcoholic, sub, name := "الضريبة الانتقائية", adValoremBp := bp, valueBase := .beforeTax, vatBp := 1500,
    statute := s!"ZATCA commodities subject to excise tax: {what}" }

def excise : List ExciseRule :=
  [drink "softDrinks" 5000 "soft drinks 50 %", drink "sweetenedDrinks" 5000 "sweetened beverages 50 %",
   drink "energyDrinks" 10000 "energy drinks 100 %",
   { good := .cigarettes, name := "الضريبة الانتقائية", adValoremBp := 10000, valueBase := .beforeTax, vatBp := 1500,
     statute := "Excise Tax Law (M/86) art. 2; Implementing Regulations art. 3(1) (tobacco 100 %)" },
   { good := .tobaccoOther, name := "الضريبة الانتقائية", adValoremBp := 10000, valueBase := .beforeTax, vatBp := 1500,
     statute := "Excise Tax Law (M/86) art. 2; Implementing Regulations art. 3(1) (tobacco 100 %)" }]

def consumption : Family :=
  { name := "5111 ضريبة القيمة المضافة, 5121 الضريبة الانتقائية", covers := [.vat, .excise],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else [vat.basketCharge g.consumption "VAT Law (M/113) art. 2 (15 %); Implementing Regulations ch. 5 (exempt), ch. 6 (zero)"])
      ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company "VAT Law (M/113) art. 2"] else [])
      ++ exciseRuleCharges excise g }

def consumptionUnsupported (g : CanonGlobal) : List String :=
  (if g.consumption.isEmpty then [] else
    ["VAT: life insurance (exempt) not split from other insurance (15 %)"])
  ++ (if g.entity == .company then ["VAT registration threshold (Implementing Regulations) not applied"] else [])
  ++ (if g.consumption.any (fun s => s.good == .cigarettes || s.good == .tobaccoOther) then
    ["tobacco excise: the standard retail price list floor (higher of declared and listed price) not applied"] else [])
  ++ (if (consumptionX g).any (fun (s, x) => s.good == .nonAlcoholic && x.sub == "") then
    ["nonAlcoholic lines without sub (softDrinks/sweetenedDrinks/energyDrinks): no excise applied"] else [])

#guard vat.embedded { good := .food, amount := 11500 } == 1500
#guard vat.embedded { good := .rent, amount := 11500 } == 0

-- 100 % on the price before excise and VAT: 230 = 100 + 100 + 15 % VAT
#guard (excise.getD 2 default).dutyOn { good := .nonAlcoholic, amount := 230 } { sub := "energyDrinks" } == 100

end SaGlobal
