import TaxKernel.Global2
import R5Common

/-!
# Oman 2025: VAT (5111); excise not computed (5121)

Source: VAT Law, Royal Decree 121/2020 (qanoon.om/p/2020/rd2020121/, as published; `law/om_vat.html`):
* art. 36: "تفرض الضريبة على استيراد وتوريد السلع أو الخدمات الخاضعة للضريبة بواقع (٥%) خمسة بالمائة".
* art. 47 exempt: 1 financial services; 2 health care and related goods and services; 3 education; 4 bare land;
  5 resale of residential property; 6 local passenger transport; 7 residential leases.
* art. 51 zero rate: 1 foodstuffs "التي يصدر بتحديدها قرار من الرئيس" (the decision was not read: all food zero-rated
  and flagged); 2 medicines and medical equipment; 7 crude oil, oil derivatives and natural gas.
* the mandatory registration threshold is defined (art. 1) but its amount is set by the Executive Regulation (not read).
The qanoon.om page is the act as published (Official Gazette); amendments after 2020, if any, are not shown: grade B.
Excise: Excise Tax Law (RD 23/2019; art. on rates: "يكون تحديد أو تعديل قيمة وأنواع السلع الانتقائية … وفئة الضريبة" by
decision; Qanoon.om archived 2025-06-20, `law/qanoon_rd2019023_20250620.html`); Ministerial Decision 112/2019 art. 2
table (archived 2025-03-27): tobacco 100, pork 100, alcoholic drinks 100, energy drinks 100, carbonated drinks 50;
Tax Authority Decision 34/2020 art. 3 (from 1 Oct 2020, archived 2025-07-20): sweetened drinks 50. MD 112/2019 art. 5:
value = retail price (or the standard list price, if higher) excluding the excise and VAT (beforeTax; list floor not
applied). The 2026 amendment (TA 192/2026, smoking-cessation products) is after 2025.
-/

namespace OmGlobal
open TaxKernel TaxKernel.Global R5Common

def vat : Vat :=
  { name := "ضريبة القيمة المضافة", standard := 500,
    classOf := fun g => match g with
      | .food | .medicines | .petrol | .diesel | .gas => .zero
      | .financial | .health | .education | .transport | .rent => .exempt
      | _ => .standard }

def exciseOf (good : Good) (sub : String) (bp : Int) (what : String) : ExciseRule :=
  { good, sub, name := "الضريبة الانتقائية", adValoremBp := bp, valueBase := .beforeTax, vatBp := 500,
    statute := s!"MD 112/2019 art. 2 (TA 34/2020 art. 3): {what}" }

def excise : List ExciseRule :=
  [exciseOf .nonAlcoholic "softDrinks" 5000 "carbonated drinks 50 %", exciseOf .nonAlcoholic "sweetenedDrinks" 5000 "sweetened drinks 50 %",
   exciseOf .nonAlcoholic "energyDrinks" 10000 "energy drinks 100 %",
   exciseOf .cigarettes "" 10000 "tobacco 100 %", exciseOf .tobaccoOther "" 10000 "tobacco 100 %",
   exciseOf .beer "" 10000 "alcoholic drinks 100 %", exciseOf .wine "" 10000 "alcoholic drinks 100 %",
   exciseOf .spirits "" 10000 "alcoholic drinks 100 %"]

def consumption : Family :=
  { name := "5111 ضريبة القيمة المضافة, 5121 الضريبة الانتقائية", covers := [.vat, .excise],
    run := fun _ g _ =>
      (if g.consumption.isEmpty then [] else
        [vat.basketCharge g.consumption "RD 121/2020 art. 36 (5 %), art. 47 (exempt), art. 51 (zero)"])
      ++ (if g.entity == .company && !g.company.sales.isEmpty then [vat.businessCharge g.company "RD 121/2020 art. 36, 47, 51"] else [])
      ++ exciseRuleCharges excise g }

def consumptionUnsupported (g : CanonGlobal) : List String :=
  (if g.consumption.any (·.good == .food) then ["VAT: zero rate only for the foods named by decision (art. 51(1)), not read: all food zero-rated"] else [])
  ++ (if g.entity == .company then ["VAT registration threshold (Executive Regulation) not applied"] else [])
  ++ (if g.consumption.any (fun s => s.good == .cigarettes || s.good == .tobaccoOther) then
    ["tobacco excise: the standard price list floor (MD 112/2019 art. 5) not applied"] else [])
  ++ (if (consumptionX g).any (fun (s, x) => s.good == .nonAlcoholic && x.sub == "") then
    ["nonAlcoholic lines without sub (softDrinks/sweetenedDrinks/energyDrinks): no excise applied"] else [])

#guard vat.embedded { good := .clothing, amount := 10500 } == 500
#guard vat.embedded { good := .rent, amount := 10500 } == 0

-- 100 % on the price before excise and VAT: 210 = 100 + 100 + 5 % VAT
#guard (excise.getD 2 default).dutyOn { good := .nonAlcoholic, amount := 210 } { sub := "energyDrinks" } == 100
#guard (excise.getD 1 default).dutyOn { good := .nonAlcoholic, amount := 1575 } { sub := "sweetenedDrinks" } == 500

end OmGlobal
